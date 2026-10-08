# Data and API contracts
Internal proposed contracts, not paid external subscriptions. Prefix `/api/v1`. Stable opaque IDs, snake_case JSON, ISO 8601 UTC timestamps; locale `en | zh-CN`. Generate frontend types from backend OpenAPI rather than maintaining contradictory schemas.

## Models
| Entity | Fields/relationships |
|---|---|
| Region | id, localized names, approved_geometry_ref nullable, review_status |
| Exhibit | id, localized title/summary, themes, estimated_minutes, publication_status, review_id |
| ExhibitRegion | exhibit_id, region_id, geographic_role (practice/origin/context) |
| Source | id, institution, title, canonical_url, fetched_at, external_id, raw_hash |
| Passage | id, source_id, text, language, locator, rights_basis, review_status, embedding_version |
| Claim | id, exhibit_id, text, passage_ids, review_status |
| Artifact | id, institution, external_object_id, catalog title/date/medium, origin, current_location, source_id |
| ArtifactExhibit | artifact_id, exhibit_id, evidence_passage_ids; relation may be absent |
| Media | id, hash, role decorative/reference/user_upload, rights_code, source_id, storage_key, expiry, owner_session |
| Review | status draft/approved/rejected/withdrawn, reviewer, reviewed_at, notes |
| StoryNode | story_id, node_id, adaptation_text, context_passage_ids, choices and target node IDs |
| Journey/Stop | owner_session, locale, total_minutes; ordered valid exhibit IDs |
| Consent/ProfileTopic | owner_session, explicit weights, behavioral_opt_in, consent version |
| InteractionEvent | owner_session, type, exhibit_id, timestamp; opted in and minimized |
| ScanJob | owner_session, media_id, status, result, model/corpus versions, expiry |

Unique artifact key `(institution, external_object_id)`. Media rights are separate from text rights. Draft/withdrawn sources never enter production retrieval. Revocation invalidates dependent caches/vectors. Imported records are not automatically approved.

## Endpoints
| Method/path | Input | Output/behavior |
|---|---|---|
| GET `/health` | none | service state without secrets |
| GET `/regions` | locale | reviewed region list |
| GET `/exhibits` | region_id?, themes?, q?, cursor?, limit | published cards + next_cursor |
| GET `/exhibits/{id}` | locale | exhibit and source/action references |
| GET `/sources/{id}` | none | public source metadata and permitted excerpts |
| POST `/journeys` | interests[] (≤8), locale, duration_minutes 5–60, region_id?, novelty_exhibit_ids[]?, start_exhibit_id? | owned deterministic ordered stops + reasons + stored-estimate total, version, notice and explanation_status |
| GET `/journeys` | locale?, limit 1–20 | newest owned routes; every stop revalidated on read |
| GET `/journeys/{id}` | locale? | owned route for reload; unavailable/over-budget stops omitted with an explicit notice |
| PATCH `/journeys/{id}` | required ordered_exhibit_ids[] (0–24), expected_version?; locale? query | ownership, publication and time revalidation; row-locked version conflict returns 409; empty route is valid |
| POST `/guide` | question 1–2000 chars, locale, exhibit_id?, conversation_id? | validated JSON or SSE via fetch |
| POST `/media` | multipart file + purpose | private owned media_id after sanitization |
| POST `/scans` | media_id, label_media_id?, locale | 202 with scan_id and queued status; idempotency key |
| GET `/scans/{id}` | owned ID | queued/running/completed/failed and result |
| DELETE `/scans/{id}` | owned ID | cancel where possible and schedule deletion |
| GET `/stories/{id}` | locale | approved graph entry/context |
| POST `/story-sessions` | story_id, locale | session and first node |
| POST `/story-sessions/{id}/choices` | choice_id, expected_node_id | validated next node; reject stale choice |
| POST `/voice/transcribe` | owned audio media_id, locale | editable transcript or explicit unavailable |
| POST `/voice/synthesize` | validated answer_id or story_node_id, voice_id | audio media reference and duration |
| GET/PATCH `/profile/topics` | explicit weights and opt-in setting | owned profile |
| DELETE `/profile/topics` | none | reset explicit and derived interests |
| GET `/recommendations` | locale | eligible exhibits and reason codes |
| DELETE `/account` | none | deletes anonymous session data too; deletion status |

Local curation CLI initially; no public admin endpoint. Render sanitized markdown with raw HTML disabled. Treat URLs from model output as untrusted; display only known source URLs.

## Error envelope
```json
{"error":{"code":"provider_unavailable","message":"The guide is temporarily unavailable.","retryable":true},"request_id":"req_example"}
```
400 malformed input; 401 missing identity; 403 denied ownership; 404 hidden/not found; 409 stale state; 413 oversized upload; 422 schema failure; 429 rate/budget limit; 503 provider unavailable. Avoid raw SQL, credentials or provider-internal details in responses.

## Guide output and streaming

The owner-authorized hybrid extension is specified in [the versioned output design](../docs/guide-hybrid-output-contract.md). Runtime schemas remain the existing contract until generation, validation and browser rendering are migrated together. Social/general sections cannot carry fabricated citations; precise local claims require evidence.
Retrieve evidence, obtain structured model output, validate, then display factual content. MVP SSE can emit progress immediately but sends only validated answer segments. Never stream raw unsupported claims as already sourced facts. First meaningful answer latency excludes progress messages.

Events: `meta` (request_id, mode, corpus_version), `status` (retrieving/generating/validating), `answer` (text + passage IDs), `sources`, `done` (answer_id), or terminal `error`. Use fetch for POST streaming; native EventSource doesn't submit POST bodies. Cancel local work on disconnect, bound retries and disable proxy buffering.

```json
{"answer_id":"ans_example","answer_text":"...","evidence_ids":["passage_example"],"uncertainty":"supported","related_exhibit_ids":[],"mode":"live"}
```
Uncertainty enum: supported/partial/insufficient. Resolvable source IDs alone do not establish that the passages support the claims. Include human sampling; a model's own support label isn't validation.

## Scan output
```json
{
  "decision_state":"related_object_class",
  "candidate_object_ids":["met:50824"],
  "visible_features":["decorated ceramic body"],
  "evidence_ids":["passage_catalog_example"],
  "follow_up_request":"Photograph the exhibit label if available.",
  "explanation":"A related catalog candidate, not an identification of your object.",
  "mode":"live"
}
```
Schema illustration, not an actual result for Met 50824. States: likely_catalog_match, related_object_class, insufficient_image, unknown. Provider failure is a service error, never a fabricated unknown or successful match. No public confidence percentages. Candidate IDs must belong to the approved retrieval set. Disable live likely_catalog_match until validation supports its decision threshold; labelled fixtures may exercise that UI.

## Ownership and cleanup
Derive owner from signed session, not client-supplied owner IDs. Random IDs don't replace authorization. Validate file signature, dimensions and decoding; strip EXIF; reject oversized decompressed images. Default raw image deletion within 24h and speech deletion after transcription requires a real scheduled cleanup job. Provider retention is separate. User uploads never go in public assets or git. Clear private caches, profile events and owned jobs on deletion.
