> Current status, 7 October 2026: Phase 3 complete. The [completion report](../report/PHASE_03_FINAL_COMPLETION.md) supersedes historical pending-review/budget status below and records measured pilot/corrections, attributed machine assessment and limitations. Phase 4 is next.

# Dated guide evaluation

The frozen [v1 set](../tests/evaluation/guide/v1.json), dated 6 October 2026 (Asia/Shanghai), contains 64 cases: 32 English/Chinese scenario pairs, with 16 development cases and 48 reserved scoring cases. Both languages of a family share the split. Expected supported statements are copied from the export's existing editorially reviewed passages, with source, reviewer, review ID and review date. The scenario targets and unacceptable answers are machine-authored drafts pending human adjudication. No new editorial approval or independent historical judgment is implied.

The manifest SHA binds gold to the dated export. The evaluator checks those statements against actual eligible passages, including approval provenance, before scoring. Changed gold or corpus requires an explicitly versioned evaluation. The set covers existing inventory listings, unavailable chronology/definitions/contested interpretations/folklore, ambiguity, depth, simplification, consent and ownership, locale switches, question/source injection, withdrawal, fabricated citations/dates/classification, timeout and budget exhaustion. These unsupported cases test abstention; they do not establish substantive coverage of those subjects.

## Running and interpreting results

From the repository root:

```sh
apps/api/.venv/bin/python -m folkverse.guide_evaluation --mode fixture --output report/evidence/phase03-part6/evaluation.json
apps/api/.venv/bin/python -m folkverse.guide_evaluation --mode live --split heldout --output report/evidence/phase03-part6/live-evaluation.json
```

`--split development|heldout|all` selects a partition; `--run-label` records its interpretation. Exit 0 means every executed functional target passed; 1 means a completed run has recorded failures; 2 means blocked or invalid input. Failure results are evidence, not grounds to silently weaken frozen targets.

Fixture mode restores the unchanged export into isolated temporary SQLite databases. Each case gets its own database and a mocked JSON generation boundary. Source injection changes only the retrieved model copy; withdrawal changes only that case's database. No real provider tokens, prices, BGE inference or PostgreSQL locking are inferred. The export is never a production database fallback.

Live mode keeps existing mode, key, model/price binding and budget gates. It creates temporary real session identities, retrieves current PostgreSQL evidence, calls the real metered gateway and removes those sessions afterward. Fault-injection cases are explicitly skipped in live mode. It never changes live reviews, provider configuration, billing limits or published content. Run only after the deployment's normal live prerequisites are configured. The operator CLI is not an HTTP/SSE latency or cookie-ownership test.

Real attempt IDs, actual observed usage and configured budget charges are reported separately. Unknown token usage remains unknown; reservations cannot certify invoice costs. Fixture usage is excluded. Local harness timing includes any follow-up seed, excludes database restoration and does not measure first meaningful SSE content. Outputs include evaluator/harness file hashes and corpus, prompt, retrieval, gateway, provider/model and embedding versions. Public evaluation responses are saved without context tokens; private visitor traffic is not collected.

## Seven separate dimensions

| Dimension | Unit and judgment |
|---|---|
| Historical correctness | Human judgment of each actual answered response against independent primary or scholarly evidence. Copying an approved passage alone does not prove historical truth. |
| Claim support | Automated per actual answered response: every claim is a complete reviewed passage in the requested language, and the entire displayed prose is its controlled attribution and statement. Abstentions earn no credit. |
| Citation validity | Automated per actual answered response: eligible IDs, exact current metadata, complete claim/source mappings, no extra or duplicated citations, and allowed gold evidence. |
| Explanatory clarity | Human judgment of each actual answered response: directness, readable explanation, terminology, requested depth and usefulness. A repeated quotation need not meet the explanation goal. |
| Bilingual faithfulness | Human judgment per answered EN/ZH family: preserved meaning, names, classification, uncertainty and attribution. Locale field agreement is a separate diagnostic only. |
| Uncertainty | Automated per returned response: the required partial/insufficient state plus a stated coverage limit. Provider errors are excluded. False abstentions fail supported targets. |
| Follow-up consistency | Automated per follow-up case: a checked seed, expected response, retained citations and partial uncertainty for answered follow-ups; honest refusal without consent or with a different owner. |

Each scored metric includes numerator, denominator and sample size. Empty automated samples have a null rate. Unreviewed human dimensions have a null numerator, zero scored denominator and the number of available review units; neither zero accuracy nor successful expertise is inferred. Overall scenario outcome and locale delivery are diagnostics, separate from these dimensions.

## Human review workflow

```sh
apps/api/.venv/bin/python -m folkverse.guide_review template --run report/evidence/phase03-part6/evaluation.json --output report/evidence/phase03-part6/human-review-template.json
apps/api/.venv/bin/python -m folkverse.guide_review grade --run report/evidence/phase03-part6/evaluation.json --reviews report/evidence/phase03-part6/human-review-template.json --output report/evidence/phase03-part6/human-review-pending.json
```

An actual reviewer fills pass/fail, identity, timezone-aware timestamp, rationale, independent basis and human-review attestation. Keep every unit, including pending ones. Grading rejects missing, duplicate, unknown or mismatched units and worksheets bound to a changed run SHA. Pending units earn no credit. The tool records attributed judgments but cannot authenticate reviewers or certify expertise; reviewing fixture prose cannot establish real provider performance.

## Recorded results and reservation limits

The [initial baseline](../report/evidence/phase03-part6/evaluation-baseline.json) scored 58/64 overall and 42/48 on the reserved partition, before the language-switch fix. The cases were authored after the earlier implementation, so this is a reserved functional assessment, not a blind expert study.

The run exposed incorrect prior-evidence validation during EN/ZH switches. Harness v2 checks signed passage versions against current eligible evidence independently of title search, locale or rank, then retrieves the new language's separately reviewed passages. It continues to reject withdrawn evidence. The [rerun](../report/evidence/phase03-part6/evaluation.json) scores 60/64 overall and 44/48 reserved after that general fix. It is labelled **diagnostic regression after baseline**, since the reserved cases have now been seen. Frozen targets were not changed. A fresh reserved set is required to measure later improvements without reusing exposed cases.

The later [push audit](../report/PHASE_03_PUSH_AUDIT.md) fixes these listing paraphrases with harness v3; its exposed-case diagnostic reaches 64/64 while preserving both Part 6 runs.

Remaining failures in the Part 6 v2 run are locality/classification paraphrases in both languages. The exact narrow grammar rejects them even though the gold inventory passage supports them. Historical correctness, explanatory clarity and bilingual faithfulness remain pending. Consult the [handoff](phase-03-handoff.md) for unresolved integration and content gates.

## Fresh hybrid v3 evaluation — 7 October 2026

The current hybrid contract is evaluated separately from the old exact-excerpt v1/v2 tooling. `scripts/evaluate-guide-hybrid.py` runs the frozen 48-case `v3-hybrid.json` through the actual owned API and model. `scripts/evaluate-guide-hybrid-faults.py` runs 16 isolated bilingual safety cases with mocked generation. First/diagnostic exposure, seeds, real usage, support/citation denominators and general-only answers are reported separately in [Part 7](../report/PHASE_03_HYBRID_PART_07.md). Do not substitute the old excerpt evaluator or fixture gold for hybrid quality.

The first v3 run scores 46/48 (initially reserved 32/32); the exposed diagnostic reaches 48/48 after a prompt correction for unsafe local detail in Chinese general context. Final support/citation integrity scores 18/18 actual sourced answers. Historical correctness, explanatory clarity, personality and bilingual faithfulness remain unscored until actual human judgments are supplied. The 200-question pilot and expert gold remain separate requirements.

The review CLI accepts hash-bound v2 worksheets including personality and clarity of conversational/insufficient responses. The [readable packet](../report/PHASE_03_HUMAN_REVIEW_PACKET.md) contains actual answers and original source links; all pending values remain null. Attribution and attestation are required for scored judgments; the tool cannot authenticate reviewer identity or expertise.
