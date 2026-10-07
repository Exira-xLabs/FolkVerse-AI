# Phase 3 autonomous completion work — 7 October 2026

The owner declined human review. Codex has completed the source assessment, broader Liaoning lookup, attribution reliability fixes and regression verification. **Final Phase 3 closure is still blocked by the existing live-test spending cap; no human worksheet is required.** The 200-question pilot is frozen and ready, but has not completed. This report supersedes the previous owner-review handoff.

## What changed

- Inspected the original captured paragraphs for all 42 official profiles and assessed the English/Chinese summaries. Removed unsupported Goguryeo/excavated-object wording from the Wunushan draft: those facts were absent from the cited profile. Corrected the inherited Panjin museum name to the actual profile subject. The revised v5 pilot freezes this correction; v4 remains historical evidence.
- Added an explicitly machine-assessed lookup tier, separate from the protected human-reviewed corpus. All 14 cities have three bilingual topics across at least two subjects, contextual summaries, concrete examples, city introductions and suggested follow-ups in the machine launch manifest. The 448 existing drafts remain unapproved.
- Fetch the original official page before using an assessed summary. Require the recorded raw and paragraph hashes; preserve source statements versus folklore. A changed source loses its summary eligibility. Changing or withdrawing the machine assessment invalidates cached evidence. No full articles or source images are republished.
- Route registered attraction names through source lookup instead of allowing a general answer simply because the question starts with “explain”. City-only questions discover the city's three registered profiles. Source inspector explicitly says Codex performed assessment and no human review occurred.
- Models select statement references; the server renders the exact assessed wording. This fixes observed English attribution omissions without allowing unsupported paraphrases or silently stripping qualifications. Invalid references, wrong passage IDs, altered text and wrong classifications fail closed.
- “Hi again” is recognized as a greeting and keeps the existing non-repetition/invitation rules. Generic questions about original objects no longer accidentally match the origin-date guard.
- The live evaluation runner now stops at an exhausted spending/quota admission gate rather than recording an entire suite of known blocked calls.

## Verification

| Check | Actual result |
| --- | --- |
| Fresh original profile/hash assessment | 42/42; all 14 cities. Temporary timeout evidence is preserved; final corrected assessment uses a 41-profile pass plus one explicit successful source retry, not a simultaneous snapshot. |
| Source discovery floor | Both languages resolve all 42 aliases uniquely; three profiles per city; multi-city queries cannot silently select one city. |
| Full API suite | 433 passed. |
| Guide/browser suite | 60 passed; English/Chinese, phone/desktop, source assessment label, withdrawal, keyboard, scroll and presentation checks. |
| Accessibility | Four axe-core 4.13.0 chat/source audits; zero violations and zero incomplete checks. |
| Isolated bilingual faults | 16/16; no paid calls or live content mutation. |
| Lint/types/build/contracts/assets/secrets | Passed; original nine assets preserved. |
| Disposable-checkout reproduction | 18 checks passed; isolated PostgreSQL/pgvector, startup, migrations, restore, web/API and cleanup. Final evidence binds runtime and new machine-manifest hashes. |
| Real model pilot | First diagnostic subset: 53/62 scenario targets; nine attribution-copy refusals. After statement-reference fix: first three live cases passed, then the existing budget admission gate stopped further paid generation. This is not a completed 200-question pilot. |

[Raw evidence](evidence/phase03-final/) preserves the incomplete runs and faults. The earlier 48/48 live diagnostic remains evidence for personality, consented follow-ups and general educational behavior; it is not a fresh score for the final broader corpus. Previous retrieval/BGE and 68 broader museum browser checks remain separately dated historical evidence.

## Source and review boundaries

[Assessment](../data/liaoning/machine-source-audit.json), [all-city launch manifest](../data/liaoning/machine-launch-manifest.json), [owner review amendment](../docs/phase-03-machine-review-acceptance.md).

These are attributed machine judgments, not fabricated human or specialist approvals, a legal clearance certificate, or proof of exhaustive Liaoning knowledge. The original inventories/research queue continue the content program. General explanations stay visibly unverified. Current hours, prices and schedules remain unsupported until a suitable current-information adapter exists. Physical screen-reader/device and independent specialist review remain later validation opportunities, rather than a request that this owner review the chatbot.

## Remaining live acceptance

Run the frozen [200-question suite](../tests/evaluation/guide/v5-phase03-pilot.json) against the final runtime, preserve exposure information, assess the actual general explanations and publish answered/refused/error denominators and meaningful latency. Do not label the exposed topic subset as blind expert gold.

The existing local daily cap is US$0.10. The ledger has US$0.091854 charged/reserved; the remaining allowance is insufficient for the next maximum-cost reservation. The API returns `budget_exhausted`. No cap increase, billing bypass or automatic paid retry was performed. A question requesting permission for up to US$0.15 additional testing is pending. No provider credentials appear in the report.
