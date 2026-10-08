# Saved personal journeys — Phase 04 implementation contract

Status: **complete within Phase 04 scope, 8 October 2026**. All four acceptance gates pass. See the [final completion report](../report/PHASE_04_FINAL_COMPLETION.md); the earlier implementation review is historical.

## Selection and ownership

The application—not the model—selects actual eligible database exhibit IDs. Every selected exhibit must pass the existing review-hash/dependency publication gate, have title and summary in the requested locale, a stored estimate of 1–60 minutes and an approved absolute HTTPS source link. Official-lookup `topic_*` profiles and decorative Shaanxi/Fujian/Guangdong examples are not journey exhibits. Restoring the existing reviewed snapshot currently yields **one eligible 3-minute exhibit**; unreviewed candidates remain unpublished.

POST preferences are explicit `interests` (up to eight), locale (`en` / `zh-CN`), 5–60 minutes, optional region, optional starting exhibit and optional `novelty_exhibit_ids` (up to 24 previously seen IDs explicitly supplied by the visitor). Novelty is a soft preference for unseen stops at equal time, never passive tracking. Stable ID/value tie-breaks, bounded time selection and theme-diverse ordering make unchanged inputs deterministic. This is a documented heuristic, not a claim of globally optimal recommendation quality. An explicit starting exhibit must fit region, locale, interests and time; it cannot silently override them. Fewer stops and a localized notice are normal for a small or empty corpus.

Signed HttpOnly session cookies derive ownership. Body-supplied owner fields are rejected. Session expiry denies access; deleting the session cascades all its journey and stop rows. Expired rows are not automatically purged by a new scheduled job; no automatic retention/deletion guarantee is made beyond explicit session deletion.

## Endpoints and reload

- POST `/api/v1/journeys` creates a new saved route and returns its current version.
- GET `/api/v1/journeys?locale=&limit=` returns at most 20 newest routes for this session. The UI restores the newest one on reload; prior generated routes are not listed in a separate history UI.
- GET `/api/v1/journeys/{identifier}?locale=` re-resolves the owned route in the requested display language.
- PATCH `/api/v1/journeys/{identifier}?locale=` takes required `ordered_exhibit_ids` (zero to 24) and optional `expected_version`. Empty is an intentional saved route; omitted IDs are a 422 error, not an implicit delete. Duplicates, unpublished IDs and over-time edits fail. IDs must satisfy stored region/interests and have content in both the saved language and requested display language, so a successful PATCH round-trips every submitted stop. A PostgreSQL row lock serializes version checking and writes; stale edits return 409.

Every read recomputes total from current stored estimates and excludes withdrawn/deleted, locale-unavailable, source-ineligible or over-budget stops with a notice. This is a **read-only projection**, not destructive pruning: a re-published exhibit can reappear. PATCH persists the edited order/removals. No free-text route, invented duration or physical transport instruction is accepted.

## Explanations and provider boundary

The existing server-only gateway supports DeepSeek and OpenAI-compatible Ollama. Configure `GUIDE_PROVIDER` and only that provider’s ignored credentials/base URL/model. An Ollama key is never sent to DeepSeek; credentials never enter the browser, response, evidence or prompt. Ollama requires an explicitly positive request quota. DeepSeek requires a positive monetary cap or explicit `DAILY_AI_BUDGET_UNLIMITED=true`, plus its key. The journey factory now honors the same unlimited setting as the guide gateway. Shared defaults remain fail-closed. The owner’s existing unlimited DeepSeek configuration was preserved: real EN/ZH generated reasons and unchanged-regeneration cache reuse were verified separately from the provider-disabled browser suite.

The model can only choose from per-stop application-verified reason codes (time fit, matched interest, actual first starting stop, explicit novelty and collection discovery). Exact IDs, allowed codes, duplicates, required coverage and extra fields are validated; the server renders bilingual wording. Free prose, dates, IDs, URLs, transport routes and model durations are rejected. Fallback selection reasons remain useful and explicitly deterministic or unavailable.

Successful reason selections use a bounded process-local LRU/TTL cache keyed by current reviewed route inputs, corpus signature, locale and preferences. Concurrent identical requests share a call; failures are not cached permanently. Unchanged successful regeneration makes no extra call within the cache lifetime. Restart/multiple workers do not share this cache. Generation runs outside the database transaction; final ownership, publication and version are freshly rechecked before returning or persisting labels.

## Web behavior and deployment

The saved-journey panel works with actual APIs in both app modes. Demo offers a separately labelled optional memory-only example; live never substitutes it. Multi-theme choices, 5–60-minute duration, region and explicit novelty feed POST. Remove/reorder immediately recalculate the visible total, indicate pending save and persist through PATCH; failed writes do not claim success. A module-level shared session bootstrap plus Web Locks (where available) prevents concurrent creation from discarding a just-saved owner cookie. Old-language mutation results are suppressed and refreshed. Focus returns to a neighbouring/moved stop after save; these keyboard behaviors pass actual Chromium browser execution, including a clearly labelled controlled two-stop fixture and real single-stop PostgreSQL saves.

Stop links open the actual exhibit detail/source drawer or `/guide?exhibit=<id>`. Map-selected city preferences and explicit exhibit entry context carry into the planner, not into automatic tracking. Publication is refreshed on focus and every 15 seconds; failures clear authoritative display.

For HTTPS proxy deployment both `PUBLIC_APP_ORIGIN` on the web process and matching API `ALLOWED_ORIGINS` are required; keep signed cookies secure on public HTTPS. The journey BFF validates same-origin mutations, forwards only the session cookie, bounds bodies and preserves no-store responses. Final acceptance includes production Chromium runs at desktop, tablet and phone sizes, EN/ZH touch input, scoped axe checks, CSS 200% zoom and reduced motion. Physical-device/Safari testing and permanent production hosting remain separate release work.
