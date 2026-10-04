import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30000,
  reporter: [["list"], ["json", { outputFile: "report/evidence/phase01/browser-results.json" }]],
  use: { baseURL: "http://127.0.0.1:3000", browserName: "chromium", viewport: { width: 1600, height: 900 }, reducedMotion: "reduce", trace: "retain-on-failure" },
  webServer: [
    { command: "uv run --project apps/api uvicorn folkverse.main:create_app --factory --host 127.0.0.1 --port 8000", url: "http://127.0.0.1:8000/health", reuseExistingServer: false, timeout: 30000 },
    { command: "pnpm --filter @folkverse/web start", url: "http://127.0.0.1:3000", reuseExistingServer: false, timeout: 30000 },
    { command: "pnpm --filter @folkverse/web exec next start --hostname 127.0.0.1 --port 3002", url: "http://127.0.0.1:3002", env: { APP_MODE: "live" }, reuseExistingServer: false, timeout: 30000 },
  ],
});
