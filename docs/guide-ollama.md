# DeepSeek through Ollama Cloud

Current integration update (6 October 2026): actual PostgreSQL and bounded Ollama EN/ZH
browser generation now pass; pinned BGE CPU inference/indexing is measured. The root
configuration remains demo/zero quota; live verification uses process-only bounded settings.
[Current report](../report/PHASE_03_COMPLETION.md), [personality policy](jinyao-personality.md),
[coverage](guide-coverage.md) and [handoff](phase-03-handoff.md) supersede earlier unavailable
integration statements below. Broader classified explanations and independent human quality
remain pending. Beginner/deeper presentation uses a lossless inventory grammar; exact
reviewed claims, attribution, revocation and browser publication validation remain enforced.


The active user-supplied credential is issued by **Ollama**, not DeepSeek's own platform. The earlier DeepSeek `/models` 401 responses resulted from sending that credential to the wrong provider. The push audit verifies Ollama authentication using an intentionally absent model: the saved key reaches model lookup (404), while an invalid control key fails authentication (401). No successful generation is needed for that diagnostic.

The adapter uses Ollama's documented hosted compatibility endpoint, `https://ollama.com/v1/chat/completions`, JSON mode and `reasoning_effort=none`. Model identifiers come from the current `https://ollama.com/api/tags` catalog; the audit found `deepseek-v4.1-flash`. See [Ollama's compatibility documentation](https://github.com/ollama/ollama/blob/main/docs/api/openai-compatibility.mdx) and [authentication documentation](https://github.com/ollama/ollama/blob/main/docs/api/authentication.mdx).

## Configuration

Store these settings only in ignored `.env`:

```dotenv
GUIDE_PROVIDER=ollama
OLLAMA_API_KEY=your_private_ollama_key
OLLAMA_BASE_URL=https://ollama.com/v1
OLLAMA_MODEL=deepseek-v4.1-flash
OLLAMA_DAILY_REQUEST_LIMIT=0
```

The existing key was migrated privately to `OLLAMA_API_KEY`, with a mode-600 backup under ignored `.local/config-backups`. `DEEPSEEK_API_KEY` was cleared to avoid routing the Ollama key to DeepSeek again. Demo mode and a zero Ollama request limit continue to disable generation. Actual live use requires `APP_MODE=live`, a deliberate positive daily request cap, a healthy migrated PostgreSQL database with current approved evidence, and a fresh API process. These activation settings were not changed by the audit.

Ollama uses shared **request quota admission**; no token USD price is invented for account/subscription usage. All admitted attempts, including retries and failed attempts, count toward the UTC daily cap. The existing per-session/global minute limits and concurrency lock still apply. The ledger stores zero monetary reservation for these attempts, but this does not mean that the service or subscription is free. Evaluation reports actual token usage when available, unknown usage separately, and no inferred USD cost. `DAILY_AI_BUDGET_USD` remains the monetary gate for the direct DeepSeek adapter.

Selecting `GUIDE_PROVIDER=deepseek` retains the original DeepSeek endpoint/model/key and exact configured price-binding gates. Credentials never fall back between providers. Ollama URLs are restricted to the official cloud endpoint, so an Ollama key cannot be silently sent to a different service. Local Ollama servers are outside this cloud configuration.

## Verify

```sh
uv run --project apps/api python -m folkverse.guide_doctor
pnpm test:guide
pnpm test:secrets
pnpm check:foundation
```

The doctor prints only provider, public endpoint/model, configuration gates and HTTP statuses. Catalog availability alone does not certify authentication. An accepted key does not certify a successful JSON completion, real historical quality, PostgreSQL integration or first meaningful SSE latency; those remain separate checks.

See the [push audit report](../report/PHASE_03_PUSH_AUDIT.md) and [phase handoff](phase-03-handoff.md).
