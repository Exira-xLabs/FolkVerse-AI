# Part 8 — reproducibility and closure audit

7 October 2026. Reproduction and the evidence audit are complete. **Phase 3 release closure is not approved** while required human/content gates remain open.

A disposable checkout copied the Git-visible candidate tree, excluding ignored credentials, local model weights, media caches and screenshot files. It installed frozen dependencies, created fresh secrets, verified repeated setup preserves them, started a separate pinned PostgreSQL/pgvector container on an isolated loopback port, migrated twice and restored the original reviewed corpus into empty tables. A second restoration was correctly refused with unchanged counts and review ledger. No populated project database or unrelated service was modified.

The checkout passed artwork synchronization, lint, types and production build. Fresh API health confirms PostgreSQL/pgvector and schema readiness; one reviewed exhibit is eligible. Owned session creation works. A live-mode guide with no provider key fails closed, making zero paid calls. Production web startup reaches the fresh API and renders `/guide`. The temporary process groups and container were stopped and removed. The audit uses the existing dependency cache (`pnpm --offline`); it is not a network-independent installation without cached packages. Linux was exercised; Windows/macOS were not.

The [initial reproduction](evidence/phase03-hybrid-part08/reproduction-first.json) recorded an incorrect audit expectation that restoration could succeed twice. That assumption was corrected in the verification script, preserving the application's existing refusal to overwrite populated content. The initial immediate cleanup check raced Docker auto-removal; the final audit polls removal and confirms completion. No application restoration rule was weakened.

Final [reproduction](evidence/phase03-hybrid-part08/reproduction-final.json): 18 successful expected outcomes, fresh setup/build/startup and zero provider calls. It records the candidate tree fingerprint and exact commands. Individual application runtime/contract/dependency hashes are recorded and match the final tree. To keep secret scanning accurate, a later format-only normalization stores each runtime path and its unchanged SHA-256 as separate fields rather than placing a path containing `api` in an object key. The reproduction generator and retained reports use this same representation. Reports and test artifacts are identified separately from runtime files.

Local verification also passes 421 API tests, 59 dedicated guide browser checks, lint/types/build and deterministic contracts/artwork/configured-secret checks. **68 broad museum browser regressions pass**, separately from the 59 guide checks. No GitHub Actions workflow is configured; local checks must not be called remote CI or production deployment.

Reproduce the isolated audit with:

```sh
uv run --project apps/api python scripts/verify-phase03-reproduction.py --output <new-dated-reproduction.json>
```

Use the [closure matrix](PHASE_03_HYBRID_CLOSURE_AUDIT.md) as the actual Phase 3 status. Human judgments, broader approved gold/content, 200-question support pilot and unavailable physical-device/native-zoom checks remain visible. Phase 4 is not used to hide those open gates.
