# FolkVerse build status

**Updated:** 5 October 2026, Asia/Shanghai. **Phase 02: complete locally; all five acceptance gates pass.** Scope: the whole Liaoning province, as explicitly requested by the user. Phase 01 remains delivered at `be911c8e4c3d34fa1b6e6c1398d4dd1436ce3172`; Phase 02 and the UI refinement are included in the four-commit delivery on `main` requested on 5 October 2026. Consult Git history for delivery hashes. Next: [Phase 03 — grounded guide](../phases/03_GROUNDED_GUIDE.md).

## Part 4 delivery — 5 October 2026

Remaining-work pass: M09 grouping semantics are fixed and N01–N10 are implemented in the local UI/visit scope. M01–M15 are complete; M16 remains partial because the owner confirmed its physical-device/Safari/screen-reader environments are unavailable. [Remaining-work delivery](../report/UI_REMAINING_COMPLETION.md). All local M16 inventory/image-QA deliverables are complete. New shared navigation/filter recovery, separate exhibit reading/evidence, approved starting points, Guide state/Stop/Retry previews, Story modes/continuations, Lens unavailable capture/privacy design and friendly 404/audio loading are implemented. Full browser suite: **61 passed, 0 failed**; **15 final focused checks pass** after the last visual refinements. Final rendered review: 108 EN/ZH states with no detected axe violations, page errors, overflow or undersized standalone controls. [Completion report](../report/UI_PART_4_COMPLETION.md), [state inventory/image checklist](../report/UI_DESIGN_STATE_INVENTORY.md). **M16 remains partial:** real phone/software keyboard, Safari and screen-reader checks are unavailable here and must not be claimed passed. Screenshots remain local. Part C is pushed at `ef7a2b5`; Part 4 implementation, reports and non-image verification evidence are included in the subsequent delivery commit.

## Part C completion — 5 October 2026

C01–C12 are complete locally. Sources/live copy and province filters match their scope; atlas publication has explicit loading/error/ready states; Guide retains drafts/multiple scripted turns during navigation; Journey retains temporary plans and separates draft criteria from applied routes. Narration has an English/text-only choice and transcript, voice availability is visible, and approved exhibit links carry revalidated context into Guide/Journey/Story/interests. No later-phase AI APIs or durable persistence are claimed. Full browser suite: **46 passed, 0 failed**. [Completion report](../report/UI_PART_C_COMPLETION.md), [visit-state contract](visit-state-and-context.md). Screenshots remain local. Next: M16 external verification of the UI audit.

## Part B completion — 5 October 2026

B01–B12 are complete locally: drawer keyboard/backdrop/scroll behavior, unified city camera, persistent graphics preference, readable map labels and 44px controls, native modal atlas and localized page titles. Earlier artwork/navigation/chart fixes are reverified. Final browser suite: **40 passed, 0 failed**; automated accessibility scan: 24 EN/ZH states with no detected violations. [Completion report and evidence](../report/UI_PART_B_COMPLETION.md). Screenshots remain local. Next: M16 external verification of the UI audit. Part B is pushed at `faed2c5`.

## Part A completion — 5 October 2026

All nine Part 1 design corrections are complete locally. The remaining A01/A08/A09 work adds a real API-backed featured exhibit on Home with exact exhibit/source navigation; distinct collection/Story covers and documented hero/card/thumbnail/detail compositions; visitor-first EN/ZH status, retry, last-check feedback and expandable diagnostics. The optional anonymous visit is explained without implying tracking or saved interests.

Full browser regression: **35 passed**. Fresh lint, typecheck, production build and original-art/content/geography preservation checks pass; final focused checks and evidence are recorded in [Part A completion](../report/UI_PART_A_COMPLETION.md). New screenshots remain local and ignored. This pass is included in the owner-requested Part A delivery commit on `main`; consult Git history for the delivery hash. The wider audit remains open; next is **M16 external device/Safari/screen-reader verification**. Later live AI integrations remain assigned phase work.

## UI refinement — 5 October 2026

The owner-selected seven changes and image-delivery pass are complete locally. Home leads to Liaoning; Explore defaults to the collection with an optional atlas; Journey/Lens/Guide previews are collapsed; Guide uses a 72px identity badge; cultural interests begin empty with a labelled example; bounded artwork and calmer task panels replace full-page scenery. Narrow navigation reveals the current tab.

Fresh lint, typecheck, production build and original-art/content/geography preservation checks pass. Final browser run: **31 passed, 0 failed, 0 skipped**, including 54 EN/ZH layout states, keyboard/touch interactions, map regressions and DPR-2 images. The healthy local production preview is restored at <http://localhost:3000>. [Results and evidence](../report/UI_REFINEMENT_RESULTS.md), [completed checklist](../report/UI_REFINEMENT_CHECKLIST.md).

New screenshots remain local per the owner's delivery instruction; text logs and structured evidence are committed. Screenshot links refer to local files.

This closes the selected refinement scope, not the entire earlier UI audit. Remaining shared UI defects and accessibility checks are listed in the results report. Live AI capabilities remain separate phase work; the implementation and evidence are included in the four-commit delivery on `main`.

## Phase 02 — reviewed content and regional discovery

The supplied artwork and earlier evidence are preserved. Shaanxi records are withdrawn after the user corrected the scope. Liaoning has **14 initial candidate exhibits, one per city: 1 approved/published and 13 drafts**. The project owner explicitly approved Fuzhou shadow puppetry, its exact EN/ZH summaries, attribution/rights and Liaoning/Dalian labels. Its **2 passages** are approved for later grounded retrieval. This is editorial review, not an external specialist endorsement.

**Met catalog:** 37 draft records, 32 locally downloaded/hash-verified CC0 image candidates, **0 published artifacts**, and no invented Liaoning exhibit links. Ten reviewed exhibits and thirty approved eligible artifacts remain targets. [Exact counts and integrity](../report/evidence/phase02/corpus-integrity.json), [review packet](content-review.md), [rights report](data-rights.md).

### Implemented and verified

- Migration `0002_content`: reviewed regions, sources, passages, claims, exhibits, artifacts, media and append-only operator review history, with evidence/geography associations. Practice/declaring region and museum repository are separate.
- Bounded, cached Met CLI using the officially documented paginated `/v1.1/search`; actual samples 50824/449479/460669 re-fetched. Per-image rights, original response/hash/date, JPEG bytes/hash and denial/error outcomes are retained. All 37 records re-imported without duplicates or changed hashes/reviews.
- Human review/publish/unpublish CLI, content/relationship fingerprints and current dependency eligibility. Imported/generated candidates stay draft. Withdrawn/uncleared/changed records disappear from published APIs immediately; sources clear dependent embedding markers.
- Database-backed `/regions`, `/exhibits`, `/exhibits/{id}`, `/sources`, `/sources/{id}` and `/artifacts`, generated OpenAPI types and an allowlisted same-origin web proxy. Filters, cursor paging, localized list/detail/source flow, empty/error/retry states and modal focus are verified.
- Explore/Sources show the real collection in demo and live modes. Explore now includes a game-style atlas of Liaoning's sourced provincial outline with all 14 cities, geographic positioning, pan/zoom, pinch, minimap and expanded view. City selection filters the actual published collection; draft cultural records stay hidden. Phase 01 examples require an explicit fixture toggle in demo mode. Later live AI experiences remain unavailable. [Atlas sources and controls](liaoning-map.md).
- Versioned corpus/ledger snapshot, empty-database restore preserving original editorial reviews, refusal to overwrite existing work and a successful fresh-migration/restore check in a disposable database. Images remain local and missing bytes stay ineligible.

### Phase 02 acceptance gates

| Gate as written in `phases/02_CONTENT_MAP.md` | Result | Evidence |
|---|---|---|
| Re-import causes no duplicate objects or media; source payload/hash retained. | PASS | All 37 real Met objects re-imported: unchanged counts/source hashes/review ledger; all 41 payload hashes and 32 image hashes verified. [Integrity](../report/evidence/phase02/corpus-integrity.json), [import](../report/evidence/phase02/met-full-reimport.json). |
| Draft/withdrawn/unlicensed entries are absent from published search. | PASS | Actual draft Liaoning and withdrawn Shaanxi IDs return 404; artifact API returns zero. Dependency/hash/rights tests against PostgreSQL. [API tests](../report/evidence/phase02/api-tests.txt), [browser tests](../report/evidence/phase02/browser-tests.txt). |
| One real approved exhibit traverses map/list → detail → source. | PASS | User-approved Fuzhou shadow puppetry: Liaoning list filter → bilingual exhibit → official first-list source, reviewer/date/hash. [Approval](../report/evidence/phase02/liaoning-editorial-approval.json), [drawer](../report/evidence/phase02/liaoning-source-drawer.png), [browser results](../report/evidence/phase02/browser-results.json). |
| Source withdrawal removes affected search content and caches. | PASS | Transaction-isolated real DB withdrawal removes list/detail/source on the next request and clears embedding markers. No published-content cache; all reads no-store. Browser intercepted 404 verifies drawer clearing/recovery on revalidation. Browser tabs poll every 15 seconds/focus; no instant push is claimed. [Tests](../apps/api/tests/test_content.py), [browser evidence](../report/evidence/phase02/browser-tests.txt). |
| Report exact approved/draft counts; target 10/30 is never manufactured. | PASS | [Corpus](../data/manifests/corpus.json), [ledger](../data/manifests/review-ledger.json), [rights](data-rights.md), [counts](../report/evidence/phase02/corpus-integrity.json). Active/archived records and downloaded/approved images are separated. |

### Verification

**Dropdown UI refinement, 5 October 2026:** Region, Theme, Interests, Time and the Lens demo scenario now share styled museum menus with gold selection checkmarks, consistent option spacing and viewport-aware positioning. Keyboard arrows, Home/End, typeahead, Enter, Escape, Tab and outside dismissal are covered; phone tests use actual touch input in Chinese and English. **27/27 browser tests passed**, along with lint, TypeScript/strict mypy, browser-test types, production build and original-asset verification. [Commands, limits and screenshots](../report/evidence/dropdown-ui/README.md). The production preview was restarted with the updated UI.

**Interrupted-session completion, 5 October 2026:** rechecked the finished atlas against the existing production build (built after the final map/CSS edits). The full browser regression suite passed again: **25/25**, without retries. Lint, TypeScript/strict mypy, geography/hash verification, foundation contracts/assets/secret checks and whitespace checks passed. The running Explore preview, web-proxied API/database health and served boundary/terrain hashes were checked successfully. [Recovery commands and evidence](../report/evidence/phase02-map/atlas-v2/recovery-completion.md). The preview remains available at <http://localhost:3000/explore>; the changes were local and uncommitted at that verification; the later four-commit delivery includes them.

**Current atlas v2:** all fourteen city territories now use valid OpenStreetMap prefecture-level MultiPolygons, with every sourced marker inside its own city. Clicking a city/territory highlights its border and fits its land extent. House icons were replaced by modern glass locator discs. Realistic terrain v2 was generated using a numerical Mapzen elevation reference over the same geographic extent; fine surface details remain approximate. Province geometry, original artwork, cultural approvals/counts and earlier evidence are preserved. [Sources and design](liaoning-map.md), [boundary verification](../report/evidence/phase02-map/atlas-v2/city-boundary-verification.json), [terrain prompt/reference](../report/evidence/phase02-map/atlas-v2/terrain-generation.json).

The final v2 browser suite passed **25 tests**, including six map tests and all content/foundation/museum regressions. All eight routes were checked at desktop, phone and tablet sizes in both languages. Build, lint, browser TypeScript, data-script lint, geographic/hash checks and foundation contracts/assets/secret checks passed. [Browser results](../report/evidence/phase02-map/atlas-v2/browser-results.json), [browser log](../report/evidence/phase02-map/atlas-v2/browser-tests.txt), [build](../report/evidence/phase02-map/atlas-v2/build.txt), [lint](../report/evidence/phase02-map/atlas-v2/lint.txt), [browser types](../report/evidence/phase02-map/atlas-v2/browser-typecheck.txt), [geography](../report/evidence/phase02-map/atlas-v2/geography-check.txt), [foundation](../report/evidence/phase02-map/atlas-v2/foundation-check.txt). Current visuals: [province](../report/evidence/phase02-map/atlas-v2/liaoning-atlas-desktop.png), [Shenyang selected](../report/evidence/phase02-map/atlas-v2/selected-shenyang-desktop.png), [Dalian selected](../report/evidence/phase02-map/atlas-v2/selected-dalian-desktop.png), [Dalian phone](../report/evidence/phase02-map/atlas-v2/selected-dalian-phone.png). The restarted preview and local-asset hashes were checked: [service evidence](../report/evidence/phase02-map/atlas-v2/live-service-check.json). Earlier verification snapshots follow.

The Liaoning atlas extension passed **23 browser tests**, covering the existing collection/foundation/museum regressions and four new map tests. All 14 official city names match the seed and every sourced city point lies inside the sourced `CN-LN` MultiPolygon. The province shape is data-derived; generated terrain is decorative. Cultural corpus counts and review hashes are unchanged. [Browser log](../report/evidence/phase02-map/browser-tests.txt), [results](../report/evidence/phase02-map/browser-results.json), [geography check](../report/evidence/phase02-map/geography-check.txt), [source/hash evidence](../report/evidence/phase02-map/geography-verification.json).

Lint, TypeScript/strict mypy, production build, browser/config TypeScript and foundation asset/contracts/secret checks passed for the map extension. [Lint](../report/evidence/phase02-map/lint.txt), [types](../report/evidence/phase02-map/typecheck.txt), [build](../report/evidence/phase02-map/build.txt), [browser types](../report/evidence/phase02-map/browser-typecheck.txt), [foundation](../report/evidence/phase02-map/foundation-check.txt). Desktop and Chinese phone atlas captures were visually inspected: [desktop](../report/evidence/phase02-map/liaoning-atlas-desktop.png), [phone](../report/evidence/phase02-map/liaoning-atlas-phone-zh.png). Earlier Phase 02 evidence below is preserved as the content foundation snapshot.

The restarted production preview returns HTTP 200 for Explore with fourteen city markers, sourced geometry and generated terrain matching their checked hashes, and healthy API/PostgreSQL/pgvector/current schema. Actual collection reads return one Liaoning exhibit and zero Shenyang drafts. [Live preview evidence](../report/evidence/phase02-map/live-service-check.json). The focused four-map-test rerun also passed after adding explicit pinch/no-page-scroll and screenshot-loading checks: [log](../report/evidence/phase02-map/map-tests.txt).

Follow-up circle fix: removed the selected-city ring's viewport-centered orbit after reproducing a 787-pixel drift. The highlight now stays stationary at its geographic anchor. **Five focused map tests passed**, including a new normal-motion regression checking all fourteen cities through animation time and zoom. Production build, lint and browser-test typechecking passed. [Cause and evidence](liaoning-map.md#selected-city-circle-correction), [test results](../report/evidence/phase02-map/circle-fix/browser-results.json).

| Check | Final result |
|---|---|
| `pnpm lint` | PASS — [log](../report/evidence/phase02/lint.txt) |
| `pnpm typecheck` | PASS — TypeScript + strict mypy; [log](../report/evidence/phase02/typecheck.txt) |
| `pnpm build` | PASS, inherited TLS override unset; [log](../report/evidence/phase02/build.txt) |
| `pnpm test:api` | **26 passed**, test approvals roll back; existing Starlette/httpx deprecation warning remains. [Log](../report/evidence/phase02/api-tests.txt) |
| `pnpm test:e2e` | **19 passed**: real collection/source flow, simulated upstream failure and drawer revalidation, six foundation regressions, museum/mode/accessibility regressions. [Log](../report/evidence/phase02/browser-tests.txt), [JSON](../report/evidence/phase02/browser-results.json) |
| `alembic check` | PASS: schema and models agree; [log](../report/evidence/phase02/migration-check.txt) |
| `python scripts/verify-content-snapshot.py` via project uv | PASS: fresh migrations/restore, original review hashes, exact counts, overwrite refusal; [log](../report/evidence/phase02/fresh-restore.txt) |
| Browser/config TypeScript | PASS — [log](../report/evidence/phase02/browser-typecheck.txt) |
| `pnpm check:foundation` | PASS: deterministic contracts, original artwork/reference hashes, ignored secrets and configured-secret scan. [Log](../report/evidence/phase02/foundation-check.txt) |

All eight routes were checked at 1600×900, 390×844 and 768×1024 in EN/ZH, with reduced motion, keyboard navigation and enlarged CSS layout. Collection captures wait for loaded artwork and API results. Desktop Explore, phone Explore and the real source drawer were visually inspected. [Desktop](../report/evidence/phase02/02-explore-1600.png), [phone](../report/evidence/phase02/02-explore-390.png), [source drawer](../report/evidence/phase02/liaoning-source-drawer.png). Native toolbar zoom, Safari, physical devices and a full screen-reader/contrast audit remain untested.

The first browser attempts exposed a refresh/focus issue and stale prototype heading assertions; both were fixed. Screenshot readiness was tightened to wait for real collection data. Final tests pass without retries.

Freshly restarted preview checks: HTTP 200 for web, API/PostgreSQL/pgvector, reviewed region list, Liaoning exhibit/detail/source and the correctly empty artifact publication list. [Live service check](../report/evidence/phase02/live-service-check.json).

### Handoff / next phase

[Content operations](curation.md) documents snapshot restoration, seeding, import, actual review, withdrawal and verification. [Review packet](content-review.md) identifies the remaining 13 candidates and 26 passages; [rights report](data-rights.md) records the pending artifact reviews. No paid providers, recognition or embeddings were introduced. Phase 03 can begin with the two approved Fuzhou passages, then implement a server-side provider gateway, evidence retrieval, citation/claim validation and actual vector/cache invalidation. Two passages support only a narrow guide; further content approvals are still needed to broaden coverage.

Local preview: <http://localhost:3000/explore>; source index: <http://localhost:3000/sources>; foundation health: <http://localhost:3000/status>. The later sections below preserve historical Phase 01/00 snapshots and are superseded by the current Phase 02 capability/counts above.


## Phase 01 — interactive museum

Phase 00 is committed/pushed at `8ca822c`. Phase 01 builds on it and is delivered on `main`; consult current Git HEAD and remote state for the delivery commit. The user requested an imaginative product using the presentation as inspiration, superseding literal screenshot reconstruction. The museum identity, original scenes and guide remain intact; no claim of exact 8px reference fidelity is made.

### Implemented

- Eight responsive screens, EN/ZH text, active navigation, logo/home links and an explicit interactive-demo footer.
- Reusable `MuseumScene`, `GlassPanel`, `GlassTabs`, `GoldButton`, `ThemeChip`, `SourceDrawer`, `ExhibitCard`, `GuidePortrait`, `AudioControls` and `InterestChart` components.
- Explore search/theme filters, illustrative exhibit list, empty results and inspectable fixture notes. Generated map borders are never functional geography.
- Editable deterministic journey stops: move up/down, remove, total minutes, duration/theme regeneration and insufficient-content feedback. This is a digital learning route.
- Original fictional lantern story with two endings, restart, EN/ZH captions and an actual local synthetic English audio recording. Play/pause/seek and time reflect the real audio. No autoplay or live TTS.
- Lens scenario controls exercise related-class, unknown, poor-image, permission-denied, unavailable and loading states. They disclose simulation; no camera, uploads, catalog identification or percentage confidence is implied.
- Bounded 2,000-character guide composer, scripted loading/response, source notes and explicit unavailable voice input. No provider calls or invented citations.
- Editable cultural-interest chart with SVG/text equivalent, immediate redraw, reset, strongest-interest suggestion and page-local opt-in preview. No behavioral collection, saved profile or ancestry claim.
- Inspectable evidence-chain stages and a native modal drawer with explicit keyboard wrap, Escape dismissal and focus restoration.
- Reduced motion, control/page transitions and a reduced-graphics switch that removes blur, shadows and animation.
- Server-only application-mode lookup; missing/unknown mode fails closed. Live-mode feature routes never return fixture success.

### Verification

| Check | Result and evidence |
|---|---|
| `pnpm lint` | PASS — [log](../report/evidence/phase01/lint.txt). |
| `pnpm typecheck` | PASS — [log](../report/evidence/phase01/typecheck.txt). |
| `pnpm build` | PASS, with insecure inherited TLS override unset — [log](../report/evidence/phase01/build.txt). |
| `pnpm check:foundation` | PASS: original assets/reference hashes and PNG modes preserved, deterministic contracts, ignored local secrets and configured-secret scan — [log](../report/evidence/phase01/foundation-check.txt). |
| `pnpm test:e2e` | **15 passed** — [log](../report/evidence/phase01/browser-tests.txt), [JSON](../report/evidence/phase01/browser-results.json). Six foundation regressions and nine new UI tests. |
| Eight routes × 1600×900 / 390×844 / 768×1024 × EN/ZH | PASS: loaded artwork, headings, no document overflow and no page errors. English captures at all sizes and eight Chinese desktop captures saved. |
| Keyboard, focus, enlarged layout | PASS: skip/navigation regression, source-modal forward/backward wrap, Escape and opener focus restoration. 200% CSS zoom with a narrowed viewport reflows without overflow; native toolbar zoom is not claimed. |
| Story audio / mode separation | PASS: actual play and advancing time, branching removes audio; separate web server with `APP_MODE=live` blocks every feature fixture. |
| Preview health after tests | HTTP 200: web → API → PostgreSQL/pgvector, schema current — [check](../report/evidence/phase01/live-service-check.json). |

The first UI test pass found missing modal keyboard wrap and journey labels/enlarged-layout overflow. These were fixed before the final 15-test passing run. Phase 00 evidence was preserved; regression captures now go under Phase 01.

### Visual evidence

All eight desktop frames and all eight phone frames were inspected as contact sheets; artwork, portrait, real text, controls, composition and readable panel density were checked. Full tablet and Chinese desktop captures are also saved. Reference-inspired differences and remaining limitations are in [design differences](design-differences.md).

- Desktop: [home](../report/evidence/phase01/01-home-1600.png), [explore](../report/evidence/phase01/02-explore-1600.png), [journey](../report/evidence/phase01/03-journey-1600.png), [story](../report/evidence/phase01/04-stories-1600.png), [lens](../report/evidence/phase01/05-lens-1600.png), [guide](../report/evidence/phase01/06-guide-1600.png), [DNA](../report/evidence/phase01/07-dna-1600.png), [sources](../report/evidence/phase01/08-sources-1600.png).
- Mobile filenames use the same prefix with `-390.png`; tablet uses `-768.png`. Chinese desktop files are `zh-1-1600.png` through `zh-8-1600.png`.
- Additional captures: [source drawer](../report/evidence/phase01/source-drawer-1600.png), [edited constellation](../report/evidence/phase01/dna-edited-1600.png), [reduced graphics](../report/evidence/phase01/guide-reduced-graphics-1600.png), [enlarged journey](../report/evidence/phase01/journey-zoom-200.png).

### Capability limits and next step

Museum UI and controls are implemented. Exhibit content, journey eligibility, guide responses, lens decisions and interests are **labelled fixtures**. Real source corpus, rights review, approved geometry, retrieval and credentialed AI integrations remain unavailable. The story is original fiction, not reviewed cultural history. English synthetic recording is available; Chinese audio and live voice are unavailable. No new AI raster imagery was needed; original artwork remains byte-identical.

Available checks use Linux and Chromium. Physical devices, Safari, Windows, full contrast/screen-reader audit and browser-toolbar zoom remain untested. No OpenDesign exports were available. There is no unresolved Phase 01 implementation blocker within the revised scope.

Preview: <http://localhost:3000>; health: <http://localhost:3000/status>. Web/API were restarted after tests. The dedicated database remains on loopback port 5440; the live-mode test server on 3002 was stopped by Playwright. Next work is Phase 02 ingestion/curation and content/map/list APIs with real source and rights gates.

## Phase 00 — preserved foundation handoff

### Interrupted-session recovery

Phase 00 was rechecked after the interrupted session. Database startup/migration, lint, typecheck, production build, deterministic contracts, asset verification and configured-secret checks passed again. API tests: **12 passed**. Browser tests: **6 passed**, including the screenshot helper that waits for every image to load and fonts to become ready. The eight screenshots were regenerated; the desktop home and phone guide were visually inspected again. The first browser startup attempt overlapped a rebuild and failed because its build output was being replaced; the subsequent run against the finished build passed. The final build and preview ran with `NODE_TLS_REJECT_UNAUTHORIZED` unset.

The web and API previews were restarted, and an actual web-proxied health request returned HTTP 200 with database/pgvector available and schema current. The home page returned HTTP 200. At this recovery snapshot, Phase 00 was delivered on `main` and Phase 01 had not started. Current Phase 01 status is above. Read current Git HEAD and remote state for the delivery commit.

Verification ran on the working tree based on `f95fa20` on `main`, before the Phase 00 delivery commit. Read actual Git status/HEAD and remote state when resuming. The supplied business-plan PDFs remain local and ignored, and the original build-kit instructions and artwork remain intact.

## Project understanding and scope

FolkVerse China / 华韵 AI is a bilingual cultural museum competition project. Its intended flow is Explore → reviewed exhibit → Journey → Guide/source → Story or Lens → save → interests/recommendation. Cultural passages and artifact catalogs are distinct corpora linked only by evidence. The initial one-region/ten-exhibit/thirty-artifact scope is a target. Source review, rights and uncertainty are required, rather than something to add after the demo.

The master brief, all three specifications, phases 00–08, OpenDesign handoff, QA plan and traceability register were read. The supplied business-plan and competition-deck PDFs and all eight actual reference frames were inspected. No application existed in this checkout, no applicable `AGENTS.md` was found, and no OpenDesign exports were present. The original kit remains canonical at the root; [the mapping](build-kit/README.md) resolves the prompts' `docs/build-kit/` paths.

## Implemented in Phase 00

- A pnpm workspace with one Next.js App Router/TypeScript/Tailwind/Motion application and a reproducibly locked Python 3.12 FastAPI/Pydantic/SQLAlchemy/Alembic service.
- Dedicated local PostgreSQL/pgvector Compose service, pinned image digest, loopback port 5440 and persistent project volume. The first migration installs the vector extension and anonymous-session table; a migration template supports subsequent revisions.
- Actual `/health` and `/api/v1/health` readiness checks: database connectivity, installed vector version and migration revision. Missing readiness returns HTTP 503 with degraded fields, without secrets.
- Shared sanitized API error envelope, request IDs, explicit CORS origins and Origin validation for state changes.
- POST/GET/DELETE `/api/v1/session`, signed HttpOnly/SameSite cookies, expiry, revocation and ownership helpers. Demo and live cookies have distinct signing namespaces; HTTPS Secure-cookie configuration is tested. No behavioral tracking is enabled.
- Same-origin web health/session proxies and `/status` with loading, healthy, degraded/unreachable, retry and anonymous-visit controls. The API's unavailable state is preserved; stopped upstreams produce a sanitized 503.
- An offline deterministic OpenAPI export, generated TypeScript definitions and typed frontend client.
- All eight museum route destinations, home discovery links, route-aware navigation, default English, Chinese translations and locale persistence. Later features show truthful unavailable states. Unknown URLs return 404.
- Original navy/ivory/gold museum shell, byte-identical copies of all nine scene/guide assets, preserved guide transparency, reference PNG copies, licensed local display/UI fonts and locally delivered Noto Chinese fallback fonts.
- Portable local configuration generation, ignored secrets, setup/verification scripts and [Linux/PowerShell documentation](setup.md).

## Phase 00 acceptance gates

| Gate as written in `phases/00_FOUNDATION.md` | Result | Evidence / limits |
|---|---|---|
| Fresh install/start commands documented and exercised on available environment. | PASS | Initial dependencies installed, frozen installs rerun, migration applied and both services started. [Setup](setup.md), [production build](../report/evidence/phase00/build.txt), [browser startup/results](../report/evidence/phase00/browser-tests.txt). Linux exercised; Windows/macOS instructions untested. |
| Web reaches API health; DB connection tested and failures are legible. | PASS | Actual web → API → PostgreSQL 17.10 / pgvector 0.8.5 / current migration. [Live checks](../report/evidence/phase00/live-service-checks.json), [API tests](../report/evidence/phase00/api-tests.txt), [status screenshot](../report/evidence/phase00/status-1600.png), [failure screenshot](../report/evidence/phase00/status-unavailable-1600.png). An auxiliary web server pointing to unused port 9 exercised the real proxy failure path and was stopped afterward. |
| No server key appears in browser code, logs, .env.example or tracked files. | PASS | No provider keys were introduced. `.env.example` contains names/comments only; real local secrets are ignored. Configured signing/database secrets were checked against source, docs, evidence and built browser outputs without printing values. [Foundation checks](../report/evidence/phase00/foundation-check.txt). |
| Correct assets and transparency preserved; no duplicate app scaffold. | PASS | Nine original asset hashes, dimensions and PNG RGB/RGBA modes match; all design reference copies are identical. One web/API scaffold exists. [Asset check](../report/evidence/phase00/foundation-check.txt), [guide screenshot](../report/evidence/phase00/guide-1600.png). |
| OpenAPI types generate deterministically; versions and scripts recorded. | PASS | Repeated generation produces identical OpenAPI JSON and TypeScript output. [Contracts](../packages/contracts/openapi.json), [foundation check](../report/evidence/phase00/foundation-check.txt), versions below and pinned manifests/locks. |

## Commands and results

| Command / procedure | Result |
|---|---|
| `pnpm install --frozen-lockfile` | PASS; resolved workspace lock installed. |
| `uv sync --project apps/api --frozen` | PASS; Python 3.12 environment synchronized from lock. |
| `pnpm setup:local` | PASS; created ignored local configuration without printing secrets. |
| `pnpm assets:sync` / `pnpm assets:verify` | PASS; nine asset hashes, dimensions and PNG modes, plus all reference copies. |
| `pnpm db:up` / `pnpm db:migrate` | PASS; dedicated container healthy and first migration applied. |
| `uv run --project apps/api alembic -c apps/api/alembic.ini check` | PASS; no new upgrade operations detected. [Output](../report/evidence/phase00/migrations.txt). |
| `pnpm contracts` / `pnpm check:foundation` | PASS; contracts regenerate identically; local env files ignored; configured-secret checks pass. |
| `pnpm lint` | PASS; ESLint and Ruff. [Output](../report/evidence/phase00/lint.txt). |
| `pnpm typecheck` | PASS; Next.js route types/TypeScript and strict mypy. [Output](../report/evidence/phase00/typecheck.txt). |
| `pnpm build` | PASS; production build. [Output](../report/evidence/phase00/build.txt). |
| `pnpm test:api` | **12 passed**; actual DB/vector readiness, outage, session reuse/revocation, cookie flags, mode isolation, tampering/expiry, origins/CORS, ownership and sanitized errors. [Output](../report/evidence/phase00/api-tests.txt). A Starlette/httpx test-client deprecation warning remains; no test failures. |
| `pnpm exec playwright install chromium` | PASS; required browser downloaded. Linux uses Playwright's Ubuntu 24.04 fallback build on this Arch host. |
| `pnpm test:e2e` | **6 passed**; all eight routes at three sizes, locale persistence, keyboard skip/navigation, actual health/session round trip, unavailable/retry, portrait layout, 404 and cross-origin rejection. [Output](../report/evidence/phase00/browser-tests.txt), [JSON](../report/evidence/phase00/browser-results.json). |
| E2E/config TypeScript check using the web package's `tsc` | PASS. |
| `pnpm peers check` / `git diff --check` | PASS; no peer conflicts or whitespace errors. |

## Versions and environment

| Component | Exercised version |
|---|---|
| OS / Node / pnpm | Linux (Arch kernel 7.0.13), Node 22.22.3, pnpm 11.10.0 |
| Web | Next.js 16.3.8, React/React DOM 19.3.0, Tailwind 4.3.3, Motion 14.0.0 |
| Web checks / contracts | TypeScript 5.9.3, ESLint 9.39.5, openapi-typescript 7.13.0, openapi-fetch 0.17.0, Playwright 1.63.0 |
| Python / uv | CPython 3.12.13, uv 0.11.24 |
| API | FastAPI 0.142.2, Pydantic 2.13.5, SQLAlchemy 2.1.3, Alembic 1.20.0, psycopg 3.3.6, Uvicorn 0.54.0 |
| Database | PostgreSQL 17.10, pgvector 0.8.5; image digest recorded in `compose.yaml` |

## Visual evidence and limits

The captured screens were visually reviewed. They preserve the supplied museum identity, readable live text, original transparent portrait and functioning navigation. Browser checks found no horizontal document overflow at **1600×900**, **390×844** or **768×1024**. Reduced motion was enabled. A half-width desktop layout check approximated 200% zoom; it is not a complete browser-zoom or accessibility audit.

- [Home desktop](../report/evidence/phase00/home-1600.png), [home phone](../report/evidence/phase00/home-390.png), [home tablet](../report/evidence/phase00/home-768.png).
- [Chinese Explore](../report/evidence/phase00/explore-zh-1600.png).
- [Guide desktop](../report/evidence/phase00/guide-1600.png), [guide phone](../report/evidence/phase00/guide-390.png).
- [Connected status](../report/evidence/phase00/status-1600.png), [injected unavailable UI state](../report/evidence/phase00/status-unavailable-1600.png).

These are eight foundation screenshots, not the eight desktop-reference fidelity gate required by Phase 01. See [intentional design differences](design-differences.md). No physical mobile device, Windows browser, Safari, full contrast audit or final pitch network was tested.

## Capability status

| Capability | Actual state |
|---|---|
| Web/API/database, health, session lifecycle, ownership helpers, contracts | Implemented and locally verified; real services. |
| Shared museum UI, route navigation, original artwork, EN/ZH shell | Implemented and browser-verified. |
| Later feature route content | Explicit unavailable states; no simulated AI success. |
| Interactive Phase 01 demo fixtures | Not implemented yet. |
| Reviewed exhibit corpus and rights-cleared artifact catalog | Not imported or published; no reviewed content or eligible artifact count is claimed. |
| Live guide, embeddings/retrieval, scan, journeys, stories, ASR/TTS, DNA/recommendations | Not implemented; phases 02–07. No credentialed provider calls performed. |
| Pilot metrics, real participants, calibrated identity thresholds | Unmeasured; original QA values remain targets. |
| Full visitor loop, competition release/rehearsal | Not ready; Phase 08 after the feature and evidence gates. |

## Changed files and next actions

Changes are grouped under `apps/web/`, `apps/api/`, `packages/contracts/`, `scripts/`, `tests/e2e/`, `design/reference/`, `docs/` and `report/evidence/phase00/`, plus the root workspace/Compose/configuration files, application README and ignore rules. Original report instructions and build-kit files were preserved.

There is no unresolved Phase 00 blocker on Linux. PowerShell setup remains a documented environment limitation. Future phases need actual human content review, source-specific rights decisions, approved geography if used, server-side provider credentials when required, and representative evaluation evidence.

Start Phase 01 from the original reference frames and supplied PNGs. Build the required UI component inventory and meaningful labelled fixture controls, then capture all eight desktop screens and mobile variants, compare panel geometry, and check drawer focus restoration, contrast, zoom and reduced graphics. Keep live AI features unavailable until their actual integrations and source prerequisites are fulfilled.

The local preview is running at <http://localhost:3000>; live foundation status is at <http://localhost:3000/status>. The API is on loopback port 8000 and the dedicated database on 5440. The auxiliary outage-check web process on 3001 has been stopped. Stop foreground web/API processes with Ctrl+C and the project database with `pnpm db:stop` when finished.
