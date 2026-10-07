# Retrieval relevance and runtime

Implemented 7 October 2026. Keep lexical retrieval as the default for the current two-passage approved collection. BGE-M3 hybrid retrieval is available explicitly after local pinned preparation and index build. Semantic similarity proposes candidates; independent factual support determines whether any claim may be published.

## Improvements

BM25 builds document frequency once per ranking call and strips question boilerplate in English and Chinese. Database snapshot and ranking timings are recorded separately. Scoped requests reuse the first retrieval when it already contains the topic's material.

The optional BGE worker loads the pinned offline CPU model once, uses two compute threads, and accepts one active request with no waiting queue. Busy/unavailable/crashed/timed-out workers degrade explicitly to lexical retrieval. Cancellation kills and reaps the subprocess. Shutdown closes it. The worker retains no provider/database credentials, allows 256 requests or 30 minutes, bounds input/output and memory (16 GiB virtual address ceiling on Linux), and keeps at most 128 hashed-query vector cache entries. File signatures invalidate the worker/cache when model artifacts change. Index parsing/validation is cached by file identity; corpus/version eligibility is still checked freshly. Optional startup prewarming exposes a cold-start result rather than silently delaying every visitor query.

Prepare/build explicitly with `uv run --project apps/api --extra embeddings python -m folkverse.guide_index prepare` and the same command ending in `build`. These commands do not approve data. Run `pnpm benchmark:guide` for the isolated diagnostic benchmark. Optional weights and generated indexes stay ignored.

## Measured limits

The diagnostic benchmark uses 84 **unapproved** bilingual passages from 42 topics across 14 cities. Its 47 queries were split into development and reserved diagnostic cases before parameter selection. No expanded expert-approved gold set exists yet. This index is temporary and never served. The actual approved database count is reported separately.

Reserved positive top-three recall: 27/27 for lexical and hybrid. Hybrid improves reciprocal rank from 0.963 to 0.981, but negative cases return unwanted candidates in 2/2 hybrid versus 1/2 lexical cases. Development recall improves from 15/16 to 16/16. Neither retrieval result establishes factual truth; lexical remains the default pending broader approved content and relevance review.

Measured on Linux/i5-11320H CPU: warm distinct-query hybrid p95 736 ms; repeated-query p95 41 ms; lexical p95 3.23 ms. Reusing validated index objects reduced repeated-query p95 from 115 ms to 41 ms in these samples. Cold one-shot model runs range approximately 14–30 seconds; final 84-passage startup/indexing took 115 seconds. Worker resident memory is about 2.1 GiB. Concurrent CPU test activity affected cold measurements, so these samples are not a controlled statistical A/B experiment. See raw failures, sample sizes and environment in the [Part 5 report](../report/PHASE_03_HYBRID_PART_05.md).

The five-second p95 meaningful-content target remains unchanged. A small real-provider browser sample measures retrieval, generation, validation and final display separately; it is not the required 200-question bilingual pilot. Large approved-corpus database scaling, intended production hardware/network/concurrency and expert relevance remain future acceptance evidence.
