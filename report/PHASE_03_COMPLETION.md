# Phase 03 working-chatbot delivery — partial acceptance

## 1. Repository, brief and verdict

6 October 2026, Asia/Shanghai; `/home/soufiane/FolkVerse-AI`, branch `main`.
The working tree was clean before `git pull --ff-only`. The pull advanced `68d6ee8` to
`7e8a0150a2c5de7c78dbf3b95c5521f54a6af3e0` and introduced
[the working-chatbot brief](PHASE_03_WORKING_CHATBOT_BRIEF.md). This delivery is an
implementation on that base. The owner subsequently authorized committing and pushing this
delivery; the resulting commit is recorded in Git history. No deployment or submission was made.
[Runtime and source hashes](evidence/phase03-completion/environment.json) identify the work.

**A real bounded bilingual Jinyao conversation works locally. Phase 03 is still partial.**
The actual browser → owned session → Next.js proxy → API → approved PostgreSQL evidence →
Ollama → validation → SSE → current source inspector path is verified. General history,
glossary, chronology, classified explanatory units, representative hybrid relevance and
independent human quality acceptance remain unfinished. This report does not certify
“perfection,” 95% expert quality, full Phase 03 or Phase 04 readiness.

The master brief, Phase 03, all three specifications, current status, handoff, push audit,
new working-chatbot brief and relevant guide/content/setup documents were read. No applicable
`AGENTS.md` existed at initial inspection. Existing artwork, Jinyao's identity and introduction,
rectangular send button, absence of Clear chat and same-page popup history were preserved.
The older Part 1–6, push-audit and Phase 00–02 reports remain dated historical evidence.

## 2. Implemented and repaired

- Restored the dedicated pinned PostgreSQL/pgvector image through the existing user proxy.
  Manifest and every blob hash were checked against the pinned upstream platform image.
  Loaded it locally and used an ignored Compose override; no daemon/system settings or unrelated
  services were changed. Applied migration `0003_gateway` and restored the original corpus/reviews.
- Installed a checksum-verified project-local Node **22.23.3**. Checks now run on the declared
  Node 22 runtime rather than the previous unsupported Node 26 host default.
- Added [versioned personality policy](../docs/jinyao-personality.md), social greeting/identity/
  thanks/start behavior, minimal consented context continuity, explicit language switches and
  beginner/deeper controls. Social turns are non-cultural application policy, **not AI generation**.
- Added constrained natural inventory explanations. A recognized reviewed listing is reordered
  into category/locality wording without losing attribution or inventing origins, dates or
  definitions. Complete reviewed claims and source excerpts remain visible. Server and browser
  reconstruct the entire permitted display; independent evaluation of explanatory quality is pending.
- Resolved follow-up references before provider selection. Live reruns exposed occasional selector
  refusals even when listing coverage existed. The selector now explicitly selects supported
  statements, uses `temperature=0`, and a refusal becomes an honest retryable service error rather
  than a false claim that the reviewed corpus lacks the listing. No canned cultural fallback was added.
- Kept retrieval/latency diagnostics in evidence rather than normal chat messages. Corrected
  obsolete DeepSeek-only disclosure and disconnected-Guide availability copy.
- Added current-source revalidation every 15 seconds and on focus while the inspector is open.
  Changed/withdrawn/unavailable sources clear its evidence display.
- Fixed genuine navigation overflow at 200% CSS zoom and decorative logo loading in low-data mode.
  Repaired stale mobile-language, Guide artwork, home-link and live-Guide regression assertions.
  Browser configurations now use separate output directories so concurrent runs cannot erase traces.
- Fixed fresh-restore verification to distinguish database records/reviews/publication from optional
  ignored catalog image bytes. Zero locally available images no longer falsely invalidates a restore.

Main changes: `guide_personality.py`, `guide_harness.py`, `guide_evaluation.py`,
`provider_gateway.py`, shared policy/contracts, Jinyao chat/stream/source inspector, museum
shell/CSS, recovery/walkthrough/review scripts, focused tests and the documentation linked here.
No new cultural passage, source, artifact or explanation unit was approved automatically.

## 3. Original Phase 03 gates, reproduced verbatim

| Gate from `phases/03_GROUNDED_GUIDE.md` | Result | Concrete evidence and limits |
|---|---|---|
| A real credentialed call is tested if authorized credentials exist; otherwise explicitly unverified. | PASS | Actual Ollama JSON calls through the browser/BFF/PostgreSQL path; [live walkthrough](evidence/phase03-completion/live-browser.json), [usage](evidence/phase03-completion/provider-usage.json). |
| Supported and unsupported questions behave differently in both languages. | PASS within narrow published scope | EN/ZH listing answers, unsupported history, reference clarification and consented follow-ups; real walkthrough plus portable bilingual regressions. |
| Invented citation IDs are rejected; source-injected instructions do not change policy. | PASS for controlled regression evidence | API/harness/browser fault cases reject invented mappings, extra prose, classification upgrades and source instructions. These adversarial cases use isolated fixtures, not malicious edits to the published corpus. |
| Revoked passages stop being retrieved; model timeout/cap exhaustion show honest errors. | PASS for stated fault environments | Actual committed PostgreSQL withdrawal and shared admission/rate/quota checks in disposable databases; provider timeout/cancellation/cap fixtures; open-inspector withdrawal regression. No actual account quota was exhausted. |
| Keys never reach browser/logs; source drawer shows actual evidence. | PASS, bounded configured-secret scan | Real current source inspector; seven scanner tests, foundation scan and server-only credentials. This is not an exhaustive unknown-secret forensic certification. |
| Jinyao's expert guide harness is implemented and evaluated on the dated bilingual set below, with measured scores and honest coverage gaps. | PARTIAL | Existing restricted harness, real conversations, v1 regression and new v2 development results. Independent historical/clarity/faithfulness/personality scores remain pending; general explanatory expertise is absent. |
| Explanations separate historical evidence, attributed interpretations, folklore/belief and creative adaptation; chronology and source support are checked. | PARTIAL | Current statements retain source attribution and unsupported classification/chronology upgrades are rejected. Classified broader explanation units and reviewed chronology are not implemented/published. The draft packet explicitly preserves attribution and a chronology conflict for review. |
| Follow-up explanations, glossary requests and depth changes retain validated citations and uncertainty; no unsupported claims appear during simplification. | PARTIAL | Actual listing simplification, depth controls and EN↔ZH retain checked citations/qualifiers. Glossary, importance and historical “why” remain coverage gaps; meaningful deeper history requires new reviewed evidence and broader unit support. |

## 4. Owner checklist

| Working-chatbot requirement | Current state |
|---|---|
| Real browser credentialed generation and migrated PostgreSQL, EN/ZH | Verified |
| Distinct supported / unsupported / ambiguous behavior | Verified within the listing scope |
| Personality implemented and independently reviewed in both languages | Policy implemented and mechanically exercised; independent review pending |
| Approved contextual/glossary/chronology coverage and meaningful depth | Only bounded listing explanation available; wider coverage/support unfinished |
| Consented supported follow-ups, simplification and language switching | Verified for the current topic; glossary unavailable |
| Citation invention, injection and unsupported publication rejected | Controlled regression evidence passes |
| Withdrawal stops retrieval/follow-up/publication | Real eligibility/current-version checks plus isolated revocation regressions |
| Timeout, cancellation, concurrency, rate and budget errors | Portable provider/browser faults and actual PostgreSQL shared limits pass |
| Server credentials and documented retention | Configured-secret checks; page-only turns, 30-minute signed topic/evidence context, content-free usage ledger |
| Actual sources and polished controls | Real walkthrough and focused Chromium tests pass |
| BGE inference/indexing/relevance/runtime evidence | Actual inference/indexing and diagnostic timings/memory recorded; representative reviewed relevance remains unverified |
| Fresh bilingual evaluation and attributed human assessment | 48 draft paired targets, 24 development cases exercised; 24 reserve unexecuted; human ratings pending |
| Actual usage and meaningful-answer latency with versions | Recorded separately from fixture timings |
| Supported-runtime tests/contracts/lint/types/build/foundation | Current checks listed below; physical-device/Safari/native-zoom checks unavailable |

## 5. Reproducible verification

All newly run evidence is under `report/evidence/phase03-completion/`. Node 22.23.3,
pnpm 11.10.0 and Python 3.12.13 were used. Exact implementation versions/hashes are in the
[environment record](evidence/phase03-completion/environment.json).

| Command / procedure | Exit / outcome | Evidence |
|---|---|---|
| `git pull --ff-only` | 0; fast-forward to the new brief | Base commit above; working tree initially clean |
| `docker compose up -d --wait db` initially | 1; daemon registry connection timeout | Recovered with pinned-image proxy helper; no fake healthy database |
| `uv run --project apps/api python scripts/pull-database-image.py` | 0; manifest/config/layer hashes verified | [Image provenance](evidence/phase03-completion/database-image.json), helper log |
| `docker load --input .local/pgvector-image/image.tar` and `docker compose -f compose.yaml -f .local/compose-proxy.yaml up -d --wait db` | 0; healthy dedicated DB | Database load/start logs |
| `uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head` | 0; `0003_gateway` | Migration log |
| `uv run --project apps/api python -m folkverse.curation restore-manifest` | 0; original reviews restored | Restore log and measured counts |
| `uv run --project apps/api python scripts/verify-content-snapshot.py` | 0; exact DB counts, original reviews, overwrite refusal | Fresh-restore log; local optional image availability 0 |
| `pnpm test:api` | **299 passed**, exit 0 | [API tests](evidence/phase03-completion/api-tests.log); one existing Starlette/httpx deprecation warning |
| `uv run --project apps/api pytest apps/api/tests/test_postgres_integration.py -q` | **3 passed**, exit 0 | [PostgreSQL tests](evidence/phase03-completion/postgres-integration.log); disposable migrated/restored databases, zero inference |
| `FOLKVERSE_EVIDENCE_DIR=report/evidence/phase03-completion/full-browser pnpm test:e2e` | **68 passed**, exit 0 | [Full browser log](evidence/phase03-completion/full-browser.log); after prerequisite/UI/test repairs |
| `FOLKVERSE_EVIDENCE_DIR=report/evidence/phase03-completion/guide-browser pnpm exec playwright test -c playwright.guide.config.ts` | **28 passed**, exit 0 | [Focused browser log](evidence/phase03-completion/guide-browser.log); includes final source-inspector change and social-publication regressions |
| `pnpm lint`, `pnpm typecheck`, `pnpm build` | Exit 0 | Lint/typecheck/build logs; strict mypy checks 28 API source files |
| `pnpm contracts`, `pnpm test:secrets`, `pnpm check:foundation`, `node scripts/verify-museum-art.mjs` | Exit 0 | Contract, secret, foundation and artwork logs; generated contracts refreshed before equality check |
| `node scripts/verify-guide-live.mjs` with bounded live API/web processes | **22 checks pass**, exit 0; no intercepted replies | [Actual walkthrough](evidence/phase03-completion/live-browser.json), local-only screenshots |
| `OLLAMA_DAILY_REQUEST_LIMIT=24 node scripts/verify-guide-recovery.mjs` | Exit 0; actual isolated DB outage, honest UI error, real provider retry | [Actual recovery](evidence/phase03-completion/live-recovery.json); auxiliary services stopped |
| `uv run --project apps/api python -m folkverse.guide_index prepare` / `build` | Exit 0; pinned offline model and current-corpus index | Model-prepare/dense-build logs |
| `uv run --project apps/api python -m folkverse.guide_index benchmark --output report/evidence/phase03-completion/dense-benchmark.json` | Exit 0; actual CPU hybrid queries | [Benchmark](evidence/phase03-completion/dense-benchmark.json); six diagnostic queries, two passages |
| Python `subprocess` build with Linux `resource.getrusage(RUSAGE_CHILDREN)` | Exit 0; maximum child RSS measured | [Memory record](evidence/phase03-completion/dense-memory.json); fallback because `/usr/bin/time` was unavailable |
| `git diff --check` | 0 | Final whitespace check |

The full 68-test run preceded the final inspector/prompt/provider-selector refinements;
their relevant 28 browser and 299 API regressions, lint/types/build and live walkthrough
were checked afterward. Broad unrelated checks were not repeated without a new reason.
The first full run had seven failures (60 passed); its log/results are preserved in
`full-browser-initial/` and `full-browser-initial.log`. They identified stale mobile/Guide
assertions, low-data logo loading and a trace-directory collision. Live selector misses and
the corrected follow-up diagnostic are likewise retained, not erased from the record.

## 6. Content, rights, retrieval and real usage

[Actual restored counts](evidence/phase03-completion/corpus-counts.json): **1 published exhibit,
2 approved passages, 1 approved source, 13 draft active exhibits, 26 draft active passages,
37 draft artifacts, 32 draft media records, 0 published artifacts and 0 local catalog image
files**. Archived former-scope records remain withdrawn. Targets of 10 exhibits/30 artifacts
are not manufactured.

The published fact is a Fuzhou / **复州** heritage listing from Wafangdian, Liaoning; it is not
Fuzhou / **福州**, Fujian. The [coverage matrix](../docs/guide-coverage.md) and
[official provincial entry 29](https://www.ln.gov.cn/web/zwgkx/zfxxgk1/zc/xzgfxwj/szf/szfwj/2023010509411077517/index.shtml)
(rechecked 6 October 2026) explain the narrow scope. The original source/rights/review hashes
are preserved. New national-history/definition statements are not inferred from that approval.

The existing 16 candidates remain draft. A new [five-unit bilingual explanation packet](../data/review-candidates/phase03-explanations.json)
prepares definitions, recognition, attributed importance, chronology conflict and folklore
qualification from named source locators. It has no reviewer/approval or publication authority.
A source date mismatch remains flagged rather than silently resolved. No full articles, new
museum images, participant data or external specialist approval were fabricated/imported.

BGE-M3 is pinned to `5617a9f61b028005a4858fdac845db406aefb181`; 2,293,315,801 artifact bytes
were verified. Actual current-corpus indexing and six CPU hybrid queries pass. Index creation
in the diagnostic benchmark took **15.10 seconds**; query workers took **10.66–14.25 seconds**.
A separate indexing/memory run took **22.27 seconds** and measured **1,987,568 KiB maximum
child RSS**, not total concurrent system memory. CPU worker threads: two. Keyword-only
ranking median **0.038 ms** excludes DB reads. No representative relevance gain is claimed
from this two-passage sample. Dense retrieval remains disabled for the normal preview.

[Actual Ollama usage](evidence/phase03-completion/provider-usage.json) records **18 admitted
attempts**, including diagnostic/earlier reruns and the real recovery: **7,403 prompt tokens,
1,778 completion tokens**, no unknown token-usage attempts. These are account request/token
measurements, not a dollar estimate; USD cost remains unknown. Final successful walkthrough:
four evidence-backed answers, **1,311–2,067 ms** to first meaningful validated content,
**1,459 ms median**. Progress messages, social replies, errors and fixture timings are excluded.

Final versions: `guide-supported-conversation-v4`, `jinyao-evidence-selector-v4`,
`guide-json-v3`, `jinyao-conversation-v1`; exact corpus/model/encoder hashes are in evidence.
The gateway selects complete supported statements; natural inventory rendering is constrained
application logic, not unrestricted model-written historical explanation.

The root `.env` remains **demo / zero quota**. The local preview uses a process-only cap of
**24 Ollama attempts per UTC day**; failed/retried attempts count and restarting does not reset
it. Earlier probes used cap 16; the bounded local test cap increased during selector verification.
No deployment budget, credential, daemon settings or unrelated service was changed.

## 7. Evaluation, human review and outstanding gates

The unchanged v1 suite remains exposed regression evidence: **64/64** functional outcomes;
claim support **22/22**, citations **22/22**, uncertainty **58/58**, follow-up **10/10**. Earlier
Part 6 baselines remain untouched. [Current v1 regression](evidence/phase03-completion/evaluation-v1-regression.json).

New v2 has **48 paired EN/ZH machine-authored targets**. Only **24 development cases** were
run: **24/24** functional outcomes, support **12/12**, citations **12/12**, uncertainty
**16/16** factual/coverage responses, follow-up **4/4**. Eight social-policy responses are
excluded from factual uncertainty scoring. The **24 reserved cases remain unexecuted** and
were not used to tune implementation. Author-written reserve is not independently reviewed
gold. [Development results](evidence/phase03-completion/evaluation-v2-development.json).

Historical correctness, explanatory clarity, bilingual faithfulness and personality acceptance
remain **unscored**, with zero human-scored denominator. The live worksheet binds its eight
actual conversation units to the run hash and has a reviewer/rationale rubric; it creates no
human ratings. [Actual-answer worksheet](evidence/phase03-completion/live-human-review-pending.json),
[v2 worksheet](evidence/phase03-completion/evaluation-v2-human-review.json).

Remaining work is concrete:

1. Obtain actual editorial, rights and translation review for broader explanation material.
2. Implement classified reviewed explanation units and broader support/intent handling against
   that material; inventory projection cannot provide chronology, glossary or historical nuance.
3. Obtain independent bilingual/personality assessment of actual answers and fresh gold targets;
   then execute the reserve/live quality evaluation. No 95% claim is currently justified.
4. Benchmark hybrid relevance on an expanded, reviewed sample and address cold-worker latency.
5. Check native browser zoom, physical devices, Safari, screen readers and actual pitch network.
   Chromium emulation, keyboard/CSS zoom and reduced motion pass; those external environments
   remain unverified.

## 8. Local walkthrough and handoff

See [the reproducible handoff](../docs/phase-03-handoff.md) for Node 22, pinned-image recovery,
startup, checks and usage-cap behavior. Preview: <http://localhost:3000/guide>.

Open Jinyao, enable topic-context consent, ask “Where is Fuzhou shadow puppetry listed?”,
inspect sources, ask “Explain that simply”, “Go deeper”, then “Say that in Chinese”. Ask an
unsupported origin-year question and confirm a coverage gap. Close/reopen preserves this
page's conversation. The separate real recovery script demonstrates an isolated unavailable
upstream followed by a successful actual retry, without changing the main database/service.

The database and bounded live preview are available locally at handoff; auxiliary recovery and
Playwright services are stopped. Original artwork is unchanged, no Clear chat was introduced,
and new screenshots remain ignored/local as requested. The evidence supports a **narrow local
museum-guide demo**, not general historical expertise or full pitch/release acceptance.
