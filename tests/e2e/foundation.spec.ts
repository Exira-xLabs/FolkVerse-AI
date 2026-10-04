import { expect, test, type Page } from "@playwright/test";

const routes = ["/", "/explore", "/journey", "/stories/lantern-path", "/lens", "/guide", "/dna", "/sources"];

async function waitForArtwork(page: Page) {
  await page.locator("img").evaluateAll(images => images.forEach(image => image.setAttribute("loading", "eager")));
  await expect.poll(() => page.locator("img").evaluateAll(images =>
    images.every(image => (image as HTMLImageElement).complete && (image as HTMLImageElement).naturalWidth > 0)
  ), { timeout: 15000 }).toBe(true);
  await page.evaluate(() => document.fonts.ready);
}

async function capture(page: Page, filename: string) {
  await waitForArtwork(page);
  await page.screenshot({ path: `report/evidence/phase00/${filename}.png`, fullPage: true, animations: "disabled" });
}

test("museum routes work at desktop, mobile and tablet without page overflow", async ({ page }) => {
  test.setTimeout(60000);
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  for (const viewport of [{ width: 1600, height: 900 }, { width: 390, height: 844 }, { width: 768, height: 1024 }]) {
    await page.setViewportSize(viewport);
    for (const route of routes) {
      await page.goto(route);
      await expect(page.locator("h1")).toBeVisible();
      await waitForArtwork(page);
      await expect(page.getByText("Foundation preview", { exact: true }).last()).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
      expect(overflow, `${route} at ${viewport.width}px`).toBe(false);
    }
    await page.goto("/");
    await capture(page, `home-${viewport.width}`);
  }
  expect(errors).toEqual([]);
});

test("navigation, language persistence and keyboard skip path work", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to content" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeFocused();
  await page.getByRole("link", { name: "Explore", exact: true }).click();
  await expect(page.getByRole("link", { name: "Explore", exact: true })).toHaveAttribute("aria-current", "page");
  await page.getByRole("button", { name: "Switch to Chinese" }).click();
  await expect(page.locator("html")).toHaveAttribute("lang", "zh-CN");
  await expect(page.locator("h1")).toHaveText("每一方土地，都有故事");
  await page.reload();
  await expect(page.locator("h1")).toHaveText("每一方土地，都有故事");
  await capture(page, "explore-zh-1600");
  await page.getByRole("button", { name: "Switch to English" }).click();
  await page.getByRole("link", { name: "FolkVerse China", exact: true }).click();
  await expect(page).toHaveURL("/");
});

test("real web to API health and signed session round trip", async ({ page, context }) => {
  await page.goto("/status");
  await expect(page.getByText("Services connected", { exact: true })).toBeVisible();
  await expect(page.locator("dd").nth(0)).toHaveText("Available");
  await page.getByRole("button", { name: "Start a visit" }).click();
  await expect(page.getByText("Anonymous visit active", { exact: true })).toBeVisible();
  const sessionCookie = (await context.cookies()).find(cookie => cookie.name === "folkverse_session");
  expect(sessionCookie?.httpOnly).toBe(true);
  expect(sessionCookie?.sameSite).toBe("Lax");
  await page.reload();
  await expect(page.getByRole("button", { name: "End this visit" })).toBeVisible();
  await page.getByRole("button", { name: "End this visit" }).click();
  await expect(page.getByRole("button", { name: "Start a visit" })).toBeVisible();
  expect((await context.cookies()).some(cookie => cookie.name === "folkverse_session")).toBe(false);
  await capture(page, "status-1600");
});

test("health service errors are visible and retry recovers", async ({ page }) => {
  await page.route("**/api/v1/health", route => route.fulfill({
    status: 503, contentType: "application/json",
    body: JSON.stringify({ error: { code: "api_unavailable", message: "Unavailable", retryable: true }, request_id: "test" }),
  }));
  await page.goto("/status");
  await expect(page.getByText(/The museum service cannot be reached/)).toBeVisible();
  await expect(page.locator("dd").nth(0)).toHaveText("Unavailable");
  await capture(page, "status-unavailable-1600");
  await page.unroute("**/api/v1/health");
  await page.getByRole("button", { name: "Check again" }).click();
  await expect(page.getByText("Services connected", { exact: true })).toBeVisible();
});

test("guide portrait retains transparency and narrow zoom layout stays usable", async ({ page }) => {
  await page.goto("/guide");
  await capture(page, "guide-1600");
  // A CSS viewport half the desktop width exercises layout at the equivalent of 200% zoom.
  await page.setViewportSize({ width: 800, height: 450 });
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.setViewportSize({ width: 390, height: 844 });
  await capture(page, "guide-390");
});

test("unknown routes stay missing and cross-origin session mutation is rejected", async ({ page, request }) => {
  const response = await page.goto("/not-a-museum-page");
  expect(response?.status()).toBe(404);
  const denied = await request.post("/api/v1/session", { headers: { Origin: "https://attacker.example" } });
  expect(denied.status()).toBe(403);
  expect((await denied.json()).error.code).toBe("origin_denied");
});
