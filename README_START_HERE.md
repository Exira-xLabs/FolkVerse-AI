# FolkVerse China — 华韵 AI: Codex build kit
Prepared 29 September 2026. Based on the current 33-page business plan (version 3.0), eight-slide competition deck, original eight app UI screens, and the supplied competition notice.

## Start in this order
1. Extract the entire ZIP. Keep assets, references, specs and phases together.
2. Read [the master prompt](00_MASTER_CODEX_PROMPT.md) and [the OpenDesign handoff](01_OPENDESIGN_UI_PROMPTS.md).
3. Upload `references/ui/01_home.png`, `02_explore.png`, `06_guide.png`, their corresponding backgrounds, and the guide PNG to OpenDesign. Use the base prompt, then each screen prompt. Don't ask for a redesign.
4. Save OpenDesign exports under `design/opendesign/` in your repository. Request desktop/mobile frames, tokens and component states. Export code or editable design source only if your OpenDesign product supports it; this kit assumes no particular OpenDesign API.
5. Open the intended repository in Codex. Copy this whole kit into `docs/build-kit/`. Paste the master prompt once, then the prompt in [Phase 00](phases/00_FOUNDATION.md). Continue in numerical order.
6. Codex can start directly from the provided screenshots while OpenDesign exports are pending. Keep the same visual target.
7. Check each phase's acceptance gates and `docs/build-status.md` before continuing.

This is an implementation specification and prompt package, not a completed application. The complete plan is ambitious for eleven days; its fallback paths preserve a credible small demo without inventing implementation results.

## Visual source of truth
`references/ui/` contains the original app screens used in the report. These define the app. `references/business/` is the latest competition deck: palette and glass reference only. Its Vision/Value/Business tabs, deadlines and financial charts are not app pages. The app uses **Explore, Journey, Stories, Lens, Guide, My DNA**, with logo linking home and Sources as a supporting page/drawer.

Build actual React controls and charts over the supplied backgrounds, never a screenshot pretending to be an app. Match desktop at 1600×900; mobile is a specified responsive adaptation. Honest scan states, accurate geography and accessibility take precedence over copying conceptual false percentages or inaccurate map boundaries.

## Scope and schedule
- **30 September:** document submission deadline. No completed app is promised by tomorrow.
- **1–10 October:** official preliminary review and proposed internal development period.
- **10 October:** internal demo/rehearsal target, not submission deadline.
- **11–18 October:** finals if selected, 5-minute pitch plus 3-minute Q&A.
- First prototype target: one region, ten reviewed exhibits, thirty eligible artifact records, one small branching story, Chinese/English, connected visitor loop.
- Later pilot: three regions, thirty exhibits, three hundred artifact records. Counts never justify invented content.
- The museum artifact catalog is distinct from the regional traditions corpus. Do not relabel Chinese ceramics as Shaanxi artifacts without provenance evidence.

## Team
Oualid Drib; Soufiane Kahfi; Achraf Ouazzani Chahidi; Nguyen Tri Dung. Agree owners for UI, backend/AI, content/rights and evaluation/demo. No individual role or credential is assumed.

## Package map
| File/folder | Purpose |
|---|---|
| `00_MASTER_CODEX_PROMPT.md` | Persistent project brief and first paste |
| `01_OPENDESIGN_UI_PROMPTS.md` | Tokens, asset mappings, exact layouts, screen prompts |
| `specs/ARCHITECTURE_AND_COSTS.md` | Repo, deployment and low-cost choices |
| `specs/DATA_AND_API_CONTRACTS.md` | Models, endpoints, schemas and states |
| `specs/CONTENT_AND_AI_RULES.md` | Curation and application runtime prompts |
| `phases/00_...` through `08_...` | Nine sequential coding prompts |
| `QA_AND_DEMO.md` | Test plan, visual gates and pitch rehearsal |
| `SOURCES_AND_TRACEABILITY.md` | Report coverage and official sources |
| `assets/ASSET_MANIFEST.json` | Original asset dimensions, hashes and roles |
| `references/` | Source report/deck PDFs and app screenshots |

## What you supply
A repository, server-side DeepSeek API credentials at Phase 03, optional live voice credentials at Phase 06, and actual human content review decisions. Never paste API keys into OpenDesign, prompts or browser code. This kit authorizes local implementation tasks, not buying hosting, publishing a site or uploading passports.
