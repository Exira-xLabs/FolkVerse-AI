import { setLocale } from "../support/locale";
const evidenceDir = process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/phase02";

import { expect, test, type Page } from "@playwright/test";

async function ready(page: Page) {
  await page.locator("img").evaluateAll(images => images.forEach(image => image.setAttribute("loading", "eager")));
  await expect.poll(() => page.locator("img").evaluateAll(images => images.every(image => (image as HTMLImageElement).complete && (image as HTMLImageElement).naturalWidth > 0))).toBe(true);
  await page.evaluate(() => document.fonts.ready);
  if (await page.locator(".featured-exhibit").count()) await expect(page.locator(".featured-record h3")).toBeVisible();
  await expect(page.locator(".collection-results [role=status]")).toHaveCount(0);
  if (await page.locator(".liaoning-atlas").count()) await expect(page.locator(".liaoning-atlas")).toHaveAttribute("data-terrain-ready", "true");
  const current = page.locator(".nav-tabs [aria-current=page]");
  if (await current.count()) await expect.poll(() => current.evaluate(node => {
    const tab = node.getBoundingClientRect(), row = node.parentElement!.getBoundingClientRect();
    return tab.left >= row.left - 1 && tab.right <= row.right + 1;
  })).toBe(true);
}

test("nine museum screens retain artwork and stay usable at three sizes in both languages", async ({ page }) => {
  test.setTimeout(120000);
  const routes = ["/", "/explore", "/journey", "/stories/lantern-path", "/lens", "/guide", "/dna", "/sources", "/status"];
  const errors: string[] = []; page.on("pageerror", e => errors.push(e.message));
  for (const size of [{ width: 1600, height: 900 }, { width: 390, height: 844 }, { width: 768, height: 1024 }]) {
    await page.setViewportSize(size);
    for (const [index, route] of routes.entries()) {
      await page.goto(route); await ready(page);
      await expect(page.locator("h1")).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${route} at ${size.width}`).toBe(true);
      await page.screenshot({ path: `${evidenceDir}/${String(index + 1).padStart(2, "0")}-${route === "/" ? "home" : route.split("/")[1]}-${size.width}.png`, fullPage: true, animations: "disabled" });
      await setLocale(page, "zh-CN");
      await expect(page.locator("html")).toHaveAttribute("lang", "zh-CN"); await ready(page);
      if (route === "/explore") await expect(page.locator(".published-card h3")).toHaveText("复州皮影戏");
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${route} Chinese at ${size.width}`).toBe(true);
      await page.screenshot({ path: `${evidenceDir}/zh-${index + 1}-${size.width}.png`, fullPage: true, animations: "disabled" });
      await setLocale(page, "en");
    }
  }
  expect(errors).toEqual([]);
});

test("explore filters, empty state and source drawer keyboard focus", async ({ page }) => {
  await page.goto("/explore");
  await page.getByRole("button", { name: "Preview examples" }).click();
  await page.getByRole("button", { name: "Music", exact: true }).click();
  await expect(page.getByRole("button", { name: /An evening of melodies/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /Behind the illuminated screen/ })).toHaveCount(0);
  const opener = page.getByRole("button", { name: /An evening of melodies/ });
  await opener.click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByRole("button", { name: "Close sources" })).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(page.getByRole("link", { name: "Explore the evidence chain" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Close sources" })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).not.toBeVisible(); await expect(opener).toBeFocused();
  await page.getByRole("searchbox").fill("unmatched"); await expect(page.getByText(/No demo exhibits match/)).toBeVisible();
});

test("journey reorder, remove and duration-constrained empty state", async ({ page }) => {
  await page.goto("/journey");
  await page.locator("summary").filter({ hasText: "Preview a learning route" }).click();
  await page.getByRole("button", { name: "Move down screen" }).click();
  await expect(page.locator(".journey-stops li").first()).toContainText("Fujian");
  await page.getByRole("button", { name: "Remove table" }).click();
  await expect(page.locator(".journey-route .panel-heading")).toContainText("13 / 20");
  await page.getByRole("combobox", { name: "Time", exact: true }).click();
  await page.getByRole("option", { name: "5 minutes", exact: true }).click();
  await page.getByRole("combobox", { name: "Interests", exact: true }).click();
  await page.getByRole("option", { name: "Craft", exact: true }).click();
  await page.getByRole("button", { name: /Shape my route/ }).click();
  await expect(page.getByText(/Not enough time/)).toBeVisible();
});

test("both story branches, restart and actual recorded audio", async ({ page }) => {
  await page.goto("/stories/lantern-path");
  await page.getByRole("button", { name: "Play narration" }).click();
  await expect(page.getByRole("button", { name: "Pause narration" })).toBeVisible();
  await expect.poll(() => page.locator("audio").evaluate(el => (el as HTMLAudioElement).currentTime)).toBeGreaterThan(0);
  await page.getByRole("button", { name: /Follow the mountain/ }).click(); await expect(page.getByRole("heading", { name: "The mountain light" })).toBeVisible();
  await expect(page.locator("audio")).toHaveCount(0);
  await page.getByRole("button", { name: /Begin again/ }).click();
  await page.getByRole("button", { name: /Cross the river/ }).click(); await expect(page.getByRole("heading", { name: "The river bridge" })).toBeVisible();
});

test("lens exposes unknown, poor image, denial, outage and loading without claiming recognition", async ({ page }) => {
  await page.goto("/lens");
  await page.locator("summary").filter({ hasText: "Preview Object Lens" }).click();
  for (const [value, heading] of [["Unknown object", "No eligible catalog match"], ["Insufficient image", "More detail is needed"], ["Permission denied", "Camera permission denied"], ["Service unavailable", "Recognition service unavailable"]]) {
    await page.getByRole("combobox", { name: "Choose a demo scenario" }).click();
    await page.getByRole("option", { name: value, exact: true }).click(); await expect(page.getByRole("heading", { name: heading })).toBeVisible();
  }
  await page.getByRole("button", { name: /Replay simulation/ }).click();
  await expect(page.getByText("Comparing demo…")).toBeVisible();
  await expect(page.getByRole("button", { name: /Replay simulation/ })).toBeEnabled();
  await expect(page.getByText("SIMULATED RESULT · NO RECOGNITION")).toBeVisible();
});

test("guide submits bounded text, clearly scripted response and voice unavailable", async ({ page }) => {
  await page.goto("/guide");
  await page.locator("summary").filter({ hasText: "Preview a conversation" }).click(); await expect(page.getByRole("button", { name: /Send/ })).toBeDisabled();
  const input = page.getByLabel("Ask the guide"); await expect(input).toHaveAttribute("maxlength", "2000");
  await input.fill("How does this tradition work?"); await page.getByRole("button", { name: /Send/ }).click();
  await expect(page.getByText("Loading the scripted response…")).toBeVisible();
  await expect(page.getByText(/I cannot answer your question from evidence yet/)).toBeVisible();
  await expect(page.getByRole("button", { name: /Voice/ })).toBeDisabled(); await expect(page.getByText(/Live microphone transcription is unavailable/)).toBeVisible();
});

test("interest edits redraw chart and reset clears suggestions", async ({ page }) => {
  await page.goto("/dna");
  await expect(page.locator(".interest-chart dd")).toHaveText(["0 / 100", "0 / 100", "0 / 100", "0 / 100"]);
  await page.getByRole("button", { name: "Try example interests" }).click();
  await expect(page.getByText("Example interests · not your profile")).toBeVisible();
  const polygon = page.locator("polygon"); const before = await polygon.getAttribute("points");
  await page.getByRole("button", { name: "Edit interests" }).click();
  await page.getByRole("slider", { name: "Craft", exact: true }).fill("12");
  expect(await polygon.getAttribute("points")).not.toBe(before);
  await expect(page.locator(".recommendation-panel h2")).toHaveText("Legends");
  await page.getByRole("button", { name: "Reset", exact: true }).click();
  await expect(page.locator(".recommendation-panel h2")).toHaveText("Begin with curiosity");
  await expect(page.locator(".interest-chart dd")).toHaveText(["0 / 100", "0 / 100", "0 / 100", "0 / 100"]);
});

test("live mode fails closed with no demo controls", async ({ page }) => {
  await page.goto("http://127.0.0.1:3002/journey");
  await expect(page.getByRole("heading", { name: "Your saved discoveries" })).toBeVisible();
  await expect(page.locator(".fixture-content")).toHaveCount(0);
  for (const route of ["lens", "dna", "stories/lantern-path"]) {
    await page.goto(`http://127.0.0.1:3002/${route}`);
    await expect(page.getByRole("heading", { name: "This experience is not available yet." })).toBeVisible();
    await expect(page.locator(".fixture-content")).toHaveCount(0);
  }
  await page.goto("http://127.0.0.1:3002/guide");
  await page.getByRole("button", { name: "Open Jinyao chat", exact: true }).click();
  await expect(page.getByRole("button", { name: "Send message", exact: true })).toBeVisible();
  await expect(page.getByText("Scripted preview · no live AI · messages are not sent")).toHaveCount(0);
  await page.getByRole("textbox", { name: "Message Jinyao" }).fill("Where is Fuzhou shadow puppetry listed?");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  // This config intentionally points a live web app at the demo API: honest failure.
  await expect(page.getByRole("button", { name: "Retry question" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Inspect answer sources" })).toHaveCount(0);
});

test("published collection works in live mode with no fixture toggle", async ({ page }) => {
  for (const route of ["explore", "sources"]) {
    await page.goto(`http://127.0.0.1:3002/${route}`);
    await expect(page.getByRole("button", { name: "Published collection" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Preview examples" })).toHaveCount(0);
    await expect(page.locator(".fixture-content")).toHaveCount(0);
  }
});

test("reduced graphics, keyboard path and 200 percent page zoom", async ({ page }) => {
  // CSS zoom plus a narrowed layout viewport stresses enlarged content and reflow.
  // This does not claim use of the browser toolbar's zoom setting.
  await page.goto("/dna");
  await page.getByRole("button", { name: "Simplify graphics" }).click();
  await expect(page.locator(".museum-scene")).toHaveClass(/reduced-graphics/);
  expect(await page.locator(".dna-panel").evaluate(el => getComputedStyle(el).backdropFilter)).toBe("none");
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setDeviceMetricsOverride", { width: 800, height: 450, deviceScaleFactor: 1, mobile: false, scale: 1 });
  for (const route of ["/explore", "/journey", "/guide", "/dna", "/sources"]) {
    await page.goto(route); await ready(page);
    await page.evaluate(() => { document.documentElement.style.zoom = "2"; });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `zoom ${route}`).toBe(true);
    await expect(page.locator("h1")).toBeVisible();
  }
});
