import { execFileSync } from "node:child_process";
import { existsSync, lstatSync, readFileSync, readlinkSync, readdirSync } from "node:fs";
import path from "node:path";

export function checkSecrets(root, values, browserFolder = "apps/web/.next/static") {
  const files = new Set(execFileSync("git", ["ls-files", "-z", "--cached", "--others", "--exclude-standard"], { cwd: root })
    .toString().split("\0").filter(Boolean));
  const tracked = execFileSync("git", ["ls-files", "-z", "--cached"], { cwd: root }).toString().split("\0").filter(Boolean);
  for (const file of tracked) {
    const name = path.basename(file);
    if ((name === ".env" || name.startsWith(".env.")) && name !== ".env.example") {
      throw new Error(`Private environment file is tracked: ${file}`);
    }
  }
  function addBrowserFiles(folder) {
    if (!existsSync(folder)) return;
    for (const entry of readdirSync(folder)) {
      const target = path.join(folder, entry);
      const stat = lstatSync(target);
      if (stat.isDirectory()) addBrowserFiles(target);
      else if (stat.isFile()) files.add(path.relative(root, target));
    }
  }
  addBrowserFiles(path.join(root, browserFolder));
  const secrets = [...new Set(values.filter(value => typeof value === "string" && value.length > 12))].map(value => Buffer.from(value));
  let checked = 0;
  for (const file of files) {
    const target = path.join(root, file);
    if (!existsSync(target)) continue; // Deleted tracked files have no pushable contents.
    const stat = lstatSync(target);
    if (!stat.isFile() && !stat.isSymbolicLink()) continue;
    const bytes = stat.isSymbolicLink() ? Buffer.from(readlinkSync(target)) : readFileSync(target);
    checked++;
    if (secrets.some(secret => bytes.includes(secret))) {
      throw new Error(`Local configured secret found in ${file}`);
    }
  }
  return checked;
}
