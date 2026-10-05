# Liaoning interactive atlas

Delivered locally on 5 October 2026 after the user requested a game-style map of the whole Liaoning province with a realistic province shape and every city. Open <http://localhost:3000/explore>.

## Geography and visual treatment

The province outline is the exact `CN-LN` MultiPolygon from [Natural Earth's 1:10m administrative provinces dataset](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_admin_1_states_provinces.geojson). Its seven polygon parts and 1,685 vertices are retained in [the public GeoJSON](../apps/web/public/folkverse/maps/liaoning.geojson) and [client geography](../apps/web/src/lib/maps/liaoning-geography.json). Natural Earth permits reuse of its [public-domain map data](https://www.naturalearthdata.com/about/terms-of-use/).

All 14 city names match the [official Liaoning administrative list](https://www.ln.gov.cn/web/sqgk/xzqh/index.shtml): Shenyang, Dalian, Anshan, Fushun, Benxi, Dandong, Jinzhou, Yingkou, Fuxin, Liaoyang, Tieling, Chaoyang, Panjin and Huludao. Twelve city-centre coordinates come from [Natural Earth's populated places](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_populated_places.geojson). Panjin and Huludao use Wikidata [Q75230](https://www.wikidata.org/wiki/Q75230) and [Q75379](https://www.wikidata.org/wiki/Q75379), under its [CC0 structured-data licence](https://www.wikidata.org/wiki/Wikidata:Licensing). The source URL for each coordinate is retained in the client data and evidence.

The province outline, city territories and markers share a north-up equirectangular projection, adjusted for longitude scale at the province's mean latitude. Label leaders move labels for readability; their marker anchors remain at the sourced coordinates. Geography is generalized for a provincial overview, rather than street navigation or cadastral use.

### City borders and modern markers

All fourteen prefecture-level city boundaries come from OpenStreetMap administrative relations (`admin_level=5`, as documented in [OSM's China boundary scheme](https://wiki.openstreetmap.org/wiki/China/Boundaries)). Complete outer member ways were polygonized, inner rings subtracted and the result simplified with a topology-preserving tolerance of 0.0008 degrees. Every marker lies inside its corresponding valid city MultiPolygon. The [per-city relation URLs, raw response hash, data timestamp and verification](../report/evidence/phase02-map/atlas-v2/city-boundary-verification.json) are retained.

The app draws subtle city boundaries, highlights the selected territory with a gold border and light tint, and fits its land extent into view. A territory can be clicked directly; city markers, directory buttons and the region selector also update the highlight. The markers are now glass locator discs with a mint/gold core; the house icons have been removed. All highlights remain stationary.

The public [city GeoJSON](../apps/web/public/folkverse/maps/liaoning-cities.geojson) and matching [client data](../apps/web/src/lib/maps/liaoning-city-boundaries.json) are available under [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), with visible © OpenStreetMap contributors attribution linking its [copyright/terms](https://www.openstreetmap.org/copyright). This is community mapping, not an official cadastral/legal boundary determination. The independent Natural Earth province and OSM city datasets have minor outer/coastal differences; city rendering is clipped to the province outline. Their union covers 99.0% of the Natural Earth province's generalized land area; gaps are retained rather than filled with invented polygons.

### Realistic terrain guided by elevation

The current [terrain v2](../apps/web/public/folkverse/maps/liaoning-terrain-v2.png) was generated with the built-in `image_gen.imagegen` tool using a [numerical shaded-relief reference](../report/evidence/phase02-map/atlas-v2/liaoning-elevation-reference.png). The reference decodes 36 zoom-8 Mapzen Terrarium elevation tiles, resamples the elevation grid to the exact atlas longitude/latitude extent and plots hypsometric tint with northwest hillshading. [Elevation tile URLs, hashes, decoding/projection method and attribution](../report/evidence/phase02-map/atlas-v2/elevation-provenance.json). Terrain data: Mapzen; SRTM/GMTED2010 courtesy of USGS; ETOPO1 NOAA. [Dataset](https://registry.opendata.aws/terrain-tiles/), [source/licence details](https://github.com/tilezen/joerd/blob/master/docs/attribution.md).

The [official Liaoning physical geography description](https://fgw.ln.gov.cn/fgw/fzgh60/l/index.shtml) also informed the prompt: central Liao River plain, forested eastern uplands, drier western hills and the southern Liaodong peninsula. The generation preserves the approximate distribution of that relief with natural forest, agricultural and coastal textures. It is an AI interpretation, not a satellite photograph or a measured elevation product. Rivers, vegetation and fine surface details remain approximate. The map visibly discloses this; no generated city/province boundaries are used.

Generation produced a 1,309×1,201 PNG. Its [complete prompt/tool/reference/path/hash record](../report/evidence/phase02-map/atlas-v2/terrain-generation.json) instructs north-up geographic alignment without cropping, labels, borders, markers, buildings or exaggerated alpine terrain. The app maps the entire image to the same extent without cover cropping. SHA256: `a742d6227d04677fa59b791bc32ddae6a6a4020be680c066fded77e9eda1eb5e`. Original supplied artwork and the earlier terrain v1 asset/evidence remain preserved.

## Visitor controls

- Select any city marker, territory or directory button to highlight its municipal boundary, fit its land territory and filter the city collection. City search accepts English or Chinese names.
- Drag to pan; wheel, two-finger pinch or plus/minus buttons to zoom; the fit button restores the whole province.
- Use the minimap to recenter. Keyboard arrows pan, plus/minus zoom, and Home fits the province.
- Expand the map for a larger view; Escape closes it. Expanded mode contains keyboard focus and restores page scrolling when closed.
- English/Chinese labels, phone/tablet layouts and reduced graphics/motion work with the existing museum controls.

All 14 cities remain navigable even where cultural records are pending review. Gold markers indicate currently published reviewed collection context. City selection never publishes draft facts: the Fuzhou shadow puppetry exhibit in Dalian remains the one approved exhibit, with thirteen city candidates still draft. Static geography is independent of the cultural corpus's review hashes and does not claim a new human editorial decision.

## Verification and evidence

Run from the repository root:

```sh
node scripts/verify-liaoning-geography.mjs
FOLKVERSE_EVIDENCE_DIR=report/evidence/phase02-map/atlas-v2 pnpm test:e2e
```

The verifier checks the public/client province and city geometry, retained hashes, fourteen official bilingual names, coordinates inside their own city and province, ODbL/source attributes, both terrain hashes and the elevation reference hash. [Original province evidence](../report/evidence/phase02-map/geography-verification.json), [current verification log](../report/evidence/phase02-map/atlas-v2/geography-check.txt).

Current browser verification covers six map tests plus the existing content, foundation and museum regressions. This includes city-to-exhibit/source navigation, all fourteen selected boundaries, direct territory clicks and clearing, unpublished-city behavior, wheel/drag/keyboard/minimap/expanded controls, Chinese phone selection and a real two-contact Chromium touch gesture. [Current results](../report/evidence/phase02-map/atlas-v2/browser-results.json), [current log](../report/evidence/phase02-map/atlas-v2/browser-tests.txt). The initial 23-test atlas evidence and five-test circle-fix evidence are preserved separately.

All eight museum routes are checked in English/Chinese at desktop, phone and tablet sizes. Current captures: [atlas desktop](../report/evidence/phase02-map/atlas-v2/liaoning-atlas-desktop.png), [Chinese phone](../report/evidence/phase02-map/atlas-v2/liaoning-atlas-phone-zh.png). Physical devices and Safari were not exercised. [Current project checks](build-status.md) retain the original content-phase evidence separately.

Developer data preparation scripts: [boundary assembly](../scripts/build-liaoning-city-boundaries.py), [numerical terrain reference](../scripts/build-liaoning-terrain-reference.py). Boundary assembly uses the cached raw Overpass response in `.local/liaoning-v2/city-relations-v2.json`; the exact query/endpoint is in the evidence above. Run it with `uv run --no-project --python 3.12 --with shapely==2.1.2 python scripts/build-liaoning-city-boundaries.py`. The terrain reference script requires numpy, Pillow and matplotlib, caches public elevation tiles locally and never edits generated artwork. Runtime maps use checked local assets and make no Overpass, DEM or paid-provider requests.

## Selected-city circle correction

The owner reported that the circle moved around after selecting a city. Reproduction with ordinary motion enabled showed the ring rotating around the SVG viewport origin rather than the city anchor: at a quarter turn it drifted 787 pixels from Dalian. [Before-fix measurement](../report/evidence/phase02-map/circle-bug-before.json). The earlier suite's reduced-motion default concealed that animation bug.

The selection ring is now stationary, centered on the selected geographic marker. Its decorative ring does not intercept pointer events. A new regression explicitly enables ordinary motion, selects every city, advances any ring animations through 35 seconds and checks center alignment before and after zoom. The five focused map tests include this regression and the existing map/city/touch interactions. [Current test log](../report/evidence/phase02-map/circle-fix/browser-tests.txt), [results](../report/evidence/phase02-map/circle-fix/browser-results.json), [production build](../report/evidence/phase02-map/circle-fix/build.txt), [lint](../report/evidence/phase02-map/circle-fix/lint.txt), [browser test types](../report/evidence/phase02-map/circle-fix/browser-typecheck.txt).

## Optional city previews and numerical detail

Hovering/focusing a marker, territory or directory button previews that city's currently published records without changing the selected city. The preview sits after the directory so introducing it cannot move a button during pointer-down/up. Its request is uncached, aborted on city change and revalidated; empty coverage is stated honestly.

Topographic detail uses nine independently hashed SVG tiles, clipped from four numerical contours (50/200/500/1000 metres) on the existing Mapzen Terrarium grid. Only tiles intersecting the camera load. A colour/metre legend, loading/retry and source/approximation explanation remain visible. Original generated scenery, elevations, province and city boundaries are unchanged; vector rendering remains sharp at zoom but adds no source resolution or surveying claim. The nine tiles total 486844 bytes before HTTP compression; this is measured asset size, not a Core Web Vitals score.

Rebuild with `uv run --no-project --python 3.12 --with numpy --with Pillow --with matplotlib python scripts/build-liaoning-contours.py`. Verify with `node scripts/verify-liaoning-contours.mjs`, which checks output hashes, source DEM hashes and the exact existing atlas bounds. Provenance is in `apps/web/src/lib/maps/liaoning-contours.json`. The runtime never fetches DEM tiles or contacts a third-party map service.
