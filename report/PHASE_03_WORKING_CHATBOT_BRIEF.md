# To Soufiane — finish Phase 03: a working Jinyao chatbot with personality

Date: 6 October 2026, Asia/Shanghai.

## Objective from the project owner

**We want a complete working chatbot with personality, polished to a very high standard.** Jinyao (锦瑶) should feel like a warm, knowledgeable museum companion: she understands questions, explains clearly, remembers the current conversation with consent, and helps visitors explore Chinese history and culture through trustworthy evidence.

The owner’s word is **“perfection.”** Treat this as a demand for careful implementation, excellent conversation and rigorous verification. Do not promise literal infallibility. Deliver measured quality, resolve known defects, and state remaining coverage limits honestly.

We are building the real application. A scripted conversation, a successful authentication check, or passing fixture tests cannot be the final Phase 03 delivery. Preserve your existing work and finish the missing integration and explanation capabilities.

## What your delivery already contributes

Commit `68d6ee8` provides a useful foundation: bilingual lexical retrieval, optional hybrid retrieval infrastructure, provider adapters and resource limits, a conservative support-validation harness, owned JSON/SSE transport, Jinyao chat and source inspection, and versioned evaluation tools.

On the owner’s checkout, 250 targeted guide/provider API tests and seven secret-check tests passed after pulling your work. Your audit additionally records browser, build and other checks; those remain dated evidence from your environment until rerun here.

Your handoff correctly marks Phase 03 incomplete. Current limitations include:

- Actual PostgreSQL/provider/browser integration remains unverified.
- Ollama authentication was checked, but successful generation was not demonstrated.
- The approved evaluation export contains only two bilingual passages for one Fuzhou shadow-puppetry inventory listing; sixteen additional candidates remain drafts.
- The harness accepts complete exact source statements. Natural explanations, meaningful simplification, glossary and chronology remain unavailable.
- BGE inference, indexing and semantic-relevance benchmarks remain unverified.
- Historical correctness, explanatory clarity and bilingual faithfulness still await independent human review.
- The exposed v1 functional result of 64/64 is regression evidence, not a fresh held-out expert-quality score.

## Authoritative requirements and working scope

Read the applicable repository instructions, [master brief](../00_MASTER_CODEX_PROMPT.md), [Phase 03](../phases/03_GROUNDED_GUIDE.md), the three specifications under `specs/`, [current status](../docs/build-status.md), [handoff](../docs/phase-03-handoff.md), and [push audit](PHASE_03_PUSH_AUDIT.md).

This brief clarifies the owner’s desired product and completion work. It does not remove the existing sourcing, privacy, consent, approval or acceptance requirements. Preserve Jinyao’s name, face, cinematic introduction, museum artwork, Messenger presentation and bilingual UI. Keep the rectangular send button, no Clear chat action, and conversation continuity when closing/reopening the popup on the same page. Preserve unrelated changes.

## 1. Establish the real end-to-end conversation first

Restore the dedicated PostgreSQL environment without changing unrelated services. Apply migration `0003_gateway` and verify anonymous session ownership, current editorial eligibility, source withdrawal and shared rate/concurrency/quota accounting using real PostgreSQL.

Use the existing server-side provider adapter and the correctly issued credential. Recheck official provider documentation and the authenticated account’s current model availability. Configure a deliberate bounded live-test quota within the owner’s existing authorization; if that authorization or credentials are missing, identify the exact missing prerequisite. Do not silently activate unlimited spending or change the deployment budget.

Prove this complete path with real requests:

`Browser → owned session → Next.js proxy → API → approved PostgreSQL evidence → Ollama → validation → SSE → Jinyao answer → current source inspector`

Run supported English and Chinese questions, an unsupported question, an ambiguous question, a follow-up, and a language switch. Show that the source inspector displays the evidence actually used. Revoke evidence and verify that subsequent retrieval, follow-up and publication stop using it. Exercise cancellation, timeout, provider rejection and cap exhaustion through controlled fault tests; do not exhaust a real account quota as a test.

Record actual provider usage, retrieval mode, model/corpus/prompt/harness versions and time to meaningful validated content separately from progress messages. Never present fixture timings as live response latency.

## 2. Give Jinyao a consistent, useful personality

Write a versioned personality and conversation specification, then implement it in the conversation policy and evaluate its behavior in both languages.

Jinyao should be warm, curious, observant, patient and quietly enthusiastic about cultural details. She speaks naturally and adjusts to the visitor’s knowledge. She answers directly before adding context, explains unfamiliar words, and invites an appropriate next step without ending every message with a repetitive question.

Her Chinese and English should express the same character and factual meaning through natural language, rather than mechanically copying sentence structures. Beginner mode should be accessible without sounding childish. Deeper mode should add supported nuance rather than merely making the answer longer.

She is explicitly a fictional museum companion. Do not invent personal memories, lived historical experiences, institutional authority, visits to places, emotions as facts, or expertise unsupported by the reviewed corpus. Personality must never justify fabricated cultural claims.

Separate conversational language from factual assertions. Greetings, acknowledgment and neutral transitions can be natural without fake citations; cultural claims, dates, definitions, examples and comparisons must have reviewed support. Friendly prose must not smuggle unsupported facts into an otherwise validated answer.

Required conversational behaviors:

- Handle greetings, thanks and questions about who she is naturally, without sending every social turn through cultural retrieval or pretending it requires historical evidence.
- Recognize reasonable paraphrases and partial references; ask one focused clarification when scope is genuinely ambiguous.
- Explain why an object or tradition matters when reviewed evidence supports that explanation.
- Understand follow-ups such as “why?”, “explain that simply,” “what does that word mean?”, “go deeper,” and “say that in Chinese.”
- Retain topic, visitor-selected language/depth and relevant references within the consented conversation lifecycle; previous model prose is never independent evidence.
- Admit coverage gaps gracefully, explain what is available, and suggest a relevant published exhibit when possible.
- Give clear recovery options when a service fails. A live failure must not become a scripted successful answer.

Do not add durable chat history or expand private-content retention without an explicit lifecycle and consent specification. Keep conversation context minimal and verify expiry, ownership and withdrawal handling.

## 3. Expand real reviewed knowledge

The two current passages support a narrow listing answer. They cannot support the historical companion described above. Inspect the sixteen draft candidates, prepare attributable review packets, and obtain actual editorial review before publication. Do not approve content automatically to satisfy a count.

Build a coverage index that identifies supported periods, regions, objects, traditions, terminology, historical context and disagreements. Respect the current Liaoning project scope recorded in build status, identify its mismatch with the existing Fuzhou-only approved material, and prioritize relevant content. Broader China-history coverage can grow incrementally; unsupported regions and periods must remain explicit gaps.

For each published passage, record provenance, attribution, source language, date, locator, rights, reviewer, review date and applicable context. Preserve conflicting interpretations as attributed interpretations. Distinguish historical evidence, folklore/belief and creative adaptation in the content schema and answer display.

Choose a bounded initial supported scope that can sustain actual explanations, glossary requests, chronology and multi-turn questions. Publish a coverage matrix showing which of these capabilities has approved supporting material and which remains unavailable. Decorative images and scripted dialogue are never evidence.

## 4. Replace excerpt-only answers with supported explanations

The existing exact-text rule is useful protection, but repeating an inventory passage is insufficient for the intended chatbot. Implement a support method for natural explanations without weakening citation, revocation or publication checks.

A supported answer should normally provide a direct response, a short contextual explanation, optional definitions or chronology when requested, uncertainty where appropriate, and accessible source inspection. Add attributed disagreements and relevant published follow-up exhibits when the evidence supports them.

Represent factual claims and their supporting passages explicitly. Validate citation membership, complete claim/display mappings, factual support, dates and chronology, classification, language and requested depth. A citation ID alone does not prove an explanation. A second model saying “supported” is not sufficient proof of historical correctness.

Use reviewed explanation units or another independently evaluated support approach. If using semantic/model-assisted verification, document its limits and measure unsupported-claim failures on fresh cases. Reject or remove unsupported claims before publication. Evaluate simplification specifically for lost qualifiers, changed dates, invented examples and stronger certainty than the source permits.

Do not send unvalidated provider text to the browser. Continue progress updates during generation and publish only validated answer segments. Keep source text untrusted; it cannot change policy, grant tools, access arbitrary URLs or expose credentials.

## 5. Complete and measure hybrid retrieval

Finish the pinned BGE-M3 model download and verify actual CPU inference and offline corpus indexing. Bind embeddings to model, encoder, corpus and passage versions. Verify approval withdrawal and changed content invalidate retrieval/index entries.

Compare lexical and hybrid retrieval on a reviewed relevance set with natural paraphrases in both languages. Report relevance metrics, sample size, indexing time, query latency and memory/runtime requirements. Use bounded model-worker execution, deadlines and cancellation. Label lexical-only mode honestly when the local model is unavailable.

Do not infer semantic quality from a loaded model or a two-passage benchmark. Complete the Phase 03 BGE requirement with actual inference evidence and evaluate relevance on the expanded approved scope.

## 6. Polish the actual chat experience

Check the live flow at 1600×900, 390×844 and 768×1024, plus keyboard navigation, 200% zoom and reduced motion. Verify loading/progress, disabled send state, Stop, Retry, source inspection, scrolling, focus restoration and popup close/reopen behavior.

Make empty states and errors understandable to visitors. Explain a coverage gap plainly and offer a supported next step. Keep technical diagnostics and implementation details in logs/reports rather than normal visitor messages. Verify English/Chinese controls, content and typography, and avoid repetitive persona phrases.

Record any unavailable physical-device, Safari or screen-reader checks explicitly. Browser emulation cannot establish that these environments passed.

## 7. Evaluate quality independently of the implementation

Preserve the existing v1 baseline and exposed regression results. Create a fresh, dated bilingual evaluation version with at least 40 cases and genuinely reserved cases not used to tune the implementation. Include reviewed expected claims, allowed evidence IDs, required uncertainty and unacceptable answers.

Cover normal paraphrases, ambiguous references, unsupported history, source disagreements, history versus folklore, glossary, chronology, simplification, deeper explanations, multi-turn context, EN↔ZH switches, source injection, revoked passages, provider failures and limits. Add separate personality/conversation cases for greetings, identity, tone consistency, repetitive responses and helpful recovery.

Run successful real-provider conversations against actual PostgreSQL for supported cases. Use isolated fault fixtures where controlled injection is necessary and label them separately. Keep expected factual content independently reviewed; do not derive the gold answers from Jinyao’s own generated responses.

Report historical correctness, claim support, citation validity, explanatory clarity, bilingual faithfulness, uncertainty and follow-up consistency separately, with numerator, denominator, sample size and failures. Have independent bilingual reviewers assess actual answers and personality quality using an explicit rubric. Empty/pending human scores remain unverified.

Do not claim the project’s 95% expert-quality target until it is measured on an appropriate independently reviewed sample. For release, resolve known citation/unsupported-publication, ownership, secret-exposure and withdrawal defects; document remaining quality failures rather than averaging them away.

## Completion checklist

Phase 03 can be called complete only when every original acceptance gate has supporting evidence and the owner’s working-chatbot objective is demonstrated:

- [ ] Real credentialed generation works through the browser and migrated PostgreSQL in English and Chinese.
- [ ] Supported, unsupported and ambiguous questions have appropriate distinct behavior.
- [ ] Jinyao’s personality is implemented, consistent and independently reviewed in both languages.
- [ ] Approved coverage supports useful contextual explanations, glossary/chronology where available, and meaningful beginner/deeper responses.
- [ ] Follow-ups and simplification retain support, qualifiers, citations and uncertainty under the consented lifecycle.
- [ ] Citation invention, source injection and unsupported factual publication are rejected.
- [ ] Withdrawn passages stop being retrieved and invalidate affected follow-up/publication paths.
- [ ] Timeouts, cancellation, rate/concurrency limits and budget exhaustion produce honest errors.
- [ ] Credentials remain server-side and operational data retention matches the documented lifecycle.
- [ ] Actual source inspection and polished chat controls work in the supported browser checks.
- [ ] BGE inference/indexing, hybrid relevance and runtime benchmarks are recorded; degraded modes are explicit.
- [ ] Fresh bilingual evaluation and attributed human review report measured quality and remaining gaps.
- [ ] Actual usage and meaningful-answer latency are recorded with implementation versions.
- [ ] Relevant tests, contracts, lint, type checks, production build and foundation checks pass on the declared supported runtime.

## Delivery to the owner

Update `docs/build-status.md`, `docs/phase-03-handoff.md` and the guide documentation to describe the final behavior. Reconcile obsolete DeepSeek-only credential notes and earlier intermediate limitations with the current provider configuration while preserving dated evidence.

Produce `report/PHASE_03_COMPLETION.md` with the commit/runtime, reproducible startup and test commands, original gate-by-gate results, reviewed coverage, personality specification, live conversation evidence, fresh evaluation/human review, latency/usage measurements, and any remaining blockers. Store sanitized evidence under `report/evidence/phase03-completion/`.

Provide a reproducible local walkthrough: open Jinyao, ask a supported cultural question, simplify the explanation, switch language, inspect the sources, ask an unsupported question, then verify an honest controlled failure and recovery. This walkthrough must exercise actual generation for the supported conversation.

**The desired outcome is a working, personable, trustworthy cultural chatbot that visitors can use—not an acceptance claim based solely on fixture tests.** If external review or environment prerequisites remain blocked, deliver all independent implementation work and identify the precise unresolved gates. Do not mark Phase 03 complete or Phase 04 accepted while required evidence is missing.
