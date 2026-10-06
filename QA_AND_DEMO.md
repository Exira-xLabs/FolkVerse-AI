# Verification, delivery plan and demo

## Proposed internal sequence
Dates are planning targets, not claims of completion. School submission work is independent and due 30 September.

| Target | Phase | Evidence before proceeding |
|---|---|---|
| 29–30 Sep | 00–01 foundation and visual shell | Local startup, exact assets, working route controls, fixture label |
| 1–2 Oct | 02 content and map/list | Real approved records and rights manifest |
| 3 Oct | 03 grounded guide | Credentialed integration if available, supported/unsupported cases |
| 4 Oct | 04 journey planner | Valid exhibit IDs and duration constraints |
| 5–6 Oct | 05 Object Lens | Real retrieval, ownership, unknown and failure behavior |
| 7 Oct | 06 story and voice | Complete story graph; actual voice mode clearly stated |
| 8 Oct | 07 DNA and full loop | Opt-in, reset/delete and explained recommendations |
| 9–10 Oct | 08 verification/rehearsal | Dated build, screenshots, measured failures and recorded backup |

Critical path: eligible reviewed corpus → retrieval → supported guide/scan decisions → integrated demo. UI can progress with labelled fixtures while review happens. Review delays are resolved by narrowing scope, not inventing approval. Defer live voice, more regions or richer animation if necessary; disclose the resulting feature scope. Do not defer source inspection, genuine unknown states or honest implementation status.

## Feature coverage checklist
| Feature | Smallest credible working behavior | Failure check |
|---|---|---|
| Map | Real region/list filters open approved exhibits | No approved geometry/empty region |
| Journeys | Real eligible stops fit selected time and can be edited | Too few exhibits or unpublished stop |
| Guide | Natural bilingual conversation; source-supported cultural explanations and distinctly unverified broad general context | Unsupported precise local claim, failed greeting delivery, timeout, invalid citation |
| Stories | One complete graph with labelled creative choices | Stale/invalid branch; restricted context |
| Lens | Uploaded photo yields catalog candidates or honest unknown | Reproduction, unrelated photo, poor photo, outage |
| Voice | Transcript edited before submission, narration interruptible | Mic denial, unavailable speech provider |
| Recommendations | Real eligible suggestions with reasons | No history, no diverse candidate available |
| DNA | Opted-in interests drive editable live graph | Reset/delete and opt-out |
| Verified knowledge | Publication/rights gates and evidence visibility | Revoked source and unsupported claim |
| Saved exhibits | Session persistence and ownership | Cross-session access |
| Chinese/English | Translated UI and preserved source terminology | Missing translation and long text wrapping |

## Visual fidelity gate
At 1600×900, compare each route with its corresponding `references/ui/` frame. Wait for fonts, set deterministic locale/state and disable animations for screenshots. Never fabricate a screenshot without running the application.

Check identical background and guide assets; comparable crop and focal point; nav bounding box; serif headline shape; glass opacity, border and radius; gold active tab; card size/gaps; drawer layering. Use image overlays and region-based diffs where possible. Do not demand whole-image pixel equality across renderers or approve a redesign because a coarse similarity score looks high.

A useful proposed geometric tolerance is about 8px at the 1600×900 reference for major panel edges, excluding documented responsive/functional differences. This is a review aid, not an achieved score. Human comparison still controls appearance. Record deviations for accurate map geometry, honest scan labels and accessible controls. Screenshot and asset checks are required because text prompts alone cannot guarantee identical UI.

At 390×844 and 768×1024: no clipped essential controls, no horizontal page scroll, 44px touch targets, legible titles and source text, functional keyboard/focus order. At 200% zoom permit scroll rather than shrinking text. No dark-on-dark text; test contrast on the actual background.

## Functional test set
- Navigate all routes with keyboard and pointer. Logo returns home; tabs identify current route.
- Open and close source drawer with focus restored; external source links use known URLs.
- Run map → exhibit → journey → question → source → story → save → DNA/recommendation.
- Ask a supported question, a source-disagreement question and an out-of-corpus question.
- Simulate provider timeout, network loss, rate limit and budget exhausted; verify no fake successful answer.
- Try unknown image, poor image, known record image and a new real view. Mark reference-image reuse separately from real-world recognition.
- Attempt another session's media, journey, scan and profile IDs; reject access.
- Submit wrong media type, oversized dimensions, EXIF-bearing image, OCR instructions and malicious markdown.
- Turn tracking off, reset profile, delete session; verify data consequences.
- Cancel camera/microphone and narration. Leaving a page stops media tracks/playback.

## Research gates from report page 23
These are full pilot targets, not the minimum evidence required to honestly show a small prototype.

| Metric | Target | How to measure honestly |
|---|---|---|
| In-scope retrieval | Top-5 recall ≥85% | Held-out real captures; report N and category coverage |
| False confident identity | ≤5% | Wrong confident IDs / all confident IDs; also report unknown false-match rate and abstention/coverage |
| Factual support | ≥95% | Human scoring of factual claims on a planned 200-question bilingual set |
| Citation integrity | 100% | IDs resolve and belong to retrieved evidence; separately check support |
| Route validity | 100% | Eligible IDs and duration constraints |
| Usability | ≥80% completion | Planned 20 consented participants; report actual recruited N |
| Guide latency | p95 meaningful content <5s | Defined device/network/model, excluding progress indicator |
| Scan latency | p95 <8s | End-to-end upload/retrieval/provider time |

Proposed scan test expansion: 200 in-scope photos and 100 unknown/out-of-scope examples, as described in the report. Do not represent a five-image smoke test as that benchmark. Exact catalog retrieval needs new captures of indexed objects; category generalization needs object-disjoint splits. Never train/tune on the held-out test photos. Record corpus/model/prompt versions and failures, not only averages.

If likelihood thresholds cannot be validated, keep live likely_catalog_match disabled and report related/unknown results. This is a limitation to state, not conceal.

## Demonstration within the five-minute pitch
The full pitch contains problem, product, technology, value, business and team. Reserve roughly 60–90 seconds within slides 3–4 for the product flow, not a separate five-minute app demo. Show one reviewed exhibit, a concise source-backed answer, source drawer, and one honest scan outcome. Story/DNA can be shown briefly or in backup.

Use a frozen demo corpus and prepared input photos with known provenance. Have an explicitly recorded backup; don't pretend a recording is a live call. Live network failure should lead to the labelled backup without wasting the pitch. The official Q&A lasts three minutes. Prepare answers to: what did you build yourselves, why a database is needed, how you limit hallucinations, why the scan is uncertain, what costs money, and which data may be reused.

## Release checklist
- [ ] Commit/tag identifier and dependency locks recorded.
- [ ] Setup, migrations, reviewed seed and media files reproducible.
- [ ] Key names documented; no secrets or private photos in package.
- [ ] Reports distinguish implemented, simulated, measured and planned.
- [ ] Rights/provenance/corpus manifest and image hashes retained.
- [ ] Screenshot evidence, test commands and failure examples retained.
- [ ] User-photo cleanup and model spending cap exercised.
- [ ] School submission is preserved; no organizer upload is performed by coding prompts.
