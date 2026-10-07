# Part 7 — fresh bilingual evaluation and human-review handoff

7 October 2026. Automated evaluation is complete; **actual human judgments remain pending**.

The new frozen [v3 suite](../tests/evaluation/guide/v3-hybrid.json) contains 48 live cases in 24 English/Chinese families: 16 development and 32 reserved cases, with whole families sharing a split. It is authored after implementation and before the first new run. The existing owner-reviewed corpus export binds the source-backed expectations; new general/official functional targets are machine-authored and not expert gold. No old reserved corpus set is silently relabelled fresh.

## First and diagnostic results

| Metric | First run | Exposed diagnostic rerun |
|---|---:|---:|
| Overall functional target | 46/48 | 48/48 |
| Development target | 14/16 | 16/16 |
| Initially reserved target | 32/32 | 32/32, now exposed |
| Actual sourced answers with support | 16/16 | 18/18 |
| Actual sourced answers with valid citations | 16/16 | 18/18 |
| Whole-display integrity | 46/46 | 46/46 |
| Uncertainty/coverage targets | 32/34 | 34/34 |
| Follow-up targets | 7/8 | 8/8 |
| Social structured delivery | 12/12 | 12/12 |

Both first-run failures were **development** Chinese deeper answers. The provider inserted unsupported local stylistic detail into a general section; the validator returned insufficiency. One bounded diagnostic probe confirmed that failure mode. The prompt now supplies the exact forbidden local names, distinguishes the generic art form from the named local variant, and limits output length/numbered content. It does not relax factual validation or silently retry. A regression rejects the actual problematic local-style statement. The frozen targets were not changed. The rerun is explicitly an exposed diagnostic, not a second blind score.

Final outcomes: 26 answered (18 source-backed, eight general), 12 conversational, eight appropriate insufficiencies and two cross-owner context errors. Abstentions do not earn support/citation credit. General correctness is unscored; a support label is not factual gold. The final API p95 for 26 meaningful answers is **2.96 seconds**, excluding seed time and browser rendering; first-run p95 was 3.07 seconds. Existing rate/budget limits were preserved. Each 48-case run includes **50 real metered calls including seeds**, with configured-rate charges $0.0174123 / $0.0190131; these are not provider invoices.

A separate 16-case bilingual [fault run](evidence/phase03-hybrid-part07/fault-evaluation.json) passes 16/16 against isolated restored SQLite evidence and mocked generation. It covers timeout, budget exhaustion, invented IDs, source instructions, withdrawal during generation, historical/folklore reclassification, rejected-fact laundering and unsafe general assertions. It never mutates live data or spends provider quota. These are diagnostic fault regressions, not real provider-quality scores.

## Human review

The actual [48-case readable packet](PHASE_03_HUMAN_REVIEW_PACKET.md), [run-bound worksheet](evidence/phase03-hybrid-part07/human-review-template.json) and [pending grading result](evidence/phase03-hybrid-part07/human-review-pending.json) are ready. The v2 review schema now includes personality, clarity of conversations/refusals, and bilingual families; actual attributed pass/fail judgments require a reviewer, timezone-aware date, rationale, independent basis and human attestation. Run changes and missing/duplicate/mismatched units are rejected. Null judgments score nothing. Owner/editor review and independent specialist review are distinct.

No reviewer has supplied ratings, so historical correctness, clarity, personality and bilingual faithfulness remain unscored. Codex cannot fill those human ratings. The 200-question bilingual pilot, independent expert review and province-wide approved content are not completed by 48 functional cases.

Reproduce:

```sh
uv run --project apps/api python scripts/evaluate-guide-hybrid.py --output <new-dated-run.json> --run-label <accurate-exposure-label>
uv run --project apps/api python scripts/evaluate-guide-hybrid-faults.py --output <new-dated-fault-run.json>
uv run --project apps/api python -m folkverse.guide_review grade --run report/evidence/phase03-hybrid-part07/evaluation-diagnostic.json --reviews report/evidence/phase03-hybrid-part07/human-review-template.json --output <new-human-summary.json>
```

Preserve [first run](evidence/phase03-hybrid-part07/evaluation-first.json) and [diagnostic run](evidence/phase03-hybrid-part07/evaluation-diagnostic.json). These do not certify historical expertise or release readiness.
