"""Bounded official-source search over the collected directory; no arbitrary URL tool."""

import asyncio
import hashlib
import ipaddress
import json
import re
import socket
import time
from collections import OrderedDict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import httpx

from folkverse.config import ROOT
from folkverse.guide_retrieval import EvidencePassage, Locale, tokenize
from folkverse.liaoning_inventory import AGENT, Article

MAX_LOOKUP_BYTES = 1024 * 1024
LOOKUP_VERSION = "official-directory-lookup-v1"
HOSTS = {"www.ln.gov.cn", "whly.ln.gov.cn", "mzt.ln.gov.cn"}


def checked_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in HOSTS
        or parsed.username
        or parsed.password
        or parsed.port not in {None, 443}
        or parsed.fragment
    ):
        raise ValueError("Unregistered official source")
    return url


async def public_ip(host: str) -> str:
    results = await asyncio.to_thread(socket.getaddrinfo, host, 443, type=socket.SOCK_STREAM)
    addresses = sorted({str(row[4][0]) for row in results})
    if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
        raise ValueError("Nonpublic official-source address")
    return addresses[0]


async def pinned_get(client: httpx.AsyncClient, url: str) -> tuple[int, bytes, str | None]:
    parsed = urlsplit(checked_url(url))
    assert parsed.hostname is not None
    address = await public_ip(parsed.hostname)
    authority = f"[{address}]" if ":" in address else address
    pinned = urlunsplit(("https", authority, parsed.path or "/", parsed.query, ""))
    # httpcore's SNI extension authenticates the original hostname while connecting
    # to the validated IP. A second DNS lookup cannot redirect this request internally.
    async with client.stream(
        "GET",
        pinned,
        headers={"Host": parsed.hostname, "User-Agent": AGENT, "Accept-Encoding": "identity"},
        extensions={"sni_hostname": parsed.hostname},
    ) as response:
        if response.headers.get("content-encoding", "identity").lower() != "identity":
            raise ValueError("Compressed lookup response is not accepted")
        data = bytearray()
        async for chunk in response.aiter_raw():
            if len(data) + len(chunk) > MAX_LOOKUP_BYTES:
                raise ValueError("Official response exceeds bound")
            data.extend(chunk)
        return response.status_code, bytes(data), response.headers.get("location")


async def fetch_official(url: str) -> bytes:
    async with asyncio.timeout(8):
        async with httpx.AsyncClient(follow_redirects=False, trust_env=False, timeout=5) as client:
            for _ in range(4):
                parsed = urlsplit(checked_url(url))
                status, raw, _ = await pinned_get(client, f"https://{parsed.hostname}/robots.txt")
                if status == 200:
                    robots = RobotFileParser()
                    robots.parse(raw.decode("utf-8", errors="replace").splitlines())
                    if not robots.can_fetch(AGENT, url):
                        raise ValueError("Official source disallows collection")
                elif status not in {404, 410}:
                    raise ValueError("Official source access policy unavailable")
                status, raw, redirect = await pinned_get(client, url)
                if status == 200:
                    return raw
                if status in {301, 302, 303, 307, 308} and redirect:
                    url = checked_url(urljoin(url, redirect))
                    continue
                raise ValueError("Official page unavailable")
            raise ValueError("Official redirect limit exceeded")


class OfficialLookup:
    def __init__(self, folder: Path = ROOT / "data/liaoning", enabled: bool = True):
        self.folder, self.enabled = folder, enabled
        self.cache: OrderedDict[str, tuple[float, EvidencePassage]] = OrderedDict()
        self.semaphore = asyncio.Semaphore(2)
        self.aliases: dict[str, dict[str, str]] = {}
        path = folder / "search-aliases.json"
        if path.exists():
            self.aliases = json.loads(path.read_text())["aliases"]

    def directory(self) -> list[dict[str, Any]]:
        path = self.folder / "registry.json"
        if not path.exists():
            return []
        sources = [s for s in json.loads(path.read_text())["sources"] if s["kind"] == "explanation"]
        discovery = self.folder / "profile-discovery.json"
        if discovery.exists():
            registered = {s["url"] for s in sources}
            for url, title in json.loads(discovery.read_text())["profiles"].items():
                if url not in registered:
                    checked_url(url)
                    sources.append(
                        {
                            "id": "directory-" + hashlib.sha256(url.encode()).hexdigest()[:24],
                            "url": url,
                            "title": title,
                            "locality": title.split("·")[0],
                            "institution": "Liaoning Department of Culture and Tourism",
                        }
                    )
        return sources

    def search(self, question: str, locale: Locale) -> list[dict[str, Any]]:
        query = set(tokenize(question)) - {
            "the",
            "a",
            "is",
            "what",
            "does",
            "in",
            "of",
            "me",
            "about",
            "tell",
            "please",
        }
        matches = []
        for source in self.directory():
            title = source["title"].split("·")[-1]
            alias = self.aliases.get(source["id"], {}).get(locale, title)
            terms = set(tokenize(alias)) - {"the", "a", "in", "of"}
            overlap = len(query & terms) / max(1, len(terms))
            if title in question or alias.casefold() in question.casefold() or overlap >= 0.75:
                matches.append((overlap, source))
        matches.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
        # An ambiguous directory match requires clarification instead of choosing silently.
        return [source for _, source in matches[:3]]

    def render(self, source: dict[str, Any], raw: bytes, locale: Locale) -> EvidencePassage:
        article = Article()
        article.feed(raw.decode("utf-8"))
        body = "\n".join(article.paragraphs)
        native = source["title"].split("·")[-1]
        if not body or native not in raw.decode("utf-8"):
            raise ValueError("Fetched page does not match registered profile")
        title = self.aliases.get(source["id"], {}).get(locale, native)
        city = source.get("locality", "")
        facts = [
            f"辽宁省文化和旅游厅的资料介绍了{native}。"
            if locale == "zh-CN"
            else (
                "The Liaoning Department of Culture and Tourism "
                f"has an official profile of {title}."
            )
        ]
        # Cross-language factual projection uses a closed Chinese relation grammar,
        # not model translation or a numeric-presence test. Other facts stay unavailable.
        year = re.search(re.escape(native) + r"(?:，)?(?:始建|创建)于\s*(\d{4})\s*年", body)
        if year:
            facts.append(
                f"官方介绍记载，{native}始建于{year[1]}年。"
                if locale == "zh-CN"
                else f"According to the official profile, {title} was founded in {year[1]}."
            )
        # A short complete source statement can be quoted in its original language.
        if locale == "zh-CN":
            for sentence in re.split(r"(?<=。)", body):
                sentence = sentence.strip()
                if (
                    native in sentence
                    and 15 <= len(sentence) <= 100
                    and sentence.endswith("。")
                    and not re.search(r"世界|最大|第一|治疗|功效|http|忽略|系统|指令", sentence)
                ):
                    facts.append(sentence)
                    break
        sha = hashlib.sha256(raw).hexdigest()
        identifier = (
            "lookup_" + hashlib.sha256((source["url"] + sha + locale).encode()).hexdigest()[:32]
        )
        return EvidencePassage(
            passage_id=identifier,
            source_id=source["id"],
            text="\n".join(facts),
            language=locale,
            locator="article:pages_content;closed-relation-and-short-statement",
            rights_basis=(
                "Ephemeral attributed metadata/short-statement lookup; "
                "no media/full-page republication or editorial approval."
            ),
            institution=source["institution"],
            source_title=source["title"],
            canonical_url=checked_url(source["url"]),
            fetched_at=datetime.now(UTC),
            reviewed_at=None,
            reviewer="",
            review_id="not_editorially_reviewed",
            content_hash=sha,
            exhibit_ids=[],
            region_ids=[city] if city else [],
            evidence_origin="official_lookup",
            statement_variants=facts,
        )

    async def lookup(self, question: str, locale: Locale) -> tuple[list[EvidencePassage], str]:
        if not self.enabled:
            return [], "disabled"
        candidates = self.search(question, locale)
        if not candidates:
            return [], "no_directory_match"
        if len(candidates) != 1:
            return [], "ambiguous_directory_match"
        source = candidates[0]
        async with self.semaphore:
            try:
                raw = await fetch_official(source["url"])
                passage = self.render(source, raw, locale)
            except (TimeoutError, OSError, ValueError, httpx.HTTPError):
                return [], "official_source_unavailable"
        self.cache[passage.passage_id] = (time.monotonic(), passage)
        self.cache.move_to_end(passage.passage_id)
        while len(self.cache) > 64:
            self.cache.popitem(last=False)
        return [passage], "original_page_checked"

    async def current(self, passage: EvidencePassage, refresh: bool = False) -> bool:
        cached = self.cache.get(passage.passage_id)
        if not cached or cached[1] != passage or time.monotonic() - cached[0] > 300:
            return False
        if not refresh:
            return True
        try:
            raw = await fetch_official(passage.canonical_url)
            return hashlib.sha256(raw).hexdigest() == passage.content_hash
        except (TimeoutError, OSError, ValueError, httpx.HTTPError):
            return False
