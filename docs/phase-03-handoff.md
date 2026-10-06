# Phase 03 handoff — 6 October 2026

Parts 1–6 are implemented as a conservative evidence baseline. Phase 03's full expert-guide acceptance remains incomplete. The [Part 6 report](../report/PHASE_03_PART_6.md) publishes fixture results, the unchanged baseline, failures and pending human judgments.

Push audit update: [Ollama authentication is verified](guide-ollama.md), and harness v3 fixes the four listing-paraphrase misses. The exposed v1 regression reaches 64/64 functional targets. Original baseline and v2 evidence remain preserved. Real generation/SSE, PostgreSQL, BGE runtime and human quality review remain unverified. See [the audit report](../report/PHASE_03_PUSH_AUDIT.md).

## Implementation map

| Responsibility | Implementation and contract |
|---|---|
| Reviewed corpus, eligibility, coverage, bounded bilingual BM25 | `guide_retrieval.py`; [retrieval contract](../report/PHASE_03_PART_1.md) |
| Optional offline CPU BGE, corpus/model invalidation, hybrid fusion | `guide_embeddings.py`, `embedding_worker.py`, `guide_index.py`, `guide_hybrid.py`; [hybrid contract](guide-hybrid-retrieval.md) |
| Provider JSON, cancellation/retry, persistent shared admission and usage | `provider_gateway.py`, `gateway_limits.py`, migration `0003_gateway`; [gateway contract](guide-gateway.md) |
| Narrow supported questions, exact statement support, signed owner-bound context | `guide_harness.py`; [harness contract](guide-harness.md) |
| Owned JSON/SSE, BFF, page-memory chat and current sources | `guide_api.py`, web `/api/v1/guide`, Jinyao chat/source inspector; [live contract](guide-live.md) |
| Frozen paired cases, independent functional scoring, bound human review worksheets | `guide_evaluation.py`, `guide_review.py`, `tests/evaluation/guide/v1.json`; [evaluation method](guide-evaluation.md) |

## Acceptance evidence

| Original Phase 03 gate | Current evidence and remaining work |
|---|---|
| Real credentialed completion | Successful completion unverified. The earlier 401 was a provider mismatch; Ollama authentication is now verified. Demo mode and zero Ollama request quota disable generation. |
| Supported/unsupported distinction in both languages | Verified in portable fixtures; v3 also handles the four previously missed listing paraphrases. Real-provider generation remains unverified. |
| Reject invented citations and source instruction attacks | Verified in harness/evaluation fixtures; real model output remains unverified. |
| Withdrawal, timeout and daily-cap errors | Verified in isolated portable tests; real PostgreSQL locking/withdrawal and live provider failure remain unverified. |
| Keys absent from browser/logs; actual source drawer | Secret/foundation checks and prior browser fixtures pass. Current real PostgreSQL/provider browser round trip remains unverified. |
| Dated bilingual evaluation and expert explanations | 64 cases with separated metrics delivered. Three human dimensions pending; broad explanatory behavior and reviewed coverage incomplete. No 95% expert-quality claim. |
| Historical evidence versus interpretations/folklore/adaptation; checked chronology | Unavailable chronology and classification upgrades are rejected. Actual competing interpretations, glossary and chronology explanations need reviewed material and support validation. |
| Follow-up simplification/depth with citations and uncertainty | Checked excerpts, consent/ownership and EN/ZH switches verified in fixtures. Simplification/depth repeats exact evidence; meaningful rewritten explanations remain unavailable. |

## Coverage and next work

The dated approved export contains two passages, English and Chinese versions of one Fuzhou shadow-puppetry inventory listing. It supports the listed locality and theatre category, not dynasty chronology, provenance, historical figures, material objects, beliefs, contested interpretations or a glossary. Sixteen prepared candidates remain drafts. Editorial review must precede publication; no approval is synthesized by the evaluator.

1. Restore the dedicated PostgreSQL environment, apply migration `0003_gateway`, and verify current reviews, withdrawal and shared admission with actual database-backed tests. Existing historical DB evidence does not establish the current machine's readiness.
2. Use the verified Ollama configuration with the deployment's positive bounded daily request quota after PostgreSQL is ready, then run live evaluation and actual SSE latency/usage checks. Fixture latency and mock tokens cannot establish provider behavior or cost.
3. Complete the pinned BGE weights, run actual CPU indexing/inference on the current eligible corpus, and measure semantic relevance and latency before enabling dense retrieval.
4. Obtain human editorial review of the draft coverage packet and independent bilingual review of actual answers. Expand explained terminology, chronology and attributed interpretations only with support checks and suitable reviewed evidence.
5. Measure paraphrase recall and broader explanations with an independently reviewed, newly reserved evaluation version. Keep v1's failures and post-exposure interpretation intact. Broader explanation quality needs a new representative sample, not repeated inventory quotations.

Phase 04 should not be reported as the next accepted phase until these Phase 03 gates have evidence. Current blockers and results are also recorded in [build status](build-status.md).
