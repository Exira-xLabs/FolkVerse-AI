# Phase 04 — implemented; browser acceptance pending

7 October 2026, Asia/Shanghai. Implementation was approved after a read-only plan review. DeepSeek v4.1 Flash performed the delegated backend/explanation work and a read-only frontend review; the parent integrated and verified the result. **This is not a Phase 04 completion claim.**

## Delivered

- [Deterministic planner](../apps/api/src/folkverse/journey_planner.py): actual published exhibit IDs, exact stored estimates, time/locale/region/theme constraints, explicit novelty, stable tie-breaks, starting-stop validation, no duplicates and at most 24 stops.
- [Owned API](../apps/api/src/folkverse/journey_api.py), [models](../apps/api/src/folkverse/journey_models.py) and [migration](../apps/api/migrations/versions/0004_journeys.py): create, latest-owned list, reload, row-locked reorder/remove, empty saved route, version conflicts, signed ownership and session-deletion cascades. Current publication/source/language/duration checks apply on every read and after generation.
- [Explanation boundary](../apps/api/src/folkverse/journey_explanations.py): the model picks only server-verified reason codes for the supplied stops; server-rendered bilingual text rejects invented facts, prose, IDs, URLs, durations and physical directions. Bounded TTL/LRU cache and same-loop singleflight preserve unchanged-generation efficiency. Optional provider outages leave a useful deterministic saved route.
- [Bilingual saved-journey panel](../apps/web/src/components/saved-journey.tsx) and [owned BFF](../apps/web/src/lib/journey-proxy.ts): connected interest/time/region/novelty controls, optimistic recalculation with honest save/error states, real source/exhibit/guide links and latest-route reload. Original gold/navy wide route treatment is retained in CSS. Existing multi-province examples remain explicitly separate and optional in demo mode; live does not display them.
- [Generated API contract](../packages/contracts/openapi.json) and [TypeScript types](../packages/contracts/src/schema.d.ts) were regenerated from finalized backend schemas, not hand-maintained competing definitions.

## Acceptance matrix

| Gate | Current evidence | Status |
| --- | --- | --- |
| Every stop published, totals within requested time | Planner/API tests; real reviewed snapshot; 27 production HTTP checks | Pass, non-browser |
| Empty/small corpus, duplicates, withdrawal/deletion handled | Synthetic isolated tests and real one-exhibit smoke; current read-time pruning/notice | Pass, non-browser |
| Reorder/remove persists, no cross-session edits | SQLite owned API suite, real two-client BFF checks, simultaneous PostgreSQL PATCH (one 200/one 409), cascade deletion | Pass |
| Desktop/mobile fidelity and working keyboard controls | Actual EN/中文 phone menu, creation/removal, focus continuation and screenshot capture; viewport discrepancy, two-stop reorder and perceptual comparison unresolved | **Partially verified; still pending** |
| Complete map → journey → guide demonstration | Actual Dalian selection → published source drawer → 3 / 5-minute saved route → same Jinyao exhibit context, followed by reload | Pass, injected-browser observed |

## Verified results

- `pytest apps/api/tests -q` under an independently owned disposable PostgreSQL/pgvector database: **550 passed** after integrating upstream `07296c7` (working tree preserved by a temporary stash and restored; contracts regenerated deterministically on top of the merged code), one existing Starlette/httpx deprecation warning. Includes 29 journey tests, 44 explanation tests, the new real PostgreSQL concurrency/cascade test and the freshly pulled guide-lookup/personality/gateway suites, plus baseline regressions.
- Web `lint`, `typecheck`, production `build`: pass using **Node 22.20.0**. Host default Node 26 is outside the repository engine range and was not used for final web checks.
- Backend `ruff check apps/api scripts/export-openapi.py` and `mypy --config-file apps/api/pyproject.toml apps/api/src`: pass; 42 source files type-check. New standalone verification script and PostgreSQL test lint separately pass.
- Final `pnpm check:foundation`: finalized OpenAPI/TypeScript regenerated identically, nine original PNG assets and reference copies verified, **1,490 Git-candidate/browser-output files** checked against configured secrets. No credentials were committed or printed. Final whitespace check passes.
- [Production HTTP/BFF/API/database smoke](evidence/phase04/http-smoke.json): **27 checks pass**, including session forwarding, no-store, bounded request size, missing/foreign origin denial, database reload, bilingual rendering, explicit small-corpus notice, deterministic regeneration, source resolution, cross-owner denial, last-stop removal and stale edit rejection. The suite was rerun against the final rebuilt preview on port 3000 after the upstream integration and passed unchanged. [Reusable verifier](../scripts/verify-journeys-http.py).
- The existing review snapshot yields **one 3-minute eligible published exhibit**, with a real HTTPS source. The 42 source-assessed guide profiles are not silently promoted to journey exhibits. No new content review approval was created.

Early verification failures are not concealed: initial root `.env` had blank database/session configuration; a serving-container recreation removed the first test database; an early regression run was contaminated by a forced Ollama provider environment; a later fail-fast run found an empty-string key in that test environment. These were isolated setup problems, resolved in the private verification runner without changing the user's `.env`, provider quota, serving database or tests' expectations. Final complete suite passes. Early contract determinism failed because types were generated before the child's final schema edits; after regenerating the finalized schema, repeat generation is identical. Two intermediate frontend type errors (unreachable legacy journey branch and DOM LockManager promise typing) were fixed; final lint/types/build pass.

## Review fixes integrated

Async explanations no longer create a new event loop per request; generation runs outside DB transactions. Completion rechecks session and current corpus in a fresh transaction, preserves concurrent edits and never returns stale withdrawal data. PostgreSQL row locking is exercised by simultaneous real requests. Missing PATCH IDs do not silently clear a route. Explicit starting context does not override interests. Last-stop removal is supported. Source-less/non-positive-duration/duplicate stops are excluded.

Frontend review led to serialized idempotent session bootstrap (including Web Locks where available), graceful session/route loss, old-locale result suppression, adjacent-stop focus restoration, error recovery focus, neutral deliberate-empty copy and clear newest-route/session-lifetime disclosure. These implementation changes are static/non-browser verified; their actual keyboard behavior is not represented as tested.

## Round 4 audit fixes and test handoff

A fresh bounded read-only Flash audit found four concrete backend gaps. The declared-start notice is now re-derived from current eligible content (no invented 0-minute/now-fitting “too long” notice). PATCH checks both stored/display language and the original normalized region/interests. Composition changes re-derive all deterministic reason codes instead of retaining model choices under a deterministic label. Actual-first starting labels are position-aware and can return on a pure reorder. Eight new API tests cover these cases, explicit starting-entry HTTP requests, concurrent PATCH during the explanation await, list locale/order/bounds and PATCH 413; the entire PostgreSQL suite now passes **526** tests.

The expanded production HTTP smoke then exposed a BFF omission: `limit` was not forwarded on owned-list reads. The narrow query whitelist now forwards it, including invalid bounds for authoritative 422 validation, and all **27 HTTP checks pass**. Browser source inspection also found stale EN/中文 drawer wording denying the now-connected saved route/guide; both were corrected and the production build rechecked. Post-edit focus restoration now uses the committed saved DOM/enabled controls rather than a racy animation-frame callback. [Five focused browser tests](../tests/e2e/journeys.spec.ts) are authored and TypeScript-checked, with two-stop synthetic fixture coverage clearly separated from the real one-exhibit collection; **the Playwright browser runner was not executed as an alternate control backend**. The legacy preview assertion is scoped to its own panel to avoid a new multi-panel locator ambiguity.

## Limits and next action

The Browser Skill tool initially reported **no browser connected** and the owner chose non-browser continuation. The owner subsequently authorized browser verification and started dedicated headless Chromium 153 with the installed extension. The connected instance was verified and explicitly bound; all interactions used injected Browser Skill tools, with no alternate control backend. Actual Dalian map → reviewed source drawer → 5-minute saved journey → Jinyao exhibit context, reload persistence, phone navigation, EN/中文 rendering, keyboard last-stop removal/focus continuation, missing-Music empty result and regeneration recovery now have [recorded browser observations](evidence/phase04/browser-observations.json). The owned Agent Window was stopped successfully. No question or provider generation was submitted.

Actual [desktop](evidence/phase04/desktop-en.png), [phone EN](evidence/phase04/mobile-en.png) and [phone 中文](evidence/phase04/mobile-zh.png) screenshots were captured. This model cannot visually inspect raster inputs, so **perceptual comparison remains pending**. Phone screenshot dimensions are 390 × 844 and measured app boxes fit 390 (hero) / 354 (controls, saved panel, footer), but the tool reports a 738 × 1598 view outside modals and 390 × 844 in modals. A read-only source/bundle audit excluded the app's own CSS, closed dropdown portals and grid sizing as causes, and a clearly labelled synthetic standalone control page served through a one-shot debug rule reported 390 × 844 under identical mobile emulation with the extension overlay still present ([exported record](evidence/phase04/viewport-control.json)); the shared ~1.89 scale factor on both axes suggests a tool/viewport-scale artifact, but final attribution is unproven, so no full-document no-overflow claim is made. One minor mobile cascade defect (`align-items` media ordering) was fixed. Controlled two-stop UI reorder/adjacent focus, error recovery, tablet/zoom and the existing full browser regression remain unexecuted. No physical-device or screen-reader certification is claimed.

Current `.env` account request/budget caps are zero. Provider explanations were verified with controlled fake gateways only. Existing settings already route the official OpenAI-compatible Ollama endpoint through server-side `OLLAMA_API_KEY` when `GUIDE_PROVIDER=ollama` is configured; this work did not change issuer, expose keys or increase quota. No real model generation, expenditure, public deployment or hosted acceptance is claimed.

Read-time pruning does not rewrite stored stops: re-publication can make a stop reappear. Regeneration creates a new route; the UI restores the latest route and has no multi-route history/deletion UI. Explicit session deletion removes all owned routes; expired rows are access-denied but no new automatic expiry-purge scheduler was implemented. These scope choices are documented in [the journey contract](../docs/personal-journeys.md).

At the owner's request the upstream branch was pulled mid-task (`git stash push --include-untracked`, `git pull --ff-only` to `07296c7`, `git stash apply`, then deterministic contract regeneration); the restored work then passed 550 API tests, lint/types/build, Ruff/mypy, the foundation secret/contract/assets scan (1,490 files) and the 27-check HTTP smoke rerun on port 3000. Earlier verification used isolated web/API ports 3014/8014 and an independently owned PostgreSQL instance on 5444, not the serving database. The previously separate image-based port-3000 app was replaced by this requested rebuilt preview (web 3000, API 8000) for the owner to view; the disposable database stays isolated and the preview/API jobs are intentionally left running for inspection unless the owner asks otherwise. No physical-device or screen-reader certification is claimed. **Phase 04 stays open until browser gates have evidence; Phase 05 is next only after acceptance.** The finalized state was committed and pushed to GitHub.

## Reproduction

With valid local PostgreSQL settings and the existing reviewed snapshot restored, run migrations to `0004_journeys`, regenerate contracts, run API tests, lint/types/build and `pnpm check:foundation`. Run the HTTP verifier against a disposable local production web/BFF/API instance with generation quota disabled:

```sh
uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head
pnpm contracts
pnpm test:api
pnpm lint
pnpm typecheck
pnpm build
pnpm check:foundation
uv run --project apps/api python scripts/verify-journeys-http.py \
  --base-url http://127.0.0.1:3014 \
  --output report/evidence/phase04/http-smoke.json
```

The HTTP verifier creates and deletes only its fresh signed sessions. It is not a browser test. The current session's private disposable-database runner lives under ignored local state and does not contain committed credentials. Browser execution remains the next acceptance step.
