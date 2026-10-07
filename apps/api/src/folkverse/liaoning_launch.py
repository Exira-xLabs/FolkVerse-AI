"""Prepare source-bound launch drafts and readable review packets, without approval."""

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from folkverse.config import ROOT
from folkverse.liaoning_inventory import collections, write_json
from folkverse.liaoning_review import Unit, coverage_report, review_template, units


class Material(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    source_id: str
    source_raw_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    city_id: str
    subject: str
    title: str
    classification: Literal["source_statement", "folklore"]
    context: dict[str, str]
    example: dict[str, str]
    status: Literal["assistant_draft_requires_human_review"]


def prepare(folder: Path) -> dict[str, Any]:
    payload = json.loads((folder / "launch-material.json").read_text())
    if payload.get("version") != "liaoning-launch-material-v1":
        raise ValueError("Unsupported launch material version")
    materials = [Material.model_validate(m) for m in payload["materials"]]
    plan = json.loads((folder / "launch-plan.json").read_text())
    city_ids = {c["id"] for c in plan["cities"]}
    captures = {c["source"]["id"]: c for c in collections(folder)}
    pending = {u.id: u for u in units(folder)}
    if len({m.source_id for m in materials}) != len(materials):
        raise ValueError("Duplicate launch source")
    for material in materials:
        capture = captures.get(material.source_id)
        if material.city_id not in city_ids or not capture or not capture["rows"]:
            raise ValueError("Material needs an in-scope city and captured source")
        if (
            capture["raw_sha256"] != material.source_raw_sha256
            or capture["source"]["kind"] != "explanation"
            or capture["source"]["subject_hint"] != material.subject
            or capture["source"]["title"] != material.title
        ):
            raise ValueError("Material does not match its registered explanatory source")
        row = capture["rows"][0]
        for bilingual in [material.context, material.example]:
            if set(bilingual) != {"en", "zh-CN"} or any(not t.strip() for t in bilingual.values()):
                raise ValueError("Material requires substantive text in both languages")
        topic = "launch-" + material.source_id
        for kind in ["introduction", "context", "example", "question"]:
            for locale in ["zh-CN", "en"]:
                if kind == "introduction":
                    text = (
                        f"辽宁省文化和旅游厅的介绍以“{material.title}”为主题。下面从背景和具体例子来理解这个地点。"
                        if locale == "zh-CN"
                        else (
                            "The Liaoning Department of Culture and Tourism profile describes "
                            f"“{material.title}”. Explore its background and a concrete example."
                        )
                    )
                elif kind == "question":
                    text = (
                        "你想先了解这里的背景，还是从刚才的具体例子说起？"
                        if locale == "zh-CN"
                        else (
                            "Would you like to explore the background first, "
                            "or start with the concrete example?"
                        )
                    )
                else:
                    text = (material.context if kind == "context" else material.example)[locale]
                unit = Unit.model_validate(
                    {
                        "id": f"{topic}-{kind}-{locale}",
                        "topic_id": topic,
                        "city_ids": [material.city_id],
                        "subject": material.subject,
                        "locale": locale,
                        "kind": kind,
                        "text": text,
                        "supporting_rows": [row["id"]],
                        "classification": material.classification,
                        "rights_basis": (
                            "Original concise paraphrase from attributed official profile; "
                            "human rights clearance remains pending."
                        ),
                        "translation_of": f"{topic}-{kind}-zh-CN" if locale == "en" else None,
                    }
                )
                pending.setdefault(unit.id, unit)
    write_json(
        folder / "units.json",
        {"version": "liaoning-units-v1", "units": [u.model_dump() for u in pending.values()]},
    )
    review_template(folder)
    report = coverage_report(folder)
    prepared = []
    for city in plan["cities"]:
        relevant = [m for m in materials if m.city_id == city["id"]]
        prepared.append(
            {
                "city_id": city["id"],
                "topics": len(relevant),
                "subjects": sorted({m.subject for m in relevant}),
                "draft_floor_prepared": len(relevant) >= plan["minimum_topics_per_city"]
                and len({m.subject for m in relevant}) >= plan["minimum_subjects_per_city"],
                "human_approved": False,
                "published": False,
            }
        )
        lines = [
            f"# {city['names']['en']} / {city['names']['zh-CN']} — review drafts",
            "",
            (
                "Assistant drafts only. Check the linked originals, classification, "
                "rights and EN/ZH wording before approval."
            ),
            "",
        ]
        for material in relevant:
            capture = captures[material.source_id]
            lines += [
                f"## {material.title}",
                "",
                f"Source: {capture['source']['url']}",
                f"Edition: {capture['source']['reference_date']}; subject: {material.subject}; "
                f"classification: {material.classification}",
                f"Raw SHA256: {capture['raw_sha256']}",
                "",
            ]
            for unit in pending.values():
                if unit.topic_id == "launch-" + material.source_id:
                    lines += [f"**{unit.kind} / {unit.locale}** ({unit.id})", "", unit.text, ""]
        (folder / "review").mkdir(exist_ok=True)
        (folder / "review" / f"{city['id']}.md").write_text("\n".join(lines))
    result = {
        "version": "liaoning-launch-preparation-v1",
        "cities": prepared,
        "draft_units": len(pending),
        "prepared_cities": sum(c["draft_floor_prepared"] for c in prepared),
        "approved_units": report["summary"]["reviewed_explanation_units"],
        "automatically_published": False,
    }
    write_json(folder / "launch-preparation.json", result)
    return result


def main() -> None:
    result = prepare(ROOT / "data/liaoning")
    print(json.dumps({key: value for key, value in result.items() if key != "cities"}, indent=2))


if __name__ == "__main__":
    main()
