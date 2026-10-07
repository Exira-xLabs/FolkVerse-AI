"""Record all-city machine-assessed lookup readiness without altering human approvals."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / "data/liaoning"
    audit = json.loads((folder / "machine-source-audit.json").read_text())
    plan = json.loads((folder / "launch-plan.json").read_text())
    aliases = json.loads((folder / "search-aliases.json").read_text())["aliases"]
    registry = {
        s["id"]: s
        for s in json.loads((folder / "registry.json").read_text())["sources"]
    }
    records = audit["records"]
    cities = []
    for city in plan["cities"]:
        topics = [r for r in records if r["city_id"] == city["id"]]
        assert all(registry[r["source_id"]]["kind"] == "explanation" for r in topics)
        ready = (
            len(topics) >= plan["minimum_topics_per_city"]
            and len({r["subject"] for r in topics}) >= plan["minimum_subjects_per_city"]
        )
        ready &= all(
            set(r["facts"]) == {"en", "zh-CN"}
            and all(len(v) == 2 for v in r["facts"].values())
            for r in topics
        )
        cities.append(
            {
                "city_id": city["id"],
                "names": city["names"],
                "mode": "live_original_page_lookup",
                "ready": ready,
                "human_approved": False,
                "introduction": {
                    locale: (
                        "Explore these source-assessed topics in "
                        + city["names"][locale]
                        + ": "
                        if locale == "en"
                        else "可以从以下已比对来源的主题了解"
                        + city["names"][locale]
                        + "："
                    )
                    + "; ".join(aliases[r["source_id"]][locale] for r in topics)
                    for locale in ["en", "zh-CN"]
                },
                "topics": [
                    {
                        "source_id": r["source_id"],
                        "names": aliases[r["source_id"]],
                        "subject": r["subject"],
                        "url": registry[r["source_id"]]["url"],
                        "classification": r["classification"],
                        "context_and_example": r["facts"],
                        "followup": {
                            "en": "Would you like the background explained simply, or the concrete example?",
                            "zh-CN": "你想先听简单的背景说明，还是了解具体例子？",
                        },
                        "machine_assessed": True,
                        "human_approved": False,
                    }
                    for r in topics
                ],
            }
        )
    result = {
        "version": "liaoning-machine-launch-v1",
        "acceptance_basis": "Owner declined human review; machine-assessed source summaries are available through original-page-checked lookup. Human publication approvals are unchanged.",
        "machine_audit_sha256": hashlib.sha256(
            (folder / "machine-source-audit.json").read_bytes()
        ).hexdigest(),
        "cities": cities,
        "ready_cities": sum(c["ready"] for c in cities),
        "total_cities": len(cities),
        "topics": len(records),
        "locales": ["en", "zh-CN"],
        "exhaustive_knowledge": False,
        "runtime_rule": "Original source must remain accessible and match the audited raw and paragraph hashes. Changes fall back to bounded generic metadata, never silently retain stale summaries.",
    }
    assert result["ready_cities"] == 14 and result["topics"] == 42
    (folder / "machine-launch-manifest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    )
    print(
        "14/14 cities; 42 bilingual source-assessed topics; human approvals unchanged."
    )


if __name__ == "__main__":
    main()
