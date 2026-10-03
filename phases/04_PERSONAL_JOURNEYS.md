# Phase 04 — Personalized digital journeys

**Prerequisite:** Approved exhibits and Phase 03 model gateway.

**Outcome:** Editable routes constrained to real exhibits and available learning time.

## Paste into Codex
```text
Read docs/build-kit/00_MASTER_CODEX_PROMPT.md and docs/build-kit/phases/04_PERSONAL_JOURNEYS.md. Inspect the repository and docs/build-status.md. Implement the following phase, preserving approved UI and unrelated work.


Implement POST/PATCH journeys from the contract. Select eligible exhibit IDs deterministically using chosen themes, region, language, time and novelty. Calculate duration from stored estimates, not invented model values. The LLM explains selected stops; it cannot add IDs or physical transport routes.

Connect duration/theme controls and route cards to API. Users can remove/reorder/regenerate with immediate total recalculation. Keep the original wide gold route visual. Save owned journeys to the database and support reload. If the corpus is too small, return fewer stops with an explicit explanation. Regenerate need not make a paid call when the result hasn't changed.

Start recommendation logic with explicit preferences, no passive tracking. Add source links from every stop and preserve guide context when entering from an exhibit. Distinguish additional region examples in decorative art from actually published scope.


Update docs/build-status.md with actual results, blockers and the next phase. Report what is live, fixture-driven, untested or unavailable. Do not claim completion unless the gates below are met.
```

## Acceptance gates

- [ ] Every stop resolves to a published exhibit; all totals obey requested time.
- [ ] Empty/too-small corpus, duplicates and removed/unpublished exhibits handled.
- [ ] Reorder/remove persists per session and never edits another session’s route.
- [ ] UI remains visually faithful while controls work at desktop/mobile sizes.


## Handoff
Route constraint tests, ownership checks and a complete map-to-journey-to-guide example.
