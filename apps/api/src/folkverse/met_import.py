"""Bounded, cached Met adapter. A denial is recorded, never bypassed."""

import hashlib
import json
import time
from datetime import UTC, datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from sqlalchemy.orm import Session

from folkverse.config import ROOT
from folkverse.content import verified_media_bytes
from folkverse.content_models import Artifact, Media, Source

BASE = "https://collectionapi.metmuseum.org/public/collection"
CACHE = ROOT / ".local/met"
ALLOWED_HOSTS = {"collectionapi.metmuseum.org", "images.metmuseum.org"}


class ImportFailure(Exception):
    pass


def checked_url(url: str) -> str:
    try:
        parts = urlsplit(url)
        trusted = (
            parts.scheme == "https"
            and parts.hostname in ALLOWED_HOSTS
            and not parts.username
            and not parts.port
        )
    except ValueError as exc:
        raise ImportFailure("Invalid upstream URL") from exc
    if not trusted:
        raise ImportFailure("Untrusted upstream URL")
    return url


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> Any:
        return super().redirect_request(req, fp, code, msg, headers, checked_url(newurl))


def download(url: str, maximum: int = 2_000_000) -> bytes:
    checked_url(url)
    for attempt in range(3):
        try:
            request = Request(
                url, headers={"User-Agent": "FolkVerseResearch/0.2 (bounded local import)"}
            )
            with build_opener(SafeRedirect()).open(request, timeout=20) as response:
                raw = bytes(response.read(maximum + 1))
                if len(raw) > maximum:
                    raise ImportFailure("Response exceeds size limit")
                return raw
        except HTTPError as exc:
            if exc.code in {403, 401}:
                raise ImportFailure(f"Access denied: HTTP {exc.code}; no retry") from exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise ImportFailure(f"HTTP {exc.code}") from exc
            retry = exc.headers.get("Retry-After", "2")
            # Never retry earlier than the server's requested delay; defer long/date-valued delays.
            if not retry.isdecimal() or int(retry) > 5:
                raise ImportFailure("Rate limited; defer import until Retry-After") from exc
            time.sleep(max(1, int(retry)))
        except (URLError, TimeoutError) as exc:
            if attempt == 2:
                raise ImportFailure("Network timeout or unavailable upstream") from exc
            time.sleep(attempt + 1)
    raise ImportFailure("Upstream unavailable")


def fetch_json(url: str, refresh: bool = False) -> tuple[dict[str, Any], str, datetime]:
    CACHE.mkdir(parents=True, exist_ok=True)
    index = CACHE / f"{hashlib.sha256(url.encode()).hexdigest()}.index.json"
    if index.exists() and not refresh:
        meta = json.loads(index.read_text())
        raw = (CACHE / f"{meta['hash']}.json").read_bytes()
        if hashlib.sha256(raw).hexdigest() != meta["hash"]:
            raise ImportFailure("Cached payload hash mismatch")
        fetched = datetime.fromisoformat(meta["fetched_at"])
    else:
        raw = download(url)
        fetched = datetime.now(UTC)
        # Reject invalid JSON before caching it as a successful response.
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                raise ValueError()
        except (ValueError, UnicodeError) as exc:
            raise ImportFailure("Invalid JSON response") from exc
        digest = hashlib.sha256(raw).hexdigest()
        (CACHE / f"{digest}.json").write_bytes(raw)
        index.write_text(
            json.dumps({"url": url, "hash": digest, "fetched_at": fetched.isoformat()})
        )
        time.sleep(0.15)
    return json.loads(raw), raw.decode("utf8"), fetched


def search(
    query: str, offset: int, limit: int, refresh: bool = False, base_url: str = BASE
) -> list[int]:
    if not 1 <= limit <= 50 or offset < 0 or offset + limit > 10000:
        raise ImportFailure("Search limit must be 1–50 and offset + limit <= 10000")
    params = urlencode(
        {
            "q": query,
            "hasImages": "true",
            "geoLocation": "China",
            "departmentId": 6,
            "offset": offset,
            "limit": limit,
        }
    )
    data, _, _ = fetch_json(f"{base_url}/v1.1/search?{params}", refresh)
    ids = data.get("objectIDs") or []
    if not isinstance(data.get("total"), int) or not isinstance(ids, list) or len(ids) > limit:
        raise ImportFailure("Unexpected paginated search schema")
    if not all(type(identifier) is int and identifier > 0 for identifier in ids):
        raise ImportFailure("Invalid object identifiers")
    return ids


def import_object(
    db: Session, identifier: int, refresh: bool = False, base_url: str = BASE
) -> dict[str, Any]:
    if identifier < 1:
        raise ImportFailure("Invalid object identifier")
    data, raw, fetched = fetch_json(f"{base_url}/v1/objects/{identifier}", refresh)
    if data.get("objectID") != identifier or not isinstance(data.get("title"), str):
        raise ImportFailure("Object payload identity/schema mismatch")
    sid, aid = f"met-source-{identifier}", f"met-{identifier}"
    digest = hashlib.sha256(raw.encode()).hexdigest()
    source = db.get(Source, sid)
    changed = source is None or source.raw_hash != digest
    if source is None:
        source = Source(
            id=sid,
            status="draft",
            institution="The Metropolitan Museum of Art",
            external_id=str(identifier),
        )
        db.add(source)
    source.title = data["title"]
    source.canonical_url = f"https://www.metmuseum.org/art/collection/search/{identifier}"
    if changed:
        source.fetched_at = fetched
    source.raw_hash, source.raw_payload = digest, raw
    source.rights_basis = "Met Open Access API metadata: CC0; image rights checked separately"
    if changed:
        source.status, source.review_id = "draft", None
    db.flush()
    artifact = db.get(Artifact, aid)
    if artifact is None:
        artifact = Artifact(
            id=aid,
            status="draft",
            institution="The Metropolitan Museum of Art",
            external_object_id=str(identifier),
            source_id=sid,
        )
        db.add(artifact)
    artifact.catalog_title = data["title"]
    artifact.catalog_date = str(data.get("objectDate") or "")
    artifact.medium = str(data.get("medium") or "")
    artifact.origin = {
        k: str(data.get(k) or "") for k in ["country", "region", "subregion", "city", "culture"]
    }
    artifact.current_location = str(data.get("repository") or "The Metropolitan Museum of Art")
    if changed:
        artifact.status, artifact.review_id = "draft", None
    db.flush()
    image_url = str(data.get("primaryImage") or "")
    media_id = f"met-image-{identifier}"
    media = db.get(Media, media_id)
    image_error = None
    eligible = data.get("isPublicDomain") is True and not data.get("rightsAndReproduction")
    if media is not None and (changed or media.url != image_url):
        media.status, media.review_id = "draft", None
        media.hash, media.storage_key = None, None
    if image_url:
        if media is None:
            media = Media(
                id=media_id, source_id=sid, artifact_id=aid, status="draft", role="reference"
            )
            db.add(media)
        media.url = image_url
        media.rights_code = "CC0" if eligible else "unresolved"
        if changed:
            media.rights_status = "candidate" if eligible else "blocked"
        media.rights_evidence = {
            "isPublicDomain": data.get("isPublicDomain"),
            "rightsAndReproduction": data.get("rightsAndReproduction"),
            "creditLine": data.get("creditLine"),
            "source_hash": digest,
            "policy": "https://www.metmuseum.org/hubs/open-access",
        }
        if eligible and not verified_media_bytes(media):
            try:
                image = download(image_url, 12_000_000)
                if not image.startswith(b"\xff\xd8\xff"):
                    raise ImportFailure("Expected a JPEG image")
                media.hash = hashlib.sha256(image).hexdigest()
                target = CACHE / "images" / f"{media.hash}.jpg"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(image)
                media.storage_key = str(target.relative_to(ROOT))
            except ImportFailure as exc:
                image_error = str(exc)
                media.hash, media.storage_key = None, None
    elif media:
        media.rights_status, media.status, media.review_id = "blocked", "draft", None
        media.hash, media.storage_key = None, None
    db.flush()
    return {
        "id": aid,
        "title": artifact.catalog_title,
        "source_hash": digest,
        "status": artifact.status,
        "cc0_candidate": eligible,
        "image_downloaded": bool(media and media.hash),
        "image_error": image_error,
        "origin": artifact.origin,
        "current_location": artifact.current_location,
    }
