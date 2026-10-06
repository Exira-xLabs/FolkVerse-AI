# Phase 03 Part 3 — conservative explanation harness

6 October 2026, Asia/Shanghai. **The narrow evidence harness is implemented. Free-form expert explanations, real provider generation and PostgreSQL integration remain unverified or gated. Phase 03 is incomplete.**

## Delivered behavior

The internal harness resolves published exhibit references, requested language/depth and consented follow-up scope. Unsupported question types receive bilingual insufficiency even with relevant vocabulary; partial names, multiple topics and unresolved pronouns receive clarification. It selects bounded reviewed evidence through existing approval/rights gates, requests JSON from the Part 2 gateway, validates all displayed claims and rechecks selected evidence before returning them.

A valid citation is insufficient: every factual segment must match a **complete reviewed passage**, retain attribution, use the correct language, map to the resolved published exhibit and occupy a checked display section. Changed dates, negations, invented origin, shortened quotations, paraphrases, definitions and free narrative are rejected. Source statements cannot be relabelled as historical certainty, folklore, scholarly interpretation or creative adaptation. Actual source metadata accompanies every published excerpt. This restriction verifies textual support; it does not independently establish the historical correctness of the reviewed source or validate arbitrary natural-language entailment.

Signed thirty-minute follow-up tokens contain session-bound ownership, topic ID, previously used evidence IDs/versions and uncertainty. Every reuse requires explicit consent. They contain no raw question or previous model prose and create no server chat-history storage. Expiry, tampering, cross-session use, revoked IDs and changed source metadata invalidate context. Locale switches use separately reviewed language material. Existing partial uncertainty cannot be upgraded by simplification.

No Jinyao UI, public endpoint, SSE transport, new content approval or deployment was added. The service is initialized on `app.state.guide_harness` for the next part. [Behavior and integration contract](../docs/guide-harness.md).

## Verification

| Check | Result | Evidence |
|---|---|---|
| Harness tests | 66 pass | Included in [focused suite](evidence/phase03-part3/tests.txt) |
| Retrieval/gateway/outage regressions | 86 pass | Same suite; **152 total** |
| `pnpm lint` | Web ESLint/API Ruff pass | [Lint](evidence/phase03-part3/lint.txt) |
| `pnpm typecheck` | Web TypeScript/API strict mypy, 19 API source files, pass | [Types](evidence/phase03-part3/typecheck.txt) |
| `pnpm check:foundation` | Contracts regenerate identically; assets and configured-secret checks pass | [Foundation](evidence/phase03-part3/foundation.txt) |
| `git diff --check` | Pass | Working-tree check |
| Server-only authentication check | DeepSeek `/models` returns HTTP 401 | [Sanitized environment result](evidence/phase03-part3/environment.txt) |

Tests cover complete statement support in both languages/depths, invented claims with real IDs, invented citation/related IDs, extra narrative/URLs, incorrect locale/depth, duplicate/unmapped statements, classification changes, lexical overlap on unsupported questions, ambiguity, consent/ownership/expiry, follow-up language switches, changed source versions, withdrawal after generation, suspicious source instructions, provider/cap failures, outer deadline and oversized evidence. One integrated test uses real gateway/ledger code with mocked HTTP and confirms that transport-completed billing does not cause an unsupported claim to publish. SQL repository checks use real eligibility helpers and disposable SQLite synthetic reviews.

These are functional/security checks, not the required held-out historical-expertise evaluation. No 95% score, provider model quality, actual completion latency, real invoice amount, PostgreSQL locking or physical-device result is claimed. The existing upstream TestClient deprecation warning persists. Node 26 remains outside the declared Node 22 supported range; successful web checks do not certify that runtime.

## Credential handling and blockers

The supplied credential was saved only in ignored `.env`, with restrictive file permissions; `.env.example` remains placeholders. The server-side authentication-only check sent no question, evidence or generation request. DeepSeek returned HTTP 401. No raw key or provider error body was included in evidence/report files. Demo mode and the zero budget were preserved; no paid generation was activated. A credential accepted by DeepSeek is still needed for real model validation.

The dedicated PostgreSQL container remains absent following the Part 1 registry timeout. No real corpus restoration, migrated database/harness traversal or credentialed completion was performed. Tests use labelled synthetic evidence/mocked generation and do not substitute them into production. Actual keys, reviewer approvals or success states are never manufactured.

## Scope limitations and next part

The current two approved bilingual passages support a narrow heritage inventory listing. The initial harness uses a strict question grammar and complete source wording. It can reject valid question paraphrases; deeper/simplification requests cannot obtain new factual content or rewritten beginner prose from this baseline. Definitions, dated chronology, competing scholarly classifications and broad historical explanation require more reviewed material plus an independently evaluated support method. Suspicious-instruction filtering is conservative and incomplete; no tool execution and constrained publication remain the core safeguards.

The output recheck has a normal small read/publication race; it is not a revocation transaction lock. The future public endpoint must authenticate session ownership, enforce mode/request boundaries, propagate cancellation, render strings as plain text, wire periodic metering maintenance and measure first validated answer latency. Part 4 owns those browser/SSE/source controls. Parts 5–6 own hybrid retrieval and the dated scored bilingual evaluation; broad expertise remains gated rather than implied by the presentation.

Changed files: `apps/api/src/folkverse/guide_harness.py`, its test file and API service initialization, harness/phase/status/decision docs and new Part 3 report/evidence. The local credential file is ignored. Prior audit, UI, Part 1–2 work and pre-existing generated development-type imports are preserved.
