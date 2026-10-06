"""Export existing draft wording/catalog metadata for human review; never approve it."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/corpus.json"
OUTPUT = ROOT / "data/review-candidates/phase03-part5.json"


def main() -> None:
    original = MANIFEST.read_bytes()
    manifest = json.loads(original)
    sources = {row["id"]: row for row in manifest["source"]}
    passages = {row["id"]: row for row in manifest["passage"]}
    claims = {row["id"]: row for row in manifest["claim"]}
    candidates = []
    for exhibit in manifest["exhibit"]:
        if exhibit["status"] != "draft":
            continue
        claim_ids = {
            row["id"] for row in claims.values() if row["exhibit_id"] == exhibit["id"]
        }
        passage_ids = sorted(
            {
                row["passage_id"]
                for row in manifest["claim_evidence"]
                if row["claim_id"] in claim_ids
            }
        )
        wording = []
        for identifier in passage_ids:
            passage = passages[identifier]
            source = sources[passage["source_id"]]
            wording.append(
                {
                    "passage_id": identifier,
                    "language": passage["language"],
                    "text": passage["text"],
                    "locator": passage["locator"],
                    "rights_status": passage["rights_status"],
                    "rights_basis": passage["rights_basis"],
                    "source": {
                        key: source[key]
                        for key in (
                            "id",
                            "institution",
                            "title",
                            "canonical_url",
                            "fetched_at",
                            "raw_hash",
                            "rights_basis",
                        )
                    },
                }
            )
        candidates.append(
            {
                "kind": "heritage_inventory",
                "status": "draft",
                "exhibit_id": exhibit["id"],
                "title": exhibit["title"],
                "existing_draft_passages": wording,
                "required_review": [
                    "Verify exact source/locator and listing scope",
                    "Review each EN/ZH passage and translation separately",
                    "Resolve rights, claim mapping and regional dependencies",
                    "Do not infer historical origins, chronology or technique",
                ],
            }
        )
    for object_id in (50824, 449479, 460669):
        source = sources.get(f"met-source-{object_id}")
        if not source or source["status"] != "draft":
            continue
        raw = json.loads(source["raw_payload"])
        candidates.append(
            {
                "kind": "museum_catalog_metadata",
                "status": "draft",
                "source": {
                    key: source[key]
                    for key in (
                        "id",
                        "institution",
                        "title",
                        "canonical_url",
                        "fetched_at",
                        "raw_hash",
                        "rights_basis",
                    )
                },
                "catalog_fields": {
                    key: raw.get(key)
                    for key in (
                        "objectID",
                        "title",
                        "culture",
                        "period",
                        "objectDate",
                        "medium",
                        "country",
                        "repository",
                        "isPublicDomain",
                    )
                },
                "required_review": [
                    "Refresh and verify the dated museum catalog record",
                    "Keep institution catalog dates/interpretations attributed",
                    "Create rights-cleared EN/ZH passages and reviewed claim links",
                    "Do not treat museum location as creation origin",
                    "No image/reference eligibility is granted by this file",
                ],
            }
        )
    report = {
        "version": "guide-review-candidates-v1",
        "prepared_date": "2026-10-06",
        "scope": "Existing Liaoning inventory drafts plus three China catalog candidates",
        "provenance": "existing_export_not_current_database",
        "manifest_sha256": hashlib.sha256(original).hexdigest(),
        "published": False,
        "human_approval_granted": False,
        "note": "Review packet only. No new passage, approval, chronology or live coverage is created.",
        "candidates": candidates,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    assert MANIFEST.read_bytes() == original
    print(
        f"Prepared {len(candidates)} draft review candidates; corpus/ledger unchanged."
    )


if __name__ == "__main__":
    main()
