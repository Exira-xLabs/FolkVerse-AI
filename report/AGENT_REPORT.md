> Current status, 7 October 2026: Phase 3 complete. The [completion report](PHASE_03_FINAL_COMPLETION.md) supersedes historical pending-review/budget status below and records measured pilot/corrections, attributed machine assessment and limitations. Phase 4 is next.

# Phases 00–02 review before Phase 03

## 1. Repository and scope

Reviewed 6 October 2026, Asia/Shanghai, in `/home/soufiane/FolkVerse-AI`, branch `main`, commit `cd7e2aa9bc7d190111cbe69be32b693834b19bd3`.

**Verdict: the foundation and reviewed-content implementation are present, but this checkout does not yet have a verified working database/content flow. Resolve the local database blocker and repair the regression checks before treating Phases 00–02 as green for Phase 03. No wholesale rebuild is indicated by this review.**

The user's clarified scope is Phases 00–02 only. Missing live AI, recognition, durable journeys/profiles and live speech are deliberately excluded as defects: those belong to later phases. Phase 03 was read only to identify its prerequisites.

The original build kit is canonical at the repository root, as mapped in `docs/build-kit/README.md`. No applicable `AGENTS.md` was found. The starting working tree contained a generated change in `apps/web/next-env.d.ts`; its original contents are preserved at handoff. Application source was not fixed by this review.

Environment: Linux, Node **26.8.2**, pnpm **11.10.0**, uv **0.11.28**, Python **3.12.13**, Docker Engine **29.8.0**. Node is outside the repository's declared `>=22 <23` range; successful checks below therefore do not establish Node 22 reproducibility. Playwright's Chromium v1243 was installed for the audit; the OS uses its Ubuntu fallback build.

## 2. Instructions reviewed

| File | Review | Relevant requirement |
|---|---|---|
| `README_START_HERE.md` | Read | Numerical phases, targets versus actual counts, source review |
| `00_MASTER_CODEX_PROMPT.md` | Read | Preserve existing app, truthful demo/live separation |
| `01_OPENDESIGN_UI_PROMPTS.md` | Read | Eight routes, bilingual/responsive controls, actual reference images |
| `specs/ARCHITECTURE_AND_COSTS.md` | Read | Next.js/FastAPI/PostgreSQL, server-only providers and session boundary |
| `specs/DATA_AND_API_CONTRACTS.md` | Read | Publication, rights, revocation, ownership and errors |
| `specs/CONTENT_AND_AI_RULES.md` | Read | Imported records remain draft; actual editorial approval |
| `phases/00_FOUNDATION.md` | Read | Five foundation gates |
| `phases/01_VISUAL_UI.md` | Read | Five UI gates; fixtures are permitted |
| `phases/02_CONTENT_MAP.md` | Read | Five reviewed-content gates; one approved exhibit is sufficient |
| `phases/03_GROUNDED_GUIDE.md` | Prerequisites read | Approved passages and credentials for live checks |
| `QA_AND_DEMO.md`, `SOURCES_AND_TRACEABILITY.md` | Read | Verification, original artwork and no fabricated measurements |
| `report/AGENT_REPORT_INSTRUCTIONS.md` | Read | Evidence-backed reporting; narrowed by the user's subsequent scope |
| `docs/setup.md`, `docs/curation.md`, `docs/data-rights.md` | Read | Setup, restoration and intentionally untracked catalog images |
| `docs/decisions.md`, `docs/design-differences.md`, `docs/build-status.md` | Relevant sections read | Documented owner-directed design changes and historical results |
| `assets/ASSET_MANIFEST.json`, `references/ui/01_home.png` through `08_sources.png` | Inspected | Original assets and all eight visual references |
| `design/opendesign/` | Absent | Direct implementation from supplied references is permitted |

The documented owner-directed design changes supersede literal reconstruction. This audit does not flag the approved Jinyao presentation or Liaoning scope as unauthorized redesigns, and does not claim an 8px reference-fidelity score.

## 3. Phase compliance

PASS below means supported within the stated evidence scope. UNVERIFIED means a current check could not establish the gate; it does not mean the implementation is absent. Older successful runs are explicitly historical.

| Phase | Current audit status | Confirmed gates / total | Main outstanding verification |
|---|---|---:|---|
| 00 | Partial verification | 3/5 | Fresh PostgreSQL startup and healthy web → API → DB round trip |
| 01 | Partial; zoom defect confirmed | 4/5 | Fix 200% navigation overflow and repair full regression suite |
| 02 | Partial verification | 1/5 | Current PostgreSQL-backed import, publication, withdrawal and detail/source tests |

### Phase 00 acceptance gates, reproduced verbatim

| Gate | Result | Evidence |
|---|---|---|
| Fresh install/start commands documented and exercised on available environment. | UNVERIFIED | Web builds/starts; Python dependencies installed. `pnpm db:up` failed downloading the pinned image. Node 22/fresh pnpm install not exercised. |
| Web reaches API health; DB connection tested and failures are legible. | UNVERIFIED | Actual unavailable proxy produces sanitized HTTP 503. Healthy database connection cannot be tested here. Historical foundation/API logs exist. |
| No server key appears in browser code, logs, .env.example or tracked files. | PASS, bounded scan | `pnpm check:foundation` checked configured local secrets across 203 files, ignored env files and generated browser output. `.env.example` contains names/comments. No provider credentials were supplied or invoked. This is not an exhaustive scan for every possible unknown secret. |
| Correct assets and transparency preserved; no duplicate app scaffold. | PASS | Nine original asset hashes, dimensions and color modes verified; all reference copies match. One web app and one API. |
| OpenAPI types generate deterministically; versions and scripts recorded. | PASS | Foundation check regenerated OpenAPI and TypeScript identically; manifests/locks and scripts present. |

### Phase 01 acceptance gates, reproduced verbatim

| Gate | Result | Evidence |
|---|---|---|
| All eight routes work; no decorative button falsely appears functional. | PASS within tested UI scope | 48 route/locale/viewport checks; labelled fixtures and explicitly unavailable capture/live APIs inspected. Fixture drawer, story/audio and journey checks are recorded in the browser probe. Not evidence of working live AI. |
| Desktop background, avatar, tabs, typography, glass and panel geometry match reference. | PASS for documented revised scope | Original asset preservation, reference inspection, current captures and documented owner revisions. Literal original panel equality is superseded and not measured. |
| 390×844 and 768×1024 have no document overflow; controls remain usable. | PASS within Chromium scope | All eight routes × both languages × three sizes: HTTP 200, no horizontal overflow, no page exceptions. Not physical-device certification. |
| Keyboard navigation, focus restoration after drawer close, 200% zoom and reduced motion checked. | FAIL at 200% CSS zoom | Fixture focus trap/restoration and reduced motion pass, but Journey at 1600×900 with `document.body.style.zoom='2'` overflows: document width 1690px, viewport 1600px. The main navigation is the overflowing element. Native browser zoom and complete keyboard/screen-reader audit remain unverified. |
| Eight desktop and representative mobile screenshots saved; intentional differences listed. | PASS | Eight desktop and eight phone English captures generated locally under `report/evidence/phase00-02-review/`; differences documented in `docs/design-differences.md`. |

### Phase 02 acceptance gates, reproduced verbatim

| Gate | Result | Evidence |
|---|---|---|
| Re-import causes no duplicate objects or media; source payload/hash retained. | UNVERIFIED currently | Unique constraints/import logic inspected; 41 snapshot payload hashes match. Historical 37-object idempotent re-import evidence exists; no current live re-import performed. |
| Draft/withdrawn/unlicensed entries are absent from published search. | UNVERIFIED currently | Per-read eligibility and approval/rights dependency code inspected. Historical PostgreSQL tests passed; current DB-backed tests cannot run successfully. |
| One real approved exhibit traverses map/list → detail → source. | UNVERIFIED currently | Approved exhibit/region/source/passages and their exact review hashes are in the delivered snapshot. Current database restoration was blocked, so the full real flow was not traversed. |
| Source withdrawal removes affected search content and caches. | UNVERIFIED currently | Source withdrawal clears embedding markers; published reads recheck dependencies; browser revalidates every 15s/focus. Historical withdrawal tests exist. No vectors or retrieval caches exist yet. |
| Report exact approved/draft counts; target 10/30 is never manufactured. | PASS for delivered snapshot | Actual per-record counts and seven approved record hashes verified independently. Local image availability is reported separately below. |

## 4. Feature capability matrix

| Phase 00–02 capability | Actual state | Current evidence/limit |
|---|---|---|
| Web, EN/ZH routes, artwork and layout | Implemented and exercised | 48 current rendered states; no exceptions/overflow |
| Health and anonymous session API | Implemented; healthy DB path unverified here | Signed HttpOnly/SameSite cookies, Origin checks and server ownership helper inspected; current unavailable handling works |
| Explore atlas | Implemented UI and shipped geometry | 14 cities and public/client geometry; runtime map renders. Full source-reference verification blocked by missing ignored files |
| Published exhibits and sources | Implemented API/UI; runtime DB flow blocked | One reviewed exhibit and its evidence in snapshot; current web does not invent content when API is absent |
| Curation/import/restoration | Implemented; current DB execution blocked | Named-human attestation, append-only CLI history, fingerprints, draft defaults and refusal to overwrite inspected |
| Journey, Guide, Lens, Stories and interests in Phase 01 | Labelled deterministic fixtures / unavailable live state | These are appropriate Phase 01 outputs, not missing Phase 00–02 AI implementation |

## 5. Verification results

| Exact command/procedure | Exit/outcome | Evidence and interpretation |
|---|---|---|
| `pnpm lint` | 0 | ESLint and Ruff pass; Node engine warning |
| `pnpm typecheck` | 0 | Next route types, TypeScript and strict mypy pass (14 Python files); Node warning |
| `pnpm build` | 0 | Production build succeeds; Node warning |
| `pnpm check:foundation` | 0 | Deterministic contracts, original assets/reference copies, configured-secret checks |
| `node scripts/verify-museum-art.mjs` | 0 | Enhanced masters, lossless guide/terrain and protected artwork/content/geography hashes pass |
| `pnpm setup:local` | 0 | Created ignored local configuration, no secret values printed |
| `pnpm db:up` | 1 | Docker registry request timed out resolving the pinned pgvector image; no project database started |
| `pnpm db:migrate` | 1 | Connection refused at configured loopback database port 5440 |
| `uv run --project apps/api python -m folkverse.curation restore-manifest` | 1 | Same unavailable database; no restored corpus/database count is claimed |
| `pnpm test:api` before setup | 1 | 6 passed, 1 failed, 19 errors; missing DATABASE_URL/SESSION_SECRET |
| `uv run --project apps/api pytest apps/api/tests --tb=no -q` after setup | 1 | 8 passed, 6 failed, 12 errors; missing running DB. These failures do not establish broken publication/session logic |
| `FOLKVERSE_EVIDENCE_DIR=report/evidence/phase00-02-review pnpm test:e2e --grep 'Liaoning published region'` | 1; zero tests executed | API health remained unavailable; webServer timed out. [Current runner evidence](evidence/phase00-02-review/browser-results.json) |
| `node scripts/verify-liaoning-geography.mjs` | 1 | Missing `report/evidence/phase02-map/atlas-v2/liaoning-elevation-reference.png`; earlier geometry assertions reached this final check |
| `node scripts/verify-liaoning-contours.mjs` | 1 | Missing `.local/liaoning-v2/elevation/8-212-93.png`; shipped SVG tile validation precedes the missing raw-reference check |
| `uv run --project apps/api python report/evidence/phase00-02-review/snapshot-probe.py` | 0 | [Snapshot evidence](evidence/phase00-02-review/snapshot-probe.json): record counts, all seven approved fingerprints and 41 source hashes pass |
| `node report/evidence/phase00-02-review/browser-probe.mjs` | 0; diagnostic script records a zoom failure | [Current UI evidence](evidence/phase00-02-review/browser-probe.json): 48 normal-size rendered states pass, fixture drawer/story/audio/journey interactions pass, CSS 200% overflow is **true**. Script completion does not mean all recorded checks pass. No intercepted/fake healthy API |
| `git diff --check` | 0 at verification | No whitespace errors |

Historical `report/evidence/phase02/api-tests.txt` records **26 passed** on another checkout. Historical `report/evidence/phase02/corpus-integrity.json` records 37 re-imported objects and 32 verified images. These are useful prior evidence, not current successes on this machine. Current findings below invalidate assuming the full browser suite still passes unchanged.

## 6. Content, rights and Phase 03 prerequisites

The delivered snapshot has **14 active Liaoning exhibits: 1 approved and 13 drafts**; **28 active passages: 2 approved and 26 drafts**; **37 artifact records, all draft**, **32 media records, all draft**, **0 published artifacts**, **1 approved source**, and **56 review records**. Archived former-scope records remain withdrawn. Seven approved entity fingerprints and all 41 stored source payload hashes match. These are snapshot measurements, not live database counts.

Both approved passages express essentially one fact in two languages:

> Fuzhou shadow puppetry is listed as traditional theatre from Wafangdian, Liaoning.

The Chinese passage identifies its listing in the provincial heritage inventory. The recorded owner editorial approval and original-summary rights basis are preserved; no specialist endorsement is inferred. Government source hashes identify stored descriptors rather than archived full HTML, as disclosed in `docs/data-rights.md`.

**Phase 03 may start with this narrow reviewed coverage.** Ten approved exhibits and thirty eligible artifacts are targets, not prerequisites of Phase 03. Zero approved artifacts blocks a later live Lens catalog, not the text guide. Broad questions about techniques, history, dynasties or other traditions require new attributable passages and real review, or an explicit insufficient-evidence answer.

All **32 catalog image files are absent locally** because `.local/` is intentionally excluded from Git. Their historical downloaded count is 32; current local downloaded availability is **0**. This is not lost published content: all media/artifacts remain draft. The restore verifier must account for this documented situation.

The importer uses `/v1.1/search`, consistent with the [official Met API documentation](https://metmuseum.github.io/) rechecked 6 October 2026; its separate image-rights boundary is consistent with the [Met Open Access policy](https://www.metmuseum.org/hubs/open-access). No new Met import, provider call, external approval or paid request was performed by this audit.

## 7. Deviations and blockers

| Priority / classification | Finding and exact evidence | Impact | Required action |
|---|---|---|---|
| **High: local verification blocker** | `pnpm db:up` cannot download Compose's pinned image: registry timeout. Migration, restore, health and DB-dependent tests therefore fail | Cannot certify the current phase 00–02 foundation before integration | Obtain the pinned image through a working permitted connection, start the dedicated DB, migrate/restore, then rerun real API/content tests. Do not substitute a fake healthy response |
| **Medium: confirmed Phase 01 zoom defect** | Journey at 1600×900 with body CSS zoom 2 produces 1690px document width. `nav.nav-tabs` and its last link extend to x=1690. Normal-size 48-state checks have no overflow | Fails the phase's enlarged-content usability check; zoomed users must scroll horizontally | Make navigation reflow/contain its scroll area at enlarged text size, then add a regression covering this state. Verify native browser zoom separately |
| **Medium: confirmed regression-test defects** | `tests/e2e/foundation.spec.ts:58` expects accessible link `FolkVerse China`, while `museum-shell.tsx:37` names it `FolkVerse home`. `tests/e2e/ui-refinement.spec.ts:56` requires `.scene-picture img` on Guide, but `museum-shell.tsx:44` excludes Guide's scene and Jinyao has its own image. Current browser counts: old selectors 0, actual replacements 1 | At least these tests cannot pass against the current rendered UI; old full-suite success is not current assurance | Update tests to the approved current UI and rerun the whole suite; preserve meaningful navigation/image assertions rather than deleting them |
| **Medium: confirmed fresh-restore verification defect** | `scripts/verify-content-snapshot.py:57,64` compare complete `counts(db)` with historical snapshot counts. `counts()` measures current local image bytes; expected downloaded count 32 versus current 0 | A correct fresh content restore will fail its verification solely because optional ignored images are absent | Separate record/review/publication checks from local media availability; assert 0 for absent image bytes, and verify 32 only after explicit recovery. PostgreSQL execution of this predicted failure is blocked; arithmetic mismatch is confirmed offline |
| **Medium: confirmed map-verification portability defects** | `scripts/verify-liaoning-geography.mjs:52` requires a Git-ignored elevation-reference PNG; `verify-liaoning-contours.mjs:11` requires ignored raw DEM tiles. Both commands currently exit 1 | A fresh collaborator cannot reproduce the full documented map provenance checks from the tracked checkout alone | Document/reproduce reference downloads/generation and separate shipped-asset integrity from optional raw-reference verification; explicit unavailable state rather than unexplained ENOENT |
| **Medium: confirmed demo/live configuration inconsistency** | `apps/api/src/folkverse/config.py:16` defaults to `demo`; `apps/web/src/lib/app-mode.ts:7–12` falls back to `live`. Constructing API settings without APP_MODE returns demo | If APP_MODE is omitted while other settings are supplied, web/API disagree; session signing mode differs. Especially relevant before adding live provider behavior | Choose a shared fail-closed default or require explicit APP_MODE in both services; test missing/invalid config. Normal setup currently supplies demo explicitly, so this is a conditional defect |
| **Low: documented UI behavior mismatch** | `visit-provider.tsx:11` defaults Explore to `map`; README/design notes say collection-first. Fresh browser confirms atlas visible and map button pressed | User reaches long atlas before collection, particularly on phones; not a grounded-guide blocker | Align default with the latest agreed UI requirement or correct the documentation if map-first is intentional |
| **Environment mismatch** | Node 26.8.2 versus package engine `>=22 <23` | Present checks are not proof of supported-runtime setup | Rerun with Node 22 using a project-local runtime; avoid system-wide changes |
| **Coverage limitation, not a failed Phase 02 target gate** | Only two short approved bilingual passages from one source | A truthful initial guide has extremely limited supported scope | Define those supported facts and unsupported examples first; broaden reviewed content in parallel if wider explanations are required |

## 8. Handoff and next actions

1. Unblock the dedicated PostgreSQL/pgvector environment. Run `pnpm db:up`, `pnpm db:migrate`, `uv run --project apps/api python -m folkverse.curation restore-manifest`, then `pnpm test:api`. Restore only into empty content tables; the CLI correctly refuses overwrite.
2. Fix the 200% navigation overflow, repair current browser selectors and fresh-clone verification assumptions. Run the complete `pnpm test:e2e` against the restored real corpus with evidence output directed to a new directory. A passing historical log is insufficient.
3. Align demo/live defaults before provider integration. Use the declared Node 22 runtime for the final check. Resolve map-first documentation/default disagreement independently; it need not delay retrieval design.
4. Begin Phase 03 using the existing approval/rights eligibility helpers and exact narrow corpus. Ensure revoked passages are rechecked before retrieval and answer publication when Phase 03 adds actual vectors/caches. No artificial exhibit/artifact count or invented cultural answer is necessary.

The source structure, locked dependencies, deterministic contracts, preserved artwork and hash-bound editorial records give a useful base. **The remaining go/no-go gate is a passing current real database → published exhibit → source flow and regression suite.** Normal-size UI presentation and offline corpus integrity pass; enlarged navigation has a confirmed defect and healthy integration is not yet verified. Phase 03 design/offline work can proceed, but do not label its integration ready on this machine until that gate passes.

Only report/evidence files were added. Audit setup created ignored local `.env`/web environment and Python/build caches and installed the matching Playwright browser. No application fix, new editorial approval, image recovery, provider request or deployment was made. Audit web processes are stopped at handoff; no FolkVerse DB container was started. Suggested status-document updates are to record this machine's blocked DB verification and current test/script discrepancies; historical evidence should remain clearly dated.
