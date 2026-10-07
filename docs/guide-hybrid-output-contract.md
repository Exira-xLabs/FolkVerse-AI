# Jinyao hybrid output design v1

Status: approved direction for the Part 4 sections migration; not the current output schema. The bounded request context and checked social composition are now implemented in [the Part 2 runtime contract](guide-personality-and-context.md).

## Request and lifecycle

Keep the current owned `POST /api/v1/guide`, question length 1–2000, EN/ZH locale, concise/beginner/deeper depth, optional exhibit, topic/evidence context and consent. Add a bounded `conversation` array of completed pairs only when context consent is true. Maximum six pairs and 8,000 characters total; validate roles/content and ignore any supplied policy, evidence assertion or owner. Body cap 64 KiB in API/BFF. The Part 2 runtime installs both request validators and the 64 KiB boundaries together.

The browser owns page-only transcript retention, with no permanent send-count cap. Signed references still expire and recheck ownership/evidence. Raw history is untrusted, not signed provenance. No durable content logs/history are introduced. Disclosure and consent must cover transmission of recent turns to the configured provider before context is enabled.

## Output design

Retain answer ID, locale/depth, response outcome, current-source metadata, provider reference and operational versions. Add `contract_version=hybrid_sections_v1`, structured `sections`, and explicit support metadata. This design must become Pydantic/OpenAPI/generated TypeScript together in Part 4; client-only hand-maintained types cannot substitute.

Each section has unique `section_id`, `kind=conversation|evidence|general`, text and claim IDs. Compose visible text from sections, rejecting extra independent display prose. Conversation sections are non-factual social language. Evidence-section factual clauses all map to validated claims; general sections have no supporting IDs and display a non-verified label. Clarification/insufficiency states cannot pretend to be source-backed answers.

Each evidence claim includes unique claim ID, statement, supporting passage/unit IDs, historical/interpretation/folklore/adaptation classification, and actual support method/version. Exact reviewed statements and reviewed explanation variants are supported baseline methods. Natural synthesis needs separately evaluated semantic support checks; model self-assessment does not establish truth. Known precise-fact failures remain rejected. Citation integrity and historical correctness are distinct.

Current eligible evidence covers every claimed source reference; related exhibit IDs resolve to current published exhibits. Source URLs are from known metadata, not generated prose. Recheck evidence immediately before emission and clear stale source-backed display on inspector revalidation. General sections cannot borrow source-backed labels or be republished as approved data.

## Routing and downgrade rules

| Input | Allowed response |
|---|---|
| Greeting, thanks, goodbye, preference | Generated non-factual conversation; greeting invitation, no forced question after goodbye |
| Cultural question with supporting evidence | Supported explanation with actual citations |
| Broad conceptual/background question | Separately labelled general explanation when evidence is unavailable |
| Precise local origin/date/provenance, quotation, disputed/current fact | Supporting evidence or insufficiency |
| Mixed social/factual message | Social acknowledgment plus the applicable factual policy |
| Rejected grounded draft | Remove/refuse unsupported content; no automatic general relabel |
| Provider failure or budget exhaustion | Terminal service error with recovery, no scripted success |

Intent/model-confidence alone cannot decide that embedded factual claims are safe. A general answer remains unverified even after structure and applicability checks. Publishing an unverified answer is not a scored historical-correctness result.

## Streaming compatibility

Keep `meta/status/answer/sources/done/error`; never forward raw provider tokens. Validate full sections and mappings server-side, then repeat structural/mapping/label checks in browser. Emit one terminal success or error; malformed/incomplete streams publish no proposed answer. Old schemas remain accepted only on their existing strict path during a deliberate migration, never through permissive fallback.

## Original gate mapping

| Original gate | Revised acceptance |
|---|---|
| Real credentialed call | Real EN/ZH UI/provider path, bounded usage and versions |
| Supported/unsupported distinction | Evidence-required gaps remain insufficient; general educational context explicitly labelled |
| Citation/injection rejection | Actual mappings and content checks; mixed/social/context cannot bypass factual policy |
| Withdrawal/timeout/caps | Current source checks and terminal honest errors, including social calls |
| Secret boundary/source drawer | Server-only credentials, known source URLs, real current-source inspection |
| Expert evaluation | Fresh bilingual support/correctness/clarity/personality scoring, uncertainty/coverage separated |
| History/folklore/chronology | Classified supported facts, attributed conflicts, no unsupported precision |
| Follow-up/glossary/depth | Useful consented conversation, supported simplification, general sections labelled; no silent delivery/permanent turn cap |

## Release and versioning

No schema declaration here claims deployed capability. Require rejection tests for fabricated mapping/display/classification, unsourced precise claims, evidence-to-general laundering, mixed-message bypass and client-history injection. Test natural varied live greetings and meaningful explanations separately from fixtures. Human gold/content review is actual attributed work. Preserve existing 200-question pilot targets separately from minimum phase samples.

## Implemented runtime — 7 October 2026

The live API/browser now use `hybrid_sections_v1`. Independent support methods, separated general sections, registered official lookup and explicit human-reviewed-unit publication are implemented. See [runtime behavior](guide-hybrid-explanations.md), [Part 4 delivery](../report/PHASE_03_HYBRID_PART_04.md) and [Part 5 measurements](../report/PHASE_03_HYBRID_PART_05.md). Earlier design targets remain targets where expert review, current-details adapters or arbitrary factual synthesis have not been validated.
