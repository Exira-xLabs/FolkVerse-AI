# Part 5 — retrieval relevance and latency

Delivery: 7 October 2026, local measurement and optimization. Raw results: [before index reuse](evidence/phase03-hybrid-part05/retrieval-before-index-cache.json), [final benchmark](evidence/phase03-hybrid-part05/retrieval.json), [final bounded worker smoke](evidence/phase03-hybrid-part05/worker-final-smoke.json).

Implemented query-boilerplate normalization, once-per-ranking BM25 document frequencies, reuse of scoped retrieval, separately timed database/ranking/generation/validation, reusable pinned offline BGE-M3 inference and validated index-object reuse. The worker isolates credentials, accepts one active request/no queue, expires after 256 requests/30 minutes, limits vector cache to 128 hashed-query entries and enforces a Linux 16 GiB virtual-memory ceiling. Cancellation/crash/shutdown kill and reap it; artifact/corpus changes cannot revive withdrawn evidence. Optional startup prewarming has an explicit outcome; visitor requests never download weights.

## Relevance sample and decision

The frozen diagnostic set has 47 queries over 84 unapproved bilingual source-derived passages from 42 topics in all 14 cities: 18 development cases and 29 reserved diagnostic cases. Source/topic identity supplies expected matches; no expert-reviewed relevance gold is claimed. Temporary diagnostic indexes are never served. The runtime eligibility count is independently recorded as two approved passages.

| Metric | Lexical | BGE hybrid |
|---|---:|---:|
| Development positive recall at 3 | 15/16 | 16/16 |
| Reserved positive recall at 3 | 27/27 | 27/27 |
| Reserved reciprocal rank | 0.963 | 0.981 |
| Development negatives with returned candidates | 0/2 | 1/2 |
| Reserved negatives with returned candidates | 1/2 | 2/2 |

Hybrid ranking improves in this small diagnostic sample but produces more irrelevant matches. Keep lexical as the runtime default for the current narrow approved corpus. Optional BGE remains implemented and actually tested; relevance never substitutes for factual-support validation. No parameter was tuned to conceal reserved negative failures. Expanded approved gold, intended-hardware concurrency and historical expert assessment remain open.

## Actual CPU timings

Linux/i5-11320H, pinned BGE-M3, two compute threads, sentence-transformers 6.1.0 / torch 2.9.1+cpu / transformers 5.18.0:

| Operation | Sample | p50 | p95 |
|---|---:|---:|---:|
| Old lexical ranking | 47 | 1.28 ms | 4.06 ms |
| New lexical ranking | 47 | 1.00 ms | 3.23 ms |
| Warm distinct hybrid queries | 47 | 515 ms | 736 ms |
| Repeated hybrid queries | 47 | 17 ms | 41 ms |
| Fresh database eligibility reads | 10 | 9.65 ms | 69.75 ms |

Repeated hybrid p95 was 115 ms before validated index-object reuse. Measurements are diagnostic samples, not controlled A/B distributions: concurrent CPU tests affected startup/load. Cold one-shot runs measured approximately 14–30 seconds; final model startup plus an 84-passage index took 115 seconds. Warm distinct maximum was 2.51 seconds. Report cold time explicitly rather than calling it acceptable visitor latency.

The final memory-cap smoke measures 10.97 seconds first load, 218 ms new warm query and 2.46 ms cached query; 1,987,264 KiB resident memory; actual `/proc` address-space limit 17,179,869,184 bytes; clean shutdown. Two simultaneous benchmark attempts produce `ready` / `model_busy`, without a hidden queue. Private weights remain ignored.

The real DeepSeek browser sample measures final meaningful UI content and server stage timings separately from retrieval. See Part 4 live artifacts/final verification for actual timing and attempt/cost counts. The five-second p95 target remains unchanged; a small development walkthrough does not fulfill the 200-question pilot or guarantee production latency. Current default avoids CPU model startup entirely. No provider tiers, budgets or model choice were silently changed.

Reproduce with `pnpm benchmark:guide`; see [runtime instructions](../docs/guide-retrieval-runtime.md).
