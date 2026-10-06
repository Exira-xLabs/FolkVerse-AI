"""Bind an unscored bilingual review worksheet to the actual recorded live walkthrough."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "report/evidence/phase03-completion"


def main() -> None:
    raw = (DIRECTORY / "live-browser.json").read_bytes()
    run = json.loads(raw)
    rubric = {
        "historical_correctness": "Verify against independent primary sources; unsupported facts fail.",
        "claim_support": "Every fact and qualifier in displayed prose must follow reviewed evidence.",
        "citation_validity": "Inspect actual links, IDs, dates and claim mappings; check current source.",
        "explanatory_clarity": "Direct, useful, appropriate depth; do not reward length or repetition.",
        "bilingual_faithfulness": "Compare EN/ZH meaning, locality, source qualifications and limits.",
        "uncertainty": "Listing scope and missing historical evidence must remain clear.",
        "followup_consistency": "Simplification and language switches retain topic and supported facts.",
        "personality": "Warm, natural, patient; no personal memories, authority or repetitive questions.",
    }
    units = []
    for turn in run["conversations"]:
        answer = turn.get("answer")
        if not answer:
            continue
        units.append({
            "answer_id": answer["answer_id"], "question": turn["question"],
            "locale": answer["locale"], "status": answer["status"],
            "display_text": answer["answer_text"], "sources": turn.get("sources", []),
            "reviewer": None, "reviewed_at": None, "ratings": {name: None for name in rubric},
            "comments": None,
        })
    worksheet = {
        "version": "jinyao-live-human-review-v1", "status": "pending_independent_review",
        "run_sha256": hashlib.sha256(raw).hexdigest(), "checked_at": run["checkedAt"],
        "scoring": "PASS/FAIL/N/A with attributed rationale; null is unscored, never passing.",
        "rubric": rubric, "units": units,
        "note": "Source text alone is not independent correctness gold. Reviewer must check "
                "authoritative references and disclose affiliation; no human scores are synthesized.",
    }
    (DIRECTORY / "live-human-review-pending.json").write_text(
        json.dumps(worksheet, ensure_ascii=False, indent=2) + "\n"
    )
    print(f"Prepared {len(units)} unscored live conversation review units.")


if __name__ == "__main__":
    main()
