import { expect, test } from "@playwright/test";

test("named control groups remain exposed to assistive navigation", async ({ page }) => {
  await page.goto("/explore");
  for (const name of ["Collection mode", "Explore view", "Active filters"]) await expect(page.getByRole("group", { name, exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  await expect(page.getByRole("group", { name: "Map controls", exact: true })).toBeVisible();
  await page.goto("/stories/lantern-path");
  await expect(page.getByRole("group", { name: "Story mode", exact: true })).toBeVisible();
});

test("visit bookmarks require opt-in, revalidate records, reset and never write browser storage", async ({ page }) => {
  await page.goto("/"); await page.getByRole("link", { name: "Read exhibit & sources" }).click();
  await expect(page.getByRole("button", { name: "Bookmark for this visit" })).toBeDisabled();
  await page.getByRole("button", { name: "Close sources" }).click();
  await page.locator(".visit-reading summary").click();
  await page.getByLabel("Enable in-memory visit bookmarks").check();
  await page.locator(".published-card").click(); await page.getByRole("button", { name: "Bookmark for this visit" }).click();
  await expect(page.getByRole("button", { name: "Remove visit bookmark" })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "Close sources" }).click();
  await page.getByRole("link", { name: "FolkVerse China", exact: true }).click();
  await expect(page.getByRole("link", { name: "Continue exploring", exact: false })).toBeVisible();
  await page.locator(".visit-reading summary").click(); await expect(page.locator(".saved-records")).toContainText("Fuzhou shadow puppetry");
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });
  await page.route("**/api/v1/exhibits/liaoning-dalian-01?*", route => route.fulfill({ status: 404, contentType: "application/json", body: "{}" }));
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect(page.locator(".saved-records")).toContainText("unavailable or withdrawn"); await expect(page.locator(".saved-records a")).toHaveCount(0);
  await page.getByLabel("Enable in-memory visit bookmarks").uncheck(); await expect(page.locator(".saved-records")).toHaveCount(0);
  await page.getByRole("button", { name: "Reset continuation" }).click(); await expect(page.getByRole("link", { name: "Continue exploring", exact: false })).toHaveCount(0);
  await page.reload(); await page.locator(".visit-reading summary").click(); await expect(page.getByLabel("Enable in-memory visit bookmarks")).not.toBeChecked();
});

test("reading sizes, light surface and actual dialog scroll progress stay usable on a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await page.goto("/"); await page.getByRole("link", { name: "Read exhibit & sources" }).click();
  const drawer = page.getByRole("dialog"); await drawer.getByRole("button", { name: "Light reading surface" }).click();
  await drawer.getByLabel("Text size", { exact: true }).selectOption("larger");
  expect(await drawer.locator(".exhibit-reading > p").evaluate(node => getComputedStyle(node).fontSize)).toBe("24px");
  await drawer.evaluate(node => { node.scrollTop = node.scrollHeight; });
  await expect(drawer.getByRole("progressbar", { name: "Reading progress", exact: false })).toHaveAttribute("value", "100");
  expect(await drawer.evaluate(node => node.scrollWidth <= node.clientWidth)).toBe(true);
  await page.keyboard.press("Escape"); await expect(drawer).not.toBeVisible();
});

test("city focus preview does not select a city and topographic tiles load at higher zoom", async ({ page }) => {
  await page.goto("/explore"); await page.getByRole("button", { name: "Explore map", exact: true }).click();
  await page.locator(".atlas-city-grid").getByRole("button", { name: "Select Dalian", exact: true }).focus();
  const preview = page.getByRole("region", { name: "City preview", exact: true });
  await expect(preview).toContainText("Fuzhou shadow puppetry"); await expect(page.getByLabel("Region", { exact: true })).toHaveText("All Liaoning");
  await page.locator(".atlas-city-grid").getByRole("button", { name: "Select Fuxin", exact: true }).focus();
  await expect(preview).toContainText("No eligible published exhibit");
  await page.getByRole("button", { name: "Topographic detail", exact: true }).click();
  await expect(page.locator(".liaoning-atlas")).toHaveAttribute("data-terrain-ready", "true");
  await expect(page.locator("image[data-contour-tile]")).toHaveCount(9);
  await page.getByRole("button", { name: "Zoom in map", exact: true }).click(); await page.getByRole("button", { name: "Zoom in map", exact: true }).click();
  await expect(page.locator(".liaoning-atlas")).toHaveAttribute("data-terrain-ready", "true");
  await expect(page.locator(".topographic-legend")).toContainText("not survey or navigation data");
});

test("fictional ending art and chapter progress differ; soundscape never autoplays and stops on exit", async ({ page }) => {
  await page.addInitScript(() => { const Original = window.AudioContext; const contexts: AudioContext[] = []; Object.assign(window, { testAudioContexts: contexts }); window.AudioContext = class extends Original { constructor(options?: AudioContextOptions) { super(options); contexts.push(this); } }; });
  await page.goto("/stories/lantern-path"); expect(await page.evaluate(() => (window as unknown as { testAudioContexts: AudioContext[] }).testAudioContexts.length)).toBe(0);
  await page.getByRole("button", { name: "Follow the mountain light", exact: false }).click(); await expect(page.getByRole("img", { name: "Fictional mountain and lantern illustration" })).toBeVisible();
  await expect(page.getByRole("progressbar", { name: "Chapter progress", exact: false })).toHaveAttribute("value", "2");
  await page.getByRole("button", { name: "Begin again", exact: false }).click(); await page.getByRole("button", { name: "Cross the river bridge", exact: false }).click(); await expect(page.getByRole("img", { name: "Fictional river and lantern illustration" })).toBeVisible();
  await page.getByRole("button", { name: "Play soft soundscape", exact: true }).click(); await expect(page.getByRole("button", { name: "Stop soundscape", exact: true })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("link", { name: "FolkVerse China", exact: true }).click();
  await expect.poll(() => page.evaluate(() => (window as unknown as { testAudioContexts: AudioContext[] }).testAudioContexts.map(context => context.state))).toEqual(["closed"]);
});

test("constellation can be edited by keyboard with equivalent sliders and reset", async ({ page }) => {
  await page.goto("/dna"); const star = page.getByRole("button", { name: "Craft 0 / 100 · Change interest", exact: true }); await star.focus(); await page.keyboard.press("Enter");
  await expect(page.locator(".interest-chart dl")).toContainText("25 / 100"); await page.getByRole("button", { name: "Edit interests", exact: true }).click();
  await expect(page.getByRole("slider", { name: "Craft", exact: true })).toHaveValue("25"); await page.getByRole("button", { name: "Reset", exact: true }).click();
  await expect(page.getByRole("slider", { name: "Craft", exact: true })).toHaveValue("0"); await expect(page.locator(".recommendation-panel h2")).toHaveText("Begin with curiosity");
});

test("low-data preference skips decorative image requests on reload and survives navigation", async ({ page }) => {
  await page.goto("/"); await page.getByRole("button", { name: "Use less data", exact: true }).click(); const images: string[] = []; page.on("request", request => { if (request.url().includes("/_next/image") || /folkverse\/.+\.(?:png|webp)/.test(request.url())) images.push(request.url()); });
  await page.reload(); await expect(page.locator(".scene-art, .card-art img")).toHaveCount(0); await expect(page.locator(".featured-record")).toContainText("Fuzhou shadow puppetry");
  await page.getByRole("link", { name: "Explore", exact: true }).click(); await expect(page.getByRole("button", { name: "Restore images", exact: true })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "Explore map", exact: true }).click(); await expect(page.locator(".liaoning-atlas")).toHaveAttribute("data-terrain-ready", "true"); expect(images).toEqual([]);
  await page.getByRole("button", { name: "Restore images", exact: true }).click(); await page.goto("/"); await expect(page.locator(".scene-art")).toBeVisible();
});
