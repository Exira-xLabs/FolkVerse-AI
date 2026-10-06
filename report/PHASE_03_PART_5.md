# Phase 03 Part 5 — hybrid retrieval and review preparation

6 October 2026, Asia/Shanghai. **Implementation and portable verification are delivered. The actual BGE-M3 benchmark and real database index remain blocked; new content is draft. Phase 03 remains incomplete.**

The guide now has an optional pinned BGE-M3 dense index/query path, deterministic BM25+dense rank fusion, model/encoder/corpus metadata and explicit lexical-only states. Offline builds accept only currently reviewed evidence and recheck the corpus before atomic publication. Runtime withdrawal, changed review/attribution/rights, model/encoder changes or malformed vectors invalidate the index. Dense similarity cannot bypass the conservative claim validator. The cancellable CPU worker never downloads a model during a visitor request, executes remote model code or records private questions. Query cold-start/hash verification costs remain visible. Jinyao labels keyword-only versus semantic matching.

The versioned private JSON artifact is the bounded small-corpus baseline, not a pgvector search implementation. PostgreSQL remains authoritative for reviews and sessions. Semantic retrieval stays opt-in/off by default; the approved bilingual corpus remains two passages from one source and one exhibit. The review packet prepares 16 draft candidates without changing the corpus, ledger or rights approvals.

| Check | Result | Evidence |
|---|---|---|
| New embedding/hybrid/benchmark tests | 32 pass | [API tests](evidence/phase03-part5/tests.log) |
| Earlier portable regression | 165 pass; **197 total** | Same log |
| Chromium fixture/browser+BFF+demo checks | **19 pass** | [Browser results](evidence/phase03-part5/browser-results.json) |
| Ruff, strict mypy, web lint/types, production build | Pass; 24 API source files | [API types](evidence/phase03-part5/api-types.log), [build](evidence/phase03-part5/web-build.log), verification record |
| Contracts/assets/configured-secret scan | Pass | [Foundation](evidence/phase03-part5/foundation.log) |
| Actual lexical ranking/bundle benchmark | Median 0.034 ms, maximum 1.242 ms, 600 measurements | [Runtime](evidence/phase03-part5/runtime-benchmark.json) |
| Real BGE-M3 weights/inference | **Unverified**; explicit download terminated at 240 seconds before completion | [Download status](evidence/phase03-part5/model-prepare-status.json) |
| Current PostgreSQL index build | **Unavailable**, no production artifact written | [DB build](evidence/phase03-part5/current-db-build.log) |
| Attributable candidate preparation | 13 inventory + 3 museum metadata candidates, all draft | [Review packet](../data/review-candidates/phase03-part5.json) |

The benchmark uses the dated exported corpus in isolated SQLite, preserving exact timezone-bound review fingerprints and all restoration/eligibility checks. It is not live PostgreSQL. Its lexical timing excludes DB reads and has only two eligible passages, so it cannot establish production performance or retrieval quality. Dense attempts remained explicitly lexical-only with `index_missing`; the batch encoder reported `model_unavailable`. No BGE latency or semantic improvement is invented. No user query or raw provider credential appears in evidence. Dependency installation is CPU-only and opt-in; cached incomplete model files stay ignored under `.local`.

Tests cover locale/exhibit filters, deterministic fusion, dense-only matches with **synthetic** vectors, score floors, complete passage/count limits, withdrawal across dependencies, review/rights/metadata changes, model/encoder mismatches, nonfinite/unnormalized/wrong-size/duplicate/corrupt artifacts, atomic publication failure, worker busy/timeout/cancellation/reaping, no missing-model spawn and async harness integration. Export benchmark tests verify retained approvals and reject modified approved wording. These are functional checks, not the held-out bilingual expert evaluation. Existing Node 26/support-range and TestClient deprecation limitations remain; physical-device/Safari/screen-reader tests were not performed.

The download timeout and absent PostgreSQL block real dense runtime/index validation. Semantic search remains disabled. Provider generation still has no successful credentialed evidence from prior parts; no new provider request or paid activation was made in Part 5. Broader reviewed historical coverage needs actual human review. Part 6 can now build the dated bilingual evaluation and handoff, but cannot manufacture the missing real-model/production/quality gates. [Implementation/configuration](../docs/guide-hybrid-retrieval.md).
