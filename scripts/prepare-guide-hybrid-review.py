"""Readable review packet for actual bilingual answers; ratings remain human-only."""

import argparse
import hashlib
import json
from pathlib import Path


def main(run_path, output):
    run = json.loads(run_path.read_text())
    lines = [
        "# Jinyao — actual bilingual human review packet",
        "",
        f"Run SHA-256: `{hashlib.sha256(run_path.read_bytes()).hexdigest()}`",
        "",
        "These are actual recorded model answers. Machine structural/support checks are reported separately. No human judgments have been supplied.",
        "",
        "Review the English/Chinese pairs for factual correctness, clarity, faithful meaning and personality. For general explanations, verify against independent primary or scholarly references; an unverified label is not proof of correctness. For precise facts, inspect original sources, dates, attribution and current applicability. Check warmth, repetition, helpful invitations and false institutional authority.",
        "",
        "Record PASS/FAIL in `human-review-template.json`, with your name, timezone-aware timestamp, rationale, independent basis and `attest_human_review: true`. Leave unanswered units null. A partial review is reported as partial; no missing rating becomes a pass.",
        "",
        "After reviewing, run:",
        "",
        "```sh",
        "uv run --project apps/api python -m folkverse.guide_review grade --run report/evidence/phase03-hybrid-part07/evaluation-diagnostic.json --reviews report/evidence/phase03-hybrid-part07/human-review-template.json --output report/evidence/phase03-hybrid-part07/human-review-completed.json",
        "```",
        "",
        "Owner/editor review and independent specialist review remain distinct. This worksheet cannot authenticate identity or certify expertise.",
        "",
    ]
    for case in run["cases"]:
        lines += [
            f"## {case['family']} — {case['locale']}",
            "",
            f"Case: `{case['id']}` · {case['actual_status']} · {case['depth']}",
            "",
            f"**Question:** {case['question']}",
            "",
        ]
        answer = case.get("answer")
        if not answer:
            lines += [f"Controlled error: `{case['error']}`", ""]
            continue
        if answer.get("sections"):
            for section in answer["sections"]:
                lines += [f"**{section['support_label']}**", "", section["text"], ""]
        else:
            lines += [answer["answer_text"], ""]
        if answer.get("coverage_limit"):
            lines += [f"Coverage: {answer['coverage_limit']}", ""]
        for source in case["sources"]:
            lines += [
                f"Source: [{source['source_title']}]({source['canonical_url']}) — {source['institution']}",
                f"Fetched: {source['fetched_at']} · classification: {source['classification']} · {source['evidence_origin']}",
                f"Editorial review: {source['reviewer'] or 'pending'} · {source['reviewed_at'] or 'pending'}",
                "",
                f"> {source['text']}",
                "",
            ]
        lines += ["Human ratings: **pending**.", ""]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines).rstrip() + "\n")
    print(
        f"Prepared readable packet with {len(run['cases'])} actual EN/ZH cases; no human ratings."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Do not overwrite a reviewed packet; choose a new version.")
    main(args.run, args.output)
