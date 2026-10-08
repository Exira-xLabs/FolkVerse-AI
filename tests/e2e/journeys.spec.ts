// Phase 04 browser acceptance against the production web/BFF/API and reviewed snapshot.
// Run with playwright.phase04.config.ts for a disposable PostgreSQL API with no generation.
// Controlled multi-stop and failure fixtures are explicitly labelled below.
import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { writeFileSync } from "node:fs";
import { setLocale } from "../support/locale";

const panel = (page: Page) => page.getByRole("region", { name: "Saved learning journey", exact: true });
const evidenceDir = process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/phase04";

async function createSavedRoute(page: Page) {
  const create = page.waitForResponse(response => response.url().endsWith("/api/v1/journeys") && response.request().method() === "POST");
  await panel(page).getByRole("button", { name: "Create & save my journey", exact: false }).click();
  const response = await create;
  expect(response.status()).toBe(200);
  const saved = await response.json();
  expect(saved.total_minutes).toBeLessThanOrEqual(saved.duration_minutes);
  await expect(panel(page).locator(".saved-journey-stops > li")).toHaveCount(saved.stops.length);
  return saved;
}

test.afterEach(async ({ page, baseURL }) => {
  // APIRequestContext shares this test's cookies; delete only its freshly owned session.
  if (baseURL) await page.request.delete("/api/v1/session", { headers: { Origin: new URL(baseURL).origin } });
});

test("published Dalian map to saved journey to source and guide context, then reload", async ({ page }) => {
  await page.goto("/explore");
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  const atlas = page.getByRole("region", { name: "Interactive map of Liaoning" });
  await expect(atlas).toHaveAttribute("data-terrain-ready", "true");
  await atlas.getByRole("button", { name: "Explore Dalian", exact: true }).click();
  await page.getByRole("button", { name: /Fuzhou shadow puppetry/ }).click();
  await page.getByRole("dialog").getByRole("link", { name: /Learn from this exhibit/ }).click();
  await expect(page).toHaveURL(/\/journey\?exhibit=/);
  const identifier = new URL(page.url()).searchParams.get("exhibit")!;
  await expect(panel(page).getByRole("combobox", { name: "Learning region" })).toHaveText("Dalian");
  await panel(page).getByRole("combobox", { name: "Learning time" }).click();
  await page.getByRole("option", { name: "5 minutes", exact: true }).click();
  const saved = await createSavedRoute(page);
  expect(saved.stops[0].exhibit_id).toBe(identifier);
  await expect(panel(page).locator(".panel-heading")).toContainText("3 / 5");
  await expect(panel(page).getByRole("heading", { name: "Your saved discoveries" })).toBeFocused();
  await expect(panel(page).locator(".saved-journey-stops nav a").first()).toHaveAttribute("href", /^https:\/\//);
  await panel(page).getByRole("link", { name: /Read exhibit/ }).click();
  await expect(page.getByRole("dialog")).toContainText("Fuzhou shadow puppetry");
  await page.keyboard.press("Escape");
  await page.goto("/journey");
  await expect(panel(page).locator(".saved-journey-stops > li")).toHaveCount(1);
  await panel(page).getByRole("link", { name: /Ask Jinyao/ }).click();
  await expect(page).toHaveURL(new RegExp(`/guide\\?exhibit=${identifier}`));
  await expect(page.getByRole("region", { name: "Exhibit context" })).toContainText("Fuzhou shadow puppetry");
  await page.goto("/journey"); await page.reload();
  await expect(panel(page).locator(".panel-heading")).toContainText("3 / 5");
  await expect(panel(page).getByRole("combobox", { name: "Learning region" })).toHaveText("Dalian");
});

test("last stop removal is keyboard operable, recalculated, persisted and recoverable", async ({ page }) => {
  await page.goto("/journey");
  await createSavedRoute(page);
  const remove = panel(page).getByRole("button", { name: /Remove saved stop/ });
  await remove.focus();
  const patch = page.waitForResponse(response => response.url().includes("/api/v1/journeys/") && response.request().method() === "PATCH");
  await page.keyboard.press("Enter");
  expect((await patch).status()).toBe(200);
  await expect(panel(page).locator(".panel-heading")).toContainText("0 / 20");
  await expect(panel(page).locator(".saved-journey-stops > li")).toHaveCount(0);
  await expect(panel(page).getByRole("heading", { name: "Your saved discoveries" })).toBeFocused();
  await expect(panel(page)).toContainText("You may have removed them");
  await page.reload();
  await expect(panel(page).locator(".panel-heading")).toContainText("0 / 20");
  const regenerate = page.waitForResponse(response => response.url().endsWith("/api/v1/journeys") && response.request().method() === "POST");
  await panel(page).getByRole("button", { name: /Apply — Regenerate & save/ }).click();
  expect((await regenerate).status()).toBe(200);
  await expect(panel(page).locator(".saved-journey-stops > li")).toHaveCount(1);
});

test("draft criteria do not relabel saved totals, empty theme is honest, session loss clears old route", async ({ page, baseURL }) => {
  await page.goto("/journey");
  await createSavedRoute(page);
  await panel(page).getByRole("combobox", { name: "Learning time" }).click();
  await page.getByRole("option", { name: "5 minutes", exact: true }).click();
  await expect(panel(page).locator(".saved-journey-draft")).toBeVisible();
  await expect(panel(page).locator(".panel-heading")).toContainText("3 / 20");
  await panel(page).getByRole("button", { name: "Music", exact: true }).click();
  await panel(page).getByRole("button", { name: /Apply — Regenerate & save/ }).click();
  await expect(panel(page).locator(".panel-heading")).toContainText("0 / 5");
  await expect(panel(page).locator(".saved-journey-notice")).toBeVisible();
  await expect(panel(page).getByRole("link", { name: /Browse available exhibits/ })).toBeVisible();
  const removed = await page.request.delete("/api/v1/session", { headers: { Origin: new URL(baseURL!).origin } });
  expect(removed.status()).toBe(200);
  await page.evaluate(() => window.dispatchEvent(new Event("focus")));
  await expect(panel(page).getByRole("button", { name: /Create & save my journey/ })).toBeEnabled();
  await expect(panel(page).locator(".saved-journey-stops > li")).toHaveCount(0);
  await expect(panel(page)).toContainText("previous visitor session or route is no longer available");
});

test("saved route re-renders EN/ZH at desktop, phone and tablet without overflow", async ({ page }) => {
  test.setTimeout(60000);
  await page.goto("/journey");
  await createSavedRoute(page);
  for (const size of [{ width: 1600, height: 900 }, { width: 390, height: 844 }, { width: 768, height: 1024 }]) {
    await page.setViewportSize(size);
    for (const locale of ["en", "zh-CN"] as const) {
      await setLocale(page, locale);
      const currentPanel = page.getByRole("region", { name: locale === "en" ? "Saved learning journey" : "已保存学习路线", exact: true });
      await expect(currentPanel.locator(".saved-journey-stops > li")).toHaveCount(1);
      await expect(currentPanel.locator(".saved-journey-stops h3")).toHaveText(locale === "en" ? "Fuzhou shadow puppetry" : "复州皮影戏");
      const layout = await page.evaluate(() => ({
        viewport: window.innerWidth, width: document.documentElement.scrollWidth,
        overflowing: [...document.querySelectorAll("main *")].map(element => {
          const box = element.getBoundingClientRect();
          return { className: element.className, left: box.left, right: box.right };
        }).filter(box => box.right > window.innerWidth + 1 || box.left < -1).slice(0, 12),
      }));
      expect(layout.width <= layout.viewport, JSON.stringify({ locale, size, layout })).toBe(true);
      const accessibility = await new AxeBuilder({ page }).include(".saved-journey").analyze();
      writeFileSync(`${evidenceDir}/journey-accessibility-${locale}-${size.width}.json`, JSON.stringify({
        viewport: size, locale, layout, violations: accessibility.violations,
        passed_rules: accessibility.passes.map(rule => rule.id),
      }, null, 2) + "\n");
      expect(accessibility.violations).toEqual([]);
      await page.screenshot({ path: `${evidenceDir}/saved-journey-${locale}-${size.width}.png`, fullPage: true, animations: "disabled" });
    }
  }
});

test("controlled stale edit shows failure, restores keyboard focus and reloads the real route", async ({ page }) => {
  await page.goto("/journey");
  await createSavedRoute(page);
  let failed = false;
  await page.route("**/api/v1/journeys/*", async route => {
    if (route.request().method() === "PATCH" && !failed) {
      failed = true;
      await route.fulfill({ status: 409, json: { error: { code: "stale_state", message: "Controlled stale edit", retryable: false }, request_id: "fixture_stale_edit" } });
    } else await route.continue();
  });
  const remove = panel(page).getByRole("button", { name: /Remove saved stop/ });
  await remove.focus(); await page.keyboard.press("Enter");
  await expect(panel(page).getByRole("alert")).toContainText("Reload before editing again");
  const recovery = panel(page).getByRole("button", { name: "Reload saved journey", exact: true });
  await expect(recovery).toBeFocused();
  await expect(panel(page).locator(".saved-journey-stops > li")).toHaveCount(0);
  await page.keyboard.press("Enter");
  await expect(panel(page).getByRole("alert")).toHaveCount(0);
  await expect(panel(page).locator(".saved-journey-stops > li")).toHaveCount(1);
  await expect(panel(page).locator(".panel-heading")).toContainText("3 / 20");
});

test("saved journey remains usable with enlarged text and reduced motion", async ({ page }) => {
  await page.setViewportSize({ width: 640, height: 900 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/journey"); await createSavedRoute(page);
  await page.evaluate(() => { document.documentElement.style.zoom = "2"; });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  const remove = panel(page).getByRole("button", { name: /Remove saved stop/ });
  await remove.focus(); await page.keyboard.press("Enter");
  await expect(panel(page).locator(".panel-heading")).toContainText("0 / 20");
  await expect(panel(page).getByRole("heading", { name: "Your saved discoveries" })).toBeFocused();
  await page.screenshot({ path: `${evidenceDir}/saved-journey-en-200-percent.png`, fullPage: true, animations: "disabled" });
});

// A two-stop route is a controlled UI fixture, NOT newly published cultural content.
// This exercises focus/order UI where the real snapshot honestly offers only one stop.
test("controlled two-stop fixture reorders and removes with adjacent keyboard focus", async ({ page }) => {
  const fixture = {
    id: "jrn_controlled_fixture", locale: "en", interests: [], duration_minutes: 20,
    region_id: "liaoning", novelty_exhibit_ids: [], total_minutes: 7, version: 1,
    explanation_status: "deterministic", notice: "Controlled synthetic UI fixture — not published content",
    updated_at: "2026-10-07T00:00:00Z",
    stops: [
      { exhibit_id: "fixture-a", title: "Synthetic A", summary: "Controlled test data", estimated_minutes: 3, region_ids: ["liaoning"], themes: ["craft"], reason: "Controlled fixture", sources: [{ id: "fixture-source", title: "Synthetic source", institution: "TEST", canonical_url: "https://example.org/test" }] },
      { exhibit_id: "fixture-b", title: "Synthetic B", summary: "Controlled test data", estimated_minutes: 4, region_ids: ["liaoning"], themes: ["craft"], reason: "Controlled fixture", sources: [{ id: "fixture-source", title: "Synthetic source", institution: "TEST", canonical_url: "https://example.org/test" }] },
    ],
  };
  await page.route("**/api/v1/journeys**", async request => {
    if (request.request().method() === "PATCH") {
      const body = request.request().postDataJSON();
      fixture.stops = body.ordered_exhibit_ids.map((id: string) => fixture.stops.find(stop => stop.exhibit_id === id)!);
      fixture.total_minutes = fixture.stops.reduce((sum, stop) => sum + stop.estimated_minutes, 0);
      fixture.version += 1;
    }
    const response = request.request().url().includes("jrn_controlled_fixture") ? fixture : { items: [fixture] };
    await request.fulfill({ status: 200, json: response });
  });
  await page.goto("/journey");
  await expect(panel(page).locator(".saved-journey-stops > li")).toHaveCount(2);
  const move = panel(page).getByRole("button", { name: "Move saved stop down Synthetic A", exact: true });
  await move.focus(); await page.keyboard.press("Enter");
  await expect(panel(page).locator(".saved-journey-stops > li").first()).toContainText("Synthetic B");
  await expect(panel(page).getByRole("button", { name: "Move saved stop up Synthetic A", exact: true })).toBeFocused();
  await panel(page).getByRole("button", { name: "Remove saved stop Synthetic A", exact: true }).click();
  await expect(panel(page).locator(".panel-heading")).toContainText("4 / 20");
  await expect(panel(page).getByRole("button", { name: "Remove saved stop Synthetic B", exact: true })).toBeFocused();
  await page.reload(); await expect(panel(page).locator(".saved-journey-stops > li")).toHaveCount(1);
});
