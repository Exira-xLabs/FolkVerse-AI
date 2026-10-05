import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import assert from "node:assert/strict";
const read = path => JSON.parse(readFileSync(path, "utf8"));
const publicShape = read("apps/web/public/folkverse/maps/liaoning.geojson");
const atlas = read("apps/web/src/lib/maps/liaoning-geography.json");
const seed = read("data/seed/liaoning.json");
const proof = read("report/evidence/phase02-map/geography-verification.json");
assert.equal(publicShape.properties.iso_3166_2, "CN-LN");
assert.equal(publicShape.geometry.type, "MultiPolygon");
assert.deepEqual(publicShape.geometry, atlas.geometry);
assert.equal(createHash("sha256").update(readFileSync("apps/web/public/folkverse/maps/liaoning.geojson")).digest("hex"), proof.geometry_hash);
assert.equal(atlas.cities.length, 14);
assert.deepEqual(atlas.cities.map(c => c.id).sort(), seed.cities.map(c => c.id).sort());
function insideRing(point, ring) {
  const [x,y] = point; let hit = false;
  for (let i=0,j=ring.length-1;i<ring.length;j=i++) {
    const [ax,ay] = ring[i], [bx,by] = ring[j];
    if ((ay>y)!==(by>y) && x < (bx-ax)*(y-ay)/(by-ay)+ax) hit = !hit;
  }
  return hit;
}
for (const city of atlas.cities) {
  assert.deepEqual(city.names, seed.cities.find(c => c.id===city.id).names);
  assert(city.coordinates.every(Number.isFinite));
  assert(atlas.geometry.coordinates.some(p => insideRing(city.coordinates,p[0]) && !p.slice(1).some(r => insideRing(city.coordinates,r))), city.id);
  assert(["www.naturalearthdata.com","www.wikidata.org"].includes(new URL(city.coordinate_source).hostname));
}
const terrain = read("report/evidence/phase02-map/terrain-generation.json");
assert.equal(createHash("sha256").update(readFileSync(terrain.asset_path)).digest("hex"), terrain.sha256);
const districts = read("apps/web/public/folkverse/maps/liaoning-cities.geojson");
const districtClient = read("apps/web/src/lib/maps/liaoning-city-boundaries.json");
const districtProof = read("report/evidence/phase02-map/atlas-v2/city-boundary-verification.json");
assert.deepEqual(districts, districtClient);
assert.equal(createHash("sha256").update(readFileSync(districtProof.public_path)).digest("hex"), districtProof.sha256);
assert.equal(districts.features.length, 14);
assert.equal(new Set(districts.features.map(f => f.properties.id)).size, 14);
assert.equal(districts.license, "https://opendatacommons.org/licenses/odbl/1-0/");
for (const city of atlas.cities) {
  const district = districts.features.find(f => f.properties.id === city.id);
  assert(district, city.id);
  assert.deepEqual(district.properties.names, city.names);
  assert.equal(district.properties.admin_level, 5);
  assert.equal(district.geometry.type, "MultiPolygon");
  assert(district.geometry.coordinates.some(p => insideRing(city.coordinates,p[0]) && !p.slice(1).some(r => insideRing(city.coordinates,r))), `${city.id} own boundary`);
  assert.equal(new URL(district.properties.source).hostname, "www.openstreetmap.org");
}
const v2 = read("report/evidence/phase02-map/atlas-v2/terrain-generation.json");
assert.equal(createHash("sha256").update(readFileSync(v2.asset_path)).digest("hex"), v2.sha256);
const elevation = read("report/evidence/phase02-map/atlas-v2/elevation-provenance.json");
assert.deepEqual(elevation.bounds, atlas.bounds);
assert.equal(createHash("sha256").update(readFileSync(elevation.reference_path)).digest("hex"), elevation.reference_sha256);
console.log("PASS: province preserved; 14 official cities inside their sourced OSM prefecture boundaries; public/client boundary hashes and ODbL attribution match; generated v1/v2 assets and sourced elevation reference hashes verified.");
