# UI refinement checklist

Started 5 October 2026, Asia/Shanghai. Scope: improve every displayed image's quality/delivery first, then fix the seven design issues explicitly selected by the owner. Preserve original artwork, sourced geography, reviewed content and unrelated work. Live AI backends remain their assigned phase work.

## Stage 1 — artwork and image delivery

- [x] Inventory the eight museum scene masters, guide portrait, current terrain and active thumbnail uses; preserve original hashes.
- [x] Generate and visually inspect enhanced scene versions with imagegen; preserve the established museum identity and use versioned sibling filenames.
- [x] Review guide identity/alpha and terrain detail; improve only with an output that preserves the required invariants.
- [x] Record prompts, input/output hashes, actual dimensions and generated/decorative roles.
- [x] Replace full-document cover backgrounds with bounded responsive scenes; verify sharpness, focal subjects and contrast at desktop, tablet, phone and DPR 2.
- [x] Deliver correctly sized images and focused card art without stretching; verify original asset hashes and sourced boundaries are unchanged.

## Stage 2 — selected design changes

- [x] **Home:** prominent Explore Liaoning action and reviewed collection entry; label secondary experience availability.
- [x] **All pages:** responsive scene compositions independent of document height.
- [x] **Explore:** collection easy to reach before the map/directory; usable Map/Collection choice.
- [x] **Guide:** compact mobile companion without the separate oversized portrait panel.
- [x] **Lens and demos:** visitor tasks first, scenario/prototype tools in explicit optional preview areas.
- [x] **Interests:** replace English DNA claims with cultural interests; voluntary empty/example states rather than unexplained personal scores.
- [x] **Shared design:** calmer reading/task surfaces, clear hierarchy and restrained glass.

## Verification and delivery

- [x] EN/ZH text and interactions verified on all nine screens at desktop, phone and tablet sizes.
- [x] Meaningful browser regressions, keyboard/touch checks, lint, typechecking and production build pass.
- [x] Image sharpness/composition and open/empty/demo states visually inspected; screenshots and exact limitations saved.
- [x] Final checklist/status updated and healthy local preview restored.

Mark items complete only with concrete output and verification evidence.

## Completion evidence

Completed 5 October 2026, Asia/Shanghai. [Results and limitations](UI_REFINEMENT_RESULTS.md) record the selected seven changes, image provenance, preservation checks and remaining broader audit work. Fresh lint, typecheck, production build and asset verification exit 0; [final browser run](evidence/ui-refinement/browser-final.log): **31 passed, 0 failed, 0 skipped**. The 54 EN/ZH default-layout captures and six overview sheets cover all nine screens at three sizes; open preview and labelled interest-example states are also captured and inspected. [Preview health](evidence/ui-refinement/preview-health.json) confirms web and API HTTP 200.

These checked items cover this selected refinement scope. They do not close every original audit finding or certify accessibility. Physical devices, Safari, native browser-toolbar zoom, full contrast/screen-reader testing and later live AI integrations remain unverified or assigned phase work.
