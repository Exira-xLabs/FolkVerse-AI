import { createHash } from "node:crypto";
import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const artifacts = ["packages/contracts/openapi.json", "packages/contracts/src/schema.d.ts"];
const hash = file => createHash("sha256").update(readFileSync(path.join(root, file))).digest("hex");
const before = artifacts.map(hash);
execFileSync("pnpm", ["contracts"], { cwd: root, stdio: "inherit", shell: process.platform === "win32" });
if (artifacts.some((file, i) => hash(file) !== before[i])) throw new Error("Contract generation is not deterministic");
execFileSync(process.execPath, ["scripts/assets.mjs"], { cwd: root, stdio: "inherit" });
for (const file of [".env", "apps/web/.env.local"]) {
  execFileSync("git", ["check-ignore", "-q", file], { cwd: root });
}
const env = readFileSync(path.join(root, ".env"), "utf8");
const secrets = env.split(/\r?\n/).filter(line => /^(SESSION_SECRET|POSTGRES_PASSWORD|DEEPSEEK_API_KEY)=/.test(line))
  .map(line => line.slice(line.indexOf("=") + 1)).filter(value => value.length > 12);
let files = 0;
function inspect(folder) {
  if (!existsSync(folder)) return;
  for (const entry of readdirSync(folder)) {
    if (["node_modules", ".venv", "__pycache__"].includes(entry)) continue;
    const target = path.join(folder, entry);
    if (statSync(target).isDirectory()) inspect(target);
    else if (/\.(tsx?|mjs|py|json|md|js|html|css)$/.test(entry)) {
      files++;
      const bytes = readFileSync(target, "utf8");
      if (secrets.some(secret => bytes.includes(secret))) throw new Error(`Local secret found in ${path.relative(root, target)}`);
    }
  }
}
for (const folder of ["apps/web/src", "apps/web/.next/static", "apps/api/src", "packages", "docs", "data", "report", "scripts", "tests"]) inspect(path.join(root, folder));
console.log(`Contracts regenerated identically; local env files ignored; ${files} source/document/browser-output files checked for configured secrets.`);
