# Phase 00 — Repository and working foundation

**Prerequisite:** Master brief read; local repository selected.

**Outcome:** Web, API and database start locally with a stable design/contract foundation.

## Paste into Codex
```text
Read docs/build-kit/00_MASTER_CODEX_PROMPT.md and docs/build-kit/phases/00_FOUNDATION.md. Inspect the repository and docs/build-status.md. Implement the following phase, preserving approved UI and unrelated work.


Inspect any existing Next.js/Python project. Reuse its compatible structure and package manager. For an empty repo use the architecture spec structure, pnpm for web and a reproducibly locked Python environment. Verify current supported runtime requirements in official docs; record chosen versions instead of guessing.

Add local PostgreSQL/pgvector setup with documented manual or container startup. Prefer existing Docker/WSL if available; don't buy services or change system-wide configuration silently. Create FastAPI health endpoint, web health connection, shared API error envelope, initial OpenAPI/client generation, lint/typecheck scripts and .env.example without secrets. Keep demo and live configuration separate.

Copy assets from docs/build-kit/assets into apps/web/public/folkverse preserving names and hashes. Copy references into design/reference. Inspect PNGs; register routes and global tokens. Create bilingual key structure and sensible default English. Add an anonymous signed-session mechanism with ownership helpers; do not implement public registration yet.

Document setup for the team's Windows/PowerShell environment as well as the actual development OS. Provide scripts that work with declared paths, not personal machine paths. Save a placeholder-free shell and docs/build-status.md. Missing prerequisites should have concrete remedies; continue tasks that don't depend on them.


Update docs/build-status.md with actual results, blockers and the next phase. Report what is live, fixture-driven, untested or unavailable. Do not claim completion unless the gates below are met.
```

## Acceptance gates

- [ ] Fresh install/start commands documented and exercised on available environment.
- [ ] Web reaches API health; DB connection tested and failures are legible.
- [ ] No server key appears in browser code, logs, .env.example or tracked files.
- [ ] Correct assets and transparency preserved; no duplicate app scaffold.
- [ ] OpenAPI types generate deterministically; versions and scripts recorded.


## Handoff
Commands, chosen versions, environment limitations and Phase 01 entry point.
