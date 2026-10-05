import { expect, test } from "@playwright/test";
const evidenceDir = process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/ui-part-c";

test("Sources instructions, live capability copy and province query match actual scope", async ({ page }) => {
  await page.goto("/sources");
  await expect(page.locator(".collection-controls")).toContainText("Browse published source records");
  await expect(page.locator(".collection-controls")).not.toContainText("Select a city");
  const provinceRequest = page.waitForRequest(request => request.url().includes("/api/v1/exhibits?") && new URL(request.url()).searchParams.get("region_id") === "liaoning");
  await page.goto("http://127.0.0.1:3002/explore"); await provinceRequest;
  await expect(page.locator(".published-card")).toHaveCount(1);
  await expect(page.locator("footer")).toContainText("Published collection available");
  await expect(page.locator("footer")).toContainText("AI experiences not connected");
  await page.getByLabel("Region", { exact: true }).click();
  await expect(page.getByRole("option")).toHaveCount(15);
  await expect(page.getByRole("option", { name: "Liaoning province", exact: true })).toHaveCount(0);
  await page.keyboard.press("Escape");
});

test("atlas distinguishes loading, outage, published city and empty city", async ({ page }) => {
  let release!: () => void; const wait = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/api/v1/regions?**", async route => { await wait; await route.continue(); });
  await page.goto("/explore"); await page.getByRole("button", { name: "Explore map", exact: true }).click();
  await page.locator(".atlas-city-grid").getByRole("button", { name: "Select Dalian", exact: true }).click();
  await expect(page.locator(".atlas-location")).toContainText("Checking collection…");
  release(); await page.unrouteAll({ behavior: "wait" });
  await expect(page.locator(".atlas-location")).toContainText("Reviewed exhibits ready to explore.");
  await page.locator(".atlas-city-grid").getByRole("button", { name: "Select Shenyang", exact: true }).click();
  await expect(page.locator(".atlas-location")).toContainText("No published exhibits currently available.");
  await page.route("**/api/v1/regions?**", route => route.fulfill({ status: 503, json: { error: { code: "unavailable" } } }));
  await page.getByRole("button", { name: "Refresh collection" }).click();
  await expect(page.locator(".atlas-location")).toContainText("Collection service unavailable.");
  await expect(page.locator(".atlas-city.has-exhibits")).toHaveCount(0);
  await page.unroute("**/api/v1/regions?**"); await page.getByRole("button", { name: "Refresh collection" }).click();
  await expect(page.locator(".atlas-bottom")).toContainText("Reviewed exhibits available");
});

test("Guide keeps conversation through navigation without a clear control and resets on reload", async ({ page }) => {
  await page.goto("/guide"); await page.locator("summary").filter({ hasText: "Preview a conversation" }).click();
  const input = page.getByLabel("Ask the guide");
  for (const question of ["First question", "Second question"]) { await input.fill(question); await page.getByRole("button", { name: "Send", exact: false }).click(); await expect(page.getByRole("button", { name: "Send", exact: false })).toBeDisabled(); await expect(page.locator(".chat-history")).toHaveAttribute("aria-busy", "false"); }
  await expect(page.locator(".chat-question")).toHaveText(["First question", "Second question"]);
  await input.fill("Unsent draft");
  await page.locator("nav.nav-tabs").getByRole("link", { name: "Journey", exact: true }).click();
  await expect(page).toHaveURL(/\/journey$/);
  await page.locator("nav.nav-tabs").getByRole("link", { name: "Guide", exact: true }).click();
  await expect(page).toHaveURL(/\/guide$/);
  const preview = page.locator("details").filter({ has: page.locator("summary").filter({ hasText: "Preview a conversation" }) });
  if (!await preview.evaluate(node => (node as HTMLDetailsElement).open)) await preview.locator("summary").click();
  await expect(input).toHaveValue("Unsent draft"); await expect(page.locator(".chat-turn")).toHaveCount(2);
  await expect(page.getByRole("button", { name: "Voice — unavailable" })).toBeDisabled();
  await expect(page.getByText("Live microphone transcription is unavailable. Type your question instead.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Clear conversation" })).toHaveCount(0);
  await expect(page.locator(".chat-turn")).toHaveCount(2);
  await input.fill("Reload clears this draft"); await page.reload();
  await page.locator("summary").filter({ hasText: "Preview a conversation" }).click(); await expect(input).toHaveValue("");
});

test("Journey draft criteria never relabel committed route and plan survives navigation", async ({ page }) => {
  await page.goto("/journey"); await page.locator("summary").filter({ hasText: "Preview a learning route" }).click();
  await expect(page.getByLabel("Interests", { exact: true })).toHaveText("All interests");
  await expect(page.getByText(/Separate example tour:/)).toBeVisible();
  await page.getByRole("button", { name: "Move down screen" }).click();
  await page.getByLabel("Time", { exact: true }).click(); await page.getByRole("option", { name: "5 minutes", exact: true }).click();
  await expect(page.locator(".journey-draft")).toContainText("Draft criteria changed");
  await expect(page.locator(".journey-route .panel-heading")).toContainText("18 / 20");
  await page.locator("nav.nav-tabs").getByRole("link", { name: "Guide", exact: true }).click();
  await page.locator("nav.nav-tabs").getByRole("link", { name: "Journey", exact: true }).click();
  await page.locator("summary").filter({ hasText: "Preview a learning route" }).click();
  await expect(page.locator(".journey-stops li").first()).toContainText("Fujian");
  await expect(page.getByLabel("Time", { exact: true })).toHaveText("5 minutes");
  await page.getByRole("button", { name: /Apply — Shape my route/ }).click();
  await expect(page.locator(".journey-route .panel-heading")).toContainText("5 / 5");
  await expect(page.locator(".journey-draft")).toHaveCount(0);
  await page.getByRole("button", { name: "Reset example plan" }).click();
  await expect(page.locator(".journey-stops li").first()).toContainText("Shaanxi");
  await expect(page.getByLabel("Time", { exact: true })).toHaveText("20 minutes");
});

test("Chinese story offers explicit English audio, text-only mode and complete transcript", async ({ page }) => {
  await page.goto("/stories/lantern-path"); await page.getByRole("button", { name: "Switch to Chinese" }).click();
  await expect(page.getByLabel("旁白语言")).toHaveValue("en");
  await page.getByText("英语录音文字稿与中文翻译").click();
  await expect(page.locator(".narration-transcript [lang=en]")).toContainText("A lantern drifts beyond the screen.");
  await expect(page.locator(".narration-transcript [lang=zh-CN]")).toContainText("一盏灯笼飘出幕布");
  await page.getByLabel("旁白语言").selectOption("off"); await expect(page.getByRole("button", { name: "播放旁白" })).toBeDisabled();
  expect(await page.locator("audio").evaluate(node => (node as HTMLAudioElement).paused)).toBe(true);
});

test("reviewed exhibit context carries to all four next screens in demo/live and fails closed", async ({ page }) => {
  let identifier = "";
  for (const base of ["http://127.0.0.1:3000", "http://127.0.0.1:3002"]) {
    for (const [name, path] of [["Ask about this exhibit", "/guide"], ["Learn from this exhibit", "/journey"], ["Explore story options", "/stories/lantern-path"], ["Explore interests", "/dna"]]) {
      await page.goto(base); await page.getByRole("link", { name: "Read exhibit & sources" }).click();
      const link = page.getByRole("dialog").getByRole("link", { name, exact: false });
      const href = await link.getAttribute("href"); identifier = new URL(href!, base).searchParams.get("exhibit")!;
      await link.click(); await expect(page).toHaveURL(new RegExp(`${path}\\?exhibit=`));
      await expect(page.getByRole("region", { name: "Exhibit context" })).toContainText("Fuzhou shadow puppetry");
      if (path === "/guide" && base.endsWith("3000")) {
        await page.getByRole("button", { name: "Draft a question about this exhibit" }).click();
        await expect(page.getByLabel("Ask the guide")).toBeVisible();
        await expect(page.getByLabel("Ask the guide")).toBeFocused();
        await expect(page.getByLabel("Ask the guide")).toHaveValue(/Fuzhou shadow puppetry/);
      }
      await page.getByRole("link", { name: "Return to exhibit & sources" }).click();
      await expect(page.getByRole("dialog")).toContainText("Fuzhou shadow puppetry");
    }
  }
  await page.goto(`/guide?exhibit=${identifier}`);
  await expect(page.getByRole("region", { name: "Exhibit context" })).toContainText("Fuzhou shadow puppetry");
  await page.route(`**/api/v1/exhibits/${identifier}?**`, route => route.fulfill({ status: 404, json: { error: { code: "withdrawn" } } }));
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect(page.getByRole("region", { name: "Exhibit context" })).toContainText("withdrawn");
  await expect(page.getByRole("button", { name: "Draft a question about this exhibit" })).toHaveCount(0);
  await page.screenshot({ path: `${evidenceDir}/withdrawn-context.png`, fullPage: true });
});
