# Guide HTTP transport and Jinyao chat

Current integration update (6 October 2026): actual PostgreSQL and bounded Ollama EN/ZH
browser generation now pass; pinned BGE CPU inference/indexing is measured. The root
configuration remains demo/zero quota; live verification uses process-only bounded settings.
[Current report](../report/PHASE_03_COMPLETION.md), [personality policy](jinyao-personality.md),
[coverage](guide-coverage.md) and [handoff](phase-03-handoff.md) supersede earlier unavailable
integration statements below. Broader classified explanations and independent human quality
remain pending. Beginner/deeper presentation uses a lossless inventory grammar; exact
reviewed claims, attribution, revocation and browser publication validation remain enforced.


Phase 03 Part 4, 6 October 2026 (Asia/Shanghai). The live UI and transport are implemented; real PostgreSQL/provider integration remains unverified. The extractive harness still supports only the narrow reviewed listing coverage described in [guide-harness.md](guide-harness.md).

Push audit: the browser additionally requires nonempty support arrays, exact claim/source/reference mappings, requested source language, full cited-source coverage and the controlled attributed display before publishing. Six added browser cases reject violations. Provider selection now includes [Ollama Cloud](guide-ollama.md); real inference remains unverified.

`POST /api/v1/guide` accepts a bounded question, locale, depth, optional exhibit ID and explicitly consented signed follow-up context. Identity comes from the signed anonymous-session HttpOnly cookie and a current database session; a client-supplied owner is forbidden. Origin checks apply before processing. Demo mode returns unavailable. Session ownership and selected evidence are checked again after generation, before publication.

JSON requests return the checked answer. `Accept: text/event-stream` returns `meta`, allowlisted `status` progress, then checked `answer`, `sources` and terminal `done`, or a sanitized terminal `error`. The first metadata frame has unknown corpus version; the checked metadata frame records the actual corpus, retrieval mode and harness version. Provider deltas and proposed claims never cross this boundary. Errors after SSE headers have been sent use an error event rather than changing HTTP status. No completion event follows an error.

The Next.js `/api/v1/guide` proxy requires the browser origin to match its Host and request scheme. Next's bind hostname can differ from the browser Host, so `request.url` alone is insufficient for this check. The API also checks configured allowed origins. The proxy forwards only the owned cookie, origin, content type, accept and request body. Authorization and unrelated cookies are excluded. It bounds the input to 16 KiB, forwards the response without buffering, disables caching, and has a 150-second upper bound. Stop/close/disconnect aborts upstream transport and pending harness/provider generation; no automatic client retry occurs.

The live Messenger dialog shows connection/retrieval/generation/validation progress and only publishes an answer after a complete checked response. Incomplete streams, mismatched evidence, provider failures and budget/rate errors remain errors with an explicit Retry control. Supported answers show limited coverage and source inspection; unsupported answers carry no fabricated citations or meaningful-answer latency. Published exhibit suggestions and optional exhibit scope provide starting points. Concise/beginner/deeper selectors preserve the conservative harness: broader rewritten explanations, glossary, chronology and historical classifications remain gated.

Source inspection uses the returned evidence plus a fresh published-source request. The drawer checks source URL/title/institution, exact passage text/language/locator/rights and editorial reviewer/date. Changed, withdrawn or unavailable evidence produces an honest unavailable state. Quotes, rights, locator, institution and editorial review are visible; original links accept only HTTP(S). Nested native dialogs preserve focus and scroll locking.

Chat stays in component memory for this page, retains turns when closing/reopening, and disappears on navigation/reload. There is no Clear action or durable history. Optional follow-up consent starts off; the server-signed, session-bound topic/evidence token lasts at most 30 minutes and contains no previous model prose or private question. Turning consent off drops the token. The gateway stores bounded operational usage metadata rather than raw questions or answers, as documented in [guide-gateway.md](guide-gateway.md).

Per-worker admission bounds cheap requests, including questions that never call a provider; PostgreSQL-backed provider rate/concurrency/budget gates remain shared across workers. The API lifespan prunes expired usage metadata every 60 seconds using the ledger's retention and stale-reservation policy. This maintenance path is implemented but real PostgreSQL scheduling/locking is unverified here.

Server latency starts at request middleware entry and measures time to checked content emission, separately from status progress. `first_meaningful_content_ms` is null for insufficiency/clarification; `response_content_ms` measures any checked response. The UI measures elapsed time from guide fetch start through receipt of the complete checked response, excluding session bootstrap. This is receipt latency, not a browser first-paint measurement or a production benchmark.

Verification commands:

```sh
uv run --project apps/api pytest apps/api/tests/test_guide_api.py -q
pnpm build
pnpm exec playwright test --config playwright.guide.config.ts
```

The dedicated browser configuration uses labelled synthetic evidence and a local fixture upstream. It exercises the real Next.js proxy separately from browser-mocked chat responses and includes the existing scripted-demo regressions. The main healthy-database browser configuration excludes these isolated fixtures. Neither configuration substitutes fixtures into the production application. Actual live activation needs an accepted DeepSeek credential, healthy migrated PostgreSQL and an explicitly configured positive daily budget. Tests do not establish historical expertise or complete Phase 03.
