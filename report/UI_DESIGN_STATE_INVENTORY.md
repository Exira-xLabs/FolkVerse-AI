# Reviewed UI design/state inventory

5 October 2026, Asia/Shanghai. Implementation inventory for Part 4. Existing artwork is preserved; screenshots are local-only. Each screenshot group has desktop 1600px, tablet 768px and phone 390px variants, in EN and zh-CN, under `report/evidence/ui-part-4/screens/`.

| Screen | Available behavior | Covered states and recovery | Screenshot group |
|---|---|---|---|
| Home | Reviewed featured record, Explore Liaoning, capability badges | Published, loading, empty, service error/retry; live badges distinguish unavailable previews | `home-{width}-{locale}.png` |
| Explore | Collection/search, province/cities/themes, optional sourced atlas | Active filters, clear/empty recovery, retained visit context, all-province reset, loading/error/offline/retry, responsive directory/gestures/full modal | `explore-*`, `map-*` |
| Exhibit reading | Reviewed title, city/themes/summary, citation anchors, back, shareable URL, next actions | Reading separate from source evidence; loading, withdrawal/error, record retry, locale change; no invented additional prose | `reading-*` |
| Sources | Published institutions/excerpts/review/rights/original links | Empty/loading/unavailable, source inspection, keyboard-accessible integrity disclosure | `sources-*`, reading evidence below the reading section |
| Guide | Context panel, approved prompts and source-linked reading; scripted conversation preview | Draft/history retained in memory, generating distinct from answer, Stop/cancel, error/Retry, insufficient-evidence refusal, clear, unavailable voice; no model/citation claim for scripted answers | `guide-*` (error preview), composer reduced-viewport capture; regression tests cover the other states |
| Journey | Retained example plan, draft/apply, applied budget, reorder/remove/reset | Empty recovery, stop reasons, source-linked approved reading; cross-province fixture tour remains separate from actual Liaoning records | `journey-*` |
| Story | Original fiction with explicit choice/ending, reading/listening modes | English recording/text only/Chinese-audio limitation, complete transcript and translation, metadata loading/error, stop playback on mode/branch exit, restart and reviewed/context continuation | `story-*` |
| Lens | Visitor-facing capture guidance, consent/privacy and honest unavailable controls | No file input/camera/media request; explicitly scripted result scenarios, denial recovery guidance, comparison/cancel/retry | `lens-*` |
| Interests | Empty onboarding, direct editing, reset, clearly labelled example | Voluntary page-local choices, no tracking/saved profile; neutral approved browsing after reset, eligible matching records or truthful no-match recovery | `interests-*` |
| Status | Friendly availability, last check/retry, optional diagnostics | Actual anonymous-visit state and benefit/privacy, unavailable/retry, session failure/reset | `status-*` |
| Missing room | Localized friendly 404 with Home/Explore recovery | Actual HTTP 404 retained; broken links have a concrete way back | `missing-*` |

## State and capability rules

Approved record links always retrieve the current published record and fail closed on withdrawal/error. Art is decorative except sourced map boundaries; the terrain remains a labelled approximate generated presentation. No generated image is represented as recognition evidence. Scripted Guide progress is not a validated answer. Its preview emits no answer citations; approved coverage links open real source evidence. Real model calls, private-media lifecycle, durable journeys, story generation and stored recommendations remain later-phase APIs.

Language/graphics preferences persist in their existing cookies. Guide, Journey and catalog city/view/filter context remain in root-provider memory during internal navigation, and clear on reload/close. Free map pan/zoom refits the selected city on reentry. Demo-mode controls do not appear as live integrations. [Exact temporary-state policy](../docs/visit-state-and-context.md).

## Image and interaction QA checklist

- [x] Original scene masters, guide transparency, map boundaries and reviewed record hashes preserved.
- [x] Heroes/covers are bounded independently of page height; portrait remains a small badge.
- [x] Responsive image candidates decode at all three sizes; decorative images remain separate from reviewed evidence.
- [x] EN/ZH composition, reading contrast and focus styling reviewed on actual rendered imagery/panels; opaque-surface token contrast measured separately.
- [x] Current mobile route visible; every destination remains accessible; compact Explore/Sources navigation available.
- [x] Standalone controls reviewed against 44×44 targets; small approved-reading links and Chinese removal controls corrected. Dense geographic shapes retain directory equivalents.
- [x] Dialog keyboard traversal includes summaries, interior whitespace stays open, background scroll/focus restore, expanded atlas is native modal.
- [x] Composer is checked at a reduced viewport and actual Send works with the compact navigation; visual-viewport adaptation is implemented.
- [x] A constrained Chromium network profile (500ms latency, 256000 B/s download, 64000 B/s upload), offline state and reconnect/retry are exercised.
- [ ] Real phone/software keyboard: no physical-device tool or adb available here. Reduced viewport/CDP tests do not substitute for this.
- [ ] Safari: unavailable on the Linux host. Chromium checks do not certify Safari.
- [ ] Real screen reader: no screen reader is installed/available here. Automated axe/focus traversal does not substitute for listening and interaction checks.

## Outstanding external verification — M16

M16 is **PARTIAL**, not complete: the inventory, image QA and available checks are delivered, while three explicitly required environments remain unverified. [Environment evidence](evidence/ui-part-4/environment-validation.json).

| Environment | Required manual procedure | Record before marking passed |
|---|---|---|
| Real phone/software keyboard | Open Guide, expand preview, focus/type/Send/Stop/Retry with keyboard open; rotate, dismiss keyboard, navigate via compact controls; test map pinch and dialog close/scroll restore | Device/OS/browser/keyboard, EN/ZH results, composer/Send visibility, screenshots and defects |
| Safari | Test all routes, images, cookies, custom dropdown keys/touch, source/atlas modal traversal, audio metadata/play/pause/seek, offline/retry and 200% reflow | macOS/iOS and Safari versions, route/state results and defects |
| Screen reader | Verify headings/landmarks/current route, focus return, summary disclosure, source citations, progress/error/refusal announcements, disabled capability explanations and interest chart text equivalent | Reader/browser/version, reading/focus sequence, spoken announcements and defects |

Part 4 must not be called fully validated until these three checks have real evidence.
