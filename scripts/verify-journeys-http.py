"""Non-browser Phase 04 BFF/API/DB smoke; creates and deletes only its own fresh sessions.

Use a local instance with provider quota disabled. This does not certify responsive visuals,
keyboard interaction or real-model explanations. No cookie, key or owner ID is recorded.
"""
import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx


def verify(base_url: str) -> dict:
    parts = urlsplit(base_url)
    if parts.hostname not in {"127.0.0.1", "localhost"} or parts.scheme != "http":
        raise ValueError("Verification is restricted to local HTTP instances")
    origin = f"{parts.scheme}://{parts.netloc}"
    checks: list[dict] = []

    def check(name: str, passed: bool, **observations: object) -> None:
        checks.append({"name": name, "passed": bool(passed), **observations})
        if not passed:
            raise AssertionError(name)
        print(f"PASS {name}")

    with httpx.Client(base_url=base_url, timeout=60, trust_env=False) as owner, httpx.Client(
        base_url=base_url, timeout=60, trust_env=False
    ) as stranger:
        try:
            check("production journey shell", owner.get("/journey").status_code == 200)
            check("owned route requires session", owner.get("/api/v1/journeys").status_code == 401)
            session = owner.post("/api/v1/session", headers={"Origin": origin})
            check("signed session proxy", session.status_code == 200 and "httponly" in session.headers.get("set-cookie", "").lower())
            body = {"locale": "en", "interests": [], "duration_minutes": 60, "region_id": "liaoning"}
            created = owner.post("/api/v1/journeys", json=body, headers={"Origin": origin})
            check("real BFF journey create", created.status_code == 200 and created.headers.get("cache-control") == "no-store")
            route = created.json()
            check("time uses stored estimates", route["total_minutes"] == sum(stop["estimated_minutes"] for stop in route["stops"]) and route["total_minutes"] <= 60,
                  stop_count=len(route["stops"]), total_minutes=route["total_minutes"], explanation_status=route["explanation_status"])
            check("small corpus notice", route["total_minutes"] == 60 or bool(route["notice"]))
            identifiers = [stop["exhibit_id"] for stop in route["stops"]]
            check("unique stops", len(identifiers) == len(set(identifiers)))
            for stop in route["stops"]:
                detail = owner.get(f'/api/v1/exhibits/{stop["exhibit_id"]}', params={"locale": "en"})
                check("stop resolves to published exhibit", detail.status_code == 200 and detail.json()["estimated_minutes"] == stop["estimated_minutes"])
                check("stop has actual source links", bool(stop["sources"]) and all(urlsplit(source["canonical_url"]).scheme == "https" for source in stop["sources"]))
            path = f'/api/v1/journeys/{route["id"]}'
            reloaded = owner.get(path).json()
            check("database reload", reloaded["stops"] == route["stops"] and reloaded["version"] == route["version"])
            translated = owner.get(path, params={"locale": "zh-CN"}).json()
            check("bilingual render", translated["locale"] == "zh-CN" and translated["total_minutes"] <= 60)
            second = owner.post("/api/v1/journeys", json=body, headers={"Origin": origin}).json()
            check("unchanged deterministic regeneration", [stop["exhibit_id"] for stop in second["stops"]] == identifiers)
            check("no unclaimed provider generation", route["explanation_status"] == second["explanation_status"] == "deterministic")
            if identifiers:
                started = owner.post("/api/v1/journeys", json={**body, "start_exhibit_id": identifiers[0]}, headers={"Origin": origin})
                check("explicit exhibit entry preserved through BFF", started.status_code == 200 and started.json()["stops"][0]["exhibit_id"] == identifiers[0])
            latest = owner.get("/api/v1/journeys", params={"locale": "zh-CN", "limit": 1}).json()
            check("latest list honors display locale and limit", len(latest["items"]) == 1 and latest["items"][0]["locale"] == "zh-CN")
            check("BFF forwards list bound validation", owner.get("/api/v1/journeys", params={"limit": 21}).status_code == 422)
            check("owner cannot be supplied", owner.post("/api/v1/journeys", json={**body, "owner_session": "invented"}, headers={"Origin": origin}).status_code == 422)
            check("BFF missing origin rejected", owner.post("/api/v1/journeys", json=body).status_code == 403)
            check("BFF foreign origin rejected", owner.post("/api/v1/journeys", json=body, headers={"Origin": "https://example.org"}).status_code == 403)
            check("bounded request body", owner.post("/api/v1/journeys", content='{"interests":["' + "a" * 70000 + '"]}', headers={"Origin": origin, "Content-Type": "application/json"}).status_code == 413)
            check("stranger bootstrap", stranger.post("/api/v1/session", headers={"Origin": origin}).status_code == 200)
            check("stranger cannot read route", stranger.get(path).status_code in {403, 404})
            check("stranger cannot edit route", stranger.patch(path, json={"ordered_exhibit_ids": []}, headers={"Origin": origin}).status_code in {403, 404})
            check("stranger list private", stranger.get("/api/v1/journeys").json()["items"] == [])
            removed = owner.patch(path, json={"ordered_exhibit_ids": [], "expected_version": route["version"]}, headers={"Origin": origin})
            check("remove all recalculates", removed.status_code == 200 and removed.json()["total_minutes"] == 0 and removed.json()["stops"] == [])
            check("empty route persists", owner.get(path).json()["stops"] == [])
            check("stale edit rejected", owner.patch(path, json={"ordered_exhibit_ids": identifiers, "expected_version": route["version"]}, headers={"Origin": origin}).status_code == 409)
        finally:
            for client in (owner, stranger):
                if client.cookies:
                    client.delete("/api/v1/session", headers={"Origin": origin})
    return {"checked_at": datetime.now(UTC).isoformat(), "scope": "local production web BFF / FastAPI / PostgreSQL; no browser or provider call", "browser_verified": False, "provider_generation_verified": False, "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:3014")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.base_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
