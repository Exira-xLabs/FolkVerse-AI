# Sources, scope and traceability

## Documents actually reviewed
- `references/FolkVerse_China_Business_Plan_Report.pdf`: current 33-page report, version 3.0, dated 29 September 2026.
- `references/FolkVerse_China_Competition_Business_Plan.pdf`: current eight-slide business pitch, with one financial slide and corrected deadline.
- `references/ui/`: original eight app UI screens; report pages 6–10 and 16 reproduce key screens. These are the layout source for the app.
- User-supplied official notice, published 23 September: [Liaoning international-student track implementation plan](https://cxcy.upln.cn/competitionDetails?id=b89a342f84f03b965c27a6af4cd4a20e). The site could not be loaded earlier; competition details here rely on the full notice supplied by the user, not an invented rubric.

## Report-to-build mapping
| Report pages | Requirement | Phase/spec |
|---|---|---|
| 1–5 | Concept, audience, nine features | Master brief, scope, QA feature checklist |
| 6 | Interactive region discovery | 01 visual shell; 02 content/map |
| 7 | Personalized digital journeys | 04 |
| 8, 18, 21 | Grounded guide and provider gateway | 03; content/runtime prompts |
| 9 | Branching stories | 06 |
| 10–14 | Camera, museum data, schema/rights | 02 and 05; data contracts |
| 15 | Voice/accessibility | 01 and 06; QA |
| 16 | Recommendations and interest profile | 07 |
| 17 | All cultural themes and curation | Content rules and schema |
| 19–20 | Architecture/API contracts | Architecture and data specs; 00 |
| 22 | Privacy/security/cultural governance | Every API phase and 08 |
| 23 | Measured acceptance criteria | QA and 08; targets not results |
| 24–26 | Commercial planning and costs | Architecture/costs; no MVP payment system |
| 27–30 | Schedule, team, pitch, expansion | README, QA, 08 |
| 31–33 | External sources and integration sketches | Links below; verify during implementation |

Supported theme taxonomy: folklore/legends, festivals/traditions, regional cultures, music/performance, clothing/adornment, crafts/artifacts, food culture, mythology. Ten pilot exhibits don't imply complete coverage. Source restrictions and reviewed terminology persist across translations and creative stories.

## Official implementation references
Rechecked 29 September 2026: DeepSeek vision, Met API documentation, Next.js installation and FastAPI SSE documentation. These confirm documentation availability, not credentialed integration, China network reliability or app benchmarks. Other references were in the source report and should be rechecked when used. Don't hardcode price, version or free-tier assumptions from this kit.

| Source | Link | Use |
|---|---|---|
| DeepSeek vision | https://api-docs.deepseek.com/guides/vision/ | Text+image request format and model alias |
| DeepSeek pricing | https://api-docs.deepseek.com/quick_start/pricing/ | Configure current budget rates before paid calls |
| DeepSeek JSON mode | https://api-docs.deepseek.com/guides/json_mode/ | Verify supported structured-output options |
| Met API | https://metmuseum.github.io/ | Current paginated search, object records and image rights |
| Cleveland API | https://openaccess-api.clevelandart.org/ | Optional second catalog; access test required |
| Chinese-CLIP | https://github.com/OFA-Sys/Chinese-CLIP | Candidate image/text encoder and license |
| BGE-M3 | https://huggingface.co/BAAI/bge-m3 | Text retrieval candidate and model license |
| pgvector | https://github.com/pgvector/pgvector | Vector columns/indexing in PostgreSQL |
| Next.js installation | https://nextjs.org/docs/app/getting-started/installation | Runtime and project setup |
| FastAPI SSE | https://fastapi.tiangolo.com/tutorial/server-sent-events/ | Check compatibility with selected FastAPI version |
| FastAPI docs | https://fastapi.tiangolo.com/ | Schemas, uploads, dependencies and API documentation |
| GLM vision | https://docs.z.ai/guides/vlm/glm-4.6v | Optional provider; verify available model ID |
| Alibaba speech | https://help.aliyun.com/zh/model-studio/realtime-tts-user-guide | Candidate live TTS integration |
| UNESCO ethics | https://ich.unesco.org/en/ethics-and-ich-00866 | Participation, attribution and cultural review |
| China heritage inventory | https://www.ihchina.cn/project.html?tid=1000 | Context research; no blanket reuse license assumed |

## Important implementation clarifications
1. API contracts are your own backend interfaces; they aren't additional subscriptions.
2. The Met catalog is an upstream data source, not a ready universal Chinese-culture recognition model.
3. Generated art illustrates the UI. It is not an artifact training dataset or reviewed geographic map.
4. Exact desktop visual matching requires rendering and comparison. Prompts alone don't prove fidelity.
5. Approved map geometry and calibrated scan labels may differ from conceptual artwork; document the difference rather than copy a false claim.
6. A GLM adapter is not a second mandatory bill. Speech can be deferred honestly; recorded narration isn't live voice.
7. Source validation is not only checking that a URL exists. Claims need supporting passages and review.
8. Build dates do not change the competition deadline: submit documents by 30 September, develop toward 10 October, pitch if selected 11–18 October.
9. This is a plan for all features with a narrow first corpus. Full production accounts, payments, institution admin and expanded regions remain later work.
