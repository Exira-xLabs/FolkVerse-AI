# Soufiane / Codex — finish Phase 03 before claiming acceptance

Date: 6 October 2026, Asia/Shanghai. Reviewed base: `a1b2a66`.

## Owner objective

**Finish Phase 03 as a real working, personable Jinyao chatbot.** The owner wants exceptional polish and useful conversation, not only a narrowly working inventory selector. Keep the current implementation, finish its missing capabilities, and verify the result. Do not rebuild the project or start Phase 04 as a substitute for completing Phase 03.

Your latest delivery is real progress: it records PostgreSQL integration, successful bilingual Ollama browser conversations, BGE inference and a personality policy. The owner's checkout also passes `node scripts/test-guide.mjs`: **271 tests, one existing deprecation warning**. Those newly rerun tests are portable regressions; your recorded live/browser/database checks remain evidence from your environment until reproduced on the delivery environment.

The phase is still partial for the reasons below. The previous [working-chatbot brief](PHASE_03_WORKING_CHATBOT_BRIEF.md) remains the product objective; this brief focuses on the remaining work after your latest commit.

## Read first and preserve

Read applicable `AGENTS.md` instructions, [master brief](../00_MASTER_CODEX_PROMPT.md), [Phase 03 and all eight gates](../phases/03_GROUNDED_GUIDE.md), the three files under `specs/`, [current status](../docs/build-status.md), [current completion report](PHASE_03_COMPLETION.md), [handoff](../docs/phase-03-handoff.md), [coverage matrix](../docs/guide-coverage.md), [personality policy](../docs/jinyao-personality.md), and [evaluation methodology](../docs/guide-evaluation.md).

Preserve the approved artwork, Jinyao's face/name/introduction, Messenger layout, rectangular send button, no Clear action and same-page close/reopen conversation continuity. Preserve unrelated edits. Use the declared Node 22 runtime and locked Python/pnpm dependencies. Do not overwrite a populated content database, fabricate approval, expose credentials, change unrelated system services or deploy publicly through this task.

Important correction to the earlier brief: **复州 is in Wafangdian, Liaoning; it is not 福州 in Fujian.** The existing approved scope is geographically consistent. The actual problem is its very limited approved explanatory coverage.

## Missing work and how to complete it

### 1. Approved knowledge that supports more than one listing

**Current state:** one published exhibit, two EN/ZH passages and one approved source. Additional exhibits/passages and the five-unit explanation packet remain drafts. More inventory rows alone will not establish explanatory expertise.

**Action:** inspect `data/review-candidates/phase03-part5.json` and `data/review-candidates/phase03-explanations.json`. Prepare a reviewer-ready packet with exact source locators, attribution, rights basis, EN/ZH wording, contextual scope and classifications. Prioritize relevant Liaoning material and enough depth to answer definitions, cultural significance, historical context and follow-ups within a clearly declared initial coverage boundary.

Resolve the flagged chronology discrepancy using independent authoritative evidence; preserve attributed source disagreement where it remains unresolved. A recognition year is not an origin year, and a source's review/fetch date is not a historical event date.

Obtain actual content, rights and translation review before publication. Source approval does not automatically approve new explanatory wording. Bind approved units to content/version/review records and existing eligibility rules. Publish a coverage matrix identifying supported questions, explanations, periods/regions and remaining gaps.

**Evidence required:** actual reviewer attribution and dates, passage/unit IDs, provenance/rights records, published counts, approved bilingual examples and withdrawal behavior. If human review is unavailable, finish the schema/import/review packet and independent implementation, then report precisely which approvals are missing. Never fill approval fields on behalf of a reviewer.

### 2. Useful explanations with validated factual support

**Current state:** `guide_harness.py` requires complete exact source statements, `source_statement` classification and a narrow listing scope. `inventory_projection()` reorders a recognized listing. Deeper mode does not supply historical depth; glossary, chronology, importance and historical “why?” remain gaps. Approving additional content alone will not make these capabilities work.

**Action:** implement versioned, classified reviewed explanation units for the initial supported scope. Extend retrieval, intent handling, answer schema, support validation and browser publication validation together. Give units explicit supporting passages, language, applicable topic/scope, classification, dates when relevant, and review/version metadata.

Support a direct answer, contextual explanation, requested glossary or chronology, attributed disagreement, useful examples where reviewed, uncertainty and published follow-up exhibits. Keep documented history, interpretation, folklore/belief and creative adaptation distinct. A fictional personality must not grant authority to cultural claims.

Allow natural wording through reviewed variants/units or another independently evaluated support method. Do not simply remove the exact-text check and trust arbitrary model prose. Validate each factual claim and all displayed prose against the evidence and classifications, including dates, qualifiers and confidence. A second model's support label alone is insufficient proof.

Continue to publish only validated content over SSE. Recheck withdrawal/current eligibility before publication and source inspection. Unsupported material must be removed or yield insufficiency rather than a plausible explanation.

**Evidence required:** real EN/ZH conversations covering a definition, cultural significance, chronology or attributed disagreement, beginner simplification and a genuinely deeper explanation within approved coverage. Include tests that reject invented examples/dates, missing qualifiers, upgraded certainty, wrong classification, irrelevant citations and revoked units.

### 3. A consistent personality across flexible conversation

**Current state:** personality is specified, but greeting/identity/thanks/start behavior is a small fixed full-match policy. Cultural output remains controlled listing presentation. These are useful implemented behaviors, not independently validated natural conversational quality.

**Action:** retain safe social replies and broaden intent handling for ordinary wording, mixed social/cultural turns, partial references and natural follow-ups. A greeting followed by a cultural question must still invoke cultural support validation. Recognize “why?”, “what does that mean?”, “explain simply”, “go deeper” and language switches without requiring one exact phrase.

Keep Jinyao warm, patient, curious and concise. Answer first, add relevant context, and offer a useful next step without repetitive closing questions. English and Chinese should feel natural with equivalent meaning. Separate non-factual conversational language from cultural assertions; enforce support checks on any facts introduced by that language.

Carry only minimum consented topic/reference/language/depth context. Verify owner binding, expiry, withdrawal and consent-off behavior. Previous model text is never an independent source. Preserve page-only history unless the owner explicitly authorizes a new storage lifecycle.

**Evidence required:** a versioned conversation rubric and real multi-turn examples demonstrating tone, useful references, corrections/clarifications, graceful gaps, language switches and recovery. Obtain independent bilingual personality review; hardcoded policy checks alone cannot pass that review.

### 4. Fresh independent quality evaluation

**Current state:** exposed v1 passes regression targets. New v2 has 48 machine-authored cases; 24 development cases pass and 24 reserved cases are unexecuted. Historical correctness, clarity, bilingual faithfulness and personality have zero human-scored denominator.

**Action:** keep v1's original baselines and exposed interpretation intact. Have independent reviewers adjudicate expected claims, permitted evidence, required uncertainty and unacceptable outputs. Keep reserved cases unavailable to implementation tuning; if they become exposed while preparing this work, explicitly version a fresh reserve instead of presenting them as untouched.

Update the evaluation to cover substantive approved explanations, not only correct abstention on glossary/chronology. Keep at least 40 dated bilingual cases with both languages of each family in the same split. Include paraphrases, ambiguity, follow-ups, simplification, depth, disagreements, folklore versus history, injection, withdrawal and failures. Add separate personality criteria and bound review records for them; the existing `guide_review.py` human dimension enum does not include personality.

Run development checks first. After implementation is frozen and gold review is complete, execute the reserve. Run supported cases against real PostgreSQL/provider integration under the authorized bounded quota. Keep injected faults and fixtures clearly separated from live answers. Have reviewers grade actual recorded answers with identity, timestamp, rationale, independent basis and run hashes.

**Evidence required:** numerator/denominator/sample size and failures for historical correctness, claim support, citation validity, clarity, bilingual faithfulness, uncertainty and follow-up consistency, plus attributed personality assessment. The project's 95% target needs a justified independently reviewed sample; no score is inferred from code, fixtures, review templates or copied passages. Pending review remains pending.

### 5. Representative hybrid retrieval and usable latency

**Current state:** BGE inference/indexing now work. Two passages and six diagnostic queries cannot establish semantic relevance. Cold query workers took roughly 10.66–14.25 seconds; dense retrieval is disabled in the normal preview.

**Action:** expand the approved corpus first, then create independently reviewed EN/ZH relevance queries with paraphrases and confusable topics. Compare lexical and hybrid retrieval using relevance metrics such as recall@k and ranked relevance, with stated sample sizes. Measure retrieval-only timing, end-to-end checked answer timing, cold/warm startup, memory and concurrent load separately.

Investigate repeated model startup. A bounded reusable worker or batched strategy may reduce cold latency, but preserve the current credential-free environment, offline model pinning, cancellation/deadline enforcement, bounded concurrency and clean shutdown. Do not enable dense retrieval merely because the weights load. Select a measured configuration and document when lexical-only degradation occurs.

**Evidence required:** actual inference/index versions, corpus hashes, reviewed relevance results, latency distributions and memory measurements. State a supported runtime/load envelope and show the selected configuration stays within its deadlines. Do not substitute two-passage diagnostic timing for a representative benchmark.

### 6. Finish visitor-facing and delivery verification

**Current state:** recorded Chromium, keyboard, CSS zoom and reduced-motion checks pass. Native zoom, physical phones/keyboards, Safari and screen-reader environments remain unverified. The recorded live preview was on your machine; ignored credentials, model weights and local runtimes do not arrive through Git.

**Action:** verify the changed real chat at 1600×900, 390×844 and 768×1024. Check keyboard focus, source dialogs, scroll behavior, Stop/Retry, close/reopen history, EN/ZH typography, 200% native zoom and reduced motion. Use physical-device/Safari/screen-reader checks where accessible; identify unavailable environments precisely.

Make a fresh checkout reproducible through setup documentation rather than copying private `.env` or assuming ignored local files exist. Reproduce migrations, provider selection, corpus eligibility, live generation and actual source inspection in the intended delivery environment. Keep process-only local-test overrides distinct from production configuration. Use only the existing authorized bounded quota; a missing credential/budget decision must be reported rather than guessed.

**Evidence required:** sanitized current screenshots/results, supported-runtime checks, live walkthrough and setup commands with documented prerequisites. Update stale credential/retrieval/metric notes so current documentation is coherent while old evidence stays clearly dated.

## Implementation sequence for Codex

1. Inspect current source/state, original eight gates and this brief. Record the baseline and preserve unrelated edits.
2. Prepare content review and independent evaluation packets early. Continue schema, unit-support, intent, personality and UI work while waiting for real reviews.
3. Complete approved-unit retrieval, explanation/classification validation and browser/SSE support as one integrated change. Add meaningful targeted tests for new behavior and failures.
4. Publish only actually approved material, then demonstrate real bilingual multi-turn explanations and sources.
5. Optimize and benchmark hybrid retrieval against that expanded supported corpus.
6. Obtain independent answer/personality review, freeze implementation, and run the fresh reserve/live evaluation. Preserve failures; do not rewrite gold to pass.
7. Finish relevant browser checks, reconcile documentation and deliver a gate-by-gate evidence report. Continue independent work if an external prerequisite is blocked, but keep the phase partial until required evidence exists.

Useful existing checks:

```sh
node scripts/test-guide.mjs
pnpm test:api
uv run --project apps/api pytest apps/api/tests/test_postgres_integration.py -q
pnpm exec playwright test -c playwright.guide.config.ts
pnpm test:e2e
pnpm lint
pnpm typecheck
pnpm contracts
pnpm build
pnpm test:secrets
pnpm check:foundation
```

Inspect each live script and its quota/settings before executing it. Extend evaluators and commands as needed for the new units; do not run an old narrow evaluator and call it evidence of new explanation quality.

## Required final handoff

Update `docs/build-status.md`, `docs/phase-03-handoff.md`, `docs/guide-coverage.md`, the personality/evaluation/retrieval docs and `report/PHASE_03_COMPLETION.md`. Record a new dated evidence directory rather than overwriting the earlier baseline.

The report must include all original Phase 03 gates with PASS/PARTIAL/FAIL/UNVERIFIED and concrete evidence, approved coverage, explanation support design, reviewed personality results, independent evaluation, actual provider usage/meaningful-content latency, hybrid relevance/runtime, reproducible setup and any remaining blockers. Distinguish this machine's checks from your machine's evidence and live responses from fixtures/social policy replies.

Final walkthrough: a visitor opens Jinyao, asks a supported cultural question, asks “why?”, requests a definition, simplifies, goes deeper, switches language, inspects actual sources, asks something unsupported, and experiences an honest controlled failure/recovery. All cultural answers must use real approved evidence and the configured live gateway; no hidden scripted fallback.

**Completion means a useful, trustworthy, personable chatbot within a clearly declared reviewed scope, with all original gates evidenced.** It does not require pretending to know all Chinese history. It does require delivering the explanation capabilities that the present listing-only implementation lacks. Phase 04 remains personalized saved journeys and is not a substitute for this unfinished work.
