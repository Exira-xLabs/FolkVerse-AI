import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync, realpathSync } from "node:fs";
import { createRequire } from "node:module";

const sharp = createRequire(realpathSync(new URL("../apps/web/node_modules/next/package.json", import.meta.url)))("sharp");
const read = path => JSON.parse(readFileSync(path, "utf8"));
const hash = path => createHash("sha256").update(readFileSync(path)).digest("hex");
for (const [path, sha] of Object.entries(read("report/evidence/ui-refinement/protected-hashes.json"))) {
  assert.equal(hash(path), sha, `Protected file changed: ${path}`);
}
const art = read("report/evidence/ui-refinement/artwork.json");
assert.equal(art.length, 8);
for (const asset of art) {
  assert.equal(hash(asset.dest), asset.sha256);
  assert.equal(hash(asset.input), asset.input_sha256);
  const metadata = await sharp(asset.dest).metadata();
  assert.equal(metadata.width, asset.width);
  assert.equal(metadata.height, asset.height);
  assert(asset.width >= 1671 && asset.height === 941);
}
for (const asset of read("report/evidence/ui-refinement/lossless-delivery.json")) {
  assert.equal(hash(asset.dest), asset.sha256);
  const a = await sharp(asset.source).ensureAlpha().raw().toBuffer();
  const b = await sharp(asset.dest).ensureAlpha().raw().toBuffer();
  assert.equal(a.length, b.length);
  for (let i = 0; i < a.length; i += 4) {
    assert.equal(a[i + 3], b[i + 3], "Alpha changed");
    if (a[i + 3] > 0) for (let c = 0; c < 3; c++) assert.equal(a[i + c], b[i + c], "Visible pixel changed");
  }
}
console.log("PASS: eight refined native scene masters; lossless guide/terrain visible pixels and alpha; all protected original artwork, geography and reviewed content hashes preserved.");
