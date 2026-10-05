# Phase 02 rights and corpus evidence

Checked 5 October 2026, Asia/Shanghai. Current project scope is the whole Liaoning province. [Editorial packet](content-review.md), [approval receipt](../report/evidence/phase02/liaoning-editorial-approval.json), [scope withdrawal](../report/evidence/phase02/scope-correction.json).

| Corpus | Actual records | Publication / rights status |
|---|---:|---|
| Active Liaoning exhibits | 14 | 1 approved/published; 13 drafts; one candidate per city |
| Active Liaoning passages | 28 | 2 approved with text rights cleared; 26 drafts |
| Active Liaoning claims | 14 | 1 approved; 13 drafts |
| Active corpus regions | 15 | Province + 14 cities; 2 approved, 13 drafts; reviewed content associations are separate from atlas geography |
| Active regional sources | 2 | First provincial list approved; sixth list draft |
| Met artifacts | 37 | All draft; 0 published; no established Liaoning exhibit links |
| Met reference media | 32 | CC0 candidates with locally downloaded/hash-verified JPEGs; all draft; 0 published |
| Archived former scope | 10 exhibits / 20 passages / 10 claims / 2 sources / 1 region | Withdrawn; retained for audit; absent from published search/detail |
| Reviews, including history | 56 | Actual owner decisions and withdrawals; automated test approvals roll back |

The 10 reviewed exhibits / 30 eligible artifacts are targets. They are not achieved reviewed-publication counts. Thirty-two downloaded public-domain image candidates do not equal 32 approved recognition references. The only current published exhibit is the user-reviewed Fuzhou shadow puppetry summary. No external specialist review is claimed.

## Source handling

The two Liaoning government pages were inspected through the browser. Only original short bilingual summaries, attribution, locators and source descriptors are stored. For those sources `raw_payload` is the explicit descriptor and `raw_hash` identifies that descriptor; neither represents an archived original HTML page. No government/UNESCO/ihchina image, full page or unrestricted text dataset is reused.

Met records preserve the exact original UTF-8 JSON response string and its SHA256, original retrieval timestamp, institution/object ID, catalog title/date/material, origin fields and present museum repository. Import cache files retain the original bytes. All 41 current source-payload hashes were verified against their stored payloads. Re-importing all 37 actual Met objects left counts, source hashes and the human ledger unchanged: [integrity evidence](../report/evidence/phase02/corpus-integrity.json), [re-import](../report/evidence/phase02/met-full-reimport.json).

The sample objects were actually fetched again: 50824 “Vase with Daoist Immortals”; 449479 “Fragment of an Imported Chinese Bowl”; 460669 “Small wine pot or teapot”. [Actual sample import](../report/evidence/phase02/met-samples.json). These are museum catalog titles, not Liaoning attributions.

Official [Met API documentation](https://metmuseum.github.io/) and [Open Access policy](https://www.metmuseum.org/hubs/open-access) were checked on 5 October 2026. The adapter uses the current paginated `/v1.1/search` endpoint, not retired `/v1/search`. API access succeeded in this environment; no restriction was bypassed.

Each candidate image stores public-domain/reproduction flags, credit line, source-response hash, policy link, original image URL, SHA256 and local storage key. A conflicting reproduction flag blocks download. Candidate media is never approved automatically. All 32 current candidate image files were verified against their hashes. Missing/corrupt bytes fail publication eligibility and are excluded from the CLI's downloaded count. Local JPEGs and API caches are ignored, separate from public decorative assets.

## Publication boundary

Every approval is tied to the exact record and relationship hash. Region/source/passage/claim/exhibit eligibility is checked on each published read; draft, withdrawn, altered, unreviewed and uncleared dependencies fail closed. Source withdrawal clears passage embedding markers and hides dependent exhibits/artifacts immediately at the API. No retrieval vectors or published-content cache exist in Phase 02. Browser focus/15-second revalidation clears stale drawers; this is not instantaneous server push.

Supplied generated backgrounds and guide remain decorative, byte-identical and excluded from artifact references. The user-requested Liaoning atlas publishes a sourced Natural Earth province outline, fourteen OpenStreetMap prefecture-level city boundaries and fourteen geographic markers, independently of cultural record approval. Natural Earth data is public domain; Panjin and Huludao coordinates come from Wikidata's CC0 structured data. The city boundary GeoJSON/client database is distributed under ODbL 1.0 with visible OpenStreetMap attribution and downloadable source data. No hand-drawn/generated administrative polygons are used. [Exact sources, licences, hashes and verification](liaoning-map.md).

Terrain v2 is generated from a numerical shaded-relief reference drawn from thirty-six public Mapzen elevation tiles. The reference retains Mapzen/USGS/NOAA credit, original tile hashes and extent. The generated artwork follows approximate relief distribution and is labelled AI terrain guided by elevation, not satellite imagery or measured elevation. Its image/prompt/reference record is [retained](../report/evidence/phase02-map/atlas-v2/terrain-generation.json); v1 is preserved as earlier decorative artwork.

Other feature experiences remain labelled Phase 01 fixtures or unavailable live capabilities; no credentialed AI provider gateway, recognition results, evaluation photos or invented participants were introduced. Image generation produced only the public decorative map texture; its tool, complete prompt, asset path and hash are retained in the [generation record](../report/evidence/phase02-map/terrain-generation.json).

Corpus and ledger: [snapshot](../data/manifests/corpus.json), [review history](../data/manifests/review-ledger.json). [Operator instructions](curation.md) explain trusted restoration, fresh drafts, review, import and withdrawal. Original human reviewer/date/hash are preserved on restore. Snapshot hashes provide integrity, not an editor authentication signature.
