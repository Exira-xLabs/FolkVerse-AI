# Dropdown UI refinement

Verified 5 October 2026, Asia/Shanghai. The requested scope is every dropdown in the current museum UI: Region and Theme in Explore; Interests and Time in Journey; the demo scenario in Lens.

`MuseumSelect` provides a labelled select-only combobox and listbox, gold selection checkmarks, readable 44px option rows, keyboard/typeahead navigation, cancellation without committing a value, outside dismissal and focus preservation. Menus render outside the glass panels to avoid clipping, scroll within a bounded height, and open upward when there is more room above the trigger. Styling uses existing museum tokens and supports reduced motion/transparency/graphics. Collection filters, map selection and demo choices retain their existing behavior.

| Command | Result | Evidence |
|---|---|---|
| `pnpm lint` | Exit 0 | [Log](lint.txt) |
| `pnpm typecheck` | Exit 0; TypeScript and strict mypy | [Log](typecheck.txt) |
| `pnpm --filter @folkverse/web exec tsc --noEmit --target es2022 --module nodenext --moduleResolution nodenext --esModuleInterop --skipLibCheck ../../tests/e2e/dropdowns.spec.ts ../../tests/e2e/content.spec.ts ../../tests/e2e/museum-ui.spec.ts ../../tests/e2e/liaoning-map.spec.ts` | Exit 0 | [Log](browser-typecheck.txt) |
| `env -u NODE_TLS_REJECT_UNAUTHORIZED pnpm build` | Exit 0 | [Log](build.txt) |
| `FOLKVERSE_EVIDENCE_DIR=report/evidence/dropdown-ui pnpm exec playwright test --config .local/playwright-recovery.config.ts` | Exit 0; 27 passed, no retries | [Log](browser-tests.txt), [JSON](browser-results.json) |
| `pnpm assets:verify` | Exit 0; nine original assets and reference copies verified | Recovery terminal output |
| `git diff --check` | Exit 0 | Recovery terminal output |

The ignored recovery config inherits the normal Playwright configuration and reuses the already running API. The browser suite includes two new menu tests, six map tests, collection/foundation/museum regressions and all eight routes at desktop/phone/tablet sizes in both languages. Existing tests now select visible options and assert displayed choices.

Visually inspected open menus: [Region desktop](region-menu-desktop.png), [Time phone](time-menu-phone.png), [Chinese scenario phone](scenario-menu-phone-zh.png). Phone interaction uses Chromium's mobile/touch context; physical devices and Safari remain untested. The production web/API previews were restarted after the test servers stopped. [Preview checks](live-service-check.json).

Existing map artwork, sourced boundaries and content reviews were preserved. Changes remain local; no commit, push or deployment was performed.
