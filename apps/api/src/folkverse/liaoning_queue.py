"""Create editable, unapproved bilingual intake drafts and specific research tasks."""

import json
from pathlib import Path
from typing import Any, Literal

from folkverse.config import ROOT
from folkverse.liaoning_inventory import collections, write_json
from folkverse.liaoning_review import Unit, coverage_report, review_template, units


def prepare(folder: Path) -> dict[str, Any]:
    report = coverage_report(folder)
    snapshots = collections(folder)
    geography = next(c for c in snapshots if c["source"]["kind"] == "geography")
    rows = {r["id"]: r for c in snapshots for r in c["rows"]}
    associations = {a["entity_id"]: a for a in report["associations"]}
    pending = {u.id: u for u in units(folder)}
    tasks = []
    for city in report["launch_manifest"]:
        city_row = next(
            r
            for r in geography["rows"]
            if r.get("level") == "city" and r["name_original"] == city["names"]["zh-CN"] + "市"
        )
        counties = [
            r
            for r in geography["rows"]
            if r.get("level") == "county" and r["city_code"] == city_row["native_code"]
        ]
        base = f"{city['id']}-city-introduction"
        zh = (
            f"按辽宁省2026年上半年行政区划目录，{city_row['name_original']}下辖"
            f"{len(counties)}个县级行政区。这里的统计反映该版本的行政区划，"
            "不能据此判断某一文化传统的历史起源。"
        )
        en = (
            f"The Liaoning administrative directory for the first half of 2026 lists "
            f"{len(counties)} county-level divisions under {city['names']['en']}. "
            "This describes administrative coverage in that edition; it does not establish "
            "where a cultural tradition originated."
        )
        city_texts: list[tuple[Literal["en", "zh-CN"], str]] = [("zh-CN", zh), ("en", en)]
        for locale, text in city_texts:
            unit = Unit(
                id=base + "-" + locale,
                topic_id=base,
                city_ids=[city["id"]],
                subject="history_geography",
                locale=locale,
                kind="city_introduction",
                text=text,
                supporting_rows=[city_row["id"]] + [r["id"] for r in counties],
                classification="source_statement",
                translation_of=base + "-zh-CN" if locale == "en" else None,
            )
            pending.setdefault(unit.id, unit)  # Never replace an operator's edited draft.
        for entity_id in city["candidate_topic_ids"]:
            association = associations[entity_id]
            row = rows[association["row_id"]]
            topic = f"{city['id']}-{entity_id}"
            zh = (
                f"所采集名录列有“{row['name_original']}”。原表的地区或单位字段为"
                f"“{row['locality_original']}”。这是名录或申报单位信息，不代表历史起源。"
            )
            en = (
                f"The collected inventory lists “{row['name_original']}”, with the locality "
                f"or institution field “{row['locality_original']}”. This is a catalog "
                "association; historical origin needs separate supporting evidence."
            )
            topic_texts: list[tuple[Literal["en", "zh-CN"], str]] = [("zh-CN", zh), ("en", en)]
            for locale, text in topic_texts:
                unit = Unit(
                    id=topic + "-" + locale,
                    topic_id=topic,
                    city_ids=[city["id"]],
                    subject=association["subject"],
                    locale=locale,
                    kind="introduction",
                    text=text,
                    supporting_rows=[row["id"]],
                    classification="source_statement",
                    translation_of=topic + "-zh-CN" if locale == "en" else None,
                )
                pending.setdefault(unit.id, unit)
            tasks.append(
                {
                    "topic_id": topic,
                    "city_id": city["id"],
                    "entity_id": entity_id,
                    "supporting_rows": [row["id"]],
                    "name_original": row["name_original"],
                    "status": "metadata_draft_only",
                    "required_research": [
                        "Find attributable context beyond list membership",
                        "Document a useful term or real example with a locator",
                        "Draft and review grounded questions in Chinese and English",
                        "Check chronology, provenance, shared traditions and conflicts",
                        "Resolve excerpt/translation rights and inspect source originals",
                    ],
                    "ready_for_publication": False,
                }
            )
    write_json(
        folder / "units.json",
        {"version": "liaoning-units-v1", "units": [u.model_dump() for u in pending.values()]},
    )
    write_json(
        folder / "research-queue.json", {"version": "liaoning-research-queue-v1", "tasks": tasks}
    )
    review_template(folder)
    coverage_report(folder)
    return {
        "draft_units": len(pending),
        "topic_research_tasks": len(tasks),
        "automatically_approved": 0,
    }


def main() -> None:
    print(json.dumps(prepare(ROOT / "data/liaoning"), indent=2))


if __name__ == "__main__":
    main()
