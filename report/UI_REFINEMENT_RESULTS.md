# UI refinement results

**Date:** 5 October 2026, Asia/Shanghai. **Repository:** `/home/oualid/Exira-X/FolkVerse_Codex_Build_Kit`, branch `main`, base commit `be911c8e4c3d34fa1b6e6c1398d4dd1436ce3172`. The refinement and existing Phase 02 changes were uncommitted during verification. The owner subsequently requested four commits and four pushes; the delivery groups are reviewed content/API, sourced atlas, refined UI/tests, and reports/evidence. Consult `git log -4 --oneline` for the delivery hashes.

**Scope:** the image-delivery pass and seven owner-selected design changes in [the checklist](UI_REFINEMENT_CHECKLIST.md). These changes are implemented and locally verified. This report does not close every finding in [the earlier UI audit](UI_AUDIT_BEFORE_PHASE_03.md) or complete the later AI phases.

**Screenshot delivery:** the owner requested that screenshots stay local. New raster evidence is excluded from the final branch tree; links below refer to local evidence files. Text reports, logs, structured results and app artwork remain committed. Some map screenshots were already uploaded in push 2; removal from the current tree does not remove them from that earlier commit history.

## Delivered changes

| Selected change | Result | Evidence |
|---|---|---|
| Home leads to Liaoning | Primary Explore Liaoning action and published-collection card open the real reviewed collection. Secondary cards state their preview/fiction status. | [Home desktop](evidence/ui-refinement/01-home-1600.png); browser test `home leads to reviewed exhibits and collection view preserves map filters`. |
| Bounded scene compositions | Artwork occupies a bounded hero instead of the entire scrolling document. Phone heroes display full scenes; phone Explore omits the decorative hero to prioritize the exhibit. | [Home phone](evidence/ui-refinement/01-home-390.png), [tablet](evidence/ui-refinement/01-home-768.png), DPR-2 image regression. |
| Explore starts with exhibits | Collection is the default; the sourced atlas is optional. Switching views retains the selected city/filter, including cities with no published records. | [Explore phone](evidence/ui-refinement/02-explore-390.png); collection/map and six atlas tests. |
| Compact Guide | Original companion becomes a 72×72-pixel identity badge beside its introduction. The separate oversized portrait panel is removed. | [Guide phone at DPR 2](evidence/ui-refinement/guide-phone-dpr2.png); badge geometry assertion. |
| Visitor tasks before previews | Journey, Lens and Guide start with availability, purpose and a link to the real collection. Scripted controls are inside collapsed, keyboard-operable optional previews. Sources retains an explicit published/preview choice. | Preview keyboard test; [Guide default](evidence/ui-refinement/06-guide-390.png), [Journey default](evidence/ui-refinement/03-journey-390.png). |
| Voluntary cultural interests | English DNA claims become cultural-interest wording. All four weights start at zero; the example is explicitly labelled and removed on manual editing. Reset clears suggestions. No behavioral tracking or saved profile is claimed. | [Empty interests](evidence/ui-refinement/07-dna-390.png); interest editing, example and reset regressions. |
| Calmer task surfaces | Opaque navy reading/task surfaces, restrained navigation glass and bounded artwork reduce competition with text. | Nine-screen EN/ZH captures at all three sizes. |

The narrow navigation row now reveals its current tab. The screenshot readiness helper verifies the whole current tab lies inside its row, in both languages and all three tested sizes. Interest-chart bars now sit inside `<dd>` elements rather than directly beside `<dt>` and `<dd>`; the definition-list structure is corrected. This is a code inspection, not a fresh full axe audit.

## Artwork and preservation

Eight versioned decorative scenes are delivered under `apps/web/public/folkverse/enhanced/`. [Artwork provenance](evidence/ui-refinement/artwork.json) records prompts, inputs, outputs, dimensions and hashes. Native outputs are 1672×941, except Lens at 1671×941: the larger requested generation target was not returned, so an increase in native resolution is not claimed.

Quality-90 responsive Next.js images and bounded layout replace full-document enlargement. Phone DPR-2 tests check loaded image candidates at least twice their displayed CSS width, full-scene `contain` framing and no horizontal document overflow. A larger candidate does not create detail beyond the native master. Focused thumbnail crops avoid stretching; decorative artwork remains separate from reviewed evidence and authoritative geography.

The guide and terrain use lossless WebP delivery. [Pixel comparison](evidence/ui-refinement/lossless-delivery.json) records zero visible RGB or alpha differences. Guide delivery is 1,154,362 bytes instead of 1,673,187; terrain is 2,470,558 instead of 3,147,927. No new guide identity or terrain geometry was generated.

[Protected hashes](evidence/ui-refinement/protected-hashes.json) cover all nine supplied masters, the original terrain, geographical data, city boundaries, corpus and review ledger. The resumed preservation check passes for all of them, all eight scene outputs and both lossless outputs.

## Verification

Checks run against the local production build on Linux/Chromium, using the existing FastAPI and PostgreSQL corpus. No provider calls or public deployment were performed.

| Exact command / procedure | Outcome | Evidence |
|---|---|---|
| `pnpm lint` | Exit 0; ESLint and Ruff pass. | [Log](evidence/ui-refinement/lint-resumed.log) |
| `pnpm typecheck` | Exit 0; route types, TypeScript and mypy pass. | [Log](evidence/ui-refinement/typecheck-resumed.log) |
| `pnpm build` | Exit 0; production build passes. | [Log](evidence/ui-refinement/build-resumed.log) |
| `node scripts/verify-museum-art.mjs` | Exit 0; protected hashes, scene dimensions and visible/alpha pixels pass. | [Log](evidence/ui-refinement/asset-verification-resumed.log) |
| `FOLKVERSE_EVIDENCE_DIR=report/evidence/ui-refinement pnpm test:e2e` | Exit 0; **31 passed, 0 failed, 0 skipped** (69.85 seconds); includes content, dropdown, foundation, map, museum UI and refinement coverage. | [Final log](evidence/ui-refinement/browser-final.log), [structured results](evidence/ui-refinement/browser-results.json) |
| Nine routes × EN/ZH × 1600×900, 390×844, 768×1024 | 54 default-layout states; images/fonts loaded, no page exceptions or document overflow. Current navigation tab stays visible where present. Chinese Explore capture waits for the translated exhibit title. | `01-home` through `09-status` captures and `zh-1` through `zh-9` captures in [evidence directory](evidence/ui-refinement/) |
| Keyboard, touch and map regression | Optional summaries open with Enter; dropdown keyboard/touch behavior, drawer wrap/Escape/focus restoration, city selection, wheel/pan, keyboard camera, minimap, expanded-map exit and touch pinch exercised. | Browser suite |
| DPR 2 / reduced motion / enlarged layout | Phone image delivery and 72px badge verified; reduced graphics/motion and 200% CSS zoom with narrowed layout checked. Browser-toolbar zoom and physical touch devices are untested. | Browser suite, [Guide DPR-2 capture](evidence/ui-refinement/guide-phone-dpr2.png) |

Historical attempts are retained: [first run](evidence/ui-refinement/browser-first-run.log) failed the wheel test after the map moved outside the viewport; the test now scrolls the map into view. [Subsequent run](evidence/ui-refinement/browser.log) passed 31/31. A resumed run also passed 31/31 with the navigation assertion. Visual inspection then found a capture timing issue where EN exhibit content was captured immediately after the Chinese shell switched; the capture now waits for the Chinese title. One follow-up startup failed because the restored preview occupied port 3000; that preview was stopped before the final run. The user interruption stopped another run before results, so it is not counted as a pass.

## Visual review and limits

Six overview sheets cover all nine default screens at each size in both languages. Six phone captures show Journey/Lens/Guide previews open in EN/ZH; two more show the labelled example-interest state. Journey/Lens open states, Chinese Guide, Chinese example interests and the corrected Chinese Explore capture were inspected individually. [Journey open](evidence/ui-refinement/journey-preview-open-en.png), [Lens open](evidence/ui-refinement/lens-preview-open-en.png), [Guide open in Chinese](evidence/ui-refinement/guide-preview-open-zh-CN.png), [Chinese interest example](evidence/ui-refinement/interests-example-zh-CN.png). Home desktop, Explore phone and Guide phone were also inspected individually. The bounded phone art retains whole scenes, the reviewed exhibit immediately follows Explore's view controls, the companion is compact, and lower reading surfaces remain calm. Chinese institutional source titles are original source-record titles, not newly generated translations.

Overview sheets: [EN desktop](evidence/ui-refinement/overview-en-1600.jpg), [EN phone](evidence/ui-refinement/overview-en-390.jpg), [EN tablet](evidence/ui-refinement/overview-en-768.jpg), [ZH desktop](evidence/ui-refinement/overview-zh-1600.jpg), [ZH phone](evidence/ui-refinement/overview-zh-390.jpg), [ZH tablet](evidence/ui-refinement/overview-zh-768.jpg).

This is local refinement verification, not accessibility certification or full audit closure. Full manual contrast/screen-reader testing, Safari, Windows, physical devices and native browser-toolbar zoom remain unverified. Remaining audit work includes complete source-drawer tabbable traversal, interior/backdrop dismissal and background scroll isolation; fullscreen-map semantics; preference persistence; distinct page titles; small map labels/targets; and context-preserving exhibit-to-guide flows. Do not mark those items resolved based on the passing regression suite. See the original audit for the full backlog.

Journey, Lens and Guide previews remain scripted fixtures. Live guide/retrieval, recognition, journey generation, profile persistence and live speech remain assigned phase work. The story remains original fiction with recorded synthetic English narration. The seven selected design changes are ready for local review; the full UI handoff still needs the outstanding audit items before a freeze.

## Local handoff

Restored preview health: web root, web-to-API health and direct API health all return HTTP 200; [measurement](evidence/ui-refinement/preview-health.json), [capture/health log](evidence/ui-refinement/open-states.log). Preview: <http://localhost:3000>; connection check: <http://localhost:3000/status>. The production web preview uses `pnpm --filter @folkverse/web start`; API startup uses `uv run --project apps/api uvicorn folkverse.main:create_app --factory --host 127.0.0.1 --port 8000`. The project database remains on its existing local port. Stop these web/API previews before reproducing the browser suite, which owns ports 3000, 3002 and 8000.

Next: resolve the remaining shared UI audit defects, then follow [Phase 03](../phases/03_GROUNDED_GUIDE.md) prerequisites for a real grounded guide. The implementation and evidence are included in the owner-requested four-commit delivery on `main`; no public deployment is claimed.
