# Liaoning collection and human review

This operator workflow collects source inventory metadata and prepares explanations for review. It does not write to PostgreSQL, approve content, call a model, or change visitor answers. The existing content publication rules still apply. Run commands from the repository root.

## Scope and source editions

`data/liaoning/registry.json` defines official institutions, source and attachment URLs, reference dates, counting units, rights limitations, expected row counts and refresh intervals. The administrative baseline covers all 14 cities and 100 county-level divisions; township enumeration and geographic boundary geometry are separate acquisition tasks.

`discovery-backlog.json` includes municipal/county heritage, museum collections and gazetteer discovery for every city. Unknown URLs and denominators remain unknown. The launch floor of three substantive topics across two subject categories per city is not a collection ceiling. Earlier ambitions of 10–15 topics per city and wider subject coverage remain future acquisition work.

Do not add overlapping batch, national and provincial list counts into a unique topic total. A 2021 heritage roster, a 2024 museum roster and a 2019 protected-sites checkpoint retain their own dates. Newer official totals do not silently upgrade those editions to current enumerations. Historical county names need a dated crosswalk; list/applicant associations and museum locations are not evidence of historical origin.

## Collect and audit

```sh
pnpm data:liaoning:collect
pnpm data:liaoning:collect --source museums-2024
pnpm data:liaoning:report
```

Collection checks robots directives and official HTTPS hosts, refuses redirects and caps each download at 32 MiB. An inaccessible resource remains blocked; do not bypass access restrictions. Partial runs preserve other sources' latest outcomes. The source registry is operator-controlled and is not an arbitrary visitor URL fetcher.

Original downloads stay in ignored `.local/liaoning/raw/<SHA256>`. Versioned manifests retain original attachment filenames, byte hashes, source editions, extraction versions, row locators, original names/categories/localities and errors. Identical intake preserves its revision and reviews; changed bytes/configuration/extractor create a revision. Old revisions remain on disk, with `collection-index.json` selecting the active one. Manifest integrity is checked before curation. Do not edit collection JSON directly.

Workbooks are detected by content, not extension. XLS/XLSX and merged category cells are supported. Registered HTML tables/numbered paragraphs and `items` JSON responses have adapters; this delivery has no live JSON API source. PDF text extraction remains a draft pending column reconciliation. Missing, duplicate and unexpected native ordinals are explicit errors. Numerical import ratios alone are not a completeness certificate; check `reconciled_complete` and errors.

Report denominators separately:

- **Catalog rows:** edition-specific factual metadata, including overlapping lists.
- **Reviewed explanation units:** current source-bound text with actual attributed review, cleared rights and applicable translation checks.
- **Published exhibits:** a read-only check of the existing PostgreSQL eligibility rules. Database failure is unverified, not zero.

`coverage.json` reports named inventory accounting, refresh dates, unresolved associations, duplicate candidates and all 100 counties × 13 subject categories. Zero catalog entries describe a known gap, not proof that a county has no culture. Blank locality and ambiguous county names remain unresolved. Category-to-subject mapping is a provisional research aid: traditional medicine is cultural history, not health advice.

## Scans and row reconciliation

The final seventh heritage batch and twelfth protected-sites batch are image tables. The 134 + 110 rows are now saved as assistant-attributed extraction with original locators and OCR evidence. Five site rows retain field ambiguity notes. None is human-approved cultural knowledge. Prefer XLS/XLSX, HTML or text-PDF alternatives; use local Tesseract token geometry and correction packets for scans. Do not repeatedly invoke vision.

The local Chinese OCR runtime uses the pinned upstream model in `ocr-runtime.json`. Install Tesseract 5 and Poppler; download that exact model URL into ignored `.local/liaoning/ocr/chi_sim.traineddata` and verify its SHA256. The CLI rejects a mismatched model or raw capture.

```sh
uv run --project apps/api python -m folkverse.liaoning_ocr --source heritage-batch-7-2026
uv run --project apps/api python -m folkverse.liaoning_ocr --source protected-sites-batch-12-2025
```

Observations retain image hashes/page URLs or PDF page numbers, actual engine version, segmentation parameters, token confidence and pixel boxes. Header-only/low-confidence output is not proof of a reconciled row. OCR confidence does not approve text. Never use OCR spelling, dates or table columns without checking the original image.

Saved packets in `data/liaoning/transcription/` distinguish `reviewer_kind: assistant` from actual human reconciliation. To revise extraction, use the current collection hash as `base_collection_hash` and retain the same capture-bound OCR evidence; stale blank templates must be rebound. A human transcriber fills reviewer, timezone-bearing review time, notes, actual visual-check attestation and rows. Each row has a native integer ordinal, original name/category/locality, optional native code, a `page_locator` exactly matching an observation page and a `visual_row_locator` identifying its table row. For example:

```json
{
  "ordinal": 1,
  "name_original": "<transcribe the actual name>",
  "category_original": "<actual category>",
  "locality_original": "<actual locality>",
  "native_code": "",
  "page_locator": "pdf-page:1",
  "visual_row_locator": "table-row:1"
}
```

```sh
uv run --project apps/api python -m folkverse.liaoning_inventory reconcile-scan --file /path/to/completed-packet.json
pnpm data:liaoning:report
```

Partial transcriptions leave missing ordinals visible. Reapplying the same packet and recollecting unchanged source bytes preserve its reviewed extraction revision. A changed source invalidates the packet. This attestation confirms extraction accuracy, not translation rights, historical truth or chatbot publication.

## Draft and review explanations

```sh
pnpm data:liaoning:queue
pnpm data:liaoning:review template
```

Queue generation preserves operator-edited drafts. The packet contains 448 unapproved units: administrative and list-membership introductions plus 336 substantive launch-topic units. All 14 cities have three draft topics across at least two subjects. `launch-material.json` holds concise attributed EN/ZH context and examples bound to original raw hashes. Regenerate these with `pnpm data:liaoning:launch`; the command preserves edited drafts and rejects mismatched source revisions. Read `data/liaoning/review/<city-id>.md` before recording decisions. Draft preparation never satisfies human approval.

Edit a unit in a separate JSON file, add an actual `rights_basis`, and import it before regenerating the packet:

```sh
pnpm data:liaoning:review draft --file /path/to/unit.json
pnpm data:liaoning:review template
```

A unit specifies topic/city/subject, locale, explanatory kind, text, classification and supporting row IDs. Supported kinds include context, chronology, technique, significance, questions and conflicts. A `not_applicable` unit requires an attributed explanation; it does not substitute for the substantive launch floor. Historical claims, folklore, interpretation and creative adaptation remain distinct. Translations reference their original unit and preserve its topic, kind, city scope, subject and classification.

In a copy of `review-packet.json`, a real human inspects source originals and independently checks wording, support, classification, rights, applicability and translation. Enter reviewer, timezone-bearing time and notes; set the actual check attestations and the decision. Then:

```sh
pnpm data:liaoning:review apply-review --file /path/to/reviewed-packet.json
```

Pending, rejected, withdrawn or stale decisions cannot count as approved. Approval requires an explicit rights basis and source-support/rights checks; translations also require translation review and an approved current original. Editing the packet's draft text does not import an edit: import the unit and regenerate the packet. Decisions append history, identical decisions are idempotent, and duplicate decisions in one packet are rejected atomically. These attestations enforce honest recording; the CLI cannot authenticate a human's identity or make their scholarly judgment for them.

## Identities, shared traditions and disagreements

Equal names create unresolved candidates, not automatic merges. Native record and entity IDs remain edition/source-specific. Submit a strict relation JSON with an ID, at least two distinct `row_ids`, `kind` (`same_entity`, `different_entities`, `shared_tradition`, `conflicting_accounts`) and explanation:

```sh
pnpm data:liaoning:review link --file /path/to/relation.json
```

A relation defaults to pending. Confirmation requires named human review, timezone-bearing time and an actual review attestation. Relations retain version bindings and history; a changed source makes a former relation stale. Relations never rewrite geography or erase an original row. Explain disputed chronology in separate source-attributed `conflict` units; preserve both accounts rather than choosing an unsupported date.

## Launch and publication handoff

`launch-manifest.json` contains all 14 cities, candidate topics, reviewed topic/subject counts, current published IDs and exact readiness state. Each city needs a reviewed EN/ZH introduction plus at least three substantive topics spanning two subject categories. Each topic needs reviewed introductions, context, a term or example, and questions in both languages.

```sh
pnpm data:liaoning:review export-approved --output .local/liaoning/approved-handoff.json
```

The exported `liaoning-reviewed-unit-handoff-v1` is deliberately separate from the existing corpus restore format and says `automatically_published: false`. It is a curation handoff, not a ready-to-restore database payload. Part 4 must connect reviewed units to the existing source/passage/claim models, preserve locale and rights/version review dependencies, and exercise withdrawal before visitor use. Until that integration passes, existing publication/review commands remain authoritative.

The trusted hybrid approach includes stored reviewed facts and bounded official-source search for missing or current details. `trusted-search-policy.json` defines host, claim-support, currentness and storage rules; `trusted-search-queue.json` records discovery and coverage work. Runtime search is a Part 4 integration task, not a capability supplied automatically by DeepSeek or Ollama.

Explicit scan ambiguities, newer museum enumeration, protected-site batches 1–10 and human rights/content review remain open. They do not block independent Part 4 engineering.
