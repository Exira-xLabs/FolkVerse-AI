import { expect, test } from "@playwright/test";
const evidenceDir = process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/ui-part-4";

test("phone quick navigation and filters retain place, clear and recover empty results", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await page.goto("/explore");
  const quick = page.getByRole("navigation", { name: "Quick navigation" });
  await expect(quick.getByRole("link", { name: "Sources", exact: true })).toBeVisible();
  await page.getByLabel("Search published exhibits").fill("nothing matches");
  await expect(page.getByText("No published exhibits match these filters.")).toBeVisible();
  await quick.getByRole("link", { name: "Sources", exact: true }).click();
  await expect(page.locator(".collection-results h2")).toHaveText("Meet the collection");
  await quick.getByRole("link", { name: "Explore Liaoning" }).click();
  await expect(page.getByLabel("Search published exhibits")).toHaveValue("nothing matches");
  await page.getByRole("button", { name: "Clear filters and browse Liaoning" }).click();
  await expect(page.locator(".published-card")).toHaveCount(1);
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  await page.locator(".atlas-city-grid").getByRole("button", { name: "Select Dalian", exact: true }).click();
  await quick.getByRole("link", { name: "Sources", exact: true }).click();
  await quick.getByRole("link", { name: "Explore Liaoning" }).click();
  await expect(page.getByLabel("Region", { exact: true })).toHaveText("Dalian");
  await expect(page.getByRole("button", { name: "Explore map", exact: true })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "Return to all Liaoning", exact: true }).click();
  await expect(page.getByLabel("Region", { exact: true })).toHaveText("All Liaoning");
});

test("reading, citations, shareable URL and evidence remain distinct and keyboard reachable", async ({ page }) => {
  await page.goto("/"); await page.getByRole("link", { name: "Read exhibit & sources" }).click();
  const drawer = page.getByRole("dialog");
  await expect(drawer.getByRole("region", { name: "Exhibit reading" })).toContainText("Dalian");
  await expect(drawer.getByRole("region", { name: "Exhibit reading" })).toContainText("Performance");
  const evidence = drawer.getByRole("region", { name: "Source evidence" });
  await expect(evidence.getByRole("link", { name: /Visit institutional source/ })).toBeVisible();
  const share = await drawer.getByRole("link", { name: "Shareable exhibit link" }).getAttribute("href");
  expect(share).toMatch(/\/explore\?exhibit=/);
  await drawer.getByRole("navigation", { name: "Exhibit citations" }).getByRole("link").first().click();
  await evidence.locator("summary").focus(); await page.keyboard.press("Enter");
  await expect(evidence.locator("code")).toBeVisible();
  await drawer.getByRole("button", { name: "Back to collection" }).click(); await expect(drawer).not.toBeVisible();
  await page.goto(share!); await expect(page.getByRole("dialog")).toContainText("Fuzhou shadow puppetry");
});

test("Guide approved prompts, stop/retry/error/insufficient states stay clearly scripted", async ({ page }) => {
  await page.goto("/guide"); await page.locator(".optional-preview summary").click();
  await expect(page.locator(".reviewed-discovery")).toContainText("Fuzhou shadow puppetry");
  await page.getByRole("button", { name: "Draft a related question" }).click();
  await expect(page.getByLabel("Ask the guide")).toHaveValue(/Fuzhou shadow puppetry/);
  await page.getByRole("button", { name: "Send", exact: false }).click();
  await expect(page.locator(".chat-progress")).toBeVisible();
  await page.getByRole("button", { name: "Stop response" }).click();
  await expect(page.getByText("Response stopped. No answer was produced.")).toBeVisible();
  await page.getByLabel("Guide preview state").click(); await page.getByRole("option", { name: "Service error preview", exact: true }).click();
  await page.getByRole("button", { name: "Retry response" }).click();
  await expect(page.locator(".chat-turn [role=alert]")).toContainText("Service error preview");
  await page.getByLabel("Guide preview state").click(); await page.getByRole("option", { name: "Insufficient evidence preview", exact: true }).click();
  await page.getByRole("button", { name: "Retry response" }).click();
  await expect(page.getByText(/Insufficient evidence preview\. I cannot support/)).toBeVisible();
  await expect(page.getByText("SCRIPTED DEMO · NO MODEL CALL")).toBeVisible();
});

test("composer adapts to narrowed viewport without hiding the active question", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await page.goto("/guide"); await page.locator(".optional-preview summary").click();
  const input = page.getByLabel("Ask the guide"); await input.fill("A draft stays visible");
  await page.setViewportSize({ width: 390, height: 420 }); await input.focus(); await input.scrollIntoViewIfNeeded();
  await expect(input).toBeInViewport(); await expect(page.getByRole("button", { name: "Send", exact: false })).toBeInViewport();
  await expect(page.locator(".quick-navigation")).toHaveCSS("visibility", "hidden");
  await page.getByRole("button", { name: "Send", exact: false }).click();
  await expect(page.locator(".chat-question")).toHaveText("A draft stays visible");
  await expect(page.locator(".chat-history")).toHaveAttribute("aria-busy", "false");
  await page.screenshot({ path: `${evidenceDir}/composer-reduced-viewport.png` });
});

test("Lens capture stays unavailable and cancelled preview cannot resume itself", async ({ page }) => {
  await page.goto("/lens");
  await expect(page.getByRole("button", { name: "Take photo — unavailable" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Choose photo — unavailable" })).toBeDisabled();
  await expect(page.getByRole("region", { name: "Capture guidance" })).toContainText("No photo is requested, stored or uploaded");
  await expect(page.locator('input[type=file]')).toHaveCount(0);
  await page.locator(".optional-preview summary").click();
  await page.getByRole("button", { name: "Replay simulation" }).click(); await page.getByRole("button", { name: "Cancel comparison" }).click();
  await expect(page.getByText("Comparison cancelled. No photo was sent.")).toBeVisible();
  await page.waitForTimeout(600); await expect(page.getByText("Comparison cancelled. No photo was sent.")).toBeVisible();
  await page.getByRole("button", { name: "Retry simulation" }).click(); await expect(page.getByText("Comparing demo…")).toBeVisible();
});

test("Story reading mode and endings offer actual continuations; interests link only approved records", async ({ page }) => {
  await page.goto("/stories/lantern-path");
  const audio = await page.locator("audio").elementHandle();
  await page.getByRole("button", { name: "Play narration" }).click();
  await expect.poll(() => audio!.evaluate(node => (node as HTMLAudioElement).paused)).toBe(false);
  await page.getByRole("button", { name: "Reading mode", exact: true }).click();
  expect(await audio!.evaluate(node => (node as HTMLAudioElement).paused)).toBe(true);
  await expect(page.locator("audio")).toHaveCount(0); await expect(page.locator(".narration-transcript")).toBeVisible();
  await page.getByRole("button", { name: /Follow the mountain/ }).click();
  await page.getByRole("link", { name: "Continue with reviewed exhibits" }).click(); await expect(page.locator(".published-card")).toHaveCount(1);
  await page.goto("/dna"); await expect(page.locator(".reviewed-discovery")).toContainText("Fuzhou shadow puppetry");
  await page.locator(".reviewed-discovery").getByRole("link", { name: /Fuzhou shadow puppetry/ }).click();
  await expect(page.getByRole("dialog")).toContainText("Fuzhou shadow puppetry");
});

test("friendly 404 and audio metadata delay have concrete recoveries", async ({ page }) => {
  const response = await page.goto("/missing-room"); expect(response?.status()).toBe(404);
  await expect(page.getByRole("heading", { name: "We couldn’t find this room" })).toBeVisible();
  await page.getByRole("link", { name: "Explore Liaoning" }).click(); await expect(page.locator(".published-card")).toHaveCount(1);
  let release!: () => void; const wait = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/folkverse/audio/lantern-demo.mp3", async route => { await wait; await route.continue(); });
  await page.goto("/stories/lantern-path", { waitUntil: "domcontentloaded" });
  await expect(page.getByText("Loading narration…")).toBeVisible(); await expect(page.getByRole("button", { name: "Play narration" })).toBeDisabled();
  release(); await page.unrouteAll({ behavior: "wait" }); await expect(page.getByRole("button", { name: "Play narration" })).toBeEnabled();
});

test("constrained network, offline collection and reconnect recovery", async ({ page, context }) => {
  test.setTimeout(60000);
  const cdp = await context.newCDPSession(page); await cdp.send("Network.enable");
  await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 500, downloadThroughput: 256000, uploadThroughput: 64000 });
  await page.goto("/explore"); await expect(page.locator(".published-card")).toHaveCount(1, { timeout: 20000 });
  await cdp.send("Network.emulateNetworkConditions", { offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0 });
  await page.getByRole("button", { name: "Refresh collection" }).click(); await expect(page.locator(".collection-results").getByRole("alert")).toContainText("temporarily unavailable");
  await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 500, downloadThroughput: 256000, uploadThroughput: 64000 });
  await page.getByRole("button", { name: "Try again", exact: true }).click(); await expect(page.locator(".published-card")).toHaveCount(1);
});
