import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const sync = process.argv.includes("--sync");
const manifest = JSON.parse(readFileSync(path.join(root, "assets/ASSET_MANIFEST.json"), "utf8"));
const dest = path.join(root, "apps/web/public/folkverse");
if (sync) mkdirSync(dest, { recursive: true });
for (const asset of manifest.assets) {
  const source = path.join(root, "assets", asset.file);
  const target = path.join(dest, asset.file);
  if (sync) copyFileSync(source, target);
  for (const file of [source, target]) {
    const bytes = readFileSync(file);
    const sha = createHash("sha256").update(bytes).digest("hex");
    if (sha !== asset.sha256) throw new Error(`Hash mismatch: ${path.relative(root, file)}`);
    if (bytes.readUInt32BE(16) !== asset.width || bytes.readUInt32BE(20) !== asset.height) {
      throw new Error(`Dimensions mismatch: ${asset.file}`);
    }
    if ((bytes[25] === 6 ? "RGBA" : "RGB") !== asset.mode) {
      throw new Error(`PNG color mode mismatch: ${asset.file}`);
    }
  }
}
if (sync) copyFileSync(path.join(root, "assets/ASSET_MANIFEST.json"), path.join(dest, "ASSET_MANIFEST.json"));
for (const folder of ["ui", "business", "brand"]) {
  const destination = path.join(root, "design/reference", folder);
  if (sync) mkdirSync(destination, { recursive: true });
  for (const file of readdirSync(path.join(root, "references", folder)).filter((p) => p.endsWith(".png"))) {
    const source = path.join(root, "references", folder, file);
    const target = path.join(destination, file);
    if (sync) copyFileSync(source, target);
    if (!existsSync(target) || !readFileSync(source).equals(readFileSync(target))) {
      throw new Error(`Reference mismatch: ${folder}/${file}`);
    }
  }
}
console.log(`Verified ${manifest.assets.length} original assets, PNG dimensions/color modes, and all reference copies.`);
