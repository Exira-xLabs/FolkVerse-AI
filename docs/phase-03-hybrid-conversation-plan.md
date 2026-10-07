> 7 October owner amendment: human review is not required from the owner. Codex performs explicitly labelled machine source assessment for original-page-checked lookup; protected human corpus publication is unchanged. See [acceptance amendment](phase-03-machine-review-acceptance.md).

# Phase 03 — hybrid Jinyao conversation plan

Status: agreed product direction; implementation design and launch scope pending final review. No application changes made.
Date: 6 October 2026, Asia/Shanghai. Owner: project owner, working with Codex directly.
Base inspected: `6d6096a` with application delivery `a1b2a66`.

## Agreed objective

Build a real English/Chinese cultural companion who understands ordinary messages, responds naturally with a consistent personality, explains clearly and uses trustworthy evidence. Cover Liaoning through a growing reviewed corpus without requiring that every possible answer be prewritten. The owner approved hybrid knowledge and explicitly requested varied greeting responses and useful questions after greetings.

This plan precedes implementation. The original Phase 03 exact-source publication contract must be revised explicitly before broader model explanations are introduced. Previous reports remain historical; new capability claims require new evidence. The owner now handles this phase rather than delegating it to the friend.

Execution order, concrete defaults, evidence requirements and part-by-part gates are defined in [the execution parts](phase-03-hybrid-execution-parts.md). Read both documents as one plan. The execution parts resolve implementation detail; original requirements remain authoritative until the documented hybrid revisions are applied in Part 0. Planning is complete when this cross-document review passes; editorial approval and actual quality scores are implementation/release prerequisites, not facts this plan can create.

## Current findings

- Live `social_intent()` recognizes a short full-match phrase list, including `hi`; it returns one fixed policy reply per intent/language.
- Live requests require application live mode and a valid database-backed session before social handling. Demo mode is a scripted preview.
- The UI stops accepting turns at 20 and has pending/controller guards. The eventual design must bound context without permanently disabling conversation at an arbitrary turn count.
- Cultural generation selects exact passages; the browser independently reconstructs permitted fixed displays. Natural generation requires coordinated schema, server and browser changes.
- The signed context contains evidence/topic references rather than ordinary conversational history. Real topic continuity and varied greetings require a defined bounded context contract.
- The friend's missing `hi` reply is not reproduced. These findings are diagnostic candidates, not an asserted root cause.

## 1. Conversation behavior

Every accepted text message reaches one terminal state: useful response, focused clarification, transparent limitation/refusal, cancellation or visible actionable error. Empty whitespace is blocked visibly at the composer. Unsupported attachments are identified as unsupported rather than ignored; uploads/vision are outside this phase.

| Message class | Intended response |
|---|---|
| First greeting, emoji greeting, casual opener | Warm short reply and one low-effort invitation; no cultural citation required |
| Repeated greeting | Acknowledge naturally, avoid repeating introduction, use current topic or offer a different invitation |
| Thanks, goodbye, praise, dissatisfaction | Appropriate brief social reply; respect closing instead of insisting on another question |
| Identity / abilities | Honest fictional identity, available capabilities and scope without invented personal experience |
| Cultural question with reviewed evidence | Direct answer and natural supported explanation, real source inspection |
| Broad educational question beyond corpus | Qualified general model explanation where appropriate, visibly distinct from reviewed evidence |
| Exact local date/origin/quotation/disputed account without support | State what is missing; clarify or offer a sourced topic; do not invent precise facts |
| Mixed greeting and factual question | Acknowledge briefly, then answer the actual question with its evidence requirements |
| Vague or ambiguous question | One focused clarification; accept its answer as conversational context |
| Follow-up, correction, requested comparison, simpler/deeper answer | Resolve the reference, honor the change, preserve support and uncertainty |
| Typos, fragments, emoji, mixed EN/ZH, unfamiliar language | Interpret when reasonably clear; otherwise ask a short clarification or explain supported languages |
| Off-topic ordinary question | Brief helpful response within capability, then optional return to culture; no forced redirect on every turn |
| Unsafe request, abusive input, malicious instructions | Appropriate safe boundary or calm redirection; never execute arbitrary tools or reveal secrets |
| Service outage, invalid session, cap/timeout | Visible recovery state; distinguish service failure from missing knowledge |

“All kinds of messages” means robust interpretation and graceful handling, not guaranteed factual answers, arbitrary tools, every language or every media type.

## 2. Personality and explanation style

Jinyao is warm, patient, curious and clear. She responds directly, uses familiar words, defines unfamiliar terms and adjusts length/depth. She claims no lived historical memories or institutional authority. Natural English and Chinese share meaning and character without mechanically translating sentence structure.

Initial greeting examples illustrate behavior, not a finite response script:

- “Hi! What would you like to explore—Liaoning's history, local food, or something else?”
- “Hello! Are you curious about a particular city, or would you like a starting point?”
- Mid-conversation: “Hi again! Shall we continue with that tradition, or explore something new?”

Generate context-aware greetings through the model in normal live operation. Retain a small localized fallback for service failures, clearly identified as limited service behavior rather than a successful AI reply. Do not guarantee uniqueness through random synonym substitution or unbounded regeneration. Supply recent assistant wording and intent so repeated introductions, questions and phrases can be avoided.

Ask one useful question after a first bare greeting. Elsewhere ask questions only when clarification or exploration helps. A direct question deserves an answer first. Thanks/goodbye can finish naturally. Beginner mode simplifies language while preserving qualifications; deeper mode adds supported context, not filler. Use lists or chronology only when they improve understanding.

## 3. Hybrid knowledge contract

Use structured response metadata and claim-level support, not a decorative trust label alone. “Reviewed evidence” describes provenance and assessed support; it is not a guarantee that every source statement is historically true. Actual historical correctness is a separate evaluated dimension.

1. **Conversational:** non-factual social language; no invented citations.
2. **Reviewed evidence:** cultural claims supported by current approved passages/units; actual citations and source inspection.
3. **General explanation:** model knowledge beyond reviewed coverage, with clear non-verified status. Suitable for broad orientation; not unsupported exact local facts, quotations, disputed claims or current information.
4. **Clarification / insufficient evidence:** explain the specific gap and ask one helpful question or suggest an available topic.

For mixed answers, identify supported claims and separate general context in the display. Do not badge an entire mixed response as verified. Model confidence is not a verification method. A retrieval match is not proof that all generated claims are supported. A failed grounded claim cannot be relabelled as general knowledge to bypass validation. Required-evidence questions stay insufficient when support is absent.

The model may explain, compare and reason from evidence. Application checks still validate schema, allowed IDs, mappings, classifications, dates, source versions and ownership. Add an evaluated support method for natural claims, using reviewed explanation units/variants for precise facts where appropriate. Semantic/model-assisted checks are supplementary and their measured limits must be recorded. Insufficiency, omission or transparent qualification handles failures; no unchecked model text reaches the browser.

General explanations are model-informed and may be inaccurate. Evidence absence must never trigger permission to invent precise local history. Current practical facts such as opening hours require current sources or an explicit unavailable state. The first release has no live web search; a later research capability needs a separate source/access/validation design.

## 4. Request, context and orchestration

Pipeline: owned request → interpret intent/language/context → decide evidence needs → retrieve when appropriate → generate structured explanation → validate → recheck current evidence/session → emit checked answer and sources.

Intent routing must not rely on a short exact phrase list. Use bounded model interpretation with schema validation and deterministic guards where necessary. Keep social turns independent of corpus availability in their reasoning; valid session identity remains required. Never let an alleged social intent bypass checks on embedded factual questions.

Proposed context lifecycle: maintain a bounded rolling window in page memory, send only recent relevant turns after explicit context consent, and retain topic/language/depth plus unresolved clarification state. No durable raw server history or logging is added. The disclosure must say when conversational turns are sent to the provider; revise the current topic-only consent before enabling this behavior.

Client context is untrusted, size-bounded and bound to the current session; it cannot supply verified evidence, ownership or policy. Signed evidence references continue to enforce current versions/expiry. Omit context when consent is off and ask for references where needed. Previous assistant prose helps interpret a pronoun but never proves a fact. Summaries are context, not authority.

Separate context-window size, UI history and admission limits. Replace the permanent 20-turn block with bounded context/history handling that preserves a working composer and honestly explains any visible history truncation. Close/reopen preserves the page conversation; pending work is cancelled; reload discards page-only history.

Keep server-side credentials, persistent bounded quotas, cancellation, request deadlines and at most one configured transient provider retry. Status progress can stream; publish only validated response content. Measure social response time, evidence-answer time and progress separately. Never automatically regenerate just to produce a different greeting.

## 5. Reliable message delivery

Reproduce `hi` in the running live UI and trace submit → owned session → BFF → API → SSE parsing → rendered terminal state. Also test demo-mode presentation, expired context/session, empty corpus, pending cancellation, double submit and the current 20-turn boundary. Record sanitized errors without private message logging.

Ensure every accepted submit creates a visible turn and eventually clears pending state. Handle incomplete streams, missing terminal events, transport closure, schema rejection and abort separately. Retry must be explicit and must not silently duplicate generation. A typed draft must not disappear without a visible submitted turn/error. Timeout and failure states remain readable and actionable.

Do not claim a root cause until reproduced. Fix the proven cause and add a meaningful regression through the real transport/UI boundary.

## 6. Province-wide knowledge and retrieval

### 6.1 Coverage objective and geographic structure

The owner's requirement is province-wide cultural coverage with a systematic way to find omissions. Cover all 14 prefecture-level cities: Shenyang, Dalian, Anshan, Fushun, Benxi, Dandong, Jinzhou, Yingkou, Fuxin, Liaoyang, Tieling, Chaoyang, Panjin and Huludao. Track relevant counties/districts beneath them using sourced administrative identifiers and names; preserve historical names and dated administrative changes separately from current geography.

Build a city × county/district × subject coverage matrix. Subjects include local history and geography, folklore/legends, mythology/belief, festivals and community traditions, crafts, artifacts, music/performance, food culture, clothing/adornment, museums, archaeological/historical sites, people and explanatory terminology. Map these to the existing cultural taxonomy rather than silently changing its meaning. Distinguish tradition/practice location, claimed origin and current museum repository. A shared tradition may belong to multiple locations; an institution's address does not establish an object's origin.

The previously suggested 10–15 topics per city is an initial delivery target only. It is not a collection ceiling or proof of completeness. A city represented by a single inventory listing is geographically present but not ready for useful cultural explanation.

### 6.2 Discover topics from complete named inventories

Begin with full relevant authoritative inventories, not only manually selected attractions. Build separate inventories for intangible heritage, museums/collections, protected sites and local-history sources. Inspect provincial lists and their national/municipal/county counterparts to identify missing subjects and entities. Record the scope/date of each inventory and distinguish original lists, expansion entries, amendments and current consolidated totals.

Starting official sources checked on 6 October 2026:

- [Liaoning heritage announcement, January 2026](https://www.mct.gov.cn/whzx/qgwhxxlb/ln/202601/t20260126_964395.htm): reports 428 provincial heritage projects, including 76 selected nationally, at that announcement date. This is a reconciliation checkpoint, not a newly imported count or a guarantee that every later list uses the same counting unit.
- [Provincial heritage/inheritor directory with spreadsheet](https://whly.ln.gov.cn/whly/ggfw/whhm/fyml/2022080810044754514/index.shtml): an older starting export; retain its stated reference date and reconcile with subsequent publications.
- [2024 museum/memorial institution information announcement](https://whly.ln.gov.cn/whly/zwgk/tzgg/2025021816091635765/index.shtml): a named museum-inventory starting point; check later editions before claiming current coverage.
- [Provincial Culture and Tourism Department](https://whly.ln.gov.cn/): discover cultural-resource publications and links to authoritative institutions.

Add verified municipal cultural departments, individual museum catalogs, accessible local gazetteers/archives, scholarly sources and relevant national heritage entries. Wikidata can help resolve names and geographic entities; it does not substitute for local cultural evidence. Record unsuccessful access and restricted material as coverage gaps. Do not bypass access restrictions.

### 6.3 Source registry and reproducible acquisition

Create a registry for every candidate source/collection with stable ID, authority/institution, URL/access method, geographic and subject scope, edition/reference date, fetched/checked date, language, rights/access restrictions, expected inventory size and counting unit where stated, checksum/version where permitted, update policy and import status.

Use explicit statuses such as discovered, inspected, importable, imported, review pending, reviewed, blocked, unavailable and superseded. Keep blocked sources in the coverage denominator where applicable; silently excluding them hides omissions. Record reasons and the next action. Official provenance alone does not establish blanket permission to copy full text or images.

Build resumable adapters for APIs, spreadsheets, HTML and PDFs. Preserve source identifiers, exact locators, permitted payloads/descriptors and hashes, extraction method/version, original wording, dates and import errors. Idempotent imports must preserve existing reviews, avoid duplicate entities and keep original source records traceable. Check OCR/table extraction for missing rows and columns; successful parsing alone is not complete acquisition.

### 6.4 Separate inventory, knowledge and publication

Track three layers explicitly:

1. **Catalog coverage:** the known entities/topics enumerated by the named inventories, including topics with no explanation yet.
2. **Explanation coverage:** supporting passages/units for what it is, locality, context, terminology, technique, significance, chronology, disagreement and common questions where applicable. Mark not-applicable separately with a reason; do not invent information to fill a field.
3. **Published coverage:** actually reviewed, rights-cleared and current EN/ZH material usable by Jinyao and the visitor routes.

Pipeline: discover → fetch/import → reconcile entities and inventory rows → prepare attributed passages and translation drafts → classify facts/interpretations/folklore → human review → publish → index → evaluate → monitor changes. Draft imports and model translations never become approved automatically.

Preserve competing accounts and provenance. Link translations to their original evidence and independent wording review. Version changes invalidate affected approvals/embeddings and trigger review; withdrawal hides dependent verified answers. Keep original language available in source inspection. Media and artifact-reference eligibility remain separate from cultural text publication.

### 6.5 Coverage dashboard and omission audit

For every city/subject/source inventory, show expected or identified topics, fetched/imported entities, duplicate/unresolved rows, reviewed/published units, EN/ZH readiness, blocked sources, stale records and unanswered questions. Unknown totals remain unknown rather than zero.

Measure catalog reconciliation against a specific inventory version: accounted-for in-scope rows / expected in-scope rows, with each row either linked to an entity or carrying an explicit unresolved/blocked disposition. Report actual import completeness separately: successfully represented in-scope rows / expected in-scope rows. Accounting for a blocked row does not mean its content was acquired. Handle repeated cross-list entries and shared traditions explicitly; summing all lists is not a unique-topic count. Report explanation completeness and publication readiness separately. Neither model familiarity nor generated general answers increases reviewed coverage.

Audit omissions through inventory-row reconciliation, city/category gaps, county/district gaps, independent source comparisons and held-out visitor questions. Record why each missing row/topic is deferred, unavailable, restricted or awaiting review. Use test/review questions or explicitly consented feedback to find gaps; do not add passive private-message logging.

Schedule checks according to source volatility and preserve source edition history. Distinguish stable historical content from current practical details such as opening hours. Publish honest coverage statements such as “all 14 cities represented; X/Y rows reconciled against inventory Z; explanation and translation gaps listed,” rather than “all facts about Liaoning collected.”

### 6.6 Delivery stages and completion boundary

Run two workstreams in parallel: chatbot engineering and province-wide collection/review. Produce the source registry and complete baseline inventory reconciliation early; deepen explanatory material city by city without dropping less prominent cities.

- **Stage A — province-wide inventory:** named baseline sources, entities assigned to city/county/topic, duplicates reconciled and inaccessible/missing sources tracked.
- **Stage B — useful province-wide knowledge:** reviewed bilingual topic packs across all 14 cities, with meaningful explanations and a documented gap matrix. Topic counts are targets, not invented approvals.
- **Stage C — deeper ongoing coverage:** additional historical periods, county traditions, objects, conflicts and terminology, driven by inventory gaps and evaluation failures; maintain source/version updates.

All-city useful coverage remains a project requirement. Exhaustive Liaoning knowledge is an ongoing content program, not an achievable one-time chatbot acceptance claim. Phase 03 must document its launch coverage and representative missing subjects instead of claiming all local details are verified. The owner must review the launch scope before final acceptance. Closing the engineering phase never silently marks the content program complete; the competition report must distinguish both statuses.

### 6.7 Retrieval validation

BGE has actual inference evidence, but existing relevance/latency diagnostics are too small. Benchmark lexical/hybrid relevance on expanded independently reviewed queries. Address repeated cold model startup with a bounded reusable execution strategy while preserving offline pinning, credential isolation, cancellation and shutdown. Enable hybrid only where measured relevance/latency justify it; label lexical-only operation correctly.

## 7. Work sequence and deliverables

1. **Specification:** revise the original Phase 03 knowledge/publication gates, owner brief and capability/privacy contract to this agreed hybrid direction. Record acceptance criteria before code changes.
2. **Delivery diagnosis:** reproduce and fix silent/nonterminal reply behavior, including `hi`; verify real transport and sustained conversation.
3. **Conversation foundation:** implement structured routing, bounded consented context, clarification, generated social replies and personality in both languages.
4. **Hybrid explanations:** coordinate API/contracts/server validation/browser validation; implement grounded generation and clearly separated general explanations. Preserve precise-fact restrictions and source revocation.
5. **Coverage and retrieval:** deliver a source registry, inventory reconciliation, city/county/subject dashboard and editorial packets; publish real approved content and benchmark relevance/runtime. Run collection and engineering in parallel while external review is pending.
6. **Polish and evaluation:** test real multi-turn flows and adversarial/malformed cases, collect independent bilingual/content/personality review, fix failures and record reproducible evidence.

Do not use the untouched reserved evaluation cases for implementation tuning. Update development cases for the revised capability and obtain independent gold review. Create a fresh version/reserve if current targets are exposed or incompatible with the new contract. At least 40 dated bilingual cases are required; distinguish live model results, fault fixtures and social fallback behavior. Never fabricate human ratings or approvals.

## 8. Phase 03 closure criteria

- Real EN/ZH live browser conversations work with PostgreSQL and the configured provider.
- First/repeated greetings, typos, mixed social/factual turns, clarifications, corrections, topic switches and ordinary off-topic inputs receive appropriate terminal responses.
- Greeting invitations are useful; varied wording and context continuity are verified by sampled real conversations, not exact-string assertions.
- Useful contextual explanation, simplification and depth changes work and remain understandable to reviewers.
- Every verified cultural claim has supporting current evidence; general context is clearly distinguished; unsupported precision/fake citations are rejected.
- Consent/ownership/expiry, withdrawal, secrets, caps, retry, cancellation and incomplete-stream recovery pass relevant checks.
- The composer keeps working beyond 20 turns while bounded context/history limits are respected.
- Reviewed launch coverage, city gaps, retrieval mode/relevance and real cold/warm latency are documented.
- Source inventory versions, reconciliation denominators, county/subject gaps, bilingual readiness and blocked/stale records are visible; general model knowledge is not counted as reviewed data. Province-wide content status is reported separately from chatbot engineering status.
- Independent review separately scores correctness, support, citations, clarity, bilingual meaning, uncertainty, follow-ups and personality; remaining errors are visible.
- Relevant API/browser checks, contracts, supported-runtime lint/types/build and accessibility checks pass; unavailable device environments stay unverified.
- The updated report maps every revised Phase 03 gate to current evidence. Pending external review keeps the corresponding gate partial; passing fixtures alone never closes the phase.

Final walkthrough: greet Jinyao, answer her invitation, ask a supported question, clarify a reference, ask why, simplify, go deeper, switch language, inspect sources, ask beyond the corpus, change topic, greet again, and recover from a controlled failure. Verify personality variety, source boundaries and delivery throughout.

## First-release design

First-release design: text conversations in EN/ZH, generated social replies, reviewed factual explanations plus qualified broad model context, explicit consent for bounded conversation context, page-only history, and no live web search. A bare greeting receives one useful invitation; ordinary answers do not all end in a question. Application code and original phase requirements have not yet been changed. Content launch targets are specified separately in the execution parts; deviations remain explicit and require the owner's launch-scope decision before acceptance.
