// Part 4 browser fixtures deliberately bypass unavailable PostgreSQL/DeepSeek.
import { defineConfig } from "@playwright/test";
export default defineConfig({
  outputDir: "test-results/guide",
  testDir: "./tests/e2e", testMatch: ["guide-live.spec.ts", "guide-hybrid.spec.ts", "jinyao.spec.ts", "guide-proxy.spec.ts"],
  workers: 1, retries: 0, timeout: 30000,
  reporter: [["list"], ["json", { outputFile: `${process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/phase03-part4"}/browser-results.json` }]],
  use: { baseURL: "http://127.0.0.1:3100", browserName: "chromium", viewport: { width: 1600, height: 900 }, reducedMotion: "reduce", trace: "retain-on-failure" },
  webServer: [
    { command: "node tests/support/guide-upstream.mjs", url: "http://127.0.0.1:3210", reuseExistingServer: false },
    { command: "pnpm --filter @folkverse/web exec next start --hostname 127.0.0.1 --port 3100", url: "http://127.0.0.1:3100", env: { APP_MODE: "demo", API_BASE_URL: "http://127.0.0.1:3210" }, reuseExistingServer: false },
    { command: "pnpm --filter @folkverse/web exec next start --hostname 127.0.0.1 --port 3102", url: "http://127.0.0.1:3102", env: { APP_MODE: "live", API_BASE_URL: "http://127.0.0.1:3210", PUBLIC_APP_ORIGIN: "https://preview.fixture.test" }, reuseExistingServer: false },
  ],
});
