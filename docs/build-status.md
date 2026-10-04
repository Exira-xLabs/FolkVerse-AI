# FolkVerse build status

**Updated:** 4 October 2026, Asia/Shanghai. **Phase 01: complete on the available Linux/Chromium environment, with the user-approved presentation-as-inspiration visual scope.** Next: [Phase 02 — content and map/list](../phases/02_CONTENT_MAP.md). Phase 02 has not started.

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
