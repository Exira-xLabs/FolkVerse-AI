# Phase 07 — Folklore DNA, recommendations and user control

**Prerequisite:** Published exhibits, owned session state and completed main flows.

**Outcome:** Editable interests influence transparent recommendations without sensitive inference.

## Paste into Codex
```text
Read docs/build-kit/00_MASTER_CODEX_PROMPT.md and docs/build-kit/phases/07_DNA_RECOMMENDATIONS.md. Inspect the repository and docs/build-status.md. Implement the following phase, preserving approved UI and unrelated work.


Build profile/topic, recommendations and deletion endpoints. Explicit interests work without passive tracking. Behavioral signals require opt-in; use save/like/completion intentionally, never interpret long dwell as automatic approval. Start with deterministic transparent weights, novelty and regional/theme diversity, with documented tie-breaking.

Reconstruct the original DNA glass panel and gold chart as real data visualization. Show an empty introduction when no preferences exist. Include text alternative, edit, pause learning, less-like-this and reset. State that Folklore DNA is cultural interests, not ethnicity or ancestry. Avoid inferred sensitive identity.

Every recommendation references a published exhibit and has a human-readable reason: selected theme, saved topic or new region. Source revocation removes recommendations too. Saved exhibits and user choices survive reload in the intended session. Implement account/session deletion, profile reset and consent revocation with appropriate distinct effects; don't silently retain supposedly deleted preference events.

Wire the complete loop: explore → exhibit → journey → guide/source → story or scan → save → updated recommendation. Fix broken context and keyboard transitions without redesigning screens.


Update docs/build-status.md with actual results, blockers and the next phase. Report what is live, fixture-driven, untested or unavailable. Do not claim completion unless the gates below are met.
```

## Acceptance gates

- [ ] Opt-out users generate no behavioral tracking events.
- [ ] Reset clears derived scores/events as specified; delete removes owned personal data.
- [ ] Chart values reflect actual preferences, never screenshot samples.
- [ ] Recommended items are eligible, diverse where corpus permits, and explained.
- [ ] Cross-session reads/updates fail; anonymous basic exploration still works.


## Handoff
Scoring rule, privacy tests and recording of one complete visitor loop.
