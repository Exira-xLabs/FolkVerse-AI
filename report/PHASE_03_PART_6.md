# Phase 03 Part 6 — bilingual evaluation and handoff

Date: 6 October 2026, Asia/Shanghai. Part 6 is implemented; Phase 03 expert-guide acceptance remains incomplete.

Delivered: [64 frozen cases](../tests/evaluation/guide/v1.json), strict manifest-bound reviewed expectations, isolated bilingual/fault evaluation, separate functional and human dimensions, real-mode preflight/usage accounting, run-bound review worksheets, and [phase handoff](../docs/phase-03-handoff.md). [Methodology and commands](../docs/guide-evaluation.md) explain the scoring units and reservation limits.

## Results

The untouched [initial baseline](evidence/phase03-part6/evaluation-baseline.json) meets **58/64** draft functional targets, with **16/16 development** and **42/48 reserved** cases. It exposed four paraphrase false abstentions and two EN/ZH follow-up failures. These are reserved functional cases authored after the earlier implementation, not independently adjudicated historical targets or a blind expert study.

Harness v2 fixes the language-switch bug by validating signed prior passage versions against current eligibility independently of title search and retrieval language/rank. New-language answers still use separately reviewed passages; withdrawal still invalidates context. The frozen dataset and gold targets are unchanged. The [post-fix diagnostic rerun](evidence/phase03-part6/evaluation.json) meets **60/64** targets, **16/16 development** and **44/48 reserved**. Reserved cases have been exposed; this rerun is regression evidence, not fresh held-out quality scoring.

| Dimension | Diagnostic numerator / scored denominator | Sample and limitation |
|---|---|---|
| Historical correctness | Pending / 0 | 18 answered responses available; independent human review required. |
| Claim support | 18 / 18 | Actual answered responses only; exact complete reviewed statements plus controlled attributed display. |
| Citation validity | 18 / 18 | Actual answered responses only; current eligible IDs/metadata and full claim/source mapping. |
| Explanatory clarity | Pending / 0 | 18 answered responses available; repeated excerpts do not establish useful explanations. |
| Bilingual faithfulness | Pending / 0 | 9 answered EN/ZH families available; locale labels are not quality scores. |
| Uncertainty | 54 / 58 | Returned responses; six errors excluded. Four supported paraphrases incorrectly abstain. |
| Follow-up consistency | 10 / 10 | Seed, expected result, owner/consent behavior, citations and uncertainty. |

All metric JSON includes numerator, denominator, sample size and rate. Empty/pending rates are null. Abstentions earn no claim-support or citation credit. The [blank human worksheet](evidence/phase03-part6/human-review-template.json) contains 45 pending units; [grading it](evidence/phase03-part6/human-review-pending.json) awards no scores or expertise certification.

Four failures remain: `paraphrase_locality` and `paraphrase_classification` in EN/ZH. Narrow question grammar rejects valid wording despite reviewed listing support. Chronology, glossary, origins, competing interpretations and free explanation are unavailable. Only two approved bilingual passages for one inventory item exist; the draft review packet has not expanded approved coverage.

## Usage, timing and environment

Fixture evaluation makes **42 mocked gateway calls and zero real generation requests**. Actual provider tokens and cost are unmeasured/null. Local elapsed time, including follow-up seeds but excluding restoration, is approximately **20.91 ms median / 116.67 ms maximum**. This is neither BGE runtime nor first meaningful SSE/provider latency. Full evaluator/harness SHA, corpus, prompt, retrieval, gateway and model versions are included in the run.

Fresh [environment evidence](evidence/phase03-part6/environment.json): PostgreSQL unavailable; authentication-only DeepSeek `/models` **HTTP 401**; demo mode, daily budget **0**, semantic retrieval disabled. [Live preflight](evidence/phase03-part6/live-preflight.json) is blocked and claims no completed score. No paid completion, database activation, review approval or budget change was made. The incomplete BGE weights from Part 5 still have no verified inference benchmark.

## Verification

The **219 portable API checks pass**, including 22 new evaluation/review/SQL regressions. Strict mypy (26 source files), Ruff/web lint, TypeScript, generated contracts and foundation asset/secret checks pass, with evidence in this directory. Node 26 is outside the declared Node 22 range; these checks do not certify the supported runtime. One existing Starlette/httpx deprecation warning remains. The new checks cover real SQL EN↔ZH follow-ups and withdrawal, gold/split integrity, independent display/claim/citation scoring, zero credit for abstentions, human review attribution/run binding, live preflight gates and isolated usage accounting. Final counts are recorded in [API test output](evidence/phase03-part6/api-tests.txt). Prior Part 5 browser/BFF checks (19 passing) and build remain dated evidence; no UI implementation changed in Part 6. Current real PostgreSQL/full database integration and real provider/browser generation remain unverified.

Remaining gates and concrete next work are listed in the [handoff](../docs/phase-03-handoff.md). No 95% historical/expert quality claim is supported by this fixture sample.
