"""Refresh original profiles and record machine-summary bindings without human approvals."""

import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
from folkverse.config import ROOT
from folkverse.guide_lookup import OfficialLookup, fetch_official


async def run(output: Path, source_ids: list[str] | None = None):
    if output.exists():
        raise ValueError("Use a fresh evidence path.")
    lookup = OfficialLookup()
    records = json.loads(
        (ROOT / "data/liaoning/machine-source-audit.json").read_text()
    )["records"]
    if source_ids:
        selected = set(source_ids)
        if not selected <= {r["source_id"] for r in records}:
            raise ValueError("Unknown assessed source")
        records = [r for r in records if r["source_id"] in selected]
    directory = {r["id"]: r for r in lookup.directory()}
    semaphore = asyncio.Semaphore(2)

    async def assess(record):
        source = directory[record["source_id"]]
        async with semaphore:
            try:
                raw = await fetch_official(source["url"])
                matching = (
                    hashlib.sha256(raw).hexdigest() == record["source_raw_sha256"]
                )
                summaries = [
                    lookup.audited_summary(source["id"], raw, locale)
                    for locale in ("en", "zh-CN")
                ]
                return {
                    "source_id": source["id"],
                    "city_id": record["city_id"],
                    "url": source["url"],
                    "original_hash_current": matching,
                    "bilingual_binding_current": all(s is not None for s in summaries),
                    "error": None,
                }
            except (TimeoutError, OSError, ValueError, httpx.HTTPError) as error:
                return {
                    "source_id": source["id"],
                    "city_id": record["city_id"],
                    "url": source["url"],
                    "original_hash_current": False,
                    "bilingual_binding_current": False,
                    "error": type(error).__name__,
                }

    rows = await asyncio.gather(*(assess(r) for r in records))
    result = {
        "version": "liaoning-machine-source-refresh-v1",
        "checked_at": datetime.now(UTC).isoformat(),
        "machine_audit_sha256": lookup.audit_signature(),
        "human_review_performed": False,
        "profiles": rows,
        "passed": sum(r["bilingual_binding_current"] for r in rows),
        "total": len(rows),
        "cities": len({r["city_id"] for r in rows}),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "profiles"}, indent=2))
    return result["passed"] == result["total"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", action="append")
    args = parser.parse_args()
    raise SystemExit(0 if asyncio.run(run(args.output, args.source)) else 1)
