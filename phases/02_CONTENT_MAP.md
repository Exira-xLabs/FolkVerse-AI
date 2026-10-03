# Phase 02 — Reviewed content, catalog and regional discovery

**Prerequisite:** Phase 01 shell works; human reviewer identified.

**Outcome:** Actual database-backed exhibits, source drawer and rights-controlled artifact catalog.

## Paste into Codex
```text
Read docs/build-kit/00_MASTER_CODEX_PROMPT.md and docs/build-kit/phases/02_CONTENT_MAP.md. Inspect the repository and docs/build-status.md. Implement the following phase, preserving approved UI and unrelated work.


Read DATA_AND_API_CONTRACTS and CONTENT_AND_AI_RULES. Build migrations for regions, exhibits, sources, passages, claims, artifacts, media and reviews. Separate cultural practice/origin from present museum location. Support draft, approved and withdrawn publication states.

Implement an idempotent Met import CLI. Verify its current paginated search format against official docs; don't use a deprecated endpoint just because an old tutorial does. Re-fetch sample IDs 50824, 449479 and 460669 and record actual results. Limit import batches, cache responses, handle timeouts/rate limits, save provenance and image-specific rights. No bypassing restrictions. Imported entries remain draft. Target 30 eligible records, but report true counts and failed entries.

Prepare ten candidate regional exhibits with attributable permitted text; require actual editorial approval. Provide review/publish/unpublish CLI with an audit log. Generated summaries stay draft. Use existing local fixtures until approval, clearly labelled. Do not claim an external specialist review that hasn't occurred.

Connect /regions, /exhibits and /sources to frontend filters, exhibit drawer and list navigation. Use approved map geometry only. If geometry is not ready, preserve cinematic illustrative background but make region list the real navigation and label the map scene illustrative; don't trace AI map borders or assign false geography.


Update docs/build-status.md with actual results, blockers and the next phase. Report what is live, fixture-driven, untested or unavailable. Do not claim completion unless the gates below are met.
```

## Acceptance gates

- [ ] Re-import causes no duplicate objects or media; source payload/hash retained.
- [ ] Draft/withdrawn/unlicensed entries are absent from published search.
- [ ] One real approved exhibit traverses map/list → detail → source.
- [ ] Source withdrawal removes affected search content and caches.
- [ ] Report exact approved/draft counts; target 10/30 is never manufactured.


## Handoff
Corpus manifest, review ledger, data rights report and missing human approvals. Phase 03 requires some approved passages, not merely placeholders.
