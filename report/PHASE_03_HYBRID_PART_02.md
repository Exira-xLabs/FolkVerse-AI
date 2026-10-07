# Phase 03 hybrid — Part 2 delivery report

Date: October 6, 2026. Personality, English/Chinese handling and bounded consented conversation context are implemented and locally verified. This is a Part 2 engineering delivery, not completion of the whole Phase 03 or the province-wide content program.

Previous Part 1 delivery was pushed to `main` as `d7d4d1b`. This Part 2 work is local and has not been pushed or deployed. [Runtime contract and limits](../docs/guide-personality-and-context.md).

## Implemented behavior

- Shared bilingual fictional AI companion policy with varied openings and invitations. One checked invitation after a greeting; thanks/goodbye/identity do not force a question. The real model selects valid phrase IDs; server and browser reconstruct the exact reply. This is constrained model composition, not unrestricted prose generation.
- Unknown messages can use a metered whole-message routing/composition call. Its cultural branch cannot supply factual text and cannot grant evidence authority. Typos/emoji and mixed greeting/factual requests have conservative direct routes; understood cultural requests retain evidence and scope checks. Classification mistakes remain possible.
- Explicit Automatic/English/Chinese controls, text-based language detection, quoted-name handling, whole-message language overrides and polite simpler/deeper follow-ups. Referenced cultural follow-ups resolve through owned exhibit/evidence scope and current source checks.
- Recent conversation is opt-in, at most six completed pairs/8,000 characters, with an additional browser 12,000-byte history bound to reserve provider input room. Server validators reject unconsented, incomplete, oversized or extra-role input. Turning consent off clears the topic token and sends no recent turns on the next request.
- Both API and BFF enforce a 64 KiB encoded request boundary. Signed topic references still expire in 30 minutes, keep owner/evidence version checks and are not renewed by social replies. Current question/provider/history/visible transcript limits remain separate.
- Updated disclosure covers social messages as well as cultural requests. Application raw history remains page-only and is not stored in the database/logs; provider processing is separately governed by its policies. Service failures stay visible, including failed greetings.

## Verification

| Check | Result |
|---|---|
| API suite | 330 passed; one existing Starlette TestClient deprecation warning |
| Python lint and strict type checking | Passed |
| Web lint/type checking/production build | Passed |
| Browser fixtures | 42 passed, including existing demo/delivery/cancellation/source regressions and new language/context/publication checks |
| Actual local browser → BFF → API → DeepSeek | Eight successful replies, 51 checks, no browser exceptions; no substituted responses |
| Actual reviewed evidence follow-ups | EN beginner → ZH beginner → EN deeper, three checked model replies, current reviewed source attached |
| Foundation/asset/contract/secret checks | Passed; OpenAPI/types regenerate identically, nine original assets preserved, configured secrets absent from candidate/browser output |
| Diff whitespace | Passed |

[Browser fixture results](evidence/phase03-hybrid-part02/browser-results.json), [live conversation](evidence/phase03-hybrid-part02/live-conversation.json), [live source follow-ups](evidence/phase03-hybrid-part02/live-evidence-followups.json), [content-free model usage](evidence/phase03-hybrid-part02/live-usage.json).

The live walkthrough covers initial/repeated greeting, consented non-repetition, automatic Chinese, an explicit English preference, context opt-out, thanks/goodbye, and unfamiliar EN/ZH small talk. It observes a clone of the original browser fetch response because Chromium's consumed SSE body is unavailable through Playwright `response.text()`; the upstream response is returned unchanged. Captures contain only controlled test messages/replies and sanitized check/usage metadata, without keys, session cookies or context tokens.

The eight final browser requests correspond to eight completed `deepseek-flash` ledger attempts: 4,936 prompt tokens and 227 completion tokens; $0.0017532 at configured conservative rates. This is local accounting, not a verified provider invoice and not the total of all diagnostic calls in this work session.

## Real-model findings and corrections

The first unknown-message route produced an extra `type` key. The strict schema rejected it and displayed recovery rather than unchecked text. Explicit four-field JSON examples corrected the observed prompt ambiguity; the final EN/ZH unknown-message sample passed. This does not prove that future provider output will always conform: malformed/extra/missing fields continue to fail closed.

Two older fixtures assumed that English text always replied in Chinese when the page was Chinese, and that the body limit was still 16 KiB. They now test the approved language behavior and 64 KiB boundary. A foundation fixture now sets its demo mode explicitly, preserving meaningful demo/live cookie-isolation tests independently of local configuration.

## Local setup and remaining work

The owner supplied the direct DeepSeek key in ignored `.env`. Authentication/model catalog checks succeeded. Local configuration now uses live mode, `https://api.deepseek.com`, API model `deepseek-flash` (V4.1 Flash), bound peak cache-miss pricing and a $0.10 daily test cap. Ollama Cloud remains the intended production provider; no Ollama credential or final production provider test was added. See [official pricing/model names](https://api-docs.deepseek.com/quick_start/pricing).

Verification used isolated API port 8014 and web port 3114 with matching allowed origin and a process-only 20-per-minute test admission setting. Normal configured rate limits were not raised. Temporary verification services are stopped afterward; the existing database is preserved. Start normal local services with `pnpm dev:api` and `pnpm dev` to use the configured live guide.

Part 3 still needs the Liaoning source/inventory/review pipeline and all-city launch accounting. Part 4 still needs broader cultural interpretation, supported natural explanations and visibly qualified general knowledge. This delivery does not add source coverage, turn an inventory listing into history, verify general model knowledge, or establish a competition-ready release. Fresh held-out/human quality evaluation and final target-provider/load/device verification remain later gates.
