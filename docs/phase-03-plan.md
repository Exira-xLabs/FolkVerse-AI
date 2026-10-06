# Phase 03 implementation parts

Started 6 October 2026 (Asia/Shanghai). Canonical requirements: [Phase 03](../phases/03_GROUNDED_GUIDE.md). Each part gets implementation, focused verification, and a status update before the next part starts. Approved artwork, Jinyao's introduction and Messenger presentation remain the UI contract.

| Part | Deliverable | Completion check | Current state |
|---|---|---|---|
| 1. Reviewed evidence foundation | Lexical EN/ZH retrieval, bounded evidence bundles, coverage/version index, current-review rechecks | Withdrawal, stale review, rights, locale, context and empty-result tests; real DB check reported separately | Baseline implemented; 23 portable tests pass; PostgreSQL integration blocked |
| 2. Provider gateway and resource limits | Recheck official DeepSeek documentation; server-only configurable adapter; timeout/cancel, one bounded retry, rate/concurrency limits, usage reservations and daily cap | Mock transport failure/limit tests, no browser secrets, credentialed check if configured and authorized | Implemented; 62 gateway tests pass; PostgreSQL/live-provider integration unverified |
| 3. Expert explanation harness | Question/exhibit/depth context, ambiguity, structured explanations, claim mappings, chronology and support checks, history/folklore distinction | Reject invented IDs and unsupported claims; injected source instructions cannot alter policy; bilingual insufficiency/follow-up tests | Conservative listing harness implemented; 66 tests pass; free-form expert explanation remains gated |
| 4. Live Guide and sources | Session-owned POST `/guide`, validated fetch SSE through BFF, Jinyao chat, source inspection, cancellation and meaningful-answer latency | Browser-supported/unsupported/error flows in both languages; raw provider text never streamed | Implemented; owned API/BFF and fixture browser checks pass; real integration blocked |
| 5. Hybrid retrieval and reviewed coverage | Offline BGE-M3 batch embeddings, model/corpus versions and invalidation, hybrid ranking, actual runtime benchmark; prepare attributable review candidates | Explicit lexical-only model-unavailable behavior, measured retrieval comparison; new content requires actual human review | Implemented; portable checks and lexical benchmark pass; actual dense/DB benchmark and human review remain blocked |
| 6. Evaluation and phase handoff | Dated versioned bilingual set of at least 40 cases, held-out scoring, failures, coverage gaps, version and usage/latency reporting | Separate correctness, support, citations, clarity, faithfulness, uncertainty and follow-up scores; every phase gate audited | Implemented: 64 cases, preserved baseline and diagnostic rerun; human dimensions and real integration remain pending |

## Part 1 implementation

`apps/api/src/folkverse/guide_retrieval.py` reuses Phase 02's hash-bound review, rights and published-exhibit dependency checks. Only passages linked to published claims enter the corpus. This is a deliberate initial scope: unattached passages are not used to imply broader museum expertise.

The module tokenizes normalized Latin words and CJK bigrams, then ranks passage text using a BM25 lexical baseline. Language and optional exhibit scope are strict filters. Bundles hold up to eight passages and 12,000 text characters; oversized passages are omitted rather than silently truncated. A lexical overlap is **not** a determination that the passage answers the question. Part 3 must establish support or return insufficiency.

Evidence includes actual source metadata, permitted passage text, locator, rights basis, editorial reviewer/date, passage fingerprint, exhibit IDs and region IDs. Corpus versions hash the eligible evidence and metadata deterministically. Every call refreshes ORM state and checks eligibility; no retrieval cache or vectors exist. `bundle_is_current` rechecks selected evidence immediately before future answer publication. The caller must bound the entire operation and avoid awaiting unrelated work between that check and publishing; this is not a transaction-wide revocation lock.

Coverage lists eligible EN/ZH passage counts, sources, exhibits and regions. Period/person/object axes are explicitly empty because the current schema lacks reviewed structured assertions for them. These are unknown/unindexed axes, not proof that every period has zero evidence. No inferred historical dates, dynasty assignments, translations or new approvals are created.

Inspection commands use the configured real PostgreSQL database:

```sh
uv run --project apps/api python -m folkverse.guide_retrieval
uv run --project apps/api python -m folkverse.guide_retrieval --question 'Where is Fuzhou shadow puppetry listed?' --locale en
uv run --project apps/api python -m folkverse.guide_retrieval --question '复州皮影戏在哪个地区？' --locale zh-CN
uv run --project apps/api pytest apps/api/tests/test_guide_retrieval.py -q
```

The command returns a sanitized failure when the configured database is unavailable. It never substitutes the exported snapshot, fixture data or a provider response. No public retrieval endpoint, chat persistence, provider request or model download is introduced in Part 1.

## Scan findings and prerequisite work

The project has one Next.js web application, one FastAPI service, generated OpenAPI contracts, PostgreSQL migrations, content curation/snapshot recovery, shipped decorative assets and map data, labelled interactive previews, and substantial historical verification reports. The active Jinyao conversation is scripted; live Guide is still unavailable. No existing embedding or provider implementation was found.

The delivered snapshot has one approved exhibit and two approved passages from one source; these establish a narrow bilingual heritage-inventory fact. They do not support broad China-history explanations. The current audit in `report/AGENT_REPORT.md` distinguishes historical local successes from this machine's blocked DB checks and also lists navigation zoom, outdated browser selectors, fresh-restore/media verification, raw map-reference portability and mode-default inconsistencies. Those prerequisite fixes should be verified before claiming live integration ready; the existing audit and unrelated working changes are preserved.

Part 1 tests use a disposable SQLite database to exercise real ORM eligibility helpers with explicitly synthetic reviews. They do not certify PostgreSQL migrations, snapshot recovery, production query performance, concurrent external revocation, historical answer quality or bilingual model faithfulness. No 95% quality claim is made.

## Part 2 implementation

The [gateway implementation and configuration](guide-gateway.md) describe server-only JSON transport, persistent PostgreSQL admission/usage accounting, configured price bindings, bounded retries/deadline/cancellation and metadata retention. Migration `0003_gateway` extends the existing database; no provider credential or live endpoint was added. Current official API/model, JSON, vision and pricing docs were inspected. API/web missing-mode defaults are aligned to live, with unconfigured provider calls unavailable.

Verification: 62 gateway tests, 23 Part 1 tests and the existing outage regression pass (86 total). Portable migration upgrade/downgrade and concurrent admission tests pass. PostgreSQL migration SQL generation, Ruff, strict mypy and foundation contract/secret checks pass. Credentials are absent and real PostgreSQL remains unavailable, so actual provider access/billing and production database locking are unverified. [Part 2 report](../report/PHASE_03_PART_2.md).

## Part 3 implementation

The [conservative explanation harness](guide-harness.md) resolves narrow published topics, rejects unsupported question types, validates complete reviewed statements beyond ID checks, attributes actual sources, and rechecks evidence before returning segments. Follow-up context is consented, session-bound, signed, temporary and contains no model prose. Uncertain coverage stays partial; unsupported chronology, glossary, historical classification and rewritten explanations remain explicit gaps.

Verification: 66 harness tests plus 86 earlier regression checks pass (152 total). Ruff/strict mypy and foundation contract/secret checks pass. The supplied credential was stored in ignored `.env`; the authentication-only check returned HTTP 401, so real DeepSeek generation remains unverified. PostgreSQL remains unavailable. This is a restricted evidence baseline, not completion of the expert-quality gates. [Part 3 report](../report/PHASE_03_PART_3.md).

## Part 4 implementation

[Live transport and chat](guide-live.md) implement session-owned JSON/SSE, final ownership/evidence rechecks, BFF forwarding/cancellation, Jinyao live controls, current-source inspection and periodic ledger maintenance. Checked response receipt latency is separated from progress and unsupported outcomes. Page-only turns and optional 30-minute signed topic/evidence context preserve the conversation lifecycle.

Verification: 13 new HTTP/SSE tests plus 152 prior portable regression checks pass (165 total). 18 isolated browser checks pass and cover EN/ZH chat, errors, incomplete/mismatched streams, Stop/Retry, source withdrawal, consent/focus/history, real BFF transport and the scripted demo. Real provider authentication still returns HTTP 401; PostgreSQL is not running. Fixtures do not establish provider generation, database locking or guide quality. [Part 4 report](../report/PHASE_03_PART_4.md).

## Part 5 implementation

[Hybrid retrieval](guide-hybrid-retrieval.md) adds pinned offline BGE-M3 model preparation, atomic corpus/model/encoder-versioned dense artifacts, cancellable CPU query workers, deterministic BM25+dense fusion and explicit lexical-only states. Current review/rights/language/exhibit gates and final claim validation remain authoritative. The review packet prepares 16 attributable draft candidates without new approvals.

Verification: 32 new tests plus 165 portable regressions pass (197 total); 19 fixture browser/BFF/demo checks pass. An actual exported-corpus lexical benchmark measures approximately 0.034 ms median ranking/bundle time, excluding DB eligibility reads. The bounded model download timed out before weights completed; BGE inference/semantic improvement and real PostgreSQL index builds remain unverified. Semantic retrieval stays disabled by default. [Part 5 report](../report/PHASE_03_PART_5.md).

## Part 6 implementation

The [dated bilingual evaluation](guide-evaluation.md) delivers 64 cases, with 16 development and 48 reserved cases, frozen reviewed mappings, explicit uncertainty and unacceptable answers. Strict scoring separates seven dimensions; human judgments remain pending. Run-bound review worksheets reject changed hashes, unattributed ratings and duplicate/dropped units. Live mode preserves provider/billing gates; fault injection remains isolated to export fixtures.

Initial fixture target score: 58/64 (42/48 reserved). The run exposed an EN/ZH follow-up version-validation bug; harness v2 checks current evidence independently of retrieval language/title while retaining withdrawal checks. Diagnostic rerun: 60/64 (44/48 reserved), with four supported paraphrase misses retained. The initial baseline is preserved; the rerun after case exposure is regression evidence. [Part 6 report](../report/PHASE_03_PART_6.md).

## Remaining phase gates

The six planned implementation parts are delivered as a restricted baseline. Real PostgreSQL/provider generation, actual BGE runtime, published review expansion and independent historical/clarity/bilingual judgments remain outstanding. The [handoff](phase-03-handoff.md) maps each acceptance gate to evidence and next work. Phase 03 is not fully accepted; broad historical explanations and the 95% expert-quality target cannot be claimed from fixture checks.
