# Remaining UI report delivery

5 October 2026, Asia/Shanghai. Scope: the reopened M09 semantics and all ten Part 5 improvements, while preserving the A/B/C/Part 4 work and explicit later-phase API boundaries. No physical-device, Safari or screen-reader result is fabricated. The owner confirmed those environments are unavailable.

## Required items

A01–A09, B01–B12, C01–C12 and M01–M15 are implemented in the local UI scope. M09's five previously unsupported group labels now use valid group semantics. M16's inventory, screenshots, constrained/offline network and available local checks are delivered; real phone/software keyboard, actual Safari and a real screen reader remain **UNAVAILABLE / UNVERIFIED**. This leaves 48 of 49 required items complete locally. The audit is not fully certified or closed.

## Optional improvements delivered

| ID | Status | Actual delivery |
|---|---|---|
| N01 | DONE | Short opacity entrance on route change; no information depends on motion. Reduced motion and Simplify graphics suppress it. Existing visit context and current route remain intact. |
| N02 | DONE | Home Continue exploring reopens the explicitly retained reviewed exhibit ID through the current withdrawal-aware loader. Reset continuation removes it; reload/close clears it. |
| N03 | DONE | Hover/focus previews on city markers, territories and directory controls, with a list from that city's currently published coverage. Selection stays unchanged; loading, no-match and service errors are truthful. Directory placement stays stable during pointer-down/up. |
| N04 | DONE | Optional topographic detail with nine independently sourced/hashed SVG contour tiles at 50/200/500/1000 metres; only camera-intersecting tiles load. Vector detail remains sharp at zoom, with colour/metre legend, loading/retry and approximate-data disclosure. It adds no elevation resolution. Original artwork and sourced borders remain unchanged. |
| N05 | DONE | Exhibit/source reading surface, Standard/Large/Larger text, visitor-controlled light surface and actual dialog-scroll progress. Source evidence and citations remain available; dialog Escape/focus/scroll behavior is preserved. |
| N06 | DONE (preview UI) | Original 72px character badge retained. A small code-drawn book/status illustration reflects ready/preparing/unavailable scripted states, with text equivalents and reduced-motion handling. No emotion inference, model response or new portrait identity is claimed. |
| N07 | DONE (original fiction) | Different code-drawn mountain/river ending scenery, chapter progress and a soft synthetic soundscape. Play is explicit, Stop works, leaving Story closes its AudioContext. Existing recorded narration is separate; no autoplay or microphone use. |
| N08 | DONE | Editable constellation stars support pointer/Enter/Space changes, with matching text values and equivalent sliders. Empty, labelled example and Reset remain voluntary preferences, not a personality measurement. |
| N09 | DONE (in-memory visit scope) | Explicit opt-in before bookmarks; maximum 50 reviewed IDs, individual remove/Clear all/revoke and shareable exhibit URLs. Cards revalidate language/publication and remove stale links on withdrawal. Nothing is written to browser storage/server; reload/close clears consent/bookmarks. Durable account saves remain later APIs. |
| N10 | DONE | Light reading surface plus a persisted low-data preference. Low-data skips decorative raster requests and keeps reviewed text/borders/numerical map detail usable. Fresh 390×844 Chromium Home contexts measure 5 image responses / 357326 bytes with images, and 0 image responses / 0 bytes in low-data mode. This is image payload, not a whole-page performance claim. |

## Validation

The full Chromium suite passes **61 tests**, including seven new regressions in [ui-remaining.spec.ts](../tests/e2e/ui-remaining.spec.ts). [Full log](evidence/ui-remaining/e2e.log), [results](evidence/ui-remaining/browser-results.json). The final rendered scan covers **108 EN/ZH states** (18 states × three widths × two languages): zero detected axe violations, page errors, horizontal overflow or undersized enabled standalone controls. Group-label incomplete findings are cleared; remaining incomplete contrast checks are recorded and assessed separately, not counted as automated passes. All **15 final focused checks pass** after the last visual refinements. The 94 remaining incomplete scan assessments are exclusively contrast; unsupported group-label findings are cleared.

- [Final focused browser checks](evidence/ui-remaining/final-focused/e2e.log), [rendered review](evidence/ui-remaining/rendered-review.md), [unavailable environments](evidence/ui-remaining/environment-validation.json).
- [Lint](evidence/ui-remaining/lint.log), [type checks](evidence/ui-remaining/typecheck.log), [production build](evidence/ui-remaining/build.log).
- [Original artwork preservation](evidence/ui-remaining/preservation.log), [geography](evidence/ui-remaining/geography.log), [contour source/output hashes](evidence/ui-remaining/contours.log), [generation](evidence/ui-remaining/contour-generation.log).
- [Light surface/star contrast](evidence/ui-remaining/contrast-reading-stars.json), [visual refresh log](evidence/ui-remaining/visual-refresh.log).
- [Final rendered scan](evidence/ui-remaining/handoff-scan.json), [scan log](evidence/ui-remaining/handoff-scan.log), [low-data image payload comparison](evidence/ui-remaining/low-data-image-payload.json).
- [Visit/storage/consent policy](../docs/visit-state-and-context.md), [numeric map provenance](../docs/liaoning-map.md).

The initial run exposed a click displaced by inserting the city preview above the directory, an SVG title made from multiple children that did not hydrate, and a text-size selector lookup needing an explicit accessible label. Those defects are corrected; the initial log is diagnostic history, not final evidence. SVG tile bounds are checked numerically so equivalent Python/JavaScript float string formatting does not create a false verifier failure.

Screenshots remain local and Git-ignored. No original raster asset, approved content, cultural source rights or geographic boundary is changed. Real Guide, recognition, durable Journey, generated Story and stored-profile services remain their assigned later phases. The user's unavailable M16 environments remain the only external verification gap before full UI certification.
