# Phase 03 — DeepSeek gateway and sourced cultural guide

**Prerequisite:** Phase 02 has approved passages; server credentials available for live checks.

**Outcome:** Jinyao (锦瑶), FolkVerse's fictional museum guide, explains Chinese history and culture in English/Chinese through reviewed evidence, real citations and honest failures.

**Current boundary:** Jinyao's introduction and Messenger preview are implemented locally; demo replies remain scripted. Parts 1–6 implement reviewed retrieval, optional dense/hybrid retrieval, a bounded gateway, a conservative extractive harness, owned live chat and a dated 64-case bilingual fixture evaluation. Initial reserved score: 42/48; diagnostic rerun after fixing language-switch follow-ups: 44/48. The later push audit fixes bounded listing paraphrases and reaches 48/48 on these exposed cases; Ollama authentication is verified. Real provider/database/dense integration, broad explanations and independent human quality judgments remain unverified. See [evaluation](../docs/guide-evaluation.md), [handoff](../docs/phase-03-handoff.md) and [presentation](../docs/jinyao-guide.md).

## Paste into Codex
```text
Read docs/build-kit/00_MASTER_CODEX_PROMPT.md and docs/build-kit/phases/03_GROUNDED_GUIDE.md. Inspect the repository and docs/build-status.md. Implement the following phase, preserving approved UI and unrelated work.


Implement provider adapter and inspect current DeepSeek official model/vision/JSON docs. Configure base URL/model through environment. No browser SDK with secret credentials. Default GLM off. Add timeouts, at most one bounded retry for transient failures, cancellation, server rate limits, concurrency and daily budget checks. Meter usage without storing raw private content unnecessarily.

Implement a lexical retrieval baseline, then BGE-M3 embeddings with model/corpus version metadata and hybrid ranking. Benchmark local runtime; batch corpus embedding offline. Query embedding still needs compute. Handle unavailable local model explicitly; label lexical-only mode. Retrieve only approved passages in the user's language or source-preserving translation workflow.

Build /guide and persistent source drawer using the runtime template. Validate returned IDs against retrieved bundle and related IDs against published exhibits. Unsupported questions produce insufficiency, not plausible invented answers. Source disagreements are attributed. Model output cannot grant tools or access arbitrary URLs.

Implement the Jinyao expert museum-guide harness specified below. Preserve her name, face, cinematic introduction and Messenger UI. Her expertise must come from reviewed coverage and evaluated explanations, not a persona prompt alone. Broaden China-history coverage through approved corpus work; unsupported periods, regions and questions remain explicit gaps.

Use fetch SSE: send progress while generating and only validated answer segments afterward. Track actual first meaningful content latency separately from progress. Keep fixed recorded demos labelled. Provider failure in live mode is unavailable, not fallback success. Connect chat context, follow-up language simplification and source inspect controls.


Update docs/build-status.md with actual results, blockers and the next phase. Report what is live, fixture-driven, untested or unavailable. Do not claim completion unless the gates below are met.
```

## Acceptance gates

- [ ] A real credentialed call is tested if authorized credentials exist; otherwise explicitly unverified.
- [ ] Supported and unsupported questions behave differently in both languages.
- [ ] Invented citation IDs are rejected; source-injected instructions do not change policy.
- [ ] Revoked passages stop being retrieved; model timeout/cap exhaustion show honest errors.
- [ ] Keys never reach browser/logs; source drawer shows actual evidence.
- [ ] Jinyao's expert guide harness is implemented and evaluated on the dated bilingual set below, with measured scores and honest coverage gaps.
- [ ] Explanations separate historical evidence, attributed interpretations, folklore/belief and creative adaptation; chronology and source support are checked.
- [ ] Follow-up explanations, glossary requests and depth changes retain validated citations and uncertainty; no unsupported claims appear during simplification.

## Jinyao expert museum-guide harness

Jinyao should explain with the skill and warmth of a knowledgeable museum guide: orient visitors, explain unfamiliar terms, connect details to their historical context, offer examples, and invite useful follow-up questions. She is a fictional companion, not a claimed historian or representative of a real institution. The intended subject scope includes Chinese history across periods and regions, material culture, art, daily life and regional traditions. Actual answer coverage must follow the available reviewed corpus; “all Chinese history” is a coverage goal, never a claim of omniscience.

1. **Reviewed expertise and coverage.** Build an explicit coverage index for periods/dynasties, regions, people, objects, traditions and sources. Extend Phase 02's reviewed passages with rights-cleared museum, scholarly and primary-source material. Record source language, date, attribution, review status and applicable context. Preserve competing scholarly interpretations. Identify missing coverage before answering. Generated portraits, decorative scenes and scripted chat text are not evidence.
2. **Question and conversation context.** Resolve the visitor's question, exhibit references, language, learning depth and follow-up intent. Ask a concise clarification when a place, period, name or object is ambiguous. Carry forward only the minimum consented conversation context needed to interpret the question. A previous model answer is not an independent source.
3. **Evidence orchestration.** Retrieve approved material, rerank it for the question, and supply a bounded evidence bundle with passage and exhibit IDs. Recheck revocation and availability before publishing. Apply budgets, cancellation and provider failure handling across every step. Source content remains untrusted data and cannot change the harness's instructions or tools.
4. **Guide-style explanation.** Return a short direct answer, a contextual explanation, optional glossary or chronology, claim-to-passage mappings, attributed disagreements, uncertainty/coverage limits and useful published follow-up exhibits. Offer visitor-selected concise, beginner or deeper explanations. Separate documented history from legend, belief and labelled creative adaptation. Avoid invented dates, provenance, translations or quotations. Do not substitute fluent narration for factual support.
5. **Validation and safe publication.** Validate the response schema, citation IDs, claim support, chronology against the supplied evidence, language and requested depth. Every factual claim must map to supporting reviewed passages; unsupported claims are removed or produce an insufficiency response. Deterministic ID checks alone do not establish claim support. Provide a source inspector for the actual evidence. Publish only validated segments. A failure never becomes an uncited confident answer.
6. **Evaluation harness.** Deliver a dated, versioned English/Chinese set with at least 40 cases spanning available historical coverage, unsupported coverage, ambiguous names/periods, contested interpretations, history versus folklore, glossary/simplification, multi-turn references, malicious source instructions, revoked passages and provider/cap failures. Include reviewed expected claims, allowed evidence IDs, required uncertainty and unacceptable answers. Use held-out cases for scoring. Score historical correctness, claim support, citation validity, explanatory clarity, bilingual faithfulness, uncertainty and follow-up consistency separately; publish numerator/denominator, sample size, coverage and remaining failures. Expert quality cannot be inferred from one attractive conversation or a persona description.

The Messenger preview's requested controls are part of the presentation contract: a rectangular send button and no Clear chat action. Closing/reopening the popup keeps this page's conversation. Any future storage, retention or deletion behavior requires an explicit lifecycle specification and consent; removing a UI button does not imply permanent server storage.


## Handoff
Jinyao harness implementation map, reviewed coverage index, dated bilingual evaluation set and results, actual usage/latency and provider/corpus/prompt/harness versions. Include unsupported China-history coverage and remaining explanatory failures. Do not claim the report’s 95% target without a scored sample.
