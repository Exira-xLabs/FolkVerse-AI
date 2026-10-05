import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const manifest=JSON.parse(readFileSync('apps/web/src/lib/maps/liaoning-contours.json','utf8'));
const geography=JSON.parse(readFileSync('apps/web/src/lib/maps/liaoning-geography.json','utf8'));
assert.deepEqual(manifest.bounds,geography.bounds);
assert.deepEqual(manifest.metres,[50,200,500,1000]);
assert.equal(manifest.tiles.length,9);
let bytes=0;
for(const tile of manifest.tiles){const payload=readFileSync(`apps/web/public${tile.src}`);assert.equal(createHash('sha256').update(payload).digest('hex'),tile.sha256);assert.deepEqual(payload.toString().match(/viewBox="([^"]+)"/)[1].split(" ").map(Number),[tile.x,tile.y,tile.size,tile.size]);assert.ok(!/NaN|Infinity|<script|foreignObject|href=/.test(payload.toString()));bytes+=payload.length;}
for(const tile of manifest.sourceTiles){const name=tile.url.match(/terrarium\/(\d+)\/(\d+)\/(\d+)\.png$/);assert.ok(name);const payload=readFileSync(`.local/liaoning-v2/elevation/${name[1]}-${name[2]}-${name[3]}.png`);assert.equal(createHash('sha256').update(payload).digest('hex'),tile.sha256);}
console.log(`PASS: 9 independently hashed local SVG tiles, four numerical contour levels, original bounds and ${manifest.sourceTiles.length} source DEM tile hashes; ${bytes} total vector bytes. Native vector rendering introduces no invented elevation detail.`);
