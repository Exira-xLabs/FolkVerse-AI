# Build-kit location in this repository

The original competition kit is already the repository root. Preserve its authoritative files there rather than making a second editable copy.

| Prompt path | Actual canonical path |
|---|---|
| `docs/build-kit/README_START_HERE.md` | `README_START_HERE.md` |
| `docs/build-kit/00_MASTER_CODEX_PROMPT.md` | `00_MASTER_CODEX_PROMPT.md` |
| `docs/build-kit/01_OPENDESIGN_UI_PROMPTS.md` | `01_OPENDESIGN_UI_PROMPTS.md` |
| `docs/build-kit/specs/` | `specs/` |
| `docs/build-kit/phases/` | `phases/` |
| `docs/build-kit/QA_AND_DEMO.md` | `QA_AND_DEMO.md` |
| `docs/build-kit/SOURCES_AND_TRACEABILITY.md` | `SOURCES_AND_TRACEABILITY.md` |
| `docs/build-kit/assets/` | `assets/` |
| `docs/build-kit/references/` | `references/` |

See [the build-kit entry point](../../README_START_HERE.md), [implementation decisions](../decisions.md) and [build status](../build-status.md). Runtime asset and screenshot copies are produced by `pnpm assets:sync`; they do not replace the originals. Confidential local source PDFs are not copied to public assets or design delivery folders.
