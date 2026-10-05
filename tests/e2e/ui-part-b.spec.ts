import { expect, test } from "@playwright/test";

test("source dialog includes integrity disclosure in keyboard order and distinguishes padding from backdrop", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Read exhibit & sources" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.locator("summary")).toBeVisible();
  await dialog.locator("summary").focus();
  await page.keyboard.press("Enter");
  await expect(dialog.locator("details")).toHaveAttribute("open", "");
  await page.keyboard.press("Tab");
  await expect(dialog.getByRole("button", { name: "Close sources" })).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(dialog.locator("summary")).toBeFocused();
  const rect = (await dialog.boundingBox())!;
  await page.mouse.click(rect.x + 3, rect.y + rect.height / 2);
  await expect(dialog).toBeVisible();
  const scroll = await page.evaluate(() => scrollY);
  await page.mouse.move(10, 300); await page.mouse.wheel(0, 800);
  await expect(page.locator("body")).toHaveCSS("position", "fixed");
  expect(await page.evaluate(() => scrollY)).toBe(scroll);
  await page.mouse.click(5, 300);
  await expect(dialog).not.toBeVisible();
  await expect(page.locator("body")).not.toHaveCSS("position", "fixed");
});

test("region dropdown and directory fit the same city camera", async ({ page }) => {
  await page.goto("/explore"); await page.getByRole("button", { name: "Explore map", exact: true }).click();
  const world = page.locator(".atlas-world");
  for (const city of ["Dalian", "Shenyang", "Dandong"]) {
    await page.locator(".atlas-city-grid").getByRole("button", { name: `Select ${city}`, exact: true }).click();
    const expected = await world.getAttribute("viewBox");
    await page.getByRole("button", { name: "Back to all Liaoning" }).click();
    await page.getByLabel("Region", { exact: true }).click();
    await page.getByRole("option", { name: city, exact: true }).click();
    await expect(world).toHaveAttribute("viewBox", expected!);
  }
});

test("graphics preference survives navigation and reload", async ({ page }) => {
  await page.goto("/guide"); await page.getByRole("button", { name: "Simplify graphics" }).click();
  await page.locator("nav").getByRole("link", { name: "Journey", exact: true }).click();
  await expect(page.locator(".museum-scene")).toHaveClass(/reduced-graphics/);
  await page.reload(); await expect(page.locator(".museum-scene")).toHaveClass(/reduced-graphics/);
  await page.getByRole("button", { name: "Full atmosphere" }).click(); await page.reload();
  await expect(page.locator(".museum-scene")).not.toHaveClass(/reduced-graphics/);
});

test("phone map labels and controls remain readable and expanded map is a native modal", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/explore"); await page.getByRole("button", { name: "Explore map", exact: true }).click();
  await expect(page.locator(".atlas-city-grid button")).toHaveCount(14);
  for (const selector of [".atlas-directory-heading input", ".atlas-camera-controls button", ".atlas-location button", ".atlas-city-grid button"]) {
    for (const control of await page.locator(selector).all()) {
      const box = (await control.boundingBox())!; expect(box.height).toBeGreaterThanOrEqual(44);
    }
  }
  const text = page.locator('.atlas-city.is-major .atlas-city-name').first();
  const pixels = await text.evaluate(node => { const m = (node as SVGGraphicsElement).getScreenCTM()!; return parseFloat(getComputedStyle(node).fontSize) * Math.hypot(m.a, m.b); });
  expect(pixels).toBeGreaterThanOrEqual(13);
  await page.getByRole("button", { name: "Expand map", exact: true }).click();
  const modal = page.getByRole("dialog");
  await expect(modal).toHaveAttribute("aria-modal", "true");
  expect(await modal.evaluate(node => node.matches(":modal"))).toBe(true);
  const mapBox = (await modal.locator(".atlas-world").boundingBox())!;
  const miniBox = (await modal.locator(".atlas-minimap").boundingBox())!;
  expect(miniBox.y + miniBox.height).toBeLessThanOrEqual(mapBox.y + mapBox.height);
  await modal.locator(".atlas-city-grid button").last().scrollIntoViewIfNeeded();
  await expect(modal.locator(".atlas-city-grid button").last()).toBeInViewport();
  await page.getByRole("button", { name: "Exit expanded map" }).focus();
  await page.keyboard.press("Escape");
  await expect(modal).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Expand map", exact: true })).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test("each screen has a distinct localized title including server reloads", async ({ page }) => {
  for (const zh of [false, true]) {
    await page.goto("/");
    if (zh) await page.getByRole("button", { name: "Switch to Chinese" }).click();
    const titles = new Set<string>();
    for (const route of ["/", "/explore", "/stories/lantern-path", "/journey", "/lens", "/guide", "/dna", "/sources", "/status"]) {
      await page.goto(route); await expect(page).toHaveTitle(/.+ \| FolkVerse China/);
      const title = await page.title(); expect(titles.has(title)).toBe(false); titles.add(title);
      if (zh) expect(title).toMatch(/[\u3400-\u9fff]/);
    }
  }
});
