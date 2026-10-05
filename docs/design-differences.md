# Visual status — Phase 01

The user clarified during implementation that the PDF/presentation is inspiration and asked for imagination and an impressive product. This replaces the phase prompt's literal reconstruction requirement. The eight original frames were inspected, and their composition remains the starting point; the original museum backgrounds, transparent guide, serif typography, navy/ivory/gold palette and glass layers are preserved. No exact 8px fidelity score is claimed.

## Screen comparisons

| Screen | Preserved direction | Intentional changes |
|---|---|---|
| Home | Spacious museum scene, four bottom cards and wider guide card | Functional discovery links, clear demo footer, optional hover lift. |
| Explore | Left filter glass, unobscured map focal point, lower-right region preview | Actual search/theme filters and an accessible exhibit list. Imaginary map markers are not clickable geography. Search-empty state is real. |
| Journey | Top preference pills, broad bottom route glass and numbered stops | Duration, ordering/removal controls and time totals. Extra panel space supports actual editing; labels identify digital learning and fixtures. |
| Story | Left player/choices over a luminous shadow screen | Original fictional two-ending tale, bilingual captions, real recorded English playback/seek, restart and context drawer. No copied fictional time. |
| Lens | Left result glass and unobscured object scene | Scenario selector and explicit simulation. Invented confidence bars replaced by descriptive related/unknown/insufficient/denied/unavailable outcomes. No camera request or upload. |
| Guide | Wide left chat, original girl at right | Bounded multiline composer, loading/scripted response, source requirements and unavailable voice feedback. Portrait is contained, never stretched; source claims are not invented. |
| DNA | Left interests glass and lower-right suggestion | Real SVG radar chart plus editable bars/text, reset and preview-only opt-in. Sample values remain labelled; recommendations respond to explicit edits. |
| Sources | Wide lower evidence chain | Four inspectable stages. Invented region/exhibit totals replaced by zero published sources and human-review requirements. |

Desktop screenshot names in `report/evidence/phase01/` are `01-home-1600.png` through `08-sources-1600.png`. The same prefixes ending in `-390.png` and `-768.png` cover phone and tablet. All eight desktop and phone frames were visually inspected. Eight Chinese desktop captures demonstrate local CJK fonts and translated UI; both languages were tested at every size.

The story/lens panels are taller than their slide counterparts because they contain real controls and disclosures. The guide chat similarly accommodates a multiline input and service state. Mobile preserves the scene and glass, stacks panels, scrolls content vertically and moves the guide below the conversation. Navigation scrolls inside its row with a partially visible next tab; the document does not scroll horizontally.

## Accessibility, graphics and interaction evidence

- Native source dialog plus explicit Tab/Shift+Tab wrap, initial close-button focus, Escape close and return to opener were tested.
- Original keyboard skip/link behavior and locale persistence continue to pass.
- All scene images and fonts load before screenshots; the guide transparency remains byte-identical to the original asset.
- `guide-reduced-graphics-1600.png` shows the opaque, blur-free, animation-free performance mode. Reduced motion is enabled in the browser suite.
- `journey-zoom-200.png` captures enlarged content using 200% CSS zoom at a narrowed layout viewport. This checks reflow, not native toolbar zoom or an operating-system magnifier.
- `source-drawer-1600.png` and `dna-edited-1600.png` show actual interaction states.

There is no new AI-generated raster artwork. The supplied scenes already provide the visual identity; the chart, control layers and transitions are implemented in code. No face regeneration, traced map boundaries or screenshot-only controls were used.

## Remaining limitations

No reviewed region geometry/content corpus exists yet. This phase cannot demonstrate real cultural accuracy, retrieval, recognition, provider latency or saved profiles. English synthetic story narration is recorded locally; Chinese audio and live speech are unavailable. Literal reference-edge equality, Safari, physical devices, native toolbar zoom and a complete screen-reader/contrast audit have not been measured. Text and modal readability were visually inspected, not represented as a full accessibility certification.

Phase 00 screenshots remain unchanged in `report/evidence/phase00/`. Its original unavailable shells were replaced only in demo mode; live mode still fails closed.

## Owner-requested refinement — 5 October 2026

The owner requested image quality improvements first, followed by seven specific design changes before Phase 03. This supersedes the historical full-page backgrounds, default prototype controls, sample interest scores and separate mobile portrait described above.

Eight versioned scene refinements now live in `apps/web/public/folkverse/enhanced/`; original scene masters remain byte-identical. The generator returned native 1672×941 scenes (Lens 1671×941), rather than the requested larger target, so no resolution increase is claimed. Bounded hero rendering and quality-90 responsive delivery remove the scrolling-page enlargement. Phones show full scene compositions; Explore prioritizes collection content and exposes its sourced map on request. Guide and terrain have lossless WebP delivery with identical visible pixels and alpha, and the original guide identity is preserved.

Home prominently opens the Liaoning collection. Explore defaults to exhibits with an optional map view. Journey, Lens and Guide put their scripted controls inside optional preview disclosures. Guide uses a compact 72-pixel identity badge. English DNA wording is replaced by cultural interests, initially empty, with a labelled example action and local editing. Task panels are opaque navy; artwork and restrained navigation glass carry the atmosphere.

Current verification and limitations belong to `report/UI_REFINEMENT_CHECKLIST.md` and `report/UI_REFINEMENT_RESULTS.md`. This UI work does not complete Phase 03 or connect live guide, journey or recognition providers. The `/dna` URL remains compatible with existing links.
