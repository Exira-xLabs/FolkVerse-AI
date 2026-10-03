# Master Codex prompt
Paste once, then paste one phase prompt at a time.

```text
Implement FolkVerse China — 华韵 AI, a bilingual interactive AI cultural museum, in the current repository. Read applicable AGENTS.md instructions, manifests, existing code and git status first. Preserve unrelated work. Reuse the existing app rather than scaffolding a duplicate.

Read docs/build-kit/README_START_HERE.md, specs/ARCHITECTURE_AND_COSTS.md, specs/DATA_AND_API_CONTRACTS.md, specs/CONTENT_AND_AI_RULES.md and 01_OPENDESIGN_UI_PROMPTS.md. Open the actual references/ui PNGs. Inspect design/opendesign exports if present. Follow the provided visual direction: cinematic museum scenes, guide artwork and museum glass design. GPT Sol, Astra, or any other model working on FolkVerse is authorized and encouraged to use an available image-generation tool to create original map/UI assets and achieve the best-looking experience possible. If image generation is unavailable, state that plainly. Keep supplied originals intact and save generated assets separately. Do not substitute a generic dashboard, white panels, purple gradients or a different avatar. Generated map imagery is visual scenery only—not authoritative geography or functional controls. Implement accessible, data-driven interactions over the artwork; don't flatten the screen into one image.

The current report is a proposal. First scope is one reviewed region, ten exhibits, thirty rights-cleared artifacts, one branching story and the connected visitor loop. Counts are targets. Generated map art is decorative, never authoritative geography. Generated art is excluded from artifact recognition references and tests.

Use Next.js App Router / TypeScript / Tailwind / Motion; FastAPI / Pydantic / SQLAlchemy / Alembic; PostgreSQL with pgvector; local media storage behind an adapter. Defer Redis, S3 and full account management until needed. DeepSeek is server-side and configurable; GLM remains optional and disabled. Verify provider model IDs and API formats in official docs before implementing calls. Pin compatible dependencies; don't gratuitously upgrade a working repository.

Complete the active phase and its necessary prerequisites. Implement code and focused verification, not just a plan. APP_MODE=demo uses labelled deterministic fixtures. APP_MODE=live must never silently return canned success. Missing credentials are an explicit unavailable state while offline work continues. Do not manufacture citations, practitioner approval, scores, accuracy, object authentication or partnerships.

Use source, rights and uncertainty gates. Guide evidence IDs must belong to the retrieved bundle; scan candidates must belong to the supplied catalog. Keep API keys server-side, out of logs and commits. Do not send user media to additional providers without consent. No paid resource purchases or public deployments without authorization in this session; continue authorized reversible local work autonomously.

After each phase update docs/build-status.md with changed files, commands and results, visual evidence paths, implemented versus simulated features, blockers and next phase. Record deviations in docs/decisions.md. Maintain .env.example using names/comments only. Run meaningful tests around the phase's real risks. Do not hide untested work as complete.
```

## Resume prompt
```text
Resume FolkVerse from docs/build-status.md and the active phase prompt. Inspect the actual repository before trusting past completion notes. Read the master brief. Preserve working code and the approved UI; complete the next unfulfilled gate, without restarting finished phases.
```

## Completion rule
A feature is complete when its main action, empty/loading/error states, ownership and source rules, keyboard path and reference appearance have been checked. A visual shell is a milestone, not an implemented AI product.
