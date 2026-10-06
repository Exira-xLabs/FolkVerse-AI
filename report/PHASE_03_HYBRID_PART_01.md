# Hybrid Phase 03 — contract alignment and delivery fixes

Date: 6 October 2026, Asia/Shanghai. Base commit: `6d6096a`.
Scope: Part 0 design/requirement alignment and Part 1 message delivery. Full hybrid Phase 03 remains in progress.

## Delivered

The original Phase 03, content rules, API specification, QA feature definition and guide documentation now acknowledge the owner-authorized hybrid direction. A versioned output design maps all eight acceptance gates and makes the distinction between conversation, evidence sections and explicitly unverified general explanation precise. Runtime schemas/generation remain restricted until their coordinated later migration; documentation does not claim they have changed.

The composer now sends on Enter, retains Shift+Enter newlines and avoids submission during IME composition. Sending no longer permanently stops after 20 turns. Visible history is bounded to 100 turns with a truncation notice and a working composer. A 60-second browser deadline covers session bootstrap and streaming, releasing pending state with a visible retryable timeout; Stop/disconnect remain distinct from timeout.

## Verification

Node 22.22.3 was used on the owner's checkout. No provider generation or quota change was needed for these checks. The existing fixed live greeting still handles `hi`.

| Check | Result and evidence |
|---|---|
| `pnpm --filter @folkverse/web typecheck` | Exit 0 |
| `pnpm --filter @folkverse/web lint` | Exit 0 |
| `pnpm build` | Exit 0; inherited host TLS-verification environment warning appeared; no TLS setting was changed by this work |
| `pnpm check:foundation` | Exit 0; nine original assets/reference copies preserved, contracts regenerate identically, 1,132 candidate/browser-output files checked for configured secrets |
| `FOLKVERSE_EVIDENCE_DIR=report/evidence/phase03-hybrid-part01 pnpm exec playwright test -c playwright.guide.config.ts` | 31 passed, exit 0; [browser results](evidence/phase03-hybrid-part01/browser-results.json) |
| `FOLKVERSE_EVIDENCE_DIR=report/evidence/phase03-hybrid-part01-extra pnpm exec playwright test -c playwright.guide.config.ts --grep 'IME confirmation\|visible history stays bounded'` | 2 additional checks passed, exit 0; [extra browser results](evidence/phase03-hybrid-part01-extra/browser-results.json) |
| Real browser → BFF → API → PostgreSQL greeting | Passed with no intercepted requests or provider calls; [result](evidence/phase03-hybrid-part01/live-greeting.json) |

The 31-check suite includes a typed `hi`, 25-turn conversation, newline/submit behavior, stalled session timeout, existing Stop/Retry, malformed/truncated streams, source withdrawal and strict publication boundaries. The two extra checks verify IME confirmation and 102 submissions with a 100-turn visible-history bound. They are controlled browser fixtures, not personality or factual-quality scoring.

Real greeting procedure: start the existing API with process-only `APP_MODE=live`, allowed origin `http://127.0.0.1:3114` and port 8014; start the built Next.js app at 3114 with the matching API base; open `/guide`, open Jinyao, type `hi`, press Enter, and wait for the rendered policy reply. Delete the temporary anonymous session afterward and stop the isolated services.

The first real check failed session creation because the test origin 3114 was absent from the API allowlist (HTTP 403); after configuring only the test process origin, the same path succeeded. The original friend's symptom remains unreproduced and is not attributed to this local test configuration. Do not weaken origin validation to make a test pass.

## Remaining work

Part 2 must implement generated, varied social conversation and bounded consented recent turns. The greeting text is still the existing fixed policy. Part 4 must migrate natural hybrid generation, output schemas, server support checks and browser validation together. No broader/general response is enabled through permissive fallback.

Province-wide source acquisition, reviewed explanatory material, representative retrieval, independent bilingual/personality assessment and full release verification remain planned in the [execution parts](../docs/phase-03-hybrid-execution-parts.md). Live factual generation and new human quality results are not established by this delivery.

Private configuration and persistent database contents are preserved. Build-generated instruction/type imports are not treated as authored source changes. No commit, push or deployment is implied by this report.
