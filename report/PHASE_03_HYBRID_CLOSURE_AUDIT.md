# Phase 3 — final evidence and closure decision

7 October 2026, Asia/Shanghai. Repository: `/home/oualid/Exira-X/FolkVerse_Codex_Build_Kit`, branch `main`. Previous delivery pushed as `7fa2e7e`; this audit describes the subsequent local implementation and verification. No production deployment is claimed.

**Decision: Phase 3 remains partial.** Parts 6–8 engineering, automated evaluation and reproducibility work are delivered. Human review is pending, the broader approved corpus remains narrow, and the required release/pilot evidence does not yet exist. Completing an audit is not passing every gate.

## Original acceptance gates

These reproduce the eight gates in [Phase 03](../phases/03_GROUNDED_GUIDE.md), with current evidence.

| Gate as written | Status | Actual evidence / remaining requirement |
|---|---|---|
| A real credentialed call is tested if authorized credentials exist; otherwise explicitly unverified. | PASS | Fresh real DeepSeek API/model evaluation and browser/BFF checks; actual persistent admission and usage. Intended production Ollama remains a separately recorded provider, not a deployment claim. |
| Supported and unsupported questions behave differently in both languages. | PASS | Final 48-case diagnostic: 26 answered, eight appropriate insufficiencies, 12 conversational and two context ownership errors. First 46/48 run retained. |
| Invented citation IDs are rejected; source-injected instructions do not change policy. | PASS | Isolated bilingual fault evaluation, API/browser invalid-publication regressions. No arbitrary model URLs/tools permitted. |
| Revoked passages stop being retrieved; model timeout/cap exhaustion show honest errors. | PASS | Fresh 16-case fault sample includes withdrawal during generation, timeout/cap faults; source inspection removes dependent UI/context. No live content or real quota is exhausted for faults. |
| Keys never reach browser/logs; source drawer shows actual evidence. | PASS within inspected scope | Configured-secret/browser-output scan, server-only keys, actual source API/original-page inspection, ignored local config. No absolute security guarantee is inferred from a scan. |
| Jinyao's hybrid conversation and explanation harness is implemented and evaluated on a dated bilingual set, with measured factual, clarity, personality and conversational results; general knowledge and reviewed coverage are distinguished. | PARTIAL | 48-case fresh functional set plus 16 isolated faults; support/citation 18/18 actual sourced answers; historical correctness, clarity, personality and bilingual human scores remain unscored. |
| Explanations separate historical evidence, attributed interpretations, folklore/belief and creative adaptation; chronology and source support are checked. | PARTIAL | Classification schema/UI, source-required mappings and date/qualifier guards pass rejection tests. The eligible corpus has only source statements; no substantive approved competing interpretations/folklore/chronology coverage is demonstrated. |
| Follow-ups, glossary and depth changes preserve factual support and uncertainty in evidence sections; general explanations remain explicitly unverified. Natural greetings, clarification and consented context work without silent failures or a permanent turn-count block. | PASS for tested engineering; content quality remains pending | Final eight follow-up cases pass; live glossary/depth/language/official follow-ups and sustained-message/cancellation/browser checks pass. This does not certify all messages or independent explanatory quality. |

## Revised execution parts

| Part | Engineering/evidence result | Open acceptance evidence |
|---|---|---|
| 0–1: aligned contract/reliable delivery | Delivered and pushed previously | No permanent turn-count block; remaining broad release gates below |
| 2: personality/language/consented context | Delivered; fresh real bilingual conversation checks | Actual human personality/clarity ratings |
| 3: Liaoning inventory/collection/review | All-city acquisition/review tooling and drafts delivered | 448 drafts remain unapproved; no automatic content/rights review |
| 4: hybrid explanations/support | Delivered with conservative exact variants, general labels and registered official lookup | Expanded approved variants/conflicts, current operational adapters and independent factual quality |
| 5: relevance/runtime | Actual diagnostic relevance/BGE measurements and bounded optimization delivered | Expanded expert-reviewed relevance gold and production hardware/load sample |
| 6: chat/sources/accessibility | Delivered; 59 dedicated browser checks, scoped EN/ZH axe audits, fresh live workflow | Physical phone/Safari/screen-reader and native browser zoom execution unavailable |
| 7: fresh bilingual evaluation/human review | 48 live cases and 16 isolated fault cases measured; actual human packet prepared | Required human judgments, independent expert assessment, 200-question pilot |
| 8: reproduction/closure | Fresh isolated setup/database/build/startup reproduction and this audit delivered | Closure withheld while required prior gates lack evidence |

## Two readiness rows

| Readiness | Current result |
|---|---|
| Chatbot engineering acceptance | Functional implementation and local verification delivered. Human quality/release assessment is still pending. |
| Province-wide content readiness | **Not ready:** all 14 cities are inventoried and have draft preparation, but only one exhibit/two stored passages are currently eligible. Registered official lookup is useful supplemental evidence, not approved whole-province coverage. |

No scope reduction from whole Liaoning is inferred. The all-city launch manifest stays binding. Stored text, acquired inventory rows, explanatory drafts, fetched official pages and actual editorial approval remain distinct denominators.

## Measurements and limits

Final local verification: **421 API tests, 59 guide browser checks and 68 broad museum browser regressions** pass, with production build/lint/types/contracts/assets/secret checks and isolated reproducibility evidence.

- Final support and citation integrity: **18/18 actual sourced answers** each; general-only answers and abstentions receive no support credit. First run: 16/16, two false refusals preserved.
- First reserved functional sample: **32/32**; diagnostic rerun remains **32/32 exposed**, not fresh independent gold.
- Final meaningful API p95: **2.96 seconds**, sample 26, excluding seeds and browser rendering. Fresh three-turn browser sample: **1.47–1.99 seconds**. The five-second target remains unchanged, and neither sample fulfills the 200-question pilot.
- Existing QA factual-support target ≥95% and citation target 100% retain their pilot interpretation. Small structural samples cannot be substituted for independent historical scoring.
- Human scored denominators: **zero**. Pending: 26 historical correctness units, 46 clarity units, 46 personality units and 23 bilingual families.
- No configured GitHub Actions workflow or public deployment verification exists. Push success and local test success are separate from remote CI/production availability.

## Concrete closure blockers and next actions

1. Actual reviewer completes the [human packet](PHASE_03_HUMAN_REVIEW_PACKET.md) and its [hash-bound worksheet](evidence/phase03-hybrid-part07/human-review-template.json); grade real judgments with the documented command. Owner/editor and independent specialist reviews remain separately attributed.
2. Complete genuine content/rights/source approvals against the whole-Liaoning launch manifest, then explicitly publish eligible units. No assistant-generated approval is permitted.
3. Prepare expanded independently reviewed relevance/quality gold and run the 200-question bilingual pilot with stated coverage, answered/refused denominators, independent assessments and intended runtime/load.
4. Record unavailable device/native-zoom checks honestly, obtain the required environment evidence, and rerun affected gates after any fixes.
5. Reissue this closure decision only when the required evidence supports it. Phase 4 saved journeys is separate work and does not close these omissions.

Delivery details: [Part 6](PHASE_03_HYBRID_PART_06.md), [Part 7](PHASE_03_HYBRID_PART_07.md), [Part 8](PHASE_03_HYBRID_PART_08.md), final machine-readable verification in `report/evidence/phase03-hybrid-part08/final-verification.json`.
