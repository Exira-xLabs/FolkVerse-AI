# Phase 03 Part 2 — provider gateway and limits

6 October 2026, Asia/Shanghai. **Implementation and portable tests delivered. Credentialed provider and PostgreSQL integration remain unverified. Phase 03 is incomplete.**

## Result

The existing FastAPI service now owns a server-only DeepSeek JSON transport with timeout/cancellation and at most one transient retry. Persistent PostgreSQL admission serializes per-session/global rate checks, shared concurrency leases and UTC daily budget reservations. Valid returned usage reconciles conservatively; unknown bills retain their committed reserves. No Guide endpoint, chat storage, vision request, additional provider or raw answer publication is introduced.

Official model/API, JSON, vision and pricing documentation was inspected. [Implementation and official references](../docs/guide-gateway.md). The current model defaults to `deepseek-flash`, while the two documented model IDs remain configurable. Current local configuration has **no DeepSeek credential**, no positive provider budget and no running project database. No credentialed or paid call was made, and no credentials were added.

## Changes

- `apps/api/src/folkverse/provider_gateway.py`: bounded nonstreaming JSON requests, documented thinking switch, sanitized failures, strict usage/output checks and cancellation-safe accounting cleanup. Returned payload is untrusted data requiring the Part 3 harness.
- `gateway_limits.py` / `gateway_models.py`: content-free persistent metering and locked admission, per-attempt reservation/reconciliation, crash leases, UTC-day handling, lazy or explicit privacy maintenance.
- `apps/api/migrations/versions/0003_gateway.py` and migration metadata: three new tables, one migration-created lock record, preserved existing data. Health now expects `0003_gateway`.
- API settings and service initialization: validated provider/limit/price configuration; missing APP_MODE defaults to live consistently with the web app. Existing setup still supplies demo explicitly.
- `httpx` is moved from development-only to runtime dependencies without changing its resolved version or upgrading other packages. Lock metadata is updated.
- `.env.example`, guide-gateway documentation, phase plan/status/decisions and new report/evidence. Existing UI, assets, prior audit, unrelated `next-env.d.ts` change and Part 1 work are preserved.

## Verification

| Check | Result | Evidence |
|---|---|---|
| Gateway mock/ledger tests | 62 passed | Included in [focused test run](evidence/phase03-part2/tests.txt) |
| Part 1 retrieval regression | 23 passed | Same test run |
| Existing database-outage regression | 1 passed | Same test run |
| `pnpm lint` | Pass, web ESLint/API Ruff | [Lint output](evidence/phase03-part2/lint.txt) |
| `pnpm typecheck` | Pass, web TypeScript/API strict mypy (18 files) | [Types](evidence/phase03-part2/typecheck.txt) |
| Alembic upgrade/downgrade | Portable SQLite test passes and preserves unrelated table | Focused test run |
| `uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head --sql` | Offline PostgreSQL SQL generation passes | [SQL](evidence/phase03-part2/migration.sql) |
| `pnpm check:foundation` | Contracts regenerate identically; assets and configured-secret checks pass | [Foundation](evidence/phase03-part2/foundation.txt) |
| `git diff --check` | Pass | Working-tree check |
| Current credentials/database | Key absent; activation disabled; `docker compose ps` has no project container | [Environment state](evidence/phase03-part2/environment.txt) |

The 86 focused checks include parallel admission preventing budget/concurrency oversubscription, persistent caps across instances, per-session/global rate limits, retry reservations, permanent-error/redirect handling, Retry-After behavior, metadata pruning, UTC rollover, cancelled/expired leases, unavailable accounting, incomplete/oversized/malformed JSON, invalid/zero usage, configured-price/model binding and mode defaults. They make no external HTTP calls.

The test run emits one upstream FastAPI/Starlette TestClient deprecation warning. Existing httpx remains compatible for these tests; no dependency migration was undertaken solely for this warning. Node 26.8.2 is outside the project's declared Node 22 range, so successful web checks do not establish supported-runtime certification.

## Limits and next work

The dedicated PostgreSQL image remains unavailable following the registry timeout recorded in Part 1. PostgreSQL migration execution, row-lock behavior under real load and real restored-corpus integration are unverified; the portable writer-transaction tests are not substitutes for those checks. No model correctness, real billing or actual provider/meaningful-answer latency has been measured.

Configured peak/cache-miss rates intentionally overestimate cache/off-peak invoices. The input byte bound, provider token limit and configured rates are assumptions to verify during live activation. If the provider reports out-of-bound usage, its tokens are recorded and the answer is rejected. Cancellation releases local resources but remote billing can continue. Unknown charges remain reserved rather than being reported as free failures. Admission uses the UTC reservation day, not a claim about provider invoice timing.

Metering stores no prompt/answer/evidence/raw session ID; temporary rate keys are HMAC pseudonyms. Cleanup occurs on successful admission or explicit `UsageLedger.prune()`, with no fixed deletion deadline during inactivity/outages. Part 4 must connect periodic maintenance, owned session identity and disconnect cancellation to the live request lifecycle. Raw payloads must pass Part 3 schema, citations, semantic support, chronology, language and uncertainty checks before publication.

Next: **Part 3 — expert explanation and support-validation harness**. UI/SSE, BGE-M3 hybrid retrieval, corpus broadening with real review and the 40-case scored bilingual evaluation remain later parts. Jinyao still presents the labelled scripted preview.
