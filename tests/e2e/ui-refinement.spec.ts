import { expect, test } from "@playwright/test";

test("Explore defaults to map and collection view preserves map filters", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Explore Liaoning", exact: true }).click();
  await expect(page.getByRole("button", { name: "Explore map", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".liaoning-atlas")).toBeVisible();
  await expect(page.getByRole("dialog", { name: "Expanded interactive map of Liaoning" })).toHaveCount(0);
  await page.getByRole("button", { name: "Browse collection", exact: true }).click();
  await expect(page.getByRole("button", { name: "Browse collection", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".liaoning-atlas")).not.toBeVisible();
  await expect(page.getByRole("button", { name: /Fuzhou shadow puppetry/ })).toBeVisible();
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  await page.getByRole("button", { name: "Select Shenyang", exact: true }).click();
  await page.getByRole("button", { name: "Browse collection", exact: true }).click();
  await expect(page.getByRole("combobox", { name: "Region", exact: true })).toHaveText("Shenyang");
  await expect(page.getByText("No published exhibits match these filters.")).toBeVisible();
  await page.reload();
  await expect(page.getByRole("button", { name: "Explore map", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".liaoning-atlas")).toBeVisible();
});

test("prototype controls are opt-in and keyboard can open every preview", async ({ page }) => {
  for (const [route, control] of [["/journey", ".journey-controls"], ["/lens", ".lens-panel"]]) {
    await page.goto(route);
    await expect(page.locator(control)).not.toBeVisible();
    await expect(page.getByRole("link", { name: "Explore the collection" })).toBeVisible();
    await page.locator(".optional-preview summary").focus();
    await page.keyboard.press("Enter");
    await expect(page.locator(control)).toBeVisible();
    await expect(page.getByText("This preview uses scripted examples. It does not connect to live AI services.")).toBeVisible();
  }
  await page.goto("/guide");
  await page.getByRole("button", { name: "Open Jinyao chat", exact: true }).click();
  await expect(page.getByRole("dialog", { name: "Jinyao", exact: true })).toBeVisible();
  await expect(page.getByRole("textbox", { name: "Message Jinyao" })).toBeVisible();
  await expect(page.getByText("Scripted preview · no live AI · messages are not sent")).toBeVisible();
});

test("interests begin empty and contain only voluntary choices", async ({ page }) => {
  await page.goto("/dna");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Your cultural interests");
  await expect(page.locator(".interest-chart dd")).toHaveText(["0 / 100", "0 / 100", "0 / 100", "0 / 100"]);
  await expect(page.getByRole("button", { name: /tracking/ })).toHaveCount(0);
  await page.getByRole("button", { name: "Edit interests" }).click();
  await page.getByRole("slider", { name: "Music", exact: true }).fill("75");
  await expect(page.locator(".recommendation-panel h2")).toHaveText("Music");
  await expect(page.getByText("Example interests · not your profile")).toHaveCount(0);
  await page.getByRole("button", { name: "Try example interests" }).click();
  await expect(page.getByText("Example interests · not your profile")).toBeVisible();
  await page.getByRole("slider", { name: "Music", exact: true }).fill("80");
  await expect(page.getByText("Example interests · not your profile")).toHaveCount(0);
});

test("phone cinematic artwork stays sharp at DPR 2 and the chat avatar stays compact", async ({ browser }) => {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, reducedMotion: "reduce" });
  const page = await context.newPage();
  try {
    for (const route of ["/", "/journey", "/stories/lantern-path", "/lens", "/guide", "/dna", "/sources", "/status"]) {
      await page.goto(route);
      if (route === "/guide") {
        const character = page.locator(".jinyao-cinematic-image img");
        await expect(character).toBeVisible();
        await expect.poll(() => character.evaluate(node =>
          (node as HTMLImageElement).complete && (node as HTMLImageElement).naturalWidth > 0
        )).toBe(true);
        await page.getByRole("button", { name: "Open Jinyao chat", exact: true }).click();
        await expect(page.locator(".jinyao-chat-header .jinyao-avatar")).toBeVisible();
        await page.screenshot({ path: `${process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/ui-refinement"}/guide-phone-dpr2.png`, fullPage: true });
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
        continue;
      }
      const scene = page.locator(".scene-picture img");
      await expect.poll(() => scene.evaluate(node => (node as HTMLImageElement).complete && (node as HTMLImageElement).naturalWidth > 0)).toBe(true);
      const geometry = await scene.evaluate(node => {
        const image = node as HTMLImageElement, box = image.getBoundingClientRect();
        const candidate = new URL(image.currentSrc).searchParams.get("w");
        return { width: box.width, height: box.height, candidateWidth: Number(candidate), fit: getComputedStyle(image).objectFit };
      });
      expect(geometry.height).toBeGreaterThan(0);
      expect(geometry.height).toBeLessThanOrEqual(844);
      expect(geometry.candidateWidth).toBeGreaterThanOrEqual(geometry.width * 2);
      expect(geometry.fit).toBe("cover");
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    }
  } finally { await context.close(); }
});
