# Phase 03 handoff — 6 October 2026

Jinyao now works through actual PostgreSQL and Ollama in English and Chinese, with owned
sessions, checked SSE, current source inspection, consented follow-ups and honest coverage
limits. **Phase 03 remains partial.** Broader approved knowledge, classified explanation units,
representative hybrid relevance and independent bilingual/personality review remain required.
The [current report](../report/PHASE_03_COMPLETION.md) records the evidence and exact checks.

## Current implementation

| Responsibility | Implementation |
|---|---|
| Reviewed corpus, rights and publication eligibility | `content.py`, `guide_retrieval.py` |
| Pinned offline CPU BGE, versioned indexes and hybrid ranking | `guide_embeddings.py`, `embedding_worker.py`, `guide_index.py`, `guide_hybrid.py` |
| Ollama/direct DeepSeek JSON gateway and shared bounded usage | `provider_gateway.py`, `gateway_limits.py`, migration `0003_gateway` |
| Exact claim support, bounded inventory explanations, signed context | `guide_harness.py`, `guide_personality.py` |
| Versioned social personality and browser display validation | `packages/contracts/src/jinyao-policy.json`, web `guide-stream.ts` |
| Owned JSON/SSE and page-memory Messenger lifecycle | `guide_api.py`, web guide BFF and `jinyao-chat.tsx` |
| Dated functional evaluation and unscored human worksheets | `guide_evaluation.py`, `guide_review.py`, v1/v2 suites and live-review script |

## Original acceptance gates

| Gate | Current evidence / remaining limit |
|---|---|
| Real credentialed call | PASS for bounded Ollama EN/ZH browser calls; actual attempts, tokens and latency recorded |
| Supported versus unsupported, both languages | PASS within one reviewed bilingual listing; ambiguity requests clarification |
| Invented IDs / source instruction attacks | Portable harness, API and browser fault regressions; no unchecked raw model prose published |
| Revocation / timeout / cap errors | Real PostgreSQL committed withdrawal/shared limits; injected provider timeout/cancellation regressions are labelled separately |
| Keys server-side / actual source drawer | Real source inspector and configured-secret checks; no deployment or credential publication |
| Dated expert-guide evaluation | PARTIAL: new functional development set passes; human correctness, clarity, faithfulness and personality remain unscored |
| History / interpretation / folklore / chronology | PARTIAL: source statements remain attributed, unsupported upgrades rejected; new explanatory drafts need review and classified support |
| Follow-up glossary / meaningful depth / simplification | PARTIAL: lossless listing simplification and language/depth controls work; glossary and broader explanations are honest coverage gaps |

The [coverage matrix](guide-coverage.md) describes the single published Liaoning exhibit.
Fuzhou / 复州 here means Wafangdian, not the Fujian city 福州. No province mismatch or new
editorial approval is inferred. The new explanation packet and the earlier 16 candidates stay
draft. Source-level approval does not approve additional wording or translations.

## Reproduce locally

Use Node 22 and the locked pnpm/Python dependencies. On this checkout the project-local
runtime is `.local/runtime/node-v22.23.3-linux-x64/bin`.

```sh
export PATH="$PWD/.local/runtime/node-v22.23.3-linux-x64/bin:$PATH"
pnpm db:up
pnpm db:migrate
```

If the daemon's image pull still fails while the user proxy works, use the verified local-image
recovery instead; it changes no daemon settings and preserves the pinned source identity:

```sh
uv run --project apps/api python scripts/pull-database-image.py
docker load --input .local/pgvector-image/image.tar
docker compose -f compose.yaml -f .local/compose-proxy.yaml up -d --wait db
pnpm db:migrate
```

Restore only a fresh empty content database. This checkout is already restored; do not seed
or overwrite it. `restore-manifest` deliberately refuses nonempty content tables.

For the authorized bounded local live preview, use two terminals:

```sh
APP_MODE=live OLLAMA_DAILY_REQUEST_LIMIT=24 MODEL_RATE_LIMIT_PER_MINUTE=20 MODEL_MAX_OUTPUT_TOKENS=1200 pnpm dev:api
APP_MODE=live API_BASE_URL=http://127.0.0.1:8000 pnpm dev
```

These overrides do not edit `.env` or change deployment budgets. Attempts persist in the
UTC daily ledger, including failures; a restart does not reset the cap. The configured provider
key stays in the ignored root configuration. Other later features still have unavailable live
states. See [Ollama configuration](guide-ollama.md).

Walkthrough: open `/guide`, open Jinyao, enable topic-context consent, ask “Where is Fuzhou
shadow puppetry listed?”, inspect sources, ask “Explain that simply”, “Go deeper”, “Say that in
Chinese”, then ask an unsupported origin-year question. Close/reopen preserves page history.
The real controlled outage/recovery script starts isolated local services and stops them afterward.

```sh
node scripts/verify-guide-live.mjs
OLLAMA_DAILY_REQUEST_LIMIT=24 node scripts/verify-guide-recovery.mjs
uv run --project apps/api python scripts/prepare-guide-live-review.py
```

Both verification scripts may consume the explicit bounded live quota. Ordinary regression
checks use isolated faults and do not exhaust an actual account's quota.

## Next required work

1. Obtain named human content/rights/translation review for the explanation packet. Implement
   and independently evaluate classified reviewed explanation units before broader publication.
2. Have independent bilingual reviewers assess the recorded actual answers and personality
   using the bound worksheet. Pending fields are not passing scores.
3. Keep v2's 24 reserved cases unexecuted until independent target review and final evaluation.
   Neither v1's exposed score nor v2's machine-authored development score proves 95% quality.
4. Expand reviewed relevance data before assessing hybrid gains. BGE now runs, but the
   two-passage/six-query diagnostic is too small and cold queries are slow on this host.
5. Check native browser zoom, Safari, physical devices, assistive technology and pitch network.
   CSS zoom and Chromium emulation do not certify those environments.

Earlier intermediate blockers are preserved in the dated Part 1–6 and push-audit reports.
The current report supersedes their unavailable database/provider/BGE statements for this
checkout. No Phase 04 acceptance or public deployment is implied.
