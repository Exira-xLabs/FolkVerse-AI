# Hybrid Phase 03 — contract alignment and delivery fixes

Date: 6 October 2026, Asia/Shanghai. Base commit: `6d6096a`.
Scope: Part 0 design/requirement alignment and Part 1 message delivery. Full hybrid Phase 03 remains in progress.

**Final Part 1 update:** the initial batch was pushed as `6094a94`. The subsequent delivery-completion changes below were pushed as `d7d4d1b`; Part 1 message-delivery acceptance is complete within the stated browser/runtime scope. Generated personality and hybrid generation remain Part 2 onward.

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

Private configuration and persistent database contents are preserved. Build-generated instruction/type imports are not treated as authored source changes. The initial batch is pushed at `6094a94`; completion changes were pushed at `d7d4d1b`. No deployment was made.

## Final Part 1 checks and fixes

Popup closure now cancels the scripted-preview timer immediately, and a timer/controller guard prevents duplicate concurrent sends. Session-connect and incomplete-stream failures have specific localized recovery messages. Turn elements expose their terminal status for reliable delivery checks without displaying technical diagnostics to visitors.

The final focused suite passes **37/37**, exit 0, including the previous checks plus failed-session recovery, rapid duplicate submit with preserved follow-up draft, close/reopen while a request is pending, and a real BFF fixture stream that remains open without a terminal event. Its browser deadline produces a visible timeout and closes the upstream connection. [Final browser results](evidence/phase03-hybrid-part01-final/browser-results.json).

The reusable [real delivery script](../scripts/verify-guide-delivery.mjs) passes **9/9 checks**, exit 0: live presentation, actual EN/ZH greeting replies, released composers, preserved close/reopen history and no browser exceptions. [Actual local delivery results](evidence/phase03-hybrid-part01-final/live-delivery.json). The script does not intercept responses or change configuration and deletes its temporary session afterward. Existing social-policy replies use no provider generation; these results are not generated-personality or historical-quality evidence.

Reproduction against running local live services:

```sh
FOLKVERSE_DELIVERY_URL=http://127.0.0.1:3114 FOLKVERSE_EVIDENCE_DIR=report/evidence/phase03-hybrid-part01-final node scripts/verify-guide-delivery.mjs
FOLKVERSE_EVIDENCE_DIR=report/evidence/phase03-hybrid-part01-final pnpm exec playwright test -c playwright.guide.config.ts
```

The first command requires the API's allowed origin and web/API base configuration to match the test port. Future generated social replies may consume the configured bounded quota; the script does not authorize or expand it.

Web typecheck/lint and `env -u NODE_TLS_REJECT_UNAUTHORIZED pnpm build` pass on Node 22.22.3; the final build runs without the inherited TLS-disable environment warning. Foundation passes with identical regenerated contracts, preserved nine original assets/reference copies and 1,135 candidate/browser-output files checked for configured secrets. Whitespace validation passes. Temporary smoke-test API/web processes are stopped; the persistent database is left intact.

| Part 1 gate | Final evidence |
|---|---|
| Typed/repeated greeting delivery | Actual EN/ZH smoke and controlled 25-turn/102-turn UI scenarios |
| Sustained composer with bounded history | 102 submissions; 100 retained turns, visible truncation notice, send still enabled |
| Session/context failure recovery | Failed bootstrap sends no guide request; explicit retry succeeds; invalid-context error and token clearing retained |
| Cancellation, duplicate send, close/reopen | Pending guard, Stop/Retry, BFF cancellation and old/new reply isolation browser checks |
| Incomplete/stalled transport | Truncated/malformed publication rejection, stalled bootstrap and open upstream stream reach visible errors |
| Honest demo/live separation | Existing labelled preview regressions and live BFF demo refusal pass |

The friend's original missing-reply cause is still unproven. This acceptance covers the specified current delivery behaviors, not a claim of zero possible defects, physical-device/Safari verification, greeting variety or full Phase 03 completion.
