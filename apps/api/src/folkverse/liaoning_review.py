"""Version-bound human curation and honest province-wide inventory/launch reports."""

import argparse
import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.orm import Session

from folkverse.config import ROOT, Settings
from folkverse.content import published_exhibits
from folkverse.content_models import ExhibitRegion
from folkverse.database import make_engine
from folkverse.liaoning_inventory import SUBJECTS, collections, digest, registry, write_json


class Unit(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,100}$")
    topic_id: str
    city_ids: list[str] = Field(min_length=1)
    subject: str
    locale: Literal["en", "zh-CN"]
    kind: Literal[
        "city_introduction",
        "introduction",
        "context",
        "term",
        "example",
        "question",
        "chronology",
        "technique",
        "significance",
        "conflict",
        "not_applicable",
    ]
    text: str = Field(min_length=1, max_length=12000)
    supporting_rows: list[str] = Field(min_length=1)
    classification: Literal[
        "source_statement", "history", "interpretation", "folklore", "creative_adaptation"
    ]
    rights_basis: str = ""
    translation_of: str | None = None
    applicability_reason: str | None = None

    @model_validator(mode="after")
    def valid_unit(self) -> "Unit":
        if not self.text.strip() or self.subject not in SUBJECTS:
            raise ValueError("Draft needs nonblank text and a known subject")
        if self.kind == "not_applicable" and not self.applicability_reason:
            raise ValueError("Not applicable needs an attributed reason")
        return self


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    unit_id: str
    review_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    decision: Literal["pending", "approved", "rejected", "withdrawn"] = "pending"
    reviewer: str | None = None
    reviewed_at: str | None = None
    notes: str | None = None
    attest_human_review: bool = False
    rights_cleared: bool = False
    source_support_checked: bool = False
    translation_checked: bool = False

    @model_validator(mode="after")
    def real_review(self) -> "Decision":
        if self.decision != "pending":
            if not self.attest_human_review or any(
                not value or not value.strip()
                for value in (self.reviewer, self.reviewed_at, self.notes)
            ):
                raise ValueError("Decisions require attributed actual human review")
            assert self.reviewed_at
            if datetime.fromisoformat(self.reviewed_at).tzinfo is None:
                raise ValueError("Review time needs timezone")
        if self.decision == "approved" and not (
            self.rights_cleared and self.source_support_checked
        ):
            raise ValueError("Approval requires rights and actual source-support checks")
        return self


class Relation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,100}$")
    row_ids: list[str] = Field(min_length=2)
    kind: Literal["same_entity", "different_entities", "shared_tradition", "conflicting_accounts"]
    explanation: str = Field(min_length=1)
    status: Literal["pending", "confirmed"] = "pending"
    reviewer: str | None = None
    reviewed_at: str | None = None
    attest_human_review: bool = False

    @model_validator(mode="after")
    def human_identity_check(self) -> "Relation":
        if len(set(self.row_ids)) != len(self.row_ids):
            raise ValueError("Relations require distinct inventory rows")
        if self.status == "confirmed" and (
            not self.attest_human_review
            or not self.reviewer
            or not self.reviewer.strip()
            or not self.reviewed_at
            or datetime.fromisoformat(self.reviewed_at).tzinfo is None
        ):
            raise ValueError(
                "Identity/conflict confirmation requires actual attributed human review"
            )
        return self


def link(folder: Path, relation: Relation) -> None:
    bindings = {
        r["id"]: digest([c["collection_hash"], r])
        for c in collections(folder)
        for r in c["rows"]
        if r["id"] in relation.row_ids
    }
    if set(bindings) != set(relation.row_ids):
        raise ValueError("Relation references missing inventory rows")
    path = folder / "relations.json"
    history = json.loads(path.read_text())["relations"] if path.exists() else []
    value = {"relation": relation.model_dump(), "source_dependencies": bindings}
    if value not in history:
        write_json(path, {"version": "liaoning-relations-v1", "relations": history + [value]})


def units(folder: Path) -> list[Unit]:
    path = folder / "units.json"
    result = (
        [Unit.model_validate(v) for v in json.loads(path.read_text())["units"]]
        if path.exists()
        else []
    )
    if len({u.id for u in result}) != len(result):
        raise ValueError("Duplicate unit identity")
    return result


def dependencies(folder: Path, unit: Unit) -> dict[str, str]:
    found: dict[str, str] = {}
    source_specs = {s.id: s.model_dump() for s in registry(folder)}
    for collection in collections(folder):
        for row in collection["rows"]:
            if row["id"] in unit.supporting_rows:
                if source_specs.get(collection["source"]["id"]) != collection["source"]:
                    raise ValueError("Source configuration/rights changed; recollect before review")
                found[row["id"]] = digest([collection["collection_hash"], row])
    if set(found) != set(unit.supporting_rows):
        raise ValueError("Supporting rows are missing from current inventory editions")
    return found


def review_hash(folder: Path, unit: Unit) -> str:
    parent = None
    if unit.translation_of:
        original = next((u for u in units(folder) if u.id == unit.translation_of), None)
        if original is None or original.locale == unit.locale:
            raise ValueError("Translation requires an original unit in the other language")
        if (
            original.topic_id != unit.topic_id
            or original.kind != unit.kind
            or original.subject != unit.subject
            or set(original.city_ids) != set(unit.city_ids)
            or original.classification != unit.classification
        ):
            raise ValueError(
                "Translation must preserve topic, kind, subject, cities and classification"
            )
        parent = digest(original.model_dump())
    return digest(
        {"unit": unit.model_dump(), "sources": dependencies(folder, unit), "original": parent}
    )


def decisions(folder: Path) -> list[dict[str, Any]]:
    path = folder / "reviews.json"
    return json.loads(path.read_text())["reviews"] if path.exists() else []


def reviewed(folder: Path, unit: Unit, visited: set[str] | None = None) -> bool:
    current = next((candidate for candidate in units(folder) if candidate.id == unit.id), None)
    if current is None or current.model_dump() != unit.model_dump():
        return False
    chain = set() if visited is None else set(visited)
    if unit.id in chain:
        return False
    chain.add(unit.id)
    records = [r for r in decisions(folder) if r["unit_id"] == unit.id]
    if not records:
        return False
    latest = Decision.model_validate({k: v for k, v in records[-1].items() if k != "id"})
    try:
        valid_hash = review_hash(folder, unit)
    except ValueError:
        return False
    if latest.decision != "approved" or latest.review_hash != valid_hash:
        return False
    if not unit.rights_basis.strip():
        return False
    if unit.translation_of:
        original = next((u for u in units(folder) if u.id == unit.translation_of), None)
        return bool(latest.translation_checked and original and reviewed(folder, original, chain))
    return True


def draft(folder: Path, unit: Unit) -> None:
    plan = json.loads((folder / "launch-plan.json").read_text())
    if not set(unit.city_ids) <= {c["id"] for c in plan["cities"]}:
        raise ValueError("Unknown city identifier")
    dependencies(folder, unit)
    existing = units(folder)
    write_json(
        folder / "units.json",
        {
            "version": "liaoning-units-v1",
            "units": [u.model_dump() for u in existing if u.id != unit.id] + [unit.model_dump()],
        },
    )


def review_template(folder: Path) -> dict[str, Any]:
    entries = []
    sources_by_row = {
        row["id"]: {
            "source_id": capture["source"]["id"],
            "source_url": capture["source"]["url"],
            "resource_url": capture["source"]["resource_url"],
            "reference_date": capture["source"]["reference_date"],
            "rights": capture["source"]["rights"],
            "raw_sha256": capture["raw_sha256"],
            "collection_hash": capture["collection_hash"],
            "row": row,
        }
        for capture in collections(folder)
        for row in capture["rows"]
    }
    for unit in units(folder):
        entries.append(
            {
                "unit": unit.model_dump(),
                "source_dependencies": dependencies(folder, unit),
                "source_material": [sources_by_row[row_id] for row_id in unit.supporting_rows],
                "review": Decision(
                    unit_id=unit.id, review_hash=review_hash(folder, unit)
                ).model_dump(),
            }
        )
    packet = {
        "version": "liaoning-review-packet-v1",
        "instructions": "A human must inspect source locators, applicability and support, "
        "classification, rights and translated wording. Never infer approval from collection. "
        "Record uncertainty/conflicting chronology explicitly. Pending entries are unapproved.",
        "entries": entries,
    }
    write_json(folder / "review-packet.json", packet)
    return packet


def apply_reviews(folder: Path, packet: dict[str, Any]) -> int:
    if packet.get("version") != "liaoning-review-packet-v1":
        raise ValueError("Unknown review packet")
    current = {u.id: u for u in units(folder)}
    additions = []
    seen = set()
    for entry in packet["entries"]:
        identifier = entry["review"]["unit_id"]
        if identifier in seen:
            raise ValueError("Duplicate unit decision in review packet")
        seen.add(identifier)
        decision = Decision.model_validate(entry["review"])
        if decision.decision == "pending":
            continue
        unit = current.get(decision.unit_id)
        if unit is None or decision.review_hash != review_hash(folder, unit):
            raise ValueError("Review is stale after source/draft/translation change")
        if entry.get("unit") != unit.model_dump() or entry.get(
            "source_dependencies"
        ) != dependencies(folder, unit):
            raise ValueError(
                "Packet draft/source bindings differ; import edits and regenerate review"
            )
        if decision.decision == "approved" and (
            not unit.rights_basis.strip()
            or (unit.translation_of and not decision.translation_checked)
        ):
            raise ValueError("Rights basis and applicable translation checks required")
        value = decision.model_dump()
        additions.append({"id": "review_" + digest(value)[:24], **value})
    history = decisions(folder)
    existing_ids = {r["id"] for r in history}
    additions = [r for r in additions if r["id"] not in existing_ids]
    write_json(
        folder / "reviews.json", {"version": "liaoning-reviews-v1", "reviews": history + additions}
    )
    return len(additions)


def published_snapshot() -> dict[str, Any]:
    try:
        with Session(make_engine(Settings())) as db:
            exhibits = published_exhibits(db)
            return {
                "status": "verified",
                "exhibits": [
                    {
                        "id": e.id,
                        "title": e.title,
                        "city_ids": [
                            r.region_id for r in db.query(ExhibitRegion).filter_by(exhibit_id=e.id)
                        ],
                        "themes": e.themes,
                    }
                    for e in exhibits
                ],
            }
    except Exception:
        return {
            "status": "unavailable",
            "exhibits": [],
            "reason": "Published corpus could not be checked",
        }


def subject(category: str, kind: str) -> str:
    if kind == "museum":
        return "museums"
    if kind == "sites":
        return "sites"
    for words, value in [
        (("文学", "故事"), "folklore"),
        (("音乐", "舞蹈", "戏剧", "曲艺", "体育"), "performance"),
        (("食品", "饮食", "酿造"), "food"),
        (("民俗",), "festivals"),
        (("美术", "技艺", "工艺"), "crafts"),
    ]:
        if any(w in category for w in words):
            return value
    return "history_geography"


def coverage_report(folder: Path, published: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = json.loads((folder / "launch-plan.json").read_text())
    snapshots = collections(folder)
    by_source = {c["source"]["id"]: c for c in snapshots}
    geography = [r for c in snapshots if c["source"]["kind"] == "geography" for r in c["rows"]]
    cities_by_name = {city["names"]["zh-CN"] + "市": city["id"] for city in plan["cities"]}
    code_city: dict[str, str] = {}
    for row in geography:
        if row.get("level") == "city" and row["name_original"] in cities_by_name:
            code_city[row["native_code"]] = cities_by_name[row["name_original"]]
    associations: list[dict[str, Any]] = []
    duplicates: dict[str, list[str]] = {}
    inventory_stats = []
    attempts_path = folder / "last-collection-run.json"
    attempts = json.loads(attempts_path.read_text())["attempts"] if attempts_path.exists() else []
    last_attempts = {a["source_id"]: a for a in attempts}
    ocr_observations = [json.loads(p.read_text()) for p in (folder / "ocr").glob("*.json")]
    for source in registry(folder):
        capture = by_source.get(source.id)
        rows = capture["rows"] if capture else []
        observations = [
            o
            for o in ocr_observations
            if capture
            and (
                o["source_collection_hash"] == capture["collection_hash"]
                or o["observation_hash"]
                == capture.get("reconciliation", {}).get("observation_hash")
            )
        ]
        observation = max(observations, key=lambda o: o["created_at"]) if observations else None
        expected = source.expected_count

        def normalized(row: dict[str, Any]) -> str:
            ordinal = str(row["ordinal"])
            return str(int(ordinal)) if ordinal.isdigit() else ordinal

        native_ids = {normalized(r) for r in rows}
        expected_ids = (
            set(map(str, range(1, expected + 1)))
            if expected is not None and source.kind in {"heritage", "museum", "sites"}
            else native_ids
        )
        identified = len(native_ids & expected_ids)
        imported = len(
            {normalized(r) for r in rows if r["disposition"] == "represented"} & expected_ids
        )
        # Checkpoints are not row-level rosters; an expected total does not create phantom rows.
        fetched = datetime.fromisoformat(capture["fetched_at"]) if capture else None
        next_check = fetched + timedelta(days=source.check_interval_days) if fetched else None
        inventory_stats.append(
            {
                "source_id": source.id,
                "reference_date": source.reference_date,
                "counting_unit": source.counting_unit,
                "expected": expected,
                "identified": identified,
                "unexpected_native_ids": sorted(native_ids - expected_ids),
                "reconciled_complete": bool(
                    capture
                    and not capture["errors"]
                    and expected is not None
                    and imported == expected
                ),
                "represented": imported,
                "missing": max(0, expected - identified) if expected is not None else None,
                "accounted_ratio": min(identified / expected, 1) if expected else None,
                "import_ratio": min(imported / expected, 1) if expected else None,
                "status": capture["status"] if capture else "not_collected",
                "last_attempt": last_attempts.get(source.id),
                "errors": capture["errors"] if capture else [],
                "extraction_review_kind": capture.get("reconciliation", {}).get("reviewer_kind")
                if capture
                else None,
                "field_issues": [
                    {"row_id": r["id"], "ordinal": r["ordinal"], "notes": r["extraction_notes"]}
                    for r in rows
                    if r.get("extraction_notes")
                ],
                "ocr": {
                    "pages": len(observation["pages"]),
                    "lines": sum(len(p["lines"]) for p in observation["pages"]),
                    "status": observation["status"],
                    "observation_hash": observation["observation_hash"],
                }
                if observation
                else None,
                "rights": source.rights,
                "source_url": source.url,
                "check_interval_days": source.check_interval_days,
                "next_check_at": next_check.isoformat() if next_check else None,
                "refresh_due": next_check < datetime.now(UTC) if next_check else True,
                "currentness": "dated_edition_not_proof_of_latest_roster",
                "unresolved": sum(r["disposition"] != "represented" for r in rows),
                "row_accounting": [
                    {
                        "ordinal": str(i),
                        "status": next(
                            (
                                r["disposition"]
                                for r in rows
                                if r["ordinal"].isdigit() and int(r["ordinal"]) == i
                            ),
                            "missing",
                        ),
                    }
                    for i in range(1, expected + 1)
                ]
                if expected and source.kind in {"heritage", "museum", "sites"}
                else [],
                "collection_hash": capture["collection_hash"] if capture else None,
            }
        )
        for row in rows:
            if source.kind == "geography":
                continue
            key = re.sub(r"\s+", "", row["name_original"])
            duplicates.setdefault(key, []).append(row["id"])
            matched_cities: set[str] = set()
            county_codes = []
            explicit = {
                g["native_code"]
                for g in geography
                if g.get("level") == "city" and g["name_original"] in row["locality_original"]
            }
            for code in explicit:
                if code in code_city:
                    matched_cities.add(code_city[code])
            county_matches = [
                g
                for g in geography
                if g.get("level") == "county"
                and g["name_original"] in row["locality_original"]
                and (not explicit or g["city_code"] in explicit)
            ]
            ambiguous = not explicit and len({g["city_code"] for g in county_matches}) > 1
            if not ambiguous:
                for geo in county_matches:
                    if geo["city_code"] in code_city:
                        matched_cities.add(code_city[geo["city_code"]])
                        county_codes.append(geo["native_code"])
            associations.append(
                {
                    "row_id": row["id"],
                    "entity_id": row["entity_id"],
                    "name": row["name_original"],
                    "city_ids": sorted(matched_cities),
                    "county_codes": sorted(set(county_codes)),
                    "subject": source.subject_hint
                    or subject(row["category_original"], source.kind),
                    "geographic_role": "repository"
                    if source.kind == "museum"
                    else "source_locality"
                    if source.kind == "explanation"
                    else "listed_applicant",
                    "original_locality": row["locality_original"],
                    "association_status": "matched_current_names"
                    if matched_cities
                    else "unresolved",
                    "notes": "List/applicant association is not evidence of historical origin.",
                }
            )
    current_units = units(folder)
    approved_units = [u for u in current_units if reviewed(folder, u)]
    live = published_snapshot() if published is None else published
    manifest = []
    for city in plan["cities"]:
        candidates = [a for a in associations if city["id"] in a["city_ids"]]
        by_topic: dict[str, list[Unit]] = {}
        relevant = [u for u in approved_units if city["id"] in u.city_ids]
        for unit in relevant:
            if unit.kind != "city_introduction":
                by_topic.setdefault(unit.topic_id, []).append(unit)
        substantive = []
        for topic_id, topic_units in by_topic.items():
            if all(
                {"introduction", "context", "question"}
                <= {u.kind for u in topic_units if u.locale == locale}
                and bool({"term", "example"} & {u.kind for u in topic_units if u.locale == locale})
                for locale in plan["required_locales"]
            ):
                substantive.append(
                    {"id": topic_id, "subjects": sorted({u.subject for u in topic_units})}
                )
        introduction = all(
            any(u.kind == "city_introduction" and u.locale == locale for u in relevant)
            for locale in plan["required_locales"]
        )
        reviewed_subjects = {s for t in substantive for s in t["subjects"]}
        ready = (
            introduction
            and len(substantive) >= plan["minimum_topics_per_city"]
            and len(reviewed_subjects) >= plan["minimum_subjects_per_city"]
        )
        selected: list[dict[str, Any]] = []
        # Proposed topics span categories before filling remaining slots; they are unreviewed.
        used_subjects: set[str] = set()
        for candidate in candidates:
            if candidate["subject"] not in used_subjects and len(selected) < 3:
                selected.append(candidate)
                used_subjects.add(candidate["subject"])
        for candidate in candidates:
            if candidate not in selected and len(selected) < 3:
                selected.append(candidate)
        manifest.append(
            {
                **city,
                "catalog_rows_associated": len(candidates),
                "candidate_topic_ids": [a["entity_id"] for a in selected],
                "candidate_subjects": sorted(used_subjects),
                "reviewed_city_introduction_en_zh": introduction,
                "reviewed_substantive_topics": substantive,
                "reviewed_subjects": sorted(reviewed_subjects),
                "published_exhibit_ids": [
                    e["id"] for e in live["exhibits"] if city["id"] in e["city_ids"]
                ],
                "publication_status": live["status"],
                "ready": ready,
                "remaining": []
                if ready
                else ["Reviewed EN/ZH introduction; three topics across two subjects required"],
            }
        )
    relation_path = folder / "relations.json"
    relation_history = (
        json.loads(relation_path.read_text())["relations"] if relation_path.exists() else []
    )
    current_bindings = {
        r["id"]: digest([c["collection_hash"], r]) for c in snapshots for r in c["rows"]
    }
    latest_relations = {entry["relation"]["id"]: entry for entry in relation_history}
    relation_report = [
        {
            **entry,
            "current": all(
                current_bindings.get(key) == value
                for key, value in entry["source_dependencies"].items()
            ),
        }
        for entry in latest_relations.values()
    ]
    report = {
        "version": "liaoning-coverage-v1",
        "relations": relation_report,
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            "cities_in_scope": len(manifest),
            "counties_cataloged": sum(r.get("level") == "county" for r in geography),
            "inventory_rows": sum(
                len(c["rows"]) for c in snapshots if c["source"]["kind"] != "explanation"
            ),
            "explanatory_source_records": sum(
                len(c["rows"]) for c in snapshots if c["source"]["kind"] == "explanation"
            ),
            "reviewed_explanation_units": len(approved_units),
            "published_corpus_status": live["status"],
            "published_exhibits": len(live["exhibits"]) if live["status"] == "verified" else None,
            "launch_ready_cities": sum(c["ready"] for c in manifest),
            "unknown_unique_topic_total": True,
        },
        "inventories": inventory_stats,
        "associations": associations,
        "duplicate_candidates": [
            {"name": n, "row_ids": ids, "decision": "unresolved_not_merged"}
            for n, ids in duplicates.items()
            if len(ids) > 1
        ],
        "county_subject_matrix": [
            {
                "county_code": g["native_code"],
                "name": g["name_original"],
                "city_id": code_city.get(g["city_code"]),
                "subjects": {
                    s: sum(
                        g["native_code"] in a["county_codes"] and a["subject"] == s
                        for a in associations
                    )
                    for s in SUBJECTS
                },
            }
            for g in geography
            if g.get("level") == "county"
        ],
        "launch_manifest": manifest,
        "note": (
            "Catalog, explanations and publication have different denominators. "
            "Overlapping inventory counts are not unique topics."
        ),
    }
    write_json(folder / "coverage.json", report)
    write_json(
        folder / "launch-manifest.json", {"version": "liaoning-launch-v1", "cities": manifest}
    )
    lines = [
        "# Liaoning collection and review dashboard",
        "",
        "Collected metadata does not become chatbot knowledge automatically.",
        "",
        "| Inventory edition | Expected | Identified | Represented | Missing | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for item in inventory_stats:
        lines.append(
            f"| {item['source_id']} | "
            f"{item['expected'] if item['expected'] is not None else 'unknown'} | "
            f"{item['identified']} | {item['represented']} | "
            f"{item['missing'] if item['missing'] is not None else 'unknown'} | {item['status']} |"
        )
    lines += [
        "",
        "| City | Catalog rows | Reviewed topics | Published exhibits | Ready |",
        "|---|---:|---:|---:|---|",
    ]
    for city in manifest:
        published_count = (
            len(city["published_exhibit_ids"]) if live["status"] == "verified" else "unverified"
        )
        lines.append(
            f"| {city['names']['en']} | {city['catalog_rows_associated']} | "
            f"{len(city['reviewed_substantive_topics'])} | "
            f"{published_count} | "
            f"{city['ready']} |"
        )
    lines += [
        "",
        "See coverage.json for extraction errors, missing rows, identities, county/subject gaps "
        "and rights dependencies.",
    ]
    (folder / "dashboard.md").write_text("\n".join(lines) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=ROOT / "data/liaoning")
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("draft")
    make.add_argument(
        "--file", type=Path, required=True, help="Strict Unit JSON, never an approval"
    )
    sub.add_parser("template")
    relation = sub.add_parser("link")
    relation.add_argument("--file", type=Path, required=True)
    apply = sub.add_parser("apply-review")
    apply.add_argument("--file", type=Path, required=True)
    export = sub.add_parser("export-approved")
    export.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "draft":
        draft(args.folder, Unit.model_validate(json.loads(args.file.read_text())))
    elif args.command == "link":
        link(args.folder, Relation.model_validate(json.loads(args.file.read_text())))
    elif args.command == "template":
        print(len(review_template(args.folder)["entries"]), "pending units")
    elif args.command == "apply-review":
        print(
            apply_reviews(args.folder, json.loads(args.file.read_text())),
            "human decisions recorded",
        )
    else:
        write_json(
            args.output,
            {
                "version": "liaoning-reviewed-unit-handoff-v1",
                "automatically_published": False,
                "units": [u.model_dump() for u in units(args.folder) if reviewed(args.folder, u)],
            },
        )
    coverage_report(args.folder)


if __name__ == "__main__":
    main()
