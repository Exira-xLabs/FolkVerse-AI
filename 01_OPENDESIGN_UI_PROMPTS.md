# OpenDesign and Codex visual handoff

## Reference hierarchy
Match the original museum: full-frame scene, dark navy shadows, ivory headings, gold accents, floating glass and the same AI girl. Reference frames are 1600×900. Layout coordinates below use 1280×720; multiply by 1.25 for screenshots. The approximately 16:9 backgrounds are 1672×941.

| Route | Reference under `references/ui/` | Background under `assets/` | Composition at 1280×720 |
|---|---|---|---|
| `/` | 01_home.png | 01_museum_entrance.png | Four discovery cards across bottom; wider final guide card |
| `/explore` | 02_explore.png | 02_interactive_map.png | Filter x48 y277 w314 h391; region preview x796 y562 w434 h104 |
| `/journey` | 03_journey.png | 03_cultural_journey.png | Controls y270; route glass x48 y454 w1184 h214 |
| `/stories/[id]` | 04_stories.png | 04_shadow_puppetry.png | Player/choices x48 y323 w432 h345 |
| `/lens` | 05_lens.png | 05_object_lens.png | Result panel x48 y302 w415 h366; object scene on right |
| `/guide` | 06_guide.png | 06_ai_guide.png | Chat x48 y291 w746 h377; avatar card x861 y308 w371 h360 |
| `/dna` | 07_dna.png | 07_folklore_dna.png | Interests x48 y294 w420 h374; recommendation lower right |
| `/sources` | 08_sources.png | 08_museum_everywhere.png | Evidence panel x48 y448 w1184 h220 |

Use `09_ai_guide_character.png` with transparency and `object-fit: contain`. No face regeneration, stretching or rectangular backdrop. `references/brand/first_concept.png` contains baked-in text: inspiration only, not a working page background. Existing artwork can contain decorative map markers or glass edges; those are not functional controls.

## Tokens extracted from the presentation builder
```css
:root {
  --museum-base: #030911;
  --museum-panel: #07111b;
  --text-primary: #fff4df;
  --text-secondary: #cfd9dd;
  --accent-gold: #f6d697;
  --glass-border: rgb(237 219 177 / 48%);
  --glass-highlight: rgb(255 247 222 / 42%);
  --glass-radius: 22px;
  --pill-radius: 999px;
  --font-display: 'DejaVu Serif', 'Noto Serif SC', serif;
  --font-ui: 'DejaVu Sans', 'Noto Sans SC', sans-serif;
}
.glass-panel {
  background: linear-gradient(125deg,
    rgb(176 196 211 / 22%) 0%, rgb(27 39 50 / 76%) 24%,
    rgb(7 17 27 / 72%) 79%, rgb(139 104 55 / 43%) 100%);
  border: 1px solid var(--glass-border);
  border-radius: var(--glass-radius);
  box-shadow: 0 20px 50px rgb(0 0 0 / 30%), inset 0 1px 0 var(--glass-highlight);
  backdrop-filter: blur(16px);
}
```
This CSS is a translation of the slide treatment, not a guaranteed pixel-equivalent renderer. Tune against screenshots. Stronger panels can start with rgb(83 101 114 / 64%). Dense text needs a dark enough panel.

- Nav x36 y24 w1208 h62. Logo x58 y34. Six 96×34 tabs begin around x483 and advance 104px. EN/ZH control at right. Logo links home.
- Kicker x54 y112, title x52 y143, subtitle x55 y214. At 1600×900 use roughly 52.5px title, 21px body, 15–16px compact controls. Reserve space when text wraps.
- Button gold gradient #EDD5A0 to #B98D47; dark #171713 text. Ivory text on all dark panels.
- Preserve generous negative space. Don't stretch cards into a dense dashboard.
- Use stable grids/positioned sections, not an inaccessible giant canvas. At the desktop reference ratio, alignment should visually match the screenshots.
- Fonts must load locally or reliably under their licenses, including a tested CJK fallback. Do not leave Chinese glyphs missing.
- Optimize delivery copies of background images while retaining original PNGs. Never crop the guide's face or cover text with her image.

## Base prompt for OpenDesign
```text
Reconstruct the attached FolkVerse China UI with maximum visual fidelity. This is not a redesign. Use the exact provided background PNGs and transparent AI guide girl. Retain museum lighting, warm ivory serif headings, gold accents, translucent blue-black glass, thin gold borders, rounded tabs and spacious art composition. Do not replace these with a generic dashboard.

Produce 1600×900 desktop frames and 390×844 responsive frames for the requested screen. Keep text, fields, navigation, cards, controls and graphs as separate design components above the background. Use app tabs Explore, Journey, Stories, Lens, Guide, My DNA, plus logo-to-home and EN/ZH. No business-deck navigation, deadlines, financial charts or slide numbers.

Supply tokens, layer names and component states: selected, focus, empty, loading and error. Preserve asset filenames. Export preview frames and editable source/code only where this OpenDesign environment actually supports it. Return the component-to-asset mapping.

The screenshot's recognition percentages are fictional: retain the glass layout but design candidate/unknown states without invented probabilities. Folklore DNA is editable interests, not ancestry. A generated map is decoration, not reviewed geographic geometry. Design an operational map/list layer with accurate reviewed region data.
```

## Screen prompts — append one to the base prompt
1. **Home:** Match `01_home.png`; journey/story/lens cards have equal widths and guide is wider. Keep upper scene spacious. All card actions navigate to real features. No unrelated marketing sections above the fold.
2. **Explore:** Match `02_explore.png`; left filters and lower-right region card. Region search, theme selection and accessible equivalent list work together. Provide a separate reviewed geometry layer. Without approved geometry, show the illustrative scene label and functional region list; do not trace generated borders.
3. **Journey:** Match `03_journey.png`; gold numbered stops, wide route card, preferences and language controls. Add duration, remove/reorder and insufficient-content states using the same style. This is a digital learning route, not physical travel navigation.
4. **Stories:** Match `04_stories.png`; left player, chapter and two choices. Add labelled creative adaptation, captions, source drawer and restart. Audio position must reflect real media rather than the screenshot's sample timer.
5. **Lens:** Match `05_lens.png`; preserve the object stage and results glass. Add camera/upload, crop preview, known-related candidate cards, insufficient-image and unknown. Remove 86/9/5 sample probabilities. Include permission-denied and service-unavailable states.
6. **Guide:** Match `06_guide.png`; same transparent girl at right, wide chat at left, source pill and composer voice control. Add scrollable conversation, multiline input and recording/transcribing/speaking states without obscuring text.
7. **DNA:** Match `07_dna.png`; reconstruct gold graph as an actual chart with text equivalent, edit/pause/reset and recommendation reasons. Use real opted-in preferences, not hardcoded sample scores.
8. **Sources:** Match `08_sources.png`; evidence chain opens real source records, access/review dates and rights. A source drawer can open anywhere without losing the user's place.

## Responsive and motion
At 390×844 keep background, gold and glass; allow vertical scroll, stack cards and use 44px touch targets. Tabs may scroll horizontally with a visible affordance; the document itself must not overflow horizontally. Guide image moves below/beside chat without hiding the input. Verify 768×1024 and 200% zoom too.

Use 180–240ms control transitions and 280–360ms page crossfades. Keep nav stable. Optional subtle desktop parallax only; disable for reduced motion, touch scrolling and performance mode. No automatic narration or per-line click reveals. Avoid continuously animated blur. Lazy-load route scenes and preload at most the next likely scene.

## Codex design import prompt
```text
Inspect actual design/opendesign exports against docs/build-kit/references/ui. Reuse compatible components, translate interactions into accessible React, and keep exact assets and layout. If there are no exports, implement directly from reference frames. Save desktop and mobile screenshots and document every intentional deviation in docs/design-differences.md. Do not accept generic design drift merely because generated code is convenient.
```
