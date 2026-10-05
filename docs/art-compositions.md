# Museum image compositions

Updated 5 October 2026, Asia/Shanghai. This closes the composition work in audit A08 using the existing versioned masters. No new generated cover, documentary image or cultural approval is claimed.

| Context | Composition | Delivery / role |
|---|---|---|
| Route hero | Bounded landscape scene on desktop/tablet; whole landscape frame below the heading on phones. Phone Explore omits its decorative scene. | Responsive quality-90 image. Decorative atmosphere, independent of document height. |
| Home collection card | Relief-map museum scene (`02_interactive_map`), focal point 68% / 50%, 16:9 cover. | Distinct from Story; labelled decorative museum illustration. This is not the sourced interactive atlas. |
| Home Story card | Shadow-puppetry stage (`04_shadow_puppetry`), focal point 78% / 46%, 16:9 cover. | Original-fiction preview with decorative illustration. |
| Home Journey card | Learning/museum scene (`03_cultural_journey`), focal point 83% / 58%, 16:9 cover. | Preview illustration, not a photograph documenting a reviewed exhibit. |
| Home Guide card | Original transparent guide, centered and contained in the 16:9 frame. | Lossless identity-preserving delivery; labelled fictional companion. |
| Performance fixture thumbnail | Shadow-stage scene, focal point 83% / 44%, 64×80px cover. | Decorative fixture thumbnail; responsive image candidate sized for the actual 64px slot. |
| Food fixture thumbnail | Journey scene, focal point 83% / 66%, 64×80px cover. | Decorative fixture thumbnail. |
| Music/interests fixture thumbnail | Cultural-constellation scene, focal point 77% / 48%, 64×80px cover. | Decorative fixture thumbnail, not inferred personal data. |
| Featured reviewed exhibit | Published title and reviewed summary from the API, with an action opening that exact exhibit and its sources. | Text-first composition. No decorative cover is represented as documentary exhibit imagery. |
| Reviewed exhibit/source detail | Title, reviewed text, excerpts, institution and source link on a calm reading surface. | No decorative scene inserted as evidence. No recognition/reference photograph is fabricated. |

Focal positions are centralized in `apps/web/src/lib/museum-art.ts`; context-specific frames live in `apps/web/src/app/globals.css`. Phone heroes preserve the full scene while smaller covers crop around their intended subject. Native master dimensions are unchanged; a larger responsive candidate cannot create additional source detail.

The original supplied masters, refined scene outputs, guide pixels/alpha, terrain, geography and reviewed-content hashes are checked by `node scripts/verify-museum-art.mjs`. Screenshots remain local under `report/evidence/ui-part-a/` and are ignored by Git. The browser tests check distinct collection/Story sources, 16:9 card frames at three sizes, published-record navigation and the existing DPR-2 image behavior. These checks do not replace a full contrast audit or physical-device review.
