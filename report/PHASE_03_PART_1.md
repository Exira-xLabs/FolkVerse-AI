# Phase 03 Part 1 — reviewed evidence foundation

6 October 2026, Asia/Shanghai. **Lexical baseline implemented; real PostgreSQL integration blocked. Phase 03 remains incomplete.**

The project was scanned across the web application, API/data layer, generated contracts, setup/verification scripts, specifications, phase requirements, review manifests and prior reports. The current corpus is narrow and Jinyao's existing conversation remains scripted. The six-part work sequence and completion boundaries are in [the implementation plan](../docs/phase-03-plan.md).

## Implemented

- Reviewed-only English/Chinese BM25 retrieval with normalized Latin/CJK tokenization and strict language/exhibit scope.
- Actual permitted passage text and source metadata, locator, rights basis, editorial reviewer/date, fingerprint and published exhibit/region IDs in bounded bundles.
- Deterministic corpus versions and a coverage index with explicit unindexed period/person/object gaps.
- Fresh eligibility checks for every retrieval and selected-evidence publication rechecks. Draft/unattached records, pending rights, withdrawn dependencies and unreviewed edits cannot retain eligibility.
- Local CLI inspection against configured PostgreSQL, with sanitized unavailable behavior and no fixture/snapshot substitution.

No new dependency, migration, provider call, model download, public endpoint, server conversation storage, UI change, content review or deployment was introduced.

## Verification

| Command/check | Result | Evidence |
|---|---|---|
| `uv run --project apps/api pytest apps/api/tests/test_guide_retrieval.py -q` | 23 passed; portable synthetic SQLite tests | [Results](evidence/phase03-part1/retrieval-tests.txt) |
| `uv run --project apps/api ruff check apps/api scripts/export-openapi.py` | Pass | [Lint](evidence/phase03-part1/lint.txt) |
| `uv run --project apps/api mypy --config-file apps/api/pyproject.toml apps/api/src` | Pass, 15 source files | [Types](evidence/phase03-part1/typecheck.txt) |
| Existing offline snapshot probe | Seven approved fingerprints and 41 source payload hashes pass; one approved exhibit/two passages; zero local catalog images | [Copied current probe result](evidence/phase03-part1/snapshot-integrity.json) |
| `docker compose up -d --wait db` | Exit 1, registry request timeout resolving pinned image | [Database result](evidence/phase03-part1/database-start.txt) |
| `uv run --project apps/api python -m folkverse.guide_retrieval` | Exit 1, honest database-unavailable error | [CLI result](evidence/phase03-part1/live-coverage.txt) |
| `git diff --check` | Pass | Local working-tree check |

The tests cover supported-language matches, unrelated queries without overlap, withdrawal at five dependency levels, unreviewed passage/source changes, pending rights, hidden exhibit scope, draft/unattached records, oversized evidence, input limits, explicit gaps and a separate-session withdrawal. They use real eligibility helpers; synthetic reviews exist only in disposable test databases. They do not establish semantic correctness of generated answers. A question with unrelated intent can still overlap vocabulary: that is a candidate requiring Part 3 support validation, never a validated answer.

PostgreSQL migrations, real restored-corpus retrieval, concurrent PostgreSQL transaction behavior and production performance remain unverified here. The offline snapshot check is not live database retrieval. No expert-quality score or provider latency is measured. Full browser tests were not rerun because this part makes no UI changes and the real database is unavailable.

## Handoff

Next is Part 2: official DeepSeek API verification, configurable server-only provider adapter and bounded resource/usage controls. Support/chronology validation, conversation context, live SSE, Jinyao/source controls, BGE-M3 and the required dated 40-case bilingual evaluation remain pending. Existing audit findings remain prerequisites for a trustworthy live integration handoff; broader cultural coverage requires actual attributable content and human review.
