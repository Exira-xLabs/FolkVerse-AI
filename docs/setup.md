# Local setup — Phases 00–02

Run all commands from the repository root. There is one Next.js application and one FastAPI service. The original build kit is already in this repository; do not scaffold another application or copy confidential PDFs into the web app.

## Prerequisites

- Node.js 22 LTS and pnpm **11.10.0**. The workspace pins pnpm and compatible package versions. Install pnpm using its [official instructions](https://pnpm.io/installation) if it is missing.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python **3.12**. Use `uv python install 3.12` if that interpreter is missing; `apps/api/.python-version` selects it without changing your system Python.
- Docker Engine with Compose on Linux, or Docker Desktop with Linux containers on Windows. Use the existing Docker/WSL installation. Docker must be running before starting the database.

Runtime references checked during implementation on 4 October 2026: [Next.js installation](https://nextjs.org/docs/app/getting-started/installation), [FastAPI manual server startup](https://fastapi.tiangolo.com/deployment/manually/), [pgvector Docker instructions](https://github.com/pgvector/pgvector#docker), and [pnpm build settings](https://pnpm.io/settings). Node 22 meets Next.js's documented Node 20.9 minimum. Python dependencies are resolved specifically for Python 3.12 in `apps/api/uv.lock`. Docker uses the recorded pgvector/PostgreSQL 17 image digest, rather than a moving image alone.

## Linux/macOS

```sh
pnpm install --frozen-lockfile
uv sync --project apps/api --frozen
pnpm setup:local
pnpm assets:sync
pnpm db:up
pnpm db:migrate
pnpm contracts
```

Start the API in one terminal:

```sh
pnpm dev:api
```

Start the web app in another terminal:

```sh
pnpm dev
```

Open <http://localhost:3000>, then <http://localhost:3000/status>. API health is also available at <http://127.0.0.1:8000/health> and <http://127.0.0.1:8000/api/v1/health>; OpenAPI is at <http://127.0.0.1:8000/openapi.json>.

## Windows / PowerShell

Open PowerShell in your cloned repository. The same commands work without Bash, a Makefile or personal machine paths:

```powershell
pnpm install --frozen-lockfile
uv sync --project apps/api --frozen
pnpm setup:local
pnpm assets:sync
pnpm db:up
pnpm db:migrate
pnpm contracts
```

In a second PowerShell window at the repository root, run `pnpm dev:api`. In a third, run `pnpm dev`. Open <http://localhost:3000>. The API is run through uv, so you do not need to activate `.venv` manually.

The commands were exercised on Linux. Windows/macOS execution remains unverified; the scripts use Node/Python path resolution and Compose rather than Linux-only setup commands. If PowerShell blocks a package-manager shim, follow the installer documentation for that installation or use its `.cmd` shim; do not blindly change the system execution policy.

## Local configuration

`pnpm setup:local` creates an ignored root `.env` with a random database password, a random signing secret, demo mode, local origins and a database connection string. It also creates `apps/web/.env.local` with the server-only API address. Re-running it preserves both files. It never prints generated secrets. `.env.example` documents variable names and comments only.

PostgreSQL binds to **127.0.0.1:5440**; the API to **127.0.0.1:8000**; the web app to **127.0.0.1:3000**. These are local development services. `COOKIE_SECURE=false` supports local HTTP; set it to true for HTTPS. Cookies are HttpOnly and SameSite=Lax. The API validates the Origin on every state-changing request against `ALLOWED_ORIGINS`. The default list allows both `http://localhost:3000` and `http://127.0.0.1:3000`.

`APP_MODE=demo` and `APP_MODE=live` use different cookie-signing namespaces. The foundation never invokes a provider in either mode. Changing mode does not make future AI capabilities work; Phase 03 must implement and verify the gateway. Do not add provider credentials to the web environment or any `NEXT_PUBLIC_*` variable. No configured daily budget is permission to spend.

For a different port, update the corresponding local configuration, command and allowed origin together. `POSTGRES_PORT` controls Compose, while `DATABASE_URL` must point to that same port. To use a manually managed local database instead of Compose, install PostgreSQL/pgvector using their official instructions, create a dedicated database/user, set `DATABASE_URL` accordingly, and run `pnpm db:migrate`. That alternative has not been exercised here.

## Verification and contracts

```sh
pnpm lint
pnpm typecheck
pnpm build
pnpm test:api
pnpm exec playwright install chromium
pnpm test:e2e
pnpm check:foundation
```

API tests use the dedicated configured database and clean up their own successful test sessions. Do not point them at a shared or production database. Browser tests require ports 3000 and 8000 to be free; they start production web/API processes themselves and stop them on completion. Stop development servers before running them. Screenshot evidence and browser results are saved under `report/evidence/phase00/`. Browser error-state tests identify their injected failures in the test source; they are not measurements of live AI behavior.

`pnpm contracts` exports a sorted OpenAPI snapshot without requiring a running API, database or local credentials, then generates TypeScript definitions. The typed frontend client uses these definitions. `pnpm check:foundation` regenerates the contracts and checks exact equality, validates assets against their manifest, verifies environment files are ignored, and searches source/docs/browser outputs for the local configured secrets without printing their values.

## Database lifecycle and recovery

`pnpm db:migrate` applies Alembic revisions, installs pgvector and creates anonymous-session storage. Re-running it is safe. `pnpm db:stop` stops only this project's database and preserves its named volume. Ctrl+C stops a foreground web/API server. Do not remove Docker volumes as a routine recovery step.

If health shows unavailable, check `docker compose ps`, run `pnpm db:up`, then `pnpm db:migrate`. The service returns HTTP 503 until the database, vector extension and expected migration are available. If the API is stopped, the web proxy returns the shared unavailable error and the status page offers retry. No success is generated locally to mask a failed service.

If credentials were changed after the database volume was initialized, restore the previous matching local configuration or deliberately rotate the database user's password. Merely editing `POSTGRES_PASSWORD` does not change an existing database user's password. Keep secrets out of shared reports and shell output.

The foundation stores only anonymous-session identifiers and timestamps. Session expiry prevents reuse, and ending a visit deletes its row and clears its cookie. Periodic expiry cleanup and deletion of future personal feature data must be added with the relevant feature lifecycle; no private media is accepted in Phase 00.

## Phase 02 content

After migrating a fresh database, restore the delivered Liaoning corpus and its original review history with `uv run --project apps/api python -m folkverse.curation restore-manifest`. Existing content is never overwritten. For drafts only, use `uv run --project apps/api python -m folkverse.curation seed` instead. See [content operations](curation.md), [review packet](content-review.md) and [rights report](data-rights.md). The browser suite now expects the delivered approved Liaoning exhibit.

## Phase 3 reproducibility and acceptance — 7 October 2026

The isolated Linux verification script copies the Git-visible candidate into a disposable checkout, installs frozen dependencies from the existing pnpm cache, creates fresh secrets and a separate temporary pinned PostgreSQL/pgvector container, migrates, restores the original corpus and verifies build/API/web startup. It never copies ignored provider keys or touches the populated project database. Ports 8004 and 3004 must be free. Docker must already work, and the locked packages/image must be locally available. Generated artifacts, weights and private config are not part of the Git-visible input.

```sh
uv run --project apps/api python scripts/verify-phase03-reproduction.py --output <new-dated-reproduction.json>
```

Restoring into populated content tables intentionally exits 2 and preserves existing content; use `curation counts`/`ledger` to inspect it. Re-running setup and migrations is safe. Do not remove a populated project volume to make verification pass. A fresh live-mode install with no key remains unavailable for generation; actual model integration is tested separately under existing authorization.

Current [Phase 3 closure audit](../report/PHASE_03_HYBRID_CLOSURE_AUDIT.md) distinguishes completed engineering from outstanding actual human/content/pilot evidence. Demo browser regressions explicitly start their web instance in demo mode; real guide fixtures/live verification use their own live configuration. No remote CI or production deployment is inferred from local startup or a Git push.

## Try the real chatbot instead of the scripted preview

The chat banner is the reliable distinction: **“Scripted preview · no live AI · messages are not sent”** means `APP_MODE=demo`. That mode deliberately plays prepared examples; it does not test DeepSeek or free conversation. A typed `hi` must be tested in live mode.

For live chat, set `APP_MODE=live` in the ignored root `.env`, configure the existing provider credentials and bounded admission there, and start both API and web. Remove any conflicting `APP_MODE=demo` web/process override, or explicitly start the web with `APP_MODE=live`. Restart both processes after changing mode. Provider keys stay server-side in the ignored root file. A suggested question is optional; users can type their own cultural questions and follow-ups.

For an HTTPS reverse proxy forwarding HTTP to Next, set server-only `PUBLIC_APP_ORIGIN=https://your-exact-hostname` in the web process or ignored `apps/web/.env.local`. Add that exact origin to the API's `ALLOWED_ORIGINS` and enable `COOKIE_SECURE=true`. The BFF still requires the request Origin and Host to match exactly; arbitrary forwarded headers do not configure a public hostname. Expose only the web service, keeping the API and database on loopback. Temporary hostname changes require updating these exact-origin settings. Never disable origin checks to make a preview work.
