# Part C — logical errors and confusing behavior

Updated 5 October 2026, Asia/Shanghai. Scope: C01–C12 of the [original UI audit](UI_AUDIT_BEFORE_PHASE_03.md). All twelve corrections are complete locally. Part B was committed and pushed to main as `faed2c5e3fe6e092e8bebc7d6caa302a2deffd1b`, with screenshots excluded. Part C does not implement later-phase AI or durable storage services.

| ID | Status | Delivered behavior |
|---|---|---|
| C01 | DONE | Sources instructions describe published source records, permitted excerpts, attribution, editorial review and rights; no city/atlas directions. |
| C02 | DONE | Live footer distinguishes published collection availability from unconnected AI experiences. Unavailable experience panels identify that capability's API and direct visitors to published exhibits/sources. |
| C03 | DONE | All interests accurately describes the `all` fixture selection; the existing correction is reverified. Craft, Food and Music are the actual example categories. |
| C04 | DONE | One All Liaoning option plus fourteen cities. Province-wide requests explicitly send `region_id=liaoning`, preventing an accidental cross-province query. |
| C05 | DONE | Atlas indicators distinguish checking collection, service unavailable, reviewed city content and no published city content. Availability markers are suppressed while loading or failing. An empty successful feed has a truthful empty-state legend; retry restores availability. Geography remains independent. |
| C06 | DONE | Guide appends up to twenty scripted turns instead of replacing one. Draft/history survive internal navigation in memory. Clear removes draft/history and prevents pending replies restoring cleared turns. Reload/close resets. No server/model/storage calls save questions or use history as AI context. Lifetime/privacy are visible. |
| C07 | DONE | Time/interests are draft criteria until Apply. A changed-criteria notice marks the route out of date; its badge retains the last applied duration. Apply regenerates using the selected criteria. |
| C08 | DONE | Temporary Journey stop order, removals and criteria survive internal navigation. Reset example plan restores defaults; reload/close clears the visit. Durable save remains deferred to Phase 04. |
| C09 | DONE | The optional tour explicitly covers Shaanxi, Fujian and Guangdong and is separate from Liaoning, both before preview selection and beside its stops. No invented Liaoning records were added. |
| C10 | DONE | Story offers the actual English recording or text only, explicitly identifies Chinese audio as unavailable, and provides the exact English transcript with Chinese translation. No autoplay or new audio claim. |
| C11 | DONE | Voice is labelled unavailable and disabled, with its explanation visible before interaction and associated with the control. Typing remains available; no microphone permission is requested. |
| C12 | DONE | Published exhibit drawer links carry the selected ID into Guide, Journey, Story and interests, then back to that exhibit/source drawer. Destination panels retrieve/revalidate the current record, suppress obsolete ID/locale/request responses and fail closed for unavailable records. Guide offers explicit question seeding in demo mode, revealing/focusing the composer and bounding the draft to 2,000 characters; other panels define reading/context actions and unavailable APIs. Separate fiction and example tours are not presented as adaptations or recommendations from the selected record. |

Implementation and policy: [visit state/context contract](../docs/visit-state-and-context.md), [visit provider](../apps/web/src/components/visit-provider.tsx), [context panel](../apps/web/src/components/exhibit-context.tsx), [catalog](../apps/web/src/components/catalog-explorer.tsx), [experiences](../apps/web/src/components/museum-experiences.tsx).

Verification:

- **46 passed, 0 failed, 0 skipped** in the full Chromium suite. Six new regression scenarios cover truthful scope/copy, delayed/outage atlas states and retry, multi-turn/draft retention and clear during pending response, Journey draft/apply/navigation/reset, Chinese narration selection/transcript and all four continuations in demo/live with displayed-record withdrawal on refresh. Existing artwork, navigation, map gestures, keyboard, zoom, demo/live isolation and content checks pass. [Final log](evidence/ui-part-c/e2e.log), [structured results](evidence/ui-part-c/browser-results.json), [regressions](../tests/e2e/ui-part-c.spec.ts).
- Lint without warnings, TypeScript/Python type checks, production build and foundation checks pass. [Lint](evidence/ui-part-c/lint.log), [types](evidence/ui-part-c/typecheck.log), [build](evidence/ui-part-c/build.log), [foundation](evidence/ui-part-c/foundation.log).
- Original artwork, geography and reviewed-content hashes pass preservation checks. [Preservation](evidence/ui-part-c/preservation.log), [geography](evidence/ui-part-c/geography.log), [content](evidence/ui-part-c/content.log).
- Expanded/new-state accessibility and layout checks: **30 EN/ZH states, zero detected axe violations and zero horizontal overflow**. Cover Sources, Guide, Journey, Story transcript and selected exhibit context at desktop/tablet/phone sizes in EN/ZH. Automated scan results retain incomplete checks as well as detected violations. [Results](evidence/ui-part-c/axe-and-layout.json), [log](evidence/ui-part-c/axe-and-layout.log).

The initial suite had one test-harness failure from removing an intercepted delayed response before its handler completed. The corrected final run passes; the initial log remains diagnostic history.

Screenshots remain local and Git-ignored. Physical devices, Safari and a complete screen-reader audit remain unverified. Next is Part 4: UI things that must be added. AI guide, personalized journeys, generated stories and real recommendations remain their respective later-phase work.
