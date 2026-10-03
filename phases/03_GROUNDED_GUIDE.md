# Phase 03 — DeepSeek gateway and sourced cultural guide

**Prerequisite:** Phase 02 has approved passages; server credentials available for live checks.

**Outcome:** Evidence-grounded English/Chinese answers with real citations and honest failures.

## Paste into Codex
```text
Read docs/build-kit/00_MASTER_CODEX_PROMPT.md and docs/build-kit/phases/03_GROUNDED_GUIDE.md. Inspect the repository and docs/build-status.md. Implement the following phase, preserving approved UI and unrelated work.


Implement provider adapter and inspect current DeepSeek official model/vision/JSON docs. Configure base URL/model through environment. No browser SDK with secret credentials. Default GLM off. Add timeouts, at most one bounded retry for transient failures, cancellation, server rate limits, concurrency and daily budget checks. Meter usage without storing raw private content unnecessarily.

Implement a lexical retrieval baseline, then BGE-M3 embeddings with model/corpus version metadata and hybrid ranking. Benchmark local runtime; batch corpus embedding offline. Query embedding still needs compute. Handle unavailable local model explicitly; label lexical-only mode. Retrieve only approved passages in the user's language or source-preserving translation workflow.

Build /guide and persistent source drawer using the runtime template. Validate returned IDs against retrieved bundle and related IDs against published exhibits. Unsupported questions produce insufficiency, not plausible invented answers. Source disagreements are attributed. Model output cannot grant tools or access arbitrary URLs.

Use fetch SSE: send progress while generating and only validated answer segments afterward. Track actual first meaningful content latency separately from progress. Keep fixed recorded demos labelled. Provider failure in live mode is unavailable, not fallback success. Connect chat context, follow-up language simplification and source inspect controls.


Update docs/build-status.md with actual results, blockers and the next phase. Report what is live, fixture-driven, untested or unavailable. Do not claim completion unless the gates below are met.
```

## Acceptance gates

- [ ] A real credentialed call is tested if authorized credentials exist; otherwise explicitly unverified.
- [ ] Supported and unsupported questions behave differently in both languages.
- [ ] Invented citation IDs are rejected; source-injected instructions do not change policy.
- [ ] Revoked passages stop being retrieved; model timeout/cap exhaustion show honest errors.
- [ ] Keys never reach browser/logs; source drawer shows actual evidence.


## Handoff
Small dated grounding test set, actual usage/latency and provider/corpus/prompt versions. Do not claim the report’s 95% target without a scored sample.
