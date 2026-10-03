# Phase 01 — Exact museum UI and OpenDesign integration

**Prerequisite:** Phase 00 health and asset gates pass.

**Outcome:** Eight responsive app screens with real controls and deterministic fixtures.

## Paste into Codex
```text
Read docs/build-kit/00_MASTER_CODEX_PROMPT.md and docs/build-kit/phases/01_VISUAL_UI.md. Inspect the repository and docs/build-status.md. Implement the following phase, preserving approved UI and unrelated work.


Read 01_OPENDESIGN_UI_PROMPTS.md. Open all eight reference UI PNGs. Inspect design/opendesign if present; integrate its usable output rather than replacing the repo. Match the actual museum scenes, glass treatment, serif typography, gold and guide girl. Do not use business-pitch tabs as app navigation.

Create MuseumScene, GlassPanel, GlassTabs, GoldButton, ThemeChip, SourceDrawer, ExhibitCard, GuidePortrait, AudioControls and InterestChart. Implement /, /explore, /journey, /stories/[id], /lens, /guide, /dna and /sources. Add route-aware tabs, logo navigation, EN/ZH and responsive layout. Use CSS overlays for contrast; artwork contains no functional text. Build charts as components, not screenshots.

Connect controls to meaningful fixture state: filters change cards, journey stops reorder, story choices change nodes, guide composer shows a clearly labelled recorded demo, lens selection shows labelled simulation, profile edits update the graph. Fixture mode must be visible. Add loading, empty, unavailable and permission-denied examples.

At 1600×900 compare every page with the matching screenshot. Match panel positions and background crops before polishing animations. Save actual screenshots and difference notes. At mobile keep theme while stacking and scrolling. Reduced-motion and reduced-graphics modes must work. Do not copy fictional scan confidence numbers into live-result components.


Update docs/build-status.md with actual results, blockers and the next phase. Report what is live, fixture-driven, untested or unavailable. Do not claim completion unless the gates below are met.
```

## Acceptance gates

- [ ] All eight routes work; no decorative button falsely appears functional.
- [ ] Desktop background, avatar, tabs, typography, glass and panel geometry match reference.
- [ ] 390×844 and 768×1024 have no document overflow; controls remain usable.
- [ ] Keyboard navigation, focus restoration after drawer close, 200% zoom and reduced motion checked.
- [ ] Eight desktop and representative mobile screenshots saved; intentional differences listed.


## Handoff
Design component inventory, screenshot paths and remaining visual discrepancies. Do not mark AI implemented.
