import { expect, test } from "@playwright/test";

test("phone menu supports links, Escape, focus restoration and desktop resizing", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await page.goto("/guide");
  const toggle = page.getByRole("button", { name: "Open navigation menu", exact: true });
  await expect(toggle).toBeVisible();
  await expect(page.locator('.museum-nav > .nav-tabs')).not.toBeVisible();
  await toggle.click();
  const menu = page.getByRole("dialog", { name: "Explore FolkVerse", exact: true });
  await expect(menu).toBeVisible();
  await expect(menu.locator('nav a svg')).toHaveCount(9);
  await expect(menu.locator('.mobile-menu-index, .mobile-menu-arrow')).toHaveCount(0);
  await expect(menu.getByRole("link", { name: "Guide", exact: false })).toHaveAttribute("aria-current", "page");
  await page.keyboard.press("Escape");
  await expect(menu).not.toBeVisible();
  await expect(toggle).toBeFocused();
  await toggle.click();
  await menu.getByRole("link", { name: "Sources", exact: false }).click();
  await expect(page).toHaveURL(/\/sources$/);
  await expect(menu).not.toBeVisible();
  await toggle.click();
  await page.setViewportSize({ width: 1440, height: 900 });
  await expect(menu).not.toBeVisible();
  await expect(toggle).not.toBeVisible();
  await expect(page.locator('.museum-nav > .nav-tabs')).toBeVisible();
  expect(await page.evaluate(() => document.body.style.position)).toBe("");
});

test("phone hero uses desktop artwork and places text in its empty left side", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  for (const width of [320, 390]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto("/guide");
    await expect(page.locator('.jinyao-cinematic-image img')).toHaveAttribute('src', /cinematic/);
    const portrait = page.locator('.jinyao-cinematic-image');
    const copy = page.locator('.jinyao-headline');
    const details = page.locator('.jinyao-hero-details');
    for (const scroll of [0, 200]) {
      await page.evaluate(value => window.scrollTo(0, value), scroll);
      await expect.poll(async () => {
        const image = await portrait.boundingBox(), text = await copy.boundingBox(), description = await details.boundingBox();
        return !!image && !!text && !!description && text.x + text.width <= image.x + image.width * .54 && description.y >= image.y + image.height;
      }).toBe(true);
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
});
