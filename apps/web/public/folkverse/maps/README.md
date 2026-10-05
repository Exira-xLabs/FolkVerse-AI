# Liaoning map asset sources

- `liaoning.geojson`: Natural Earth 1:10m `CN-LN` province outline; public domain. https://www.naturalearthdata.com/about/terms-of-use/
- `liaoning-cities.geojson`: fourteen simplified prefecture-level city boundaries derived from OpenStreetMap administrative relations. © OpenStreetMap contributors. This derived boundary database is available under ODbL 1.0: https://opendatacommons.org/licenses/odbl/1-0/ . Source relation URLs are retained per feature; attribution/terms: https://www.openstreetmap.org/copyright . Independently sourced province/coastline differences are handled by display clipping, not invented subdivision data.
- `liaoning-terrain-v2.png`: AI-generated terrain interpretation using a numerical elevation reference. Mapzen terrain reference includes SRTM/GMTED2010 courtesy of USGS and ETOPO1 NOAA. Dataset/source attribution: https://github.com/tilezen/joerd/blob/master/docs/attribution.md . Geographic relief distribution is approximate; generated details are not measured terrain or satellite imagery.
- `liaoning-terrain-v1.png`: preserved earlier AI decorative terrain, superseded in the app by v2.

Full data provenance, hashes, generation prompt and checks: `docs/liaoning-map.md` and `report/evidence/phase02-map/atlas-v2/` in the repository.
