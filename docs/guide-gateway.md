# Guide provider gateway

**Push audit update:** production uses `GuideGateway` (`guide-json-v2`), with explicit DeepSeek or Ollama Cloud selection. The active user key is Ollama-issued; its endpoint, request-cap accounting and authentication diagnostic are documented in [Ollama configuration](guide-ollama.md). The DeepSeek-specific price/key requirements below apply when selecting the direct DeepSeek adapter. Original verification remains dated evidence.

Part 2, 6 October 2026 (Asia/Shanghai). The server transport and persistent admission controls are implemented. **No live AI Guide endpoint or validated cultural explanation is delivered by this part.** The Guide preview remains unchanged. [Phase sequence](phase-03-plan.md).

## Provider verification

The official [Chat Completions reference](https://api-docs.deepseek.com/api/create-chat-completion/) documents `POST /chat/completions`, `deepseek-flash` / `deepseek-v4-pro`, JSON mode, disabling thinking, output limits and usage fields. The [JSON guide](https://api-docs.deepseek.com/guides/json_mode/) requires a JSON instruction/example in the prompt and warns about empty output. The application rejects empty, malformed, duplicate-key, non-finite, truncated, tool-call and incomplete replies. The harness must supply its own schema/example and validate factual support afterward; transport JSON checks alone establish neither correct citations nor historical truth.

The [pricing table](https://api-docs.deepseek.com/quick_start/pricing/) currently lists Flash peak cache-miss input at USD 0.30/million tokens and peak output at USD 1.20/million tokens. Pro has different rates. Rates are configurable and have no automatic default. Configure reviewed **peak/cache-miss** rates to reserve conservatively regardless of caching or time of day; token counts reconcile a cost upper estimate rather than claiming the provider invoice amount. Review prices again before activation because they can change.

The [vision guide](https://api-docs.deepseek.com/guides/vision/) confirms Flash image inputs. This Part 2 adapter accepts **text only**. No media is uploaded or sent to any provider. Lens needs a separately bounded media/vision extension in its own phase. GLM is off by default and no GLM adapter/fallback exists.

## Configuration and activation

The implementation reads server-only settings from the ignored root `.env`. `.env.example` contains names/comments only. Calls require all of the following:

- `APP_MODE=live`, a nonempty `DEEPSEEK_API_KEY`, and a positive `DAILY_AI_BUDGET_USD` (default is zero).
- `DEEPSEEK_MODEL` is one of the two documented IDs; default is `deepseek-flash`.
- `DEEPSEEK_BASE_URL` is an HTTPS origin with optional `/v1`; default is `https://api.deepseek.com`. No embedded credentials, query or fragment. Redirects and inherited proxy environment are disabled. An operator-configured host is trusted server configuration, never selected by model output.
- `DEEPSEEK_PRICE_MODEL` and `DEEPSEEK_PRICE_BASE_URL` exactly match the configured model and normalized base URL; positive reviewed `DEEPSEEK_INPUT_USD_PER_MILLION` and `DEEPSEEK_OUTPUT_USD_PER_MILLION` are present.
- Migration `0003_gateway` is installed on the existing project PostgreSQL database. The shared singleton admission lock is inserted by the migration. Missing database/schema/lock fails closed before sending a request.

No credentials or activation settings were added locally. Current credentialed provider access is unverified. Both web/API now default to live when APP_MODE is missing; setup still explicitly creates demo mode. Invalid API mode configuration is rejected.

Defaults: 24,000 input-token reserve, 800 maximum output tokens, 30-second total provider-operation deadline, two concurrent attempts, six attempts per session/minute and thirty attempts globally/minute. Override the corresponding `MODEL_*` variables within validated ranges. A conservative UTF-8 byte bound plus framing allowance gates input size; actual usage exceeding configured bounds is recorded but its output is rejected. Provider/tokenizer assumptions and prices still require live verification before treating a local budget as an exact billing guarantee.

Install and verify:

```sh
uv sync --project apps/api --frozen
pnpm db:migrate
uv run --project apps/api pytest apps/api/tests/test_provider_gateway.py -q
```

A database migrated only through Phase 02 now reports an outdated schema on `/health` until `0003_gateway` is applied. PostgreSQL execution remains blocked on this machine; portable migration tests and offline PostgreSQL SQL generation pass.

## Admission, failure and accounting

`DeepSeekGateway.complete` is an internal service on `app.state.guide_gateway`. Its caller must supply an authenticated anonymous-session identity and trusted server prompt. It is not exposed as a browser endpoint. Part 3 supplies the evidence harness; Part 4 supplies owned POST/SSE and disconnect cancellation.

Before each attempt, `UsageLedger` locks a persistent singleton row, checks recent global/session attempts and active leases, and commits a worst-case cost against that UTC admission day's budget. Admission is serialized across workers sharing the database. A retry gets a separate reserve and also counts against limits. Successful reconciliation is idempotent and keeps the original admission day even across midnight. Restarting an API process does not reset totals.

There is at most one retry, with 250ms backoff, for selected transient HTTP/transport failures inside the total deadline. A provider `Retry-After` header suppresses the short automatic retry. Permanent HTTP errors, redirects, malformed output and schema/content failures are not retried. HTTP error bodies are never surfaced. The adapter requests nonstreaming JSON and bounds decoded response size to 128 KiB. No tools, model-chosen URLs or fallback provider are executed.

Missing or inconsistent usage, transport failure, cancellation and interrupted work retain the committed reserve because billing is uncertain. Valid usage reconciles even when the generated content is rejected. Cancellation closes local HTTP work and records a cancelled attempt; it cannot guarantee the remote provider stopped billing. Worker crashes retain cost and release the local concurrency slot after the deadline plus a 15-second lease margin. Database/reconciliation failure cannot produce a successful result or release an unknown bill. Cleanup may extend the operation deadline by bounded database work.

## Stored data and limits

The ledger stores attempt ID, UTC admission day, model, start/lease times, status, conservative charged amount, validated token counts and attempt latency. It stores no prompt, evidence, question, answer, API key, raw provider response or raw session ID. Session rate keys are HMAC pseudonyms using the server session secret.

Expired rate pseudonyms and attempt details older than seven days are removed on successful admission; `UsageLedger.prune()` also supports explicit maintenance. Daily aggregate totals remain. This is lazy maintenance, not a guaranteed wall-clock deletion deadline during inactivity or prolonged outages. Part 4 must wire lifecycle maintenance alongside service operation. Conversation storage is not introduced by these metering records.

Attempt latency is measured, including the HTTP/read/parse stage, and excludes preceding retrieval. It is **not first meaningful answer latency**; Part 4 must measure validated answer publication separately.

Portable tests use SQLite writer transactions and mocked HTTP. They verify algorithmic admission, persisted totals, cancellation and failure paths; they do not certify PostgreSQL row-lock behavior under production load, real billing, mainland-China network access or model answer quality.

Part 4 update, 6 October 2026: the API lifespan now calls ledger maintenance every 60 seconds and the owned SSE/UI measure checked-content emission/receipt separately from progress. Outages still prevent guaranteed wall-clock deletion. Real PostgreSQL maintenance remains unverified. [Transport contract](guide-live.md).
