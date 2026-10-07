# Phase 3 evidence index — 7 October 2026

Current decision and interpretation: [final completion report](../../PHASE_03_FINAL_COMPLETION.md).

- `pilot-v5-live.json`: complete 200-question run; 192/200 scenario targets, 89/89 returned source support/citation checks. Original failures are preserved.
- `pilot-v5-corrective-first.json`: eight exposed failures after Chinese definition routing fix; not a second full pilot. Its exact subset is the eight failed IDs in the full pilot, using the same frozen v5 case metadata.
- `pilot-v5-corrective-suite.json` / `pilot-v5-corrective-final.json`: 28 exposed bilingual checks, 27/28; includes a guarded Chinese archaeology refusal. Prompt corrections were present; metadata still reports v6 because the running process predated the version-label restart. Later v7/v8 labels are not retrospectively written into this record.
- `pilot-v5-archaeology-suite.json` / `pilot-v5-archaeology-final.json`: two exposed successful archaeology checks on v7.
- `pilot-v5-editorial-suite.json` / `pilot-v5-editorial-final.json`: six actual final v8 editorial checks, all pass.
- `machine-answer-assessment.json`: hash-bound Codex assessment of actual answers for all question IDs. Selected corrections form a composite diagnostic; never a fresh final-prompt 200/200 pilot or expert gold. Human worksheets remain unscored.
- `closure-browser/`: 60 browser regressions and four decoded axe audits. Screenshot metadata refers to ignored local files; no image data is embedded.
- `live-browser-closure/live-hybrid.json`: three real browser/BFF/API/provider turns and actual inspector checks; no response interception.
- `reproduction-final-accepted.json`: final authoritative reproduction, bound to final runtime hashes. Prior `reproduction-closure.json` succeeds before final editorial prompt changes; `reproduction-accepted.json` preserves a lint failure on two overlong prompt lines, corrected before final acceptance.
- `closure-verification.json`: final tests, runtime hashes, authorized cap and complete gateway ledger usage.

Earlier `pilot-first.json`, `pilot-budget-limited.json`, `final-verification.json`, source refresh retries and reproduction iterations are historical diagnostics. The old pending cap/approval fields do not describe the final state. All failed/partial outputs are retained rather than rewritten as successes. The source audit and all-city manifest remain separate from protected human publication.
