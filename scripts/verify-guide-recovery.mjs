// Real isolated upstream outage and recovery through the browser; one bounded provider call.
import { chromium } from "@playwright/test";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { writeFileSync } from "node:fs";
import path from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
const requireWeb = createRequire(new URL("../apps/web/package.json", import.meta.url));
const output = process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/phase03-completion";
const environment = { ...process.env, APP_MODE: "live", OLLAMA_DAILY_REQUEST_LIMIT: process.env.OLLAMA_DAILY_REQUEST_LIMIT ?? "16",
  MODEL_MAX_OUTPUT_TOKENS: "1200", ALLOWED_ORIGINS: '["http://127.0.0.1:3300"]' };
let api, web, browser;
const result = { checkedAt: new Date().toISOString(), provenance: "real_isolated_database_outage_then_actual_provider_recovery", checks: [], errors: [] };
const check = (name, passed) => result.checks.push({ name, passed });
const stop = async child => {
  if (!child || child.exitCode !== null) return;
  const exited = new Promise(resolve => child.once("exit", resolve));
  child.kill("SIGTERM");
  const deadline = setTimeout(() => child.kill("SIGKILL"), 5000);
  await exited; clearTimeout(deadline);
};
async function waitFor(url, status) {
  for (let i = 0; i < 60; i++) {
    try { if ((await fetch(url, { signal: AbortSignal.timeout(1000) })).status === status) return; } catch { /* Startup. */ }
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  throw new Error("Isolated verification service did not become ready.");
}
const startApi = (broken = false) => spawn(path.join(root, "apps/api/.venv/bin/python"),
  ["-m", "uvicorn", "folkverse.main:create_app", "--factory", "--host", "127.0.0.1", "--port", "3301"],
  { cwd: root, env: broken ? { ...environment, DATABASE_URL: "postgresql+psycopg://blocked:hidden@127.0.0.1:9/unavailable" } : environment, stdio: "ignore" });
try {
  api = startApi(true); await waitFor("http://127.0.0.1:3301/health", 503);
  web = spawn(process.execPath, [requireWeb.resolve("next/dist/bin/next"), "start", "--hostname", "127.0.0.1", "--port", "3300"],
    { cwd: path.join(root, "apps/web"), env: { ...environment, API_BASE_URL: "http://127.0.0.1:3301" }, stdio: "ignore" });
  await waitFor("http://127.0.0.1:3300/guide", 200);
  browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: "reduce" });
  await page.goto("http://127.0.0.1:3300/guide");
  await page.getByRole("button", { name: "Open Jinyao chat", exact: true }).click();
  await page.getByRole("textbox").fill("Where is Fuzhou shadow puppetry listed?");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await page.getByRole("button", { name: "Retry question" }).waitFor();
  check("actual outage has retry and no cited success", await page.getByRole("button", { name: "Inspect answer sources" }).count() === 0);
  await page.screenshot({ path: path.join(output, "real-outage-phone.png") });
  await stop(api); api = startApi(); await waitFor("http://127.0.0.1:3301/health", 200);
  await page.getByRole("button", { name: "Retry question" }).click();
  await page.getByRole("button", { name: "Inspect answer sources" }).waitFor({ timeout: 60000 });
  check("retry obtains actual validated answer", (await page.getByRole("log").innerText()).includes("Wafangdian, Liaoning"));
  await page.screenshot({ path: path.join(output, "real-recovery-phone.png") });
} catch (error) { result.errors.push(error.message); }
finally {
  if (browser) await browser.close();
  await stop(web); await stop(api);
  writeFileSync(path.join(output, "live-recovery.json"), JSON.stringify(result, null, 2) + "\n");
}
console.log(JSON.stringify(result, null, 2));
process.exitCode = result.errors.length || result.checks.some(c => !c.passed) ? 1 : 0;
