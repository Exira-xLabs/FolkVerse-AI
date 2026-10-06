# FolkVerse China — 华韵 AI

FolkVerse is a competition project for a bilingual interactive cultural museum. Its visitor loop connects regional exploration, learning journeys, source-backed questions, branching stories, object discovery and editable cultural interests.

The supplied business plan and competition deck are proposals. The first prototype targets one reviewed region, ten reviewed exhibits, thirty eligible artifact records and one small branching story. These counts are targets, not imported or approved content. The competition schedule recorded in the kit has a 30 September document deadline, a 10 October internal rehearsal target and finals on 11–18 October if selected; this implementation does not alter submitted materials.

Current Phase 03: a real bounded bilingual Jinyao guide is verified through PostgreSQL and Ollama; broader reviewed explanations and independent quality review remain pending. [Current delivery report](report/PHASE_03_COMPLETION.md), [personality](docs/jinyao-personality.md), [coverage](docs/guide-coverage.md).

Current scope: **the whole Liaoning province**. Phase 02 is locally complete with 14 city candidates, 1 user-approved published exhibit and 2 approved passages. The separate Met catalog has 37 draft records and 32 downloaded CC0 image candidates; none is published or assigned invented Liaoning provenance. See the [current verified status](docs/build-status.md).

Explore opens an interactive atlas with Liaoning's sourced province outline and all 14 municipal territories. Selecting a city highlights its boundary and fits it into view; modern locator markers, drag, wheel/pinch zoom, a minimap and expanded view work in English and Chinese. Realistic generated terrain follows a sourced elevation reference, while fine terrain details remain approximate. [Map implementation and sources](docs/liaoning-map.md). Preview: <http://localhost:3000/explore>.

## Start here

- [Local setup for Linux and Windows/PowerShell](docs/setup.md)
- [Current build status and verification](docs/build-status.md)
- [Phase 03 push audit](report/PHASE_03_PUSH_AUDIT.md) and [DeepSeek through Ollama Cloud](docs/guide-ollama.md)
- [Architecture decisions and path mapping](docs/decisions.md)
- [Original competition build-kit entry point](README_START_HERE.md)
- [Phase 00 requirements](phases/00_FOUNDATION.md)
- [Phase 02 content operations and snapshot recovery](docs/curation.md)
- [Liaoning editorial review packet](docs/content-review.md)
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

For Phase 02 on a fresh database, first run `uv run --project apps/api python -m folkverse.curation restore-manifest` to load the delivered corpus and its original review history. Existing data is preserved; [curation instructions](docs/curation.md) explain drafts and local image recovery.

Then run `pnpm dev:api` and `pnpm dev` in separate terminals. Open <http://localhost:3000>. The `/status` page checks the actual web → API → PostgreSQL/pgvector connection and can start or revoke an anonymous visit. No AI API credentials are needed for Phase 00.

```sh
pnpm lint
pnpm typecheck
pnpm build
pnpm test:api
pnpm test:e2e
pnpm check:foundation
```

Phase 01 provides labelled interactive fixtures for Explore, Journey, Stories, Lens, Guide, My DNA and Sources. Demo filters, route edits, story branches, recorded narration and interest-chart edits work locally. These are not reviewed content or live AI. Set `APP_MODE=live` in server configuration to disable fixtures and display unavailable feature states; see [current status](docs/build-status.md).
