# Phase 03 push audit — 6 October 2026

The implemented baseline is suitable for source review and push after the checks below. Full Phase 03 production/expert-guide acceptance remains incomplete; deployment readiness is not inferred.

## Findings and fixes

1. **Provider mismatch.** The user clarified that the saved key is issued by Ollama. It was being sent to DeepSeek's own API, causing 401. Added explicit provider selection, separate credentials, the Ollama Cloud compatibility endpoint and current catalog model `deepseek-v4.1-flash`. Actual [Ollama diagnostic](evidence/phase03-push-audit/provider-diagnostic.json) confirms authentication: saved key gets model-not-found 404 for a deliberately absent model, invalid control gets 401. No successful generation ran. The key was migrated only within ignored private configuration, with a private backup.
2. **Account quota accounting.** Ollama uses a persistent, shared UTC daily request cap, including retries/failures, while retaining minute/concurrency limits. Zero cap or demo mode disables generation. No subscription USD/token price is guessed. Direct DeepSeek retains exact configured monetary price/budget gates. Neither provider falls back to the other's credential.
3. **Browser publication validation.** Stream parsing previously checked passage text/IDs but could accept empty support arrays, unmapped claim/source references, wrong-language sources, unused cited passages or unsupported extra display prose. It now checks all mappings, source coverage and the entire controlled attributed display before publishing. Six added browser regressions exercise these failures; valid EN/ZH streams still work.
4. **Secret-check coverage.** The former scanner omitted root-level files, `.env.example`, `.txt` logs and other extensions, and parsed quoted dotenv values incorrectly. It now scans every tracked/unignored Git candidate plus browser output, handles decoded dotenv values, rejects force-tracked private env files and checks bytes independent of extension. Seven isolated Node tests cover these boundaries. It checks configured local secrets; it is not a general credential-forensics guarantee.
5. **Worker environment.** The old environment denylist missed `DATABASE_URL` and custom credential names. The local embedding subprocess now receives only necessary runtime/localization paths and explicit offline flags. Timeout/cancellation tests verify that database and custom provider credentials are excluded and workers are killed/reaped.
6. **Supported paraphrase recall.** Harness v3 recognizes bounded full-title inventory/locality/category wording in both languages. Seventeen additional cases verify positive listing paraphrases and rejection of origins, dynasty qualifiers or extra injected/history requests. Reviewed exact statement support, review/rights gates and final revocation checks remain authoritative.

## Verification

| Check | Result |
|---|---|
| Portable guide/API/gateway regression suite | **251 passed**; [output](evidence/phase03-push-audit/api-tests.txt). Full database-backed content/foundation integration remains unavailable. |
| Browser/BFF/demo scenarios | **25 passed**, including six added malformed-publication regressions; [output](evidence/phase03-push-audit/browser-tests.txt). These use isolated fixtures. |
| Secret-check unit tests | **7 passed**; [output](evidence/phase03-push-audit/secret-tests.txt). |
| Ruff, ESLint, TypeScript, strict mypy | Passed; strict mypy covers 27 source files; browser/config TypeScript also passes. |
| Production web build | Passed; [output](evidence/phase03-push-audit/build.txt). |
| Production JavaScript dependency audit | Zero reported advisories across 140 dependencies; [output](evidence/phase03-push-audit/dependency-audit.json). This is the registry's current advisory coverage, not proof of zero vulnerabilities or a Python dependency audit. |
| Contracts, foundation assets/configured secrets, whitespace | Verified in the evidence directory. No Git candidate exceeds 10 MiB. Private configuration, weights, screenshots and confidential PDFs stay ignored according to existing rules. |
| Actual Ollama authentication/catalog | Verified independently of successful inference; saved key accepted, configured model in current catalog. |
| Actual PostgreSQL | Blocked: dedicated image pull failed at the Docker registry connection; [output](evidence/phase03-push-audit/database-start.txt). Unrelated containers were not changed. |

Node 26 remains outside the declared Node 22 range, and one existing Starlette/httpx test-client deprecation warning remains. Passing checks on this host do not certify the supported runtime.

## Evaluation and limits

The [audit regression run](evidence/phase03-push-audit/evaluation.json) meets **64/64 exposed v1 functional targets**, including 16 development and 48 previously reserved cases. Original Part 6 baseline (58/64) and its v2 diagnostic rerun (60/64) are unchanged. This improved result follows exposure and targeted development; it is not a fresh held-out expert-quality assessment.

| Dimension | Numerator / scored denominator | Available sample |
|---|---|---|
| Historical correctness | Pending / 0 | 22 answered responses |
| Claim support | 22 / 22 | 22 actual answered responses; abstentions excluded |
| Citation validity | 22 / 22 | 22 actual answered responses; full mappings/current evidence |
| Explanatory clarity | Pending / 0 | 22 answered responses |
| Bilingual faithfulness | Pending / 0 | 11 answered bilingual families |
| Uncertainty | 58 / 58 | Returned responses; six provider/errors excluded |
| Follow-up consistency | 10 / 10 | Checked seed, consent/ownership, citations and uncertainty |

The [human worksheet](evidence/phase03-push-audit/human-review-template.json) has 55 pending units and grants no expertise scores. Evaluation uses 46 mocked gateway calls and zero real inference calls; actual provider tokens/cost remain unmeasured. Timing and full corpus/harness/prompt/provider versions/hashes are in the run and describe local fixture work, not actual provider/BGE/SSE latency.

Current live configuration remains demo with zero Ollama daily request quota. Complete PostgreSQL restoration/migration and actual bounded Ollama JSON/SSE testing, finish pinned BGE inference/index benchmarks, obtain independent human review, and extend reviewed cultural coverage before claiming full Phase 03 acceptance. Only the two existing approved inventory passages support current answers. The draft review packet has not been approved.
