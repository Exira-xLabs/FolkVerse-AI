# Guide explanation harness

Part 3, 6 October 2026 (Asia/Shanghai). The internal harness is implemented for the **existing narrow reviewed heritage-listing corpus**. It is a conservative evidence harness, not a demonstrated expert on Chinese history. [Phase sequence](phase-03-plan.md).

Part 6 updates `guide-extractive-v2`: signed prior evidence versions are checked against current eligible passages independently of retrieval rank, title query or requested language. Locale switches then retrieve separately reviewed passages in the new language. Actual SQL EN↔ZH and withdrawal regressions verify this behavior. Frozen evaluation results and the initial baseline are in the [evaluation contract](guide-evaluation.md).

Push audit updates `guide-extractive-v3` with bounded full-title inventory/locality/category paraphrases in EN/ZH. Origin/dynasty qualifiers and added instructions still fail the scope gate; generated rewriting remains unavailable. The exposed v1 regression now meets 64/64 functional targets, with human dimensions pending. [Audit](../report/PHASE_03_PUSH_AUDIT.md).

## Request and context

`GuideRequest` accepts a bounded question, EN/ZH locale, concise/beginner/deeper depth, optional published exhibit ID and optional explicitly consented follow-up token. Unknown fields are rejected. Raw previous answers cannot be submitted as trusted context. The eventual public endpoint must authenticate the anonymous session before calling the harness; Part 3 itself adds no public endpoint.

The SQL repository derives topics from currently published localized exhibit titles and retrieves only approved, rights-cleared passages through the Part 1 gates. Exact supported listing/overview question patterns and full topic names are required in this initial version. Partial names, multiple topics and unresolved follow-up references prompt clarification. Questions about periods, technique, definitions or chronology receive bilingual insufficiency even if they share the exhibit's vocabulary. This deliberately limited grammar can reject reasonable paraphrases; broad question interpretation remains an extension requiring evaluation.

Follow-up tokens contain only an HMAC-bound session owner, exhibit ID, previously used evidence IDs/versions and uncertainty. They are signed, expire after thirty minutes and require explicit consent on every request that uses them. They contain no raw question or model answer and are not stored server-side. Closing or reloading UI does not create server history. Cross-session, tampered and expired tokens are rejected. Explicit selection of another exhibit discards old scope. A language switch uses separately reviewed passages in the new language; no model translation is treated as evidence.

## Explanation and factual support

A trusted bilingual scaffold introduces source statements. Every factual segment must be a **complete, exact reviewed passage**, mapped to its actual passage/source IDs, and associated with the resolved published exhibit. Source title/institution attribution is generated from approved metadata. Generated free prose, shortened quotations, removed qualifiers, paraphrases, fabricated dates, invented glossary definitions and extra narrative/URLs cannot pass.

This is a conservative entailment restriction beyond ID validity: a real citation with a changed statement fails. It does not claim to validate arbitrary semantic paraphrases or establish the historical correctness of the source independently of review. New expert explanations need a stronger independently evaluated support method and broader real reviewed coverage. A second model's own support label is not introduced as proof.

Locale/depth, unique claim IDs, unique statements, mapped displayed sections and related exhibit IDs are checked. Concise depth permits one statement; beginner/deeper permit up to three distinct available statements. Evidence is bounded to fit output framing without truncating a source fact. If only one narrow fact exists, a deeper request cannot invent more. Simplification follow-ups can re-display the original reviewed wording with citations and partial uncertainty; **rewritten beginner explanations are not yet delivered**.

All current statements remain labelled attributed `source_statement`. The model cannot promote them to historical certainty, scholarly interpretation, folklore or creative adaptation. Structured reviewed classifications, dated events, glossary definitions and conflicting interpretations are absent from the current corpus; those requested explanations remain gaps. No automated historical chronology is inferred from review/fetch dates, no creative narrative is offered as history, and no historian/institutional identity is claimed for fictional Jinyao.

## Orchestration and publication

The harness loads current reviewed coverage, resolves scope, checks bounded listing eligibility, requests structured selection from the Part 2 gateway, validates the entire candidate, and rechecks revocation/metadata before returning answer segments. SQL operations run in worker threads with fresh sessions; the configured outer deadline covers retrieval, generation and final validation/recheck. Part 2 independently enforces admission, per-attempt budgets, cancellation and provider limits. Cancellation/failure never returns a canned sourced answer.

Question and passage content are JSON-delimited untrusted data; the system policy comes from application code. Known suspicious instruction markers cause an early insufficient response. That conservative filter is not a general prompt-injection detector: additional protection comes from no tools/URL execution and the exact reviewed-statement publication rule. Model-selected source links are forbidden; the answer inspector receives original approved metadata. Part 4 must render source/user strings as plain text and implement the actual inspector/SSE controls.

A provider failure propagates its sanitized unavailable/timeout/cap error. Schema, citation, support, classification or mapping failure returns localized insufficiency without the rejected factual content. Any evidence change between retrieval and publication removes the entire answer. No claim is streamed during generation. Final rechecks still have a small normal database read/publication race; no cross-transaction editorial lock is claimed.

Returned answers include claims, source excerpts/metadata, evidence and published related IDs, coverage limit, corpus/retrieval/prompt/harness versions and provider attempt reference. Every answered result is `partial` for this corpus. The metering ledger's completed status means provider transport completed; it does not mean the explanation was accepted or published. Actual meaningful-answer latency remains Part 4's responsibility.

## Credential and verification state

The supplied credential was saved only in ignored `.env` with restrictive permissions. `.env.example` remains placeholders. A server-side authentication-only `GET /models` check returned HTTP 401; no evidence/question, generation request or paid completion was sent. The key is not currently verified for DeepSeek. Demo mode and the zero budget remain in place; no live activation was inferred from storing a credential.

The dedicated PostgreSQL container is still absent. SQL repository and safety rules are tested against disposable SQLite/synthetic reviews; the gateway uses mocked HTTP. These results do not certify real PostgreSQL concurrency, credentialed model replies, production performance or historical expertise.

The Part 3 test file covers 66 cases. Combined with retrieval/gateway/outage regressions, 152 checks pass. These are deterministic functional/security tests, **not** the dated held-out 40-case expert evaluation or a 95% quality score. Part 6 still owns that evaluation, and broader explanations still require reviewed evidence.

## Integration handoff

`app.state.guide_harness.answer(request, authenticated_session_id)` returns a fully checked `GuideAnswer` or a sanitized failure. The instance is ready for Part 4's owned POST endpoint, validated fetch SSE, Jinyao chat, source inspection, disconnect cancellation and lifecycle maintenance. The UI and existing labelled previews were not changed by Part 3.

Part 4 update, 6 October 2026: the owned JSON/SSE endpoint, BFF, plain-text Jinyao chat/source inspector and lifecycle maintenance are now connected. [Transport and publication contract](guide-live.md). The broader expert explanation/evaluation limitations above remain.
