# UI audit — Part A completion

**Completed:** 5 October 2026, Asia/Shanghai. Repository: `/home/oualid/Exira-X/FolkVerse_Codex_Build_Kit`, branch `main`, base `faf0a978efda14026bc4815aea22713cfc4b6133`. This pass is included in the owner-requested Part A delivery commit on `main`; consult Git history for its hash. The earlier report edit was preserved. No public deployment is claimed.

**Result:** all nine Part 1 corrections, A01–A09, are complete in the locally verified scope. This pass finishes the three previously remaining items. [Original audit with current statuses](UI_AUDIT_BEFORE_PHASE_03.md) remains the backlog for Parts 2–4. Screenshots are retained locally and ignored by Git.

## Remaining items delivered

| Item | Completed behavior | Evidence |
|---|---|---|
| A01 — actual featured exhibit on Home | Home reads one published Liaoning record from the publication API and displays its real title and reviewed summary before secondary discovery cards. The action navigates to `/explore?exhibit=<id>` and opens that exact record with its sources. The collection remains usable in demo and live modes. Loading, error/retry, empty, locale changes and withdrawal fail closed; no fabricated fallback exhibit or review is inserted. Reads are uncached and revalidated on focus and every 15 seconds. | `featured-exhibit.tsx`; EN/ZH and both-mode workflow, error/empty/withdrawal tests in `tests/e2e/ui-part-a.spec.ts`. |
| A08 — context-specific image compositions | Collection and Story cards use distinct existing scenes. Discovery covers have 16:9 frames and named focal positions; fixture thumbnails have their own subject crops and appropriately sized 64px image candidates. Heroes retain their bounded full-scene phone treatment. The original transparent Guide is contained within its card. Decorative/fictional captions clarify image roles. Reviewed features/details remain text-first rather than presenting decorative art as documentary imagery. | [Composition inventory](../docs/art-compositions.md), crop registry in `museum-art.ts`, three-size card regression and existing DPR-2 regression. |
| A09 — visitor-first status/error design | EN/ZH status leads with availability, retry, an Explore action and a last-check time. Database/vector/schema/mode details start collapsed inside a keyboard-operable disclosure. Unavailable states no longer tell visitors to start a local API. Optional anonymous-visit controls explain browsing without a session, no behavioral tracking or saved interests, and ending the actual session. | `service-status.tsx`, bilingual copy; keyboard disclosure, actual foundation health/session and injected outage/retry regressions. |

A02–A07 retain their previous corrections: bounded responsive scenes, collection-first Explore, compact Guide, optional previews, voluntary empty/example interests and calmer task panels. The original masters, scene outputs, guide visible pixels/alpha, terrain, authoritative geometry and reviewed corpus/ledger hashes still pass preservation checks.

## Verification results

| Exact command | Outcome | Evidence |
|---|---|---|
| `pnpm lint` | Exit 0; ESLint and Ruff pass. | [Log](evidence/ui-part-a/lint.log) |
| `pnpm typecheck` | Exit 0; TypeScript/route types and mypy pass. | [Log](evidence/ui-part-a/typecheck.log) |
| `pnpm build` | Exit 0; production build passes. | [Log](evidence/ui-part-a/build.log) |
| `node scripts/verify-museum-art.mjs` | Exit 0; all protected originals, scene outputs and lossless visible/alpha pixels pass. | [Log](evidence/ui-part-a/art-preservation.log) |
| `pnpm check:foundation` | Exit 0; deterministic contracts, original assets, ignored local configuration and configured-secret checks pass. | [Log](evidence/ui-part-a/foundation.log) |
| `FOLKVERSE_EVIDENCE_DIR=report/evidence/ui-part-a pnpm test:e2e` | Exit 0; **35 passed, 0 failed, 0 skipped**. Includes existing content, dropdown, map, health/session, keyboard/touch and refinement regressions, plus four Part A tests. | [Full log](evidence/ui-part-a/browser.log), [structured results](evidence/ui-part-a/browser-results.json) |
| Final focused browser command below | Exit 0; **5 passed, 0 failed, 0 skipped** after the final status-link wording change and rebuild. Includes 54 default-layout states: nine screens × EN/ZH × three sizes. | [Final focused log](evidence/ui-part-a/final-browser.log), [structured results](evidence/ui-part-a/final/browser-results.json) |

Final focused command:

```sh
FOLKVERSE_EVIDENCE_DIR=report/evidence/ui-part-a/final pnpm test:e2e --grep 'nine museum screens|Home features|featured publication|status keeps|decorative card'
```

Environment: Linux, Chromium, production Next.js, existing local FastAPI/PostgreSQL corpus. The full suite checks API-backed behavior; injected empty/error/withdrawal cases are labelled test scenarios, not observed production outages. No provider call was made.

## Visual review and local handoff

Home desktop/phone and Chinese tablet captures show the real featured record, distinct collection/Story covers and consistent contained portrait. Phone EN/ZH Status captures show readable visitor feedback with diagnostics collapsed. Additional local captures cover expanded diagnostics, Home unavailable/empty states and fixture thumbnails. Image/font loading is awaited before captures; no horizontal document overflow or page exceptions were found across the recorded 54 default states.

New captures are under `report/evidence/ui-part-a/` and its `final/` subdirectory. They are ignored by Git per the owner's instruction; local screenshot links do not imply screenshot delivery to GitHub. Original image assets and reviewed records were not overwritten.

The production preview is restored at <http://localhost:3000>, with connection checks at <http://localhost:3000/status>. [Web and API health measurement](evidence/ui-part-a/final/preview-health.json), [additional capture log](evidence/ui-part-a/final-captures.log). Web/API use the existing `pnpm --filter @folkverse/web start` and `uv run --project apps/api uvicorn folkverse.main:create_app --factory --host 127.0.0.1 --port 8000` commands. Stop them before reproducing the browser suite, which owns its test ports.

## Next work and limits

Next are **B03–B05**: source-drawer complete keyboard traversal, internal-padding/backdrop dismissal and background-scroll isolation. The remaining Parts 2–4 are not marked complete by this Part A pass. The new featured-record link opens the existing drawer; it does not claim those drawer defects were corrected.

Full contrast/screen-reader review, physical phones/software keyboards, Safari and native browser-toolbar zoom remain unverified. Live guide/retrieval, recognition, journey generation, saved profiles and live speech remain their assigned phase work. Part A completion supports local review, not a full UI freeze or competition-ready release.
