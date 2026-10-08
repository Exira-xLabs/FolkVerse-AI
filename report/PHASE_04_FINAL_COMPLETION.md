# Phase 04 — final completion, 8 October 2026

**Status: COMPLETE within the approved personal-journeys scope.** All four gates in [Phase 04](../phases/04_PERSONAL_JOURNEYS.md) are met. This report supersedes the historical [implementation review](PHASE_04_IMPLEMENTATION_REVIEW.md). Phase 05 camera scan and artifact retrieval is next; it is not started or accepted by this report.

Saved learning journeys use real published exhibit IDs, stored learning estimates and explicit visitor preferences. Visitors can choose interests, time and city, save, reorder, remove, regenerate, reload, inspect sources and carry the same exhibit into Jinyao. The server owns selection, duration, eligibility and session authorization. Model explanation cannot invent a stop, route, duration or factual reason.

## Acceptance evidence

| Required gate | Actual evidence | Result |
| --- | --- | --- |
| Every stop published; totals within requested time | Full API suite exercises publication dependencies, locale, sources, time boundaries and selection; actual restored snapshot and production HTTP/browser creation use stored estimates | PASS |
| Empty/small corpus, duplicate and removed/unpublished exhibits | API cases cover empty/insufficient corpus, invalid/duplicate edits, withdrawal, deletion, locale and source eligibility; real browser covers honest empty Music and one-stop notices | PASS |
| Reorder/remove persists without cross-session edits | API ownership/expiry/delete checks, actual PostgreSQL concurrent PATCH/version serialization and cascade deletion, 27 BFF/HTTP checks, real-browser single-stop removal/reload and controlled two-stop reorder UI | PASS |
| Faithful desktop/mobile visuals and working controls | Original museum/gold/navy artwork preserved; EN/ZH at 1600×900, 390×844 and 768×1024; document width equals viewport at all six points; touch, keyboard, adjacent focus, save-error recovery, CSS 200% zoom and reduced motion pass; six scoped axe audits have zero violations | PASS |

Handoff demonstration is browser-executed: **Dalian map → real Fuzhou shadow puppetry exhibit → 3 / 5-minute saved journey → source drawer → Jinyao with that exhibit context → saved reload**. The eight journey cases include actual English/Chinese touch creation, city/time/theme selection, opt-in novelty, regeneration, last-stop removal and persistence through PostgreSQL.

## Corrections made during closure

1. The reported 738-pixel document on a 390-pixel phone was a real CSS defect. Column flex wrapping and the interests group's inherited flex basis displaced time/region controls into a second column. The mobile saved-controls container now disables wrapping and gives its interests group a content-sized basis. This fixes layout rather than hiding overflow, while preserving artwork and desktop layout.
2. The journey explanation factory ignored the guide's explicit unlimited-budget setting when the monetary cap was zero. It now follows the same admission rule, still requiring the selected provider's credentials and any applicable request quota. Existing factory tests cover unlimited success, bounded rejection and missing credentials. The owner's private unlimited DeepSeek setting was preserved; shared fail-closed defaults remain unchanged.
3. An old regression selector matched both the new real saved controls and optional demo controls. The test now explicitly checks the labelled optional preview and separately requires the working real controls. The first failed run remains in evidence.
4. Reproducible browser acceptance now owns a fresh migrated PostgreSQL database, restores the real reviewed snapshot, disables provider calls and cleans up on graceful shutdown. Uvicorn signal handling and Playwright's explicit SIGTERM timeout allow the database cleanup finally block to run. Early runner-owned leftovers were removed; the corrected clean run verifies zero remaining owned test databases.

## Measured verification

- **550 API tests pass**, including ownership, publication constraints, model reason validation and real PostgreSQL concurrent editing/cascade checks. One existing Starlette/httpx deprecation warning is recorded.
- **76 production Chromium foundation/browser tests pass in the clean checkout**, including eight Phase 04 journey cases, map/gallery/source behavior and existing museum regressions. The previous clean run of 75 also passed; the additional phone-touch case was then added and verified.
- **61 isolated guide browser tests pass**: guide regressions remain intact. Injected provider/failure fixtures are controlled tests, not real-model evidence.
- **27 real web/BFF/API/PostgreSQL HTTP checks pass**: no-store, source IDs, time, reload, origin/body limits, cross-owner denial, stale edits and empty saved routes.
- **Six scoped EN/ZH saved-panel axe audits: zero violations**; no horizontal document overflow at the tested desktop/phone/tablet widths. Keyboard movement/removal/recovery and CSS 200% enlargement/reduced motion pass.
- **Two actual DeepSeek explanation calls**, one per locale, return `generated`. Unchanged regeneration adds **zero provider attempts in each locale**, measured against the actual usage ledger. No response interception or fake gateway was used for these calls. The configured model identifier is `deepseek-flash`.
- Lint, TypeScript, backend mypy, production build, deterministic contracts, nine original artwork files, configured-secret scans and whitespace checks pass. The new runner passes Ruff. Commits pass the staged gitleaks gate.
- Clean reproduction independently installs frozen pnpm dependencies from cache and a fresh Python virtual environment, supplies provider-free private configuration, creates/migrates/restores test data, builds production Next, runs the full API/browser checks and removes its owned acceptance database. Node 22.22.3, pnpm 11.10.0 and Python 3.12.13 were exercised.

See [verification manifest](evidence/phase04-final/verification.json), [clean browser result](evidence/phase04-final/reproduction/browser-results.json), [HTTP checks](evidence/phase04-final/http-smoke.json), [actual provider/cache checks](evidence/phase04-final/real-model.json) and [guide regression results](evidence/phase04-final/guide/browser-results.json). The manifest binds evidence to tested source commits and records reproduction commands. Six axe files accompany the clean browser result. Screenshots were captured and a desktop/phone/reference comparison inspected; they remain local under the screenshot-ignore policy. At the owner’s request, 52 historical evidence screenshots (58.36 MiB) were also removed from Git’s index and preserved locally; future clones use the [evidence policy](evidence/README.md) and browser reproduction commands instead of depending on those image links. Git history was not rewritten. This is preservation of the approved museum treatment, not an assertion of pixel-identical composition to every earlier reference.

## Corpus, fixtures and release boundaries

The restored published journey corpus contains **one eligible 3-minute exhibit**, Fuzhou shadow puppetry in Dalian, with the Liaoning Provincial Government source. No new review approval was created. The 42 machine-assessed guide profiles are a separate factual-explanation resource and are not silently promoted to published route stops. More approved exhibits will expand route variety; they are not needed to make the implemented empty/small-corpus behavior pass its explicitly defined gate.

The browser two-stop reorder and stale-save cases are explicitly labelled controlled response fixtures. Real order persistence and rejection of foreign-owner edits are independently covered through the real API/database/HTTP suites. Synthetic fixture content is never represented as the published collection, a live model answer or whole-province editorial coverage.

This closure records Codex assessment and automated evidence, not a human review, physical-device test, Safari certification, calibrated recommendation pilot or exhaustive Liaoning corpus. The explanation cache is process-local and bounded; restart or another worker can require a new call. Journeys are learning sequences, not physical travel itineraries. Permanent hosting and broader release/device/load testing remain Phase 08 work.

## Restored live preview

The temporary HTTPS preview was restored and checked through an actual Chromium browser with response interception disabled: creation returned HTTP 200 with `generated` explanations, the real single-stop route survived reload with the secure session cookie, source links resolved to HTTPS, and entering Jinyao preserved Fuzhou exhibit context. The test’s owned session was deleted afterward. See [public preview evidence](evidence/phase04-final/public-preview.json). This is a temporary tunnel, not a permanent hosted release. API health reports live mode, available PostgreSQL/pgvector and current migrations.

## Reproduce and proceed

Follow [setup](../docs/setup.md#phase-04-isolated-browser-acceptance--8-october-2026) and the [journey contract](../docs/personal-journeys.md). Keep provider credentials in the ignored local environment. Free ports 3000, 3002 and 8000 before browser acceptance; the dedicated PostgreSQL role must permit creating the runner's own temporary database. Do not run test cleanup against shared or production data. Provider-disabled acceptance does not consume model quota.

Proceed to [Phase 05 — camera scan and artifact retrieval](../phases/05_OBJECT_LENS.md): secure camera/upload, validated private media with expiry/deletion, rights-eligible artifact references, honest retrieval/unknown decisions, source links and ownership. Its reference catalog and calibration gates must be verified separately; a saved-journey pass does not establish object-recognition accuracy.
