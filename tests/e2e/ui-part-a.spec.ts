import { expect, test } from "@playwright/test";

test("Home features published EN/ZH text and opens that exhibit with its sources in both modes", async ({ page }) => {
  for (const base of ["http://127.0.0.1:3000", "http://127.0.0.1:3002"]) {
    await page.goto(base);
    await expect(page.locator(".featured-record h3")).toHaveText("Fuzhou shadow puppetry");
    await page.getByRole("link", { name: "Read exhibit & sources" }).click();
    await expect(page).toHaveURL(/\/explore\?exhibit=/);
    await expect(page.getByRole("dialog").getByRole("heading", { name: "Fuzhou shadow puppetry", exact: true })).toBeVisible();
    await expect(page.getByRole("dialog").getByRole("link", { name: /Visit institutional source/ })).toBeVisible();
    await page.keyboard.press("Escape");
    await page.goto(base);
    await page.getByRole("button", { name: "Switch to Chinese" }).click();
    await expect(page.locator(".featured-record h3")).toHaveText("复州皮影戏");
    await expect(page.locator(".featured-record")).not.toContainText("Fuzhou shadow puppetry");
    await page.getByRole("link", { name: "阅读展览与来源" }).click();
    await expect(page.getByRole("dialog").getByRole("heading", { name: "复州皮影戏", exact: true })).toBeVisible();
    await page.keyboard.press("Escape");
    await page.getByRole("button", { name: "Switch to English" }).click();
  }
});

test("featured publication fails closed for errors, empty results and withdrawn records", async ({ page }) => {
  await page.route("**/api/v1/exhibits?**", route => route.fulfill({ status: 503, json: { error: { code: "unavailable" } } }));
  await page.goto("/");
  await expect(page.locator(".featured-exhibit [role=alert]")).toBeVisible();
  await expect(page.locator(".featured-record")).toHaveCount(0);
  await page.unroute("**/api/v1/exhibits?**");
  await page.locator(".featured-exhibit").getByRole("button", { name: "Try again" }).click();
  await expect(page.locator(".featured-record h3")).toHaveText("Fuzhou shadow puppetry");
  await page.route("**/api/v1/exhibits?**", route => route.fulfill({ json: { items: [], total: 0, next_cursor: null } }));
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect(page.locator(".featured-exhibit")).toContainText("No published exhibit is available to feature yet.");
  await expect(page.locator(".featured-record")).toHaveCount(0);
  await page.goto("/explore?exhibit=withdrawn-example");
  await expect(page.getByRole("dialog")).toContainText("This record was withdrawn or cannot currently be reached.");
});

test("status keeps diagnostics optional and recovers from an outage in both languages", async ({ page }) => {
  for (const zh of [false, true]) {
    await page.route("**/api/v1/health", route => route.fulfill({ status: 503, json: { error: { code: "unavailable" } } }));
    await page.goto("/status");
    if (zh) await page.getByRole("button", { name: "Switch to Chinese" }).click();
    const panel = page.locator('.status-panel').first();
    await expect(panel.getByRole("status")).toHaveText(zh ? "暂时无法连接博物馆，请重试。" : "We couldn’t connect to the museum right now. Please try again.");
    await expect(panel.locator(".service-list")).not.toBeVisible();
    await expect(panel.getByRole("status")).not.toContainText(/API|数据库|Database/);
    await expect(panel.locator("time")).toBeVisible();
    await panel.locator("summary").focus(); await page.keyboard.press("Enter");
    await expect(panel.locator(".service-list")).toBeVisible();
    await expect(panel.locator("dd").first()).toHaveText(zh ? "不可用" : "Unavailable");
    await page.unroute("**/api/v1/health");
    await panel.getByRole("button", { name: zh ? "重新检查" : "Check again" }).click();
    await expect(panel.getByRole("status")).toHaveText(zh ? "可以开始探索" : "Ready to explore");
    await expect(panel.locator("dd").first()).toHaveText(zh ? "可用" : "Available");
  }
});

test("decorative card purposes stay distinct and crops retain their aspect ratio", async ({ page }) => {
  for (const viewport of [{ width: 1600, height: 900 }, { width: 768, height: 1024 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport); await page.goto("/");
    await expect(page.locator(".featured-record h3")).toBeVisible();
    const map = await page.locator(".card-explore img").getAttribute("src");
    const story = await page.locator(".card-stories img").getAttribute("src");
    expect(map).not.toEqual(story);
    expect(map).toContain("02_interactive_map");
    for (const card of await page.locator(".card-art").all()) {
      const box = (await card.boundingBox())!;
      expect(Math.abs(box.width / box.height - 16 / 9)).toBeLessThan(.02);
    }
    await expect(page.locator(".art-caption")).toHaveCount(4);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
});
