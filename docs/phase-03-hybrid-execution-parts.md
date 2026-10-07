# Phase 03 — ordered implementation parts and acceptance

Planning date: 6 October 2026, Asia/Shanghai. Execution update: Parts 0–1 requirements/design and delivery behavior are implemented; [dated report and limits](../report/PHASE_03_HYBRID_PART_01.md). Part 2 is implemented locally ([dated verification](../report/PHASE_03_HYBRID_PART_02.md)). Part 3 collection/curation and all-city draft preparation are implemented, with actual human content/rights review still open ([report](../report/PHASE_03_HYBRID_PART_03.md)). Parts 4–8 engineering/evaluation/audit are delivered. The owner declined human review on 7 October; machine source assessment now supplies a separate official-lookup launch tier. Phase 3 is accepted with complete live-pilot and machine-assessment evidence ([closure audit](../report/PHASE_03_HYBRID_CLOSURE_AUDIT.md)). This document is the execution contract, not standalone completion evidence.

Read with [the conversation and Liaoning collection design](phase-03-hybrid-conversation-plan.md). The owner will work with Codex directly. This document replaces vague next steps with dependencies, concrete defaults, review checkpoints and evidence. It makes no promise of zero defects: claims of completion require checks and recorded limitations.

## Scope and dependency order

First release: EN/ZH text, varied model-generated conversation, source-supported cultural explanations, visibly distinct broad general knowledge, bounded consented page-only context, current source inspection and honest service errors. Existing provider selection stays in the server gateway; no assumed model migration, new subscription, public deployment, voice or image analysis is included. Owner update: bounded trusted-source search is included in Part 4; registered official-directory lookup is connected to visitor chat; current operational-data adapters remain unavailable.

| Part | Deliverable | Depends on |
|---|---|---|
| 0 | Revised requirements, schemas and acceptance map | Current repository inspection |
| 1 | Reliable message delivery and sustained composer | 0 |
| 2 | Context, language and personality conversation | 1 |
| 3 | Source registry, complete baseline catalog and review pipeline | 0; can proceed alongside 1–2 |
| 4 | Supported natural explanations and general-knowledge boundaries | 2; reviewed material from 3 |
| 5 | Retrieval relevance and runtime improvements | 3–4 and a meaningful corpus |
| 6 | Final chat UX, source presentation and accessibility | 1–5 |
| 7 | Fresh functional/live evaluation and attributed machine source assessment | 2–6; implementation freeze for reserved evaluation |
| 8 | Reproducible handoff and Phase 03 closure | All required preceding gates |

Parallel workstreams mean task scheduling, not permission to spawn additional agents. No phase can pass by relying on another part's planned work. Follow the existing project instructions before changing source; preserve unrelated edits and dated evidence.

## Part 0 — settle the contract before coding

Inspect branch/status, current code, runtime, private configuration names without values, provider availability, PostgreSQL schema/corpus and old evidence. Record a baseline. Test official provider documentation/catalog only as needed; storing a credential or finding a model in a catalog does not establish successful inference.

Apply the owner's hybrid decision coherently to `phases/03_GROUNDED_GUIDE.md`, `specs/CONTENT_AND_AI_RULES.md`, guide sections in `specs/DATA_AND_API_CONTRACTS.md`, `QA_AND_DEMO.md`, `docs/guide-harness.md`, `docs/guide-live.md` and `docs/jinyao-personality.md`. Update prior completion briefs with a superseding link, preserving historical findings. Do not claim the old evidence-only rule and the new general-knowledge rule both apply to the same output.

Define structured sections with stable IDs, kind (`conversation`, `evidence`, `general`), display text, claim references and uncertainty/coverage where applicable. Each factual claim in an evidence section maps to actual current passage/unit IDs and its historical/interpretation/folklore/adaptation classification. General sections have no fabricated source mappings. Known application source URLs are the only clickable citations; model-suggested URLs remain untrusted.

Define response outcomes separately from evidence class: answered, conversational, clarification and insufficient. Transport errors remain errors rather than answer classes. Derive full displayed prose from structured sections, or validate that the composed display matches them, so an unchecked `answer_text` cannot bypass checks. Validate all source/mapping fields in server and browser and regenerate OpenAPI/types together.

Produce a requirement matrix mapping all eight old gates to their revised meaning and evidence. Preserve source honesty, withdrawal, secrets, ownership, failures, bilingual explanation and evaluation. Explicitly distinguish citation membership, claim support and independent historical correctness.

**Gate:** no contradictory live output policy; concrete schemas and downgrade rules documented; requirements describe the owner's greeting/personality and hybrid decisions. No general-knowledge output enabled ahead of its validators/UI.

## Part 1 — diagnose delivery and make every submit terminate

Reproduce the friend's `hi` symptom against the actual live browser, tracing session bootstrap, submit, BFF, API, stream parsing and rendering. Test the scripted preview separately. Do not invent a root cause if it cannot be reproduced; record the observed path and instrument safe status/error codes.

Implement an explicit turn lifecycle: draft → pending → ready/error/cancelled. Preserve the submitted question and show actionable errors. Clear pending guards on every exit. Bound transport and server deadlines, reject malformed/incomplete streams, and prevent duplicate concurrent submission. A retry is a new explicit attempt with admission accounting; do not replay a disconnected request automatically.

Remove the hard 20-turn composer stop. Bound retained history separately from the ability to send. Retain the rectangular send button, no Clear action, same-page close/reopen history and close/disconnect cancellation. Demo mode remains visibly a preview, not a fake live chat. Invalid/missing live configuration produces a visible error; no silent switch to scripted success.

**Gate:** first `hi`, repeated `hi`, 25+ turns, expired session/context, Stop/Retry, double submit, timeout, broken stream and reopen all terminate visibly. Fault tests are isolated and do not exhaust a real account quota. Preserve a reproduction/regression for any actual root cause found.

## Part 2 — language, bounded context and natural personality

Implementation and current limits: [runtime contract](guide-personality-and-context.md), [Part 2 verification](../report/PHASE_03_HYBRID_PART_02.md). Social generation currently composes vetted phrases; unrestricted cultural explanation remains Part 4.

Route complete messages rather than matching only a phrase list. Handle mixed greeting/question messages, typos, emoji, corrections, clarification answers and topic switches. A classifier may propose an intent but cannot grant policy/evidence privileges. Where a separate model routing call is needed, meter it and include it in the same total deadline; avoid unnecessary multi-call routing for simple turns.

Generate social wording in live operation. A first bare greeting receives one short invitation; repeated greetings use consented context and avoid unnecessary reintroduction. Varied wording is a behavior target, not a guarantee that no phrase ever recurs. Do not rerun generation simply because a response resembles a prior greeting. In service failure, show a localized unavailable message and recovery; a friendly prewritten line may accompany the error but cannot hide it.

Initial configurable application defaults, to verify under the documented load:

- Current message: retain the 2,000-character limit and visibly explain it.
- Consented context: newest six completed user/assistant pairs, at most 8,000 characters total; exclude pending/error/cancelled turns and secrets/tokens. Send no prior turns without consent. Keep incomplete pairs out when trimming; current question gets priority.
- Page transcript: newest 100 completed pairs, with an honest notice when older visible turns are discarded. Closing does not delete history; reload/unmount does. These are retention limits, not a 100-turn admission cap.
- Request: 64 KiB maximum encoded body in both BFF and API; validate context array roles, counts and character bounds. The larger envelope accommodates worst-case UTF-8/JSON within the smaller semantic limits, not larger unrestricted prompts.
- Signed topic/evidence context: retain a maximum 30-minute expiry and owner/version checks. Raw conversational text remains browser-supplied untrusted context; do not treat it as server-attested transcript or reviewed evidence.
- Whole pipeline: initial 40-second server deadline including routing, retrieval, generation, validation and permitted retry. BFF/client deadlines must exceed the server limit enough to receive a terminal error and stay consistent; choose and document the exact margins during implementation.

Consent is off by default. Before enabling the context window, revise the disclosure to say that recent turns will be sent to the configured provider. Raw content is not stored in application logs or durable server history; provider retention is separate and must be documented from the applicable service. Ownership comes from the signed session cookie, never submitted context.

Language precedence: explicit UI selection or recognized user request, then confidently detected EN/ZH for the current message, then last selected language for short/ambiguous input. A Chinese user message should not require one exact command to receive Chinese. Explain unsupported languages gracefully. Keep simplified/deeper intent distinct from language switching. Do not silently overwrite the visitor's choice based on quoted source language.

**Gate:** real multi-turn clarification, pronouns, correction, topic changes, EN↔ZH and varied greetings work with consent on. With consent off, unresolved references ask for clarification. Context injection, cross-session signed tokens, expiry and withdrawal fail safely. Personality is implemented here; independent quality acceptance occurs in Part 7.

## Part 3 — data acquisition and reviewed launch coverage

**6 October execution:** collection/review workflow and all-city draft floor delivered locally. 60 official resources, 1,114 inventory rows, 42 explanatory source records and 448 unapproved bilingual units. All 14 cities have three substantive topic drafts across at least two subjects. Scan extraction is saved with assistant attribution and explicit ambiguities. Actual human rights/content review remains open. No new chatbot knowledge was published. [Report](../report/PHASE_03_HYBRID_PART_03.md).

Implement the registry, named inventory reconciliation and coverage dashboard from section 6 of the companion plan. Follow source access/rights requirements. Prefer operator CLI and report artifacts for curation rather than introducing an unauthenticated admin UI.

Deliver versioned manifests for source collections, inventory rows/entities, extraction errors, duplicate/shared identities, city/county/subject associations, rights and review dependencies. Never combine API/page/OCR output into published facts automatically. Model drafting/translation assists review but creates no approval. Preserve original locators and wording, distinguish list inclusion from historical origin, and expose unresolved chronology conflicts.

Prepare a concrete launch manifest. Proposed province-wide content gate: each of the 14 cities has a reviewed EN/ZH introduction and at least three substantive topics spanning at least two applicable subject categories. A substantive topic supports an introduction, contextual explanation, at least one useful term or example, and reviewed questions/follow-ups; explain legitimately unavailable chronology/technique instead of inventing it. These targets are a readiness floor, not an acquisition ceiling or proof of exhaustive coverage.

Acquire and account for every in-scope row in the named baseline inventories. Report actual imports versus blocked/unresolved rows separately. Expand toward the earlier 10–15-topic-per-city ambition and beyond without blocking independent chatbot engineering. If launch material cannot meet the proposed all-city gate, show the exact gaps to the owner; do not unilaterally accept a smaller geographic scope.

**Gate:** reproducible idempotent imports, provenance/rights/review/version tracking, no accidental publication, inventory accounting and separate catalog/explanation/published denominators. The human publication manifest and separate machine lookup launch manifest record all city readiness statuses. Human review still gates the protected corpus publication route. Separately labelled, hash-bound machine summaries can be served through original-page-checked official lookup under the owner-authorized assessment amendment.

## Part 4 — hybrid explanation generation without evidence laundering

Owner-approved addition: connect bounded trusted-source search for missing specific facts and current details. Use reviewed stored data for stable explanations; search snippets are discovery, never final evidence. Fetch the original official page, cite URL/institution/edition/access time, assess claim support and disclose conflicts. Enforce the [trusted-search policy](../data/liaoning/trusted-search-policy.json), strict host/redirect/network bounds, content-as-data isolation and failure states. Do not grant publication approval from retrieval. The provider model alone is not a search implementation.

Replace exact-passage-only selection with structured explanation generation. Use reviewed units/variants for precise dates, quotations, glossary facts and high-risk assertions. Permit synthesis/paraphrase only through an evaluated support method. Preserve attribution, uncertainty, classification and source conflicts.

Policy table:

| Request/claim | Evidence rule |
|---|---|
| Social interaction or learning preference | Natural conversation; no cultural citation needed |
| Broad background explanation or conceptual analogy | General mode allowed with visible unverified status; do not present imagined examples as real Liaoning events |
| Specific local origin/date/person/object provenance, quotation, disputed account | Current supporting evidence required |
| Current opening hours, fees or schedules | Bounded lookup on registered trusted sources; inspect original pages and current applicability; unavailable when supporting evidence cannot be obtained |
| Medical/legal or other high-stakes advice | No specialist advice capability added by cultural scope; use an appropriate bounded response |
| Unsupported claim from a grounded draft | Remove or return insufficiency; never relabel it general to pass validation |

Evidence answers can include a direct answer, contextual explanation, requested glossary/chronology, attributed disagreements and published next exhibits. Mixed outputs label sections separately. A general explanation cannot generate source URLs or count as reviewed coverage. No claim that structural validation proves general-knowledge truth.

Validate schema, locale/depth, full display mappings, IDs, current eligibility, factual support, dates/qualifiers, classification and uncertainty. Evaluate semantic support separately from model self-assessment; known failures must be rejected or constrained. Recheck current evidence/session before SSE publication. General sections get applicability/content checks but are explicitly not fact-verified.

**Gate:** actual EN/ZH definition/context/why/simpler/deeper conversations with reviewed support; general educational answers visibly distinguished; precise unsupported local requests insufficient; mixed messages and source injection cannot bypass constraints. Server and browser agree on all new schemas.

## Part 5 — retrieval relevance and acceptable runtime

Benchmark before replacing current model execution. Use real expanded approved material and reviewed queries from different cities, categories, paraphrases and confusing names. Separate development queries from reserved relevance evaluation. Compare lexical/hybrid top-k recall/ranking and the rate of retrieving irrelevant evidence; include failures and sample sizes.

Measure model load/index time, cold/warm query duration, DB retrieval, generation/validation, end-to-end meaningful content, memory and intended concurrency. A 10–14-second cold worker is a measured optimization concern, not an acceptable hidden delay.

Investigate a bounded reusable local worker, reusing the model across queries with credential isolation and offline pinning. Bound its queue, memory, concurrency and lifetime; test cancellation, shutdown, crashes and model/corpus invalidation. A worker failure has explicit lexical-only degradation; provider failure is still an error.

Retain the existing QA target of p95 meaningful guide content below five seconds under a declared device/network/model/load, while distinguishing development timing from the full pilot sample. If the target is missed, publish measurements and the optimization/degradation decision instead of loosening it silently. A greeting uses no corpus query and is measured separately.

**Gate:** actual representative relevance/runtime evidence, no two-passage generalization, bounded execution and documented retrieval selection/degradation. BGE capability remains tested even if lexical mode is selected for a constrained runtime.

## Part 6 — finish the visitor experience

Keep the approved visual presentation. Display concise support states: “Sources checked” for assessed source-backed sections, “General explanation · not checked against our collection” for general sections, and clear coverage/service messages. Avoid an entire-answer “verified” badge. Put operational versions/timings in diagnostics, not normal chat prose.

Render structured paragraphs and optional lists accessibly, without raw HTML or arbitrary model links. Separate source-supported claims and original excerpts. Current-source polling/focus checks continue; withdrawing evidence removes the affected source-backed display and does not convert it to general knowledge.

Verify phone/desktop composition, readable EN/ZH, keyboard/IME composition, Enter/newline behavior, scroll anchoring, long messages, source focus restoration, reduced motion, 200% native zoom, Stop/Retry and reopen. Do not steal focus on every incoming message or force scroll when a visitor is reading older turns. Announce progress/errors/answers accessibly without duplicate announcements. Physically unavailable devices/Safari/screen readers remain recorded limitations.

**Gate:** meaningful desktop/mobile live workflow and accessible errors/sources; preserved artwork/controls; every required visual/environment check recorded as passed, failed or unavailable.

## Part 7 — quality evaluation and source assessment

Use a new dataset version reflecting the hybrid contract; old exact-string fixtures do not prove new conversation quality. Retain v1/v2 evidence and do not tune against their reserved cases. Prepare at least 40 dated bilingual cases, with whole EN/ZH scenario families sharing a split, reviewed gold and explicit exclusions. This minimum is phase evidence; the existing 200-question bilingual factual-support pilot remains a separate target and is not fulfilled by a 40-case run.

Include greetings, repeated greetings, fragments, emoji, typos, mixed messages, corrections, vague references, topic changes, off-topic requests, understandable definitions/context, simplification, depth, language switches, source disagreements/folklore, unsupported precision, malicious source/context, revoked evidence and service faults. Reserve a sufficient stratified portion before tuning; record authorship, review and exposure. Use sampled live greeting conversations to assess variation and invitations, not a test requiring a different exact string every time.

Use actual recorded live answers for explanation and personality assessment. Per the owner’s 7 October instruction, Codex performs machine source/bilingual/editorial assessment; owner human ratings are not required. Attribute that assessment honestly, without claiming independent specialist credentials or filling human ratings. Preserve the hash-bound human worksheet as an optional later review tool. See [the acceptance amendment](phase-03-machine-review-acceptance.md).

Report historical correctness, support, citation integrity, clarity, bilingual faithfulness, uncertainty and follow-up consistency separately. General answers are not automatically correct because they carry a label: review them against external factual evidence as well. Report scored answers, coverage/abstentions, false refusals and eligible denominators so a system cannot achieve apparent accuracy by refusing everything. Personality scoring covers warmth, directness, repetition, useful questions and honesty.

Release blockers: known unsupported precise-fact publication, invented citations, cross-session access, credential exposure, revoked-evidence reuse or silent/nonterminal message delivery. Resolve those cases and their regressions before closure; passing average scores do not erase them. Preserve the existing 100% citation-integrity target and ≥95% factual-support pilot target with their original interpretation/sample requirements; clearly distinguish measured phase samples from unfulfilled pilot targets.

Run live tests only within available explicit bounded provider authorization. Count routing/validation/generation attempts, retries and failures. Missing review, credentials, quota or hardware is a precise blocker, not permission to fabricate results. Fault fixtures are separate and no production quota is exhausted as a test.

**Gate:** fresh functional/live evidence, attributed actual review, separate numerator/denominator/sample/exposure reports, no unresolved release blockers, and remaining pilot/device/coverage limitations explicitly classified.

## Part 8 — closure and reproducibility

Run relevant supported-runtime API/browser suites, deterministic contracts, lint/types/build, secret/foundation/artwork checks. Re-run broad suites when changes or failures justify it, not repeatedly to manufacture confidence. Reproduce startup/migrations from a clean intended environment without committing ignored credentials, weights or optional caches. Never restore over populated content tables or delete volumes to resolve an unexplained issue.

Update status, setup, guide docs, privacy disclosure, coverage/retrieval manifests and the completion report. Add new dated evidence rather than overwrite original failures. Record actual provider, approved corpus and model/prompt/harness versions; real usage, meaningful-content latency, fixture results and unavailable environments remain distinct.

Maintain two status rows: **chatbot engineering acceptance** and **province-wide content readiness**. The broader content program can continue, but Phase 03 product acceptance needs the agreed launch manifest and all revised required gates. A narrower launch is an explicit owner scope decision, never inferred from elapsed time, review delays or a successful narrow demo.

Final walkthrough: greet → answer invitation → supported cultural question → why/definition → simplify/deepen → language switch → sources → general knowledge beyond corpus → unsupported exact local detail → topic change → repeated greeting → controlled failure/recovery. Test a long session separately. Keep live and injected-fault evidence distinguishable.

**Gate:** every revised gate has concrete evidence, launch scope is documented, reproduction succeeds, and the report contains no false completeness or quality claim. Phase 04 starts as a separate saved-journey implementation; it does not conceal unfinished Phase 03 gates.

## Plan review checklist before implementation

- [ ] Part 0 maps all original gates and updates conflicting source/publication rules together.
- [ ] Context disclosure, bounds, provider usage and retained history have explicit behavior with consent on/off.
- [ ] Every message class and failure has a terminal UI state; no permanent turn-count block.
- [ ] Evidence-required claims cannot escape through social/general classification or fallback.
- [ ] Complete source inventories are tracked separately from acquired, explained and reviewed content.
- [ ] All 14 cities are in the launch readiness manifest; blocked/unknown denominators stay visible.
- [x] Assessment authorship and reserved evaluation exposure are explicit; no human ratings are fabricated.
- [ ] Application changes, secrets, migrations, production activation and deployment are not implied by this planning document.

Track implementation of each part in `docs/build-status.md` with exact pass/fail/blocker evidence. These empty checklist boxes are future execution gates, not missing planning prose or invented completed work.

## Parts 4–5 implementation evidence — 7 October 2026

Hybrid explanation/support engineering and retrieval measurement/optimization are delivered locally: [Part 4](../report/PHASE_03_HYBRID_PART_04.md), [Part 5](../report/PHASE_03_HYBRID_PART_05.md). Official lookup covers the registered directory and conservative projections; current operational details remain unavailable. Expanded approved relevance gold and independent human assessments are still open acceptance evidence. Diagnostic drafts are never runtime evidence. Parts 6–8 and province-wide content readiness are not closed by these deliveries.

**7 October amendment:** The owner declined human review. Machine source comparison and bilingual editorial assessment now cover 42 official profiles, with a separate all-city lookup launch manifest and explicit no-human-review labels. Historical references above to open human publication or independent human assessment do not require the owner to complete a worksheet. The protected corpus remains separately gated. The full 200-question pilot completed (192/200 scenarios; 89/89 source support/citations), followed by exposed corrective checks and actual-answer assessment. The additional $0.15 was explicitly authorized. [Final closure evidence](../report/PHASE_03_FINAL_COMPLETION.md); Phase 4 is next.

**Closure — 7 October:** Parts 0–8 are implemented and accepted against the linked evidence. The unchecked planning-review boxes above preserve the original preimplementation checklist; current phase acceptance is recorded in the phase file and closure audit. No promise of exhaustive content or perfect model output.
