import { defineConfig } from "@playwright/test";
import foundation from "./playwright.config";

// Same production UI and browser regression, with an independently owned database.
// Ports 3000/3002/8000 must be free; no serving database or provider quota is changed.
export default defineConfig({
  ...foundation,
  outputDir: "test-results/phase04",
  reporter: [["list"], ["json", {
    outputFile: `${process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/phase04-final"}/browser-results.json`,
  }]],
  webServer: [
    { command: "uv run --project apps/api python scripts/phase04-acceptance-api.py", url: "http://127.0.0.1:8000/health", reuseExistingServer: false, timeout: 60000 },
    { command: "pnpm --filter @folkverse/web start", url: "http://127.0.0.1:3000", env: { APP_MODE: "demo", API_BASE_URL: "http://127.0.0.1:8000", PUBLIC_APP_ORIGIN: "" }, reuseExistingServer: false },
    { command: "pnpm --filter @folkverse/web exec next start --hostname 127.0.0.1 --port 3002", url: "http://127.0.0.1:3002", env: { APP_MODE: "live", API_BASE_URL: "http://127.0.0.1:8000", PUBLIC_APP_ORIGIN: "" }, reuseExistingServer: false },
  ],
});
