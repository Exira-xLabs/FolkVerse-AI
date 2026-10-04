# FolkVerse China — 华韵 AI

FolkVerse is a competition project for a bilingual interactive cultural museum. Its visitor loop connects regional exploration, learning journeys, source-backed questions, branching stories, object discovery and editable cultural interests.

The supplied business plan and competition deck are proposals. The first prototype targets one reviewed region, ten reviewed exhibits, thirty eligible artifact records and one small branching story. These counts are targets, not imported or approved content. The competition schedule recorded in the kit has a 30 September document deadline, a 10 October internal rehearsal target and finals on 11–18 October if selected; this implementation does not alter submitted materials.

## Start here

- [Local setup for Linux and Windows/PowerShell](docs/setup.md)
- [Current build status and verification](docs/build-status.md)
- [Architecture decisions and path mapping](docs/decisions.md)
- [Original competition build-kit entry point](README_START_HERE.md)
- [Phase 00 requirements](phases/00_FOUNDATION.md)
- [Instructions for a friend's reporting agent](report/AGENT_REPORT_INSTRUCTIONS.md)

The build kit remains at the repository root. Its original Markdown files, artwork and confidential local PDFs are preserved. Application code lives in `apps/web` and `apps/api`; generated API types live in `packages/contracts`. Read the actual source files and phase gates before continuing.

## Local development

With Node.js 22, pnpm 11.10.0, uv, Python 3.12 and Docker available, run these commands from the repository root:

```sh
pnpm install --frozen-lockfile
uv sync --project apps/api --frozen
pnpm setup:local
pnpm assets:sync
pnpm db:up
pnpm db:migrate
pnpm contracts
```

Then run `pnpm dev:api` and `pnpm dev` in separate terminals. Open <http://localhost:3000>. The `/status` page checks the actual web → API → PostgreSQL/pgvector connection and can start or revoke an anonymous visit. No AI API credentials are needed for Phase 00.

```sh
pnpm lint
pnpm typecheck
pnpm build
pnpm test:api
pnpm test:e2e
pnpm check:foundation
```

Later feature routes currently display explicit unavailable states. They do not simulate live guide answers, artifact recognition or reviewed cultural content.
