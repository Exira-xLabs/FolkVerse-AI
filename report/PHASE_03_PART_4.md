# Phase 03 Part 4 — owned live Guide and sources

6 October 2026, Asia/Shanghai. **Implementation and fixture verification are complete for Part 4. Real DeepSeek/PostgreSQL integration remains blocked; Phase 03 remains incomplete.**

The Guide now has a session-owned JSON/fetch-SSE endpoint, a streaming Next.js BFF, live Jinyao Messenger controls and source inspection. Current session ownership and reviewed evidence are rechecked before answer publication. Progress streams before validation; provider deltas do not. Failed, interrupted or mismatched streams never display a successful factual response. Stop, close and disconnection cancel upstream work; Retry is explicit.

The live UI supports English/Chinese, published exhibit suggestions, optional exhibit scope, three requested depths and opt-in signed topic/evidence context. It preserves Jinyao's approved presentation, rectangular send button, no Clear action and page-only history retained on popup close/reopen. The conservative complete-passage harness remains in force: depth controls cannot manufacture broader expert explanations. Source inspection rechecks published source metadata and passage/review/rights fields, with honest changed/withdrawn/unavailable states and nested-dialog focus restoration.

The BFF bounds inputs, checks origin, forwards only the anonymous-session cookie and propagates upstream status/cancellation. Direct proxy checks caught Next.js using its bind hostname in `request.url` while the browser used a different Host; origin verification now checks the browser Host plus scheme, and the API still enforces configured allowed origins. The API also bounds cheap requests per worker, keeps shared provider admission/budget enforcement in PostgreSQL and runs ledger retention maintenance every 60 seconds. Checked-content emission/receipt latency is separated from progress and insufficient outcomes; no production latency benchmark is claimed.

| Verification | Result | Evidence |
|---|---|---|
| New HTTP/SSE boundary suite | 13 pass | [Verification record](evidence/phase03-part4/verification.json) |
| Retrieval, gateway, harness and outage regression | 152 pass; **165 total** | Same record |
| Isolated Chromium browser suite | **18 pass**: 12 live presentation, 2 real BFF fixture transport, 4 existing demo regressions | [Browser results](evidence/phase03-part4/browser-results.json) |
| API Ruff / strict mypy | Pass; 20 source files | Verification record |
| Web ESLint / TypeScript | Pass | [Types](evidence/phase03-part4/web-typecheck.log), verification record |
| Production build | Pass | Verification record |
| Contract regeneration, shipped assets and configured-secret checks | Pass | [Foundation](evidence/phase03-part4/foundation.log) |
| Whitespace checks | Pass | Verification record |
| Fresh DeepSeek authentication-only check | **HTTP 401** | Verification record; no response body or credential recorded |
| Real database/provider/quality evaluation | Unverified | PostgreSQL container absent; no paid completion |

Browser coverage includes EN desktop and ZH phone layouts, supported/unsupported outcomes, consented follow-ups, source focus/history, timeout/cap/rate/context errors, truncated/mismatched evidence, Stop/Retry, withdrawn-source inspection, real proxy forwarding/status/origin/body bounds/upstream cancellation and scripted-demo privacy/layout/motion/low-data regressions. Fixture evidence is explicitly synthetic and used only by tests. The production code never substitutes a fixture for real data or provider failure. The dedicated configuration runs without PostgreSQL; the main database-backed configuration excludes these isolated fixtures.

The initial demo regression failed because the unavailable API produced a console resource error; the isolated upstream now returns a labelled empty catalog for presentation tests. A subsequent exploratory browser run was interrupted after rebuilding the server output during that run; it is not counted as passing evidence. The final fixed-build run passes all 18 checks. Physical phones, Safari and screen readers were not executed. Node 26 is outside the declared Node 22 range; successful checks do not certify supported-runtime compatibility. The existing FastAPI TestClient deprecation warning remains.

The fresh server-side `/models` authentication probe sent no museum question or generation request and still received 401. The key is confined to ignored `.env`, and `.env.example` stays placeholders. Demo mode and zero provider budget remain unchanged; paid generation was not activated. PostgreSQL is not running, so real session/corpus traversal, production locking, migrations and scheduled maintenance remain unverified. Parts 5–6 still own hybrid retrieval, broader reviewed coverage and the dated bilingual evaluation. No historical expertise, 95% score or phase completion is claimed.

Changed areas: API guide route/progress/maintenance, generated contracts, BFF, Jinyao chat and current-source inspector, dedicated tests/configuration, phase/presentation/decision/status docs and this report. Prior work and pre-existing development type imports are preserved. [Transport and lifecycle contract](../docs/guide-live.md).
