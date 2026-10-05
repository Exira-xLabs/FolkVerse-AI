# Part B — confirmed bugs and accessibility defects

Updated 5 October 2026. Scope: B01–B12 from the [original UI audit](UI_AUDIT_BEFORE_PHASE_03.md). All twelve corrections are implemented and verified locally. Parts C, 4 and 5 remain separate backlog work.

| ID | Status | Delivered behavior |
|---|---|---|
| B01 | DONE | Earlier bounded scene/cover artwork retained; fresh phone layout and image checks pass. |
| B02 | DONE | Current navigation tab stays visible on all nine phone routes in EN/ZH. |
| B03 | DONE | Shared dialog traversal includes native summaries, links, enabled inputs and SVG keyboard controls; forward/backward wrapping reaches Record integrity. |
| B04 | DONE | Only clicks outside the drawer rectangle dismiss it. Interior padding stays open. |
| B05 | DONE | Reference-counted document scroll lock preserves prior inline styles and page position; closing restores the opener's focus. |
| B06 | DONE | Dropdown, directory, marker and territory selection share the same city fit, including selecting a city again after returning to the province. Province return resets the camera. Pan/zoom remain available. |
| B07 | DONE | Root graphics preference persists in a one-year same-site cookie across internal navigation and reload, including server rendering. |
| B08 | DONE | Valid interest chart definition-list structure retained; fresh axe scans show no definition-list violation in all six EN/ZH size states. |
| B09 | DONE | Labels keep a 14px screen-space font when zooming. Phone overview shows major/selected/focused city labels; the searchable fourteen-city list remains available. Dalian's label is shifted inward. |
| B10 | DONE | Standalone map search, camera/directory/location actions and attribution links have at least 44px usable height. Dense geographic markers retain equivalent directory buttons. Phone city-list text is 14px in both map modes. |
| B11 | DONE | Expanded atlas uses a labelled native modal dialog with aria-modal, native background isolation, shared scroll lock, keyboard traversal, Escape/exit controls and focus restoration. Wheel listeners reconnect when the map moves into the dialog. On phones the entire expanded atlas scrolls, preserving the map/minimap and access to the last directory button. |
| B12 | DONE | All nine screens have distinct EN/ZH titles in server metadata and after client language/navigation changes. Absolute titles avoid Home's streamed metadata overriding its full title. |

Verification:

- Production build, lint without warnings, TypeScript/Python type checks, foundation checks and original-artwork/content/geography preservation pass. [Build](evidence/ui-part-b/build.log), [lint](evidence/ui-part-b/lint.log), [types](evidence/ui-part-b/typecheck.log), [foundation](evidence/ui-part-b/foundation.log), [preservation](evidence/ui-part-b/preservation.log), [geography](evidence/ui-part-b/geography.log), [reviewed content](evidence/ui-part-b/content.log).
- Full Chromium browser suite: **40 passed, 0 failed, 0 skipped**. Includes published content, demo/live modes, keyboard/touch/pinch, camera regressions, images, three layouts, languages and five new Part B regression checks. [Final log](evidence/ui-part-b/e2e.log), [structured results](evidence/ui-part-b/browser-results.json), [new tests](../tests/e2e/ui-part-b.spec.ts).
- Fresh axe 4.13.0 scans cover interests, ordinary map, expanded map and published drawer at desktop/tablet/phone sizes in EN/ZH: 24 states, zero detected violations. [Results](evidence/ui-part-b/axe.json). Incomplete checks are retained for review; this is automated Chromium evidence, not a complete accessibility certification.
- Separate phone measurements check current tabs, page overflow and bounded artwork on all nine routes in both languages (18 states). Drawer close restores scrollY exactly (EN 781px, ZH 619px) and returns focus to the opener. [Measurements](evidence/ui-part-b/layout-and-scroll.json).

Initial runs exposed an enlarged-label pointer regression, stale camera selection after province return and Home title streaming. These were corrected before final verification. Early logs remain as diagnostic history; the final log is authoritative.

Screenshots remain local and Git-ignored. Physical device, Safari and full screen-reader testing remain unverified. No AI capability or review status was expanded by these UI corrections.
