# Liaoning content operations

Run commands from the repository root after [local setup](setup.md) and `pnpm db:migrate`. These are local operator commands; there is no public review endpoint. Reviewers are responsible for the actual text, translation, rights and locality decision. The CLI requires an explicit attestation and records content hashes, reviewer, date, notes and previous status.

## First setup and recovery

For a new database with empty content tables, restore the delivered corpus:

```sh
uv run --project apps/api python -m folkverse.curation restore-manifest
uv run --project apps/api python -m folkverse.curation counts
```

This restores the recorded approvals, including the project owner's approved Liaoning exhibit, with original reviewer/date/hash intact. It creates no new approval. It checks review hashes and refuses to overwrite any existing content. Treat the snapshot as a trusted local operator artifact; hashes provide integrity checking, not a digital signature proving an editor's identity.

Reference image bytes are deliberately excluded from Git. The manifest contains hashes/storage keys and per-image rights evidence; images remain unavailable until downloaded and verified locally. Restore leaves missing media ineligible. Re-import the Met objects to recover their reference bytes. Imports never create reviews and changed upstream payloads return affected records to draft.

For an empty database where drafts are wanted instead of the delivered review history:

```sh
uv run --project apps/api python -m folkverse.curation seed
```

This seeds 14 bilingual Liaoning candidates, the province and 14 cities. Repeated seeding preserves existing edits and reviews. It does not restore approval or republish withdrawn entries. See the [editorial review packet](content-review.md).

## Met import

Official [API documentation](https://metmuseum.github.io/) checked 5 October 2026 documents `/v1.1/search`, `offset`/`limit`, and the 10,000-result paging boundary. The importer restricts each batch to at most 50 objects and uses the official object endpoint.

```sh
uv run --project apps/api python -m folkverse.curation import-met --ids 50824 449479 460669
uv run --project apps/api python -m folkverse.curation import-met --query China --offset 0 --limit 30
uv run --project apps/api python -m folkverse.curation import-met --query China --offset 30 --limit 5
```

`--refresh` re-fetches upstream JSON. Otherwise content-addressed original responses and timestamps are cached under ignored `.local/met`. JSON responses are limited to 2 MB; JPEG downloads to 12 MB; requests time out after 20 seconds. Transient errors have at most three attempts. 401/403 are recorded without retry or bypass. Long/date-valued Retry-After responses defer the import. Only the official API/image hosts and HTTPS redirects are accepted. `--base-url` configures an official-host endpoint, not an arbitrary proxy.

Met metadata and image rights are separate. Only an explicitly public-domain object without unresolved reproduction restrictions is an image candidate. Each image has its own rights evidence and downloaded SHA256. A CC0 flag alone does not publish an artifact or establish Liaoning relevance. Country/culture/origin remain distinct from the current museum location. `ArtifactExhibit` links require evidence; none were invented.

## Actual review and publication

Inspect records before recording a decision:

```sh
uv run --project apps/api python -m folkverse.curation inspect exhibit liaoning-shenyang-01
uv run --project apps/api python -m folkverse.curation inspect passage passage-liaoning-shenyang-01-en
```

After an actual human review, use this command shape, replacing the IDs, reviewer and notes:

```sh
uv run --project apps/api python -m folkverse.curation review passage PASSAGE_ID --decision approved --reviewer "Reviewer name" --notes "Evidence, wording, translation and rights actually reviewed" --attest-human-review --clear-rights
```

Review the region, source, both language passages and claim before approving the exhibit. For media, approval additionally requires reference role, CC0 rights and verified downloaded bytes. Never use a generated reviewer or claim specialist review. The project owner is the agreed editorial reviewer.

Publication states are `draft`, `approved`, `rejected`, `withdrawn`. Every decision appends to the ledger. Approved records whose text/metadata/links change fail hash validation and are hidden until reviewed again. An exhibit is visible only while every linked region, claim, evidence passage and source is eligible.

## Withdrawal

```sh
uv run --project apps/api python -m folkverse.curation review source SOURCE_ID --decision withdrawn --reviewer "Reviewer name" --notes "Reason for actual withdrawal" --attest-human-review
```

Withdrawal immediately removes dependent search/detail content from the API. There is no published-content cache; reads recompute eligibility and return `Cache-Control: no-store`. Source withdrawal clears dependent embedding-version markers. Real vectors and retrieval caches do not exist yet; Phase 03 must implement their invalidation when added. An already open browser tab revalidates on focus and every 15 seconds, removing stale drawer content after a failed check. This is polling, not an instant push notification.

## Handoff and verification

```sh
uv run --project apps/api python -m folkverse.curation counts
uv run --project apps/api python -m folkverse.curation ledger
uv run --project apps/api python -m folkverse.curation export
uv run --project apps/api python scripts/verify-content-snapshot.py
pnpm test:api
pnpm build
pnpm test:e2e
```

The export includes all records, evidence/geography relationships and review history in `data/manifests/corpus.json`. `data/manifests/review-ledger.json` is the corresponding human audit snapshot. The restore verification creates and drops only its own disposable database; it requires the local database role to have CREATE DATABASE permission. Browser tests require the delivered snapshot in the local database, the finished production build, and free ports 3000/3002/8000.
