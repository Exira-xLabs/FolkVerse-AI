"""Explicit publication of actually reviewed units; drafts and stale reviews stay private."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from folkverse.config import ROOT
from folkverse.guide_retrieval import EvidencePassage
from folkverse.liaoning_inventory import collections, digest, write_json
from folkverse.liaoning_review import decisions, review_hash, reviewed, units


def publish(folder: Path, unit_ids: list[str]) -> int:
    by_id = {u.id: u for u in units(folder)}
    if not unit_ids or len(unit_ids) != len(set(unit_ids)):
        raise ValueError("Explicit distinct reviewed unit IDs required")
    entries = []
    for identifier in unit_ids:
        unit = by_id.get(identifier)
        if unit is None or not reviewed(folder, unit):
            raise ValueError(
                "Only actually reviewed, current, rights-cleared units can be published"
            )
        entries.append({"unit_id": unit.id, "review_hash": review_hash(folder, unit)})
    path = folder / "publication.json"
    previous = json.loads(path.read_text())["units"] if path.exists() else []
    selected = {entry["unit_id"]: entry for entry in previous + entries}
    write_json(path, {"version": "liaoning-unit-publication-v1", "units": list(selected.values())})
    return len(entries)


def published_unit_evidence(folder: Path = ROOT / "data/liaoning") -> list[EvidencePassage]:
    path = folder / "publication.json"
    if not path.exists():
        return []
    publication = json.loads(path.read_text())
    if publication.get("version") != "liaoning-unit-publication-v1":
        raise ValueError("Unsupported unit publication manifest")
    if not publication["units"]:
        return []
    by_id = {u.id: u for u in units(folder)}
    captures = collections(folder)
    by_row = {row["id"]: capture for capture in captures for row in capture["rows"]}
    latest = {d["unit_id"]: d for d in decisions(folder)}
    result = []
    for entry in publication["units"]:
        unit = by_id.get(entry["unit_id"])
        if (
            unit is None
            or not reviewed(folder, unit)
            or entry["review_hash"] != review_hash(folder, unit)
        ):
            continue
        review = latest[unit.id]
        supporting = {by_row[r]["source"]["id"]: by_row[r] for r in unit.supporting_rows}
        ids = ["unit_" + digest([unit.id, source_id])[:32] for source_id in sorted(supporting)]
        for source_id, identifier in zip(sorted(supporting), ids, strict=True):
            capture = supporting[source_id]
            source = capture["source"]
            result.append(
                EvidencePassage(
                    passage_id=identifier,
                    source_id=source_id,
                    text=unit.text,
                    language=unit.locale,
                    locator="reviewed-unit:" + unit.id,
                    rights_basis=unit.rights_basis,
                    institution=source["institution"],
                    source_title=source["title"],
                    canonical_url=source["url"],
                    fetched_at=datetime.fromisoformat(capture["fetched_at"]),
                    reviewed_at=datetime.fromisoformat(review["reviewed_at"]),
                    reviewer=review["reviewer"],
                    review_id=review["id"],
                    content_hash=digest([entry, capture["collection_hash"], review]),
                    exhibit_ids=["topic_" + digest(unit.topic_id)[:24]],
                    region_ids=unit.city_ids,
                    evidence_origin="reviewed_unit",
                    classification=unit.classification,
                    statement_variants=[unit.text],
                    required_support_ids=ids,
                )
            )
    return result


def published_unit_topics(folder: Path = ROOT / "data/liaoning") -> dict[str, dict[str, str]]:
    evidence = published_unit_evidence(folder)
    if not evidence:
        return {}
    by_unit = {u.id: u for u in units(folder)}
    aliases_path = folder / "search-aliases.json"
    aliases = json.loads(aliases_path.read_text())["aliases"] if aliases_path.exists() else {}
    materials_path = folder / "launch-material.json"
    materials = (
        json.loads(materials_path.read_text())["materials"] if materials_path.exists() else []
    )
    by_topic = {"launch-" + m["source_id"]: m for m in materials}
    result: dict[str, dict[str, str]] = {}
    for passage in evidence:
        unit = by_unit[passage.locator.removeprefix("reviewed-unit:")]
        material: dict[str, Any] = by_topic.get(unit.topic_id, {})
        title = aliases.get(material.get("source_id"), {}).get(
            unit.locale, material.get("title", unit.topic_id)
        )
        result.setdefault(passage.exhibit_ids[0], {})[unit.locale] = title
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=ROOT / "data/liaoning")
    parser.add_argument("--unit", action="append", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            {
                "published_reviewed_units": publish(args.folder, args.unit),
                "automatically_approved": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
