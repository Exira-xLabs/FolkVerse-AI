# Phase 03 hybrid Part 3 — Liaoning collection and review

6 October 2026. **Acquisition and review tooling, source discovery, and the all-city draft floor are implemented locally. Actual human content/rights approval remains open. Nothing from this intake was published.**

The low-cost workflow prefers structured workbooks and official HTML, then local Tesseract OCR for scans. The existing scan checks were saved as explicitly **assistant** extraction packets. No more vision calls or paid model calls were needed after the user's request to stop vision. [Operator guide](../docs/liaoning-collection-and-review.md), [dashboard](../data/liaoning/dashboard.md), [city review files](../data/liaoning/review/).

## Actual collection

60 registered official resources; **1,114 edition-specific inventory rows** and **42 explanatory source records**, counted separately. These are not unique traditions or proof of exhaustive province-wide coverage.

| Inventory | Rows |
|---|---:|
| June 2026 administrative directory: 14 cities + 100 county-level divisions | 114 |
| National / provincial heritage worksheets, May 2021 | 76 / 218 |
| Provincial heritage batches 1–7 | 60 / 54 / 41 / 35 / 58 / 46 / 134 |
| Registered museum roster, 2024 | 135 |
| Protected-site batches 11 / 12 | 33 / 110 |

All seven provincial heritage batches are enumerated: their batch counts sum to the reported 428 projects. Earlier worksheets overlap those batches; they must not be added to create a unique-project total. Shared identities still require review.

The 134 + 110 scanned rows retain native ordinals, original wording, source locators, OCR evidence and extraction attribution. Five protected-site rows retain explicit field ambiguity notes; assistant transcription does not equal scholarly or rights approval. The 2024 checkpoint reports 702 provincial and 159 national protected sites; the older 673 figure is a dated historical checkpoint. Neither checkpoint supplies a complete row roster. The 2025 museum checkpoint reports 152 museums; the acquired 2024 roster contains 135. Missing newer rosters and protected-site batches 1–10 remain explicit acquisition tasks.

## Concrete review material

Ten official culture/tourism index pages yielded **189 profile links**, recorded with source capture hashes. Forty-two profiles were acquired and indexed: **three per city across at least two subjects in every city**. Full source prose stays in ignored private captures; versioned records contain paragraph locators, lengths and hashes.

The packet now has **448 unapproved bilingual units**: 28 administrative city introductions, 84 earlier list-membership introductions, and 336 launch-topic units (42 topics × introduction/context/example/question × EN/ZH). Short source-attributed paraphrases provide real context and concrete examples. Folklore and source statements stay distinct; promotional superlatives, unsupported medical effects and assumed current operational information were excluded.

[Launch preparation](../data/liaoning/launch-preparation.json) confirms the draft floor for all 14 cities. [Review packet](../data/liaoning/review-packet.json) binds units and translations to exact source revisions. Per-city Markdown files make the proposed content readable. Editing or refreshing a source invalidates relevant approvals; regeneration preserves operator-edited drafts. Assistant extraction can receive later human reconciliation without rerunning vision or silently changing the source capture.

**Human-approved units: 0. Launch-ready cities: 0.** The existing database still has one eligible exhibit. Those numbers are not changed by completing collection tooling or drafting material.

## Trusted-source search and Part 4 handoff

The user's hybrid scope now explicitly includes trusted-source search. [Policy](../data/liaoning/trusted-search-policy.json) and [search backlog](../data/liaoning/trusted-search-queue.json) distinguish stable reviewed knowledge, bounded official lookup, and clearly labelled general model explanation. Search results discover pages; original pages, dates and responsible institutions must support claims. Lookup does not grant rights or create human approval.

**Visitor runtime search is not connected yet.** Part 4 must wire search and reviewed-unit publication into hybrid answers, with original-page citations, currentness checks, source-change withdrawal, retrieval injection/SSRF protection and honest unavailable states. Missing data does not require downloading all Liaoning information before proceeding with independent chatbot engineering.

## Verification

363 API tests pass, including 33 inventory/curation checks. Ruff and strict mypy pass for 33 source files. Foundation contract/secret checks and all nine original asset checks pass. Tests cover official-host/access restrictions, parsing, row accounting, immutable revisions, rights/human review gates, translation invalidation, assistant-to-human extraction revision, chronological column separation, source-bound launch drafts, edit preservation and prevention of automatic approval/publication.

Current evidence: [verification record](evidence/phase03-hybrid-part03/verification.json). No Part 3 database writes or paid provider calls were performed. Work is local and not pushed.

**Remaining content gate:** a real human reviews the prepared EN/ZH texts, rights and source support; unresolved fields and missing inventories remain visible. Engineering and review preparation are delivered; human approval and exhaustive data coverage are not claimed.
