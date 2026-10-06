import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { checkSecrets } from "./check-secrets.mjs";

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
// Parse quoted/interpolated dotenv values rather than scanning their raw representation.
// Capture this subprocess output internally; credentials never reach console or files.
const secrets = JSON.parse(execFileSync("uv", ["run", "--project", "apps/api", "python", "-c", `
import json, os
from dotenv import dotenv_values
names = ("SESSION_SECRET", "POSTGRES_PASSWORD", "DEEPSEEK_API_KEY", "OLLAMA_API_KEY", "DATABASE_URL")
values = [os.environ.get(name) for name in names]
for file in (".env", "apps/web/.env.local"):
    settings = dotenv_values(file)
    values.extend(settings.get(name) for name in names)
print(json.dumps([value for value in values if value]))
`], { cwd: root, stdio: ["ignore", "pipe", "pipe"] }).toString());
const files = checkSecrets(root, secrets);
console.log(`Contracts regenerated identically; local env files ignored; ${files} Git candidate/browser-output files checked for configured secrets.`);
