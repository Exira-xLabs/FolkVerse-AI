import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { checkSecrets } from "./check-secrets.mjs";

const secret = "synthetic-configured-secret-for-test";
function fixture(action) {
  const root = mkdtempSync(path.join(tmpdir(), "folkverse-secret-check-"));
  try {
    execFileSync("git", ["init", "-q"], { cwd: root });
    action(root);
  } finally { rmSync(root, { recursive: true, force: true }); }
}
for (const filename of [".env.example", "push-log.txt", "README.md", "binary.bin"]) {
  test(`rejects configured secret in Git candidate ${filename}`, () => fixture(root => {
    writeFileSync(path.join(root, filename), `before\0${secret}\0after`);
    assert.throws(() => checkSecrets(root, [secret]), error => error.message.includes(filename) && !error.message.includes(secret));
  }));
}
test("rejects force-tracked private configuration even when ignored", () => fixture(root => {
  writeFileSync(path.join(root, ".gitignore"), ".env\n");
  writeFileSync(path.join(root, ".env"), "PRIVATE=short\n");
  execFileSync("git", ["add", "-f", ".env"], { cwd: root });
  assert.throws(() => checkSecrets(root, [secret]), /Private environment file is tracked/);
}));
test("scans ignored browser output while allowing ignored local env", () => fixture(root => {
  writeFileSync(path.join(root, ".gitignore"), ".env\n.next/\n");
  writeFileSync(path.join(root, ".env"), secret);
  mkdirSync(path.join(root, ".next/static"), { recursive: true });
  writeFileSync(path.join(root, ".next/static/client.js"), secret);
  assert.throws(() => checkSecrets(root, [secret], ".next/static"), /client.js/);
}));
test("allows safe examples and ignored local secrets", () => fixture(root => {
  writeFileSync(path.join(root, ".gitignore"), ".env\n");
  writeFileSync(path.join(root, ".env"), secret);
  writeFileSync(path.join(root, ".env.example"), "DEEPSEEK_API_KEY=\n");
  assert.equal(checkSecrets(root, [secret]), 2);
}));
