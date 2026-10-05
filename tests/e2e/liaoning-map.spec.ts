import { expect, test } from "@playwright/test";
const evidenceDir = process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/phase02-map";

test("real Liaoning silhouette, 14 city markers and geographical city selection", async ({ page, request }) => {
  await page.goto("/explore");
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  const atlas = page.getByRole("region", { name: "Interactive map of Liaoning" });
  await expect(atlas).toHaveAttribute("data-terrain-ready", "true");
  await expect(atlas.locator(".atlas-city")).toHaveCount(14);
  await expect(atlas.locator(".atlas-city-grid button")).toHaveCount(14);
  await expect(atlas.locator(".atlas-district")).toHaveCount(14);
  const geo = await request.get("/folkverse/maps/liaoning.geojson");
  expect(geo.ok()).toBe(true);
  const body = await geo.json(); expect(body.properties.iso_3166_2).toBe("CN-LN");
  expect(body.geometry.type).toBe("MultiPolygon");
  await atlas.getByRole("button", { name: "Explore Dalian", exact: true }).click();
  await expect(page.getByLabel("Region", { exact: true })).toHaveText("Dalian");
  await expect(atlas.locator(".atlas-location strong")).toHaveText("Dalian");
  await expect(page.getByRole("button", { name: /Fuzhou shadow puppetry/ })).toBeVisible();
  await atlas.getByRole("button", { name: "See city collection" }).click();
  await page.getByRole("button", { name: /Fuzhou shadow puppetry/ }).click();
  await expect(page.getByRole("dialog").getByRole("link", { name: /Visit institutional source/ })).toBeVisible();
  await page.keyboard.press("Escape");
  await atlas.getByRole("button", { name: "Select Shenyang", exact: true }).click();
  await expect(page.getByLabel("Region", { exact: true })).toHaveText("Shenyang");
  await expect(page.getByText("No published exhibits match these filters.")).toBeVisible();
  await expect(atlas.getByText("No published exhibits currently available.")).toBeVisible();
  await expect(page.getByRole("button", { name: /Lanterns of Shenyang/ })).toHaveCount(0);
  await atlas.getByRole("button", { name: "Back to all Liaoning" }).click();
  await expect(page.getByRole("button", { name: /Fuzhou shadow puppetry/ })).toBeVisible();
  await atlas.getByRole("button", { name: "Fit Liaoning province" }).click();
  await expect(page.locator(".collection-results [role=status]")).toHaveCount(0);
  await page.screenshot({ path: `${evidenceDir}/liaoning-atlas-desktop.png`, fullPage: true, animations: "disabled" });
});

test("map pan, wheel zoom, keyboard camera, minimap and expanded map", async ({ page }) => {
  await page.goto("/explore");
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  const atlas = page.getByRole("region", { name: "Interactive map of Liaoning" });
  const world = atlas.locator(".atlas-world");
  await expect(atlas).toHaveAttribute("data-terrain-ready", "true");
  const original = await world.getAttribute("viewBox");
  await atlas.getByRole("button", { name: "Zoom in map", exact: true }).click();
  expect(Number(await world.getAttribute("data-zoom"))).toBeGreaterThan(1);
  await world.scrollIntoViewIfNeeded();
  const bounds = await world.boundingBox(); expect(bounds).not.toBeNull();
  await page.mouse.move(bounds!.x + bounds!.width / 2, bounds!.y + bounds!.height / 2);
  await page.mouse.wheel(0, -220);
  await expect.poll(async () => Number(await world.getAttribute("data-zoom"))).toBeGreaterThan(1.3);
  const zoomed = await world.getAttribute("viewBox");
  await page.mouse.move(bounds!.x + 80, bounds!.y + 80); await page.mouse.down();
  await page.mouse.move(bounds!.x + 140, bounds!.y + 135, { steps: 8 }); await page.mouse.up();
  expect(await world.getAttribute("viewBox")).not.toEqual(zoomed);
  await world.focus(); await page.keyboard.press("Home");
  await expect(world).toHaveAttribute("viewBox", original!);
  await page.keyboard.press("ArrowRight"); expect(await world.getAttribute("viewBox")).not.toEqual(original);
  await atlas.getByRole("button", { name: "Recenter using minimap" }).focus(); await page.keyboard.press("Enter");
  await expect(world).toHaveAttribute("viewBox", original!);
  await atlas.getByRole("button", { name: "Expand map", exact: true }).click();
  await expect(atlas).toHaveClass(/atlas-expanded/);
  await expect(page.locator("body")).toHaveCSS("overflow", "hidden");
  await page.keyboard.press("Escape"); await expect(atlas).not.toHaveClass(/atlas-expanded/);
  await expect(page.locator("body")).not.toHaveCSS("overflow", "hidden");
});

test("selected city circle stays centered through time and zoom for all fourteen cities", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/explore");
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  const atlas = page.getByRole("region", { name: "Interactive map of Liaoning" });
  const cities = atlas.locator(".atlas-city-grid button");
  await expect(cities).toHaveCount(14);
  for (let i = 0; i < 14; i++) {
    await cities.nth(i).click();
    await expect(atlas.locator(".atlas-city[aria-pressed=true]")).toHaveCount(1);
    const selectedCityId = await atlas.locator(".atlas-city[aria-pressed=true]").getAttribute("data-city-id");
    await expect(atlas.locator(".atlas-district-selected")).toHaveCount(1);
    await expect(atlas.locator(".atlas-district-selected")).toHaveAttribute("data-city-id", selectedCityId!);
    const ring = atlas.locator(".atlas-selection-ring");
    await expect(ring).toHaveCount(1);
    const distances = await ring.evaluate(node => {
      const city = node.closest(".atlas-city") as SVGGraphicsElement;
      const anchor = new DOMPoint(0, 0).matrixTransform(city.getScreenCTM()!);
      return [0, 8750, 17500, 35000].map(time => {
        for (const animation of node.getAnimations()) { animation.pause(); animation.currentTime = time; }
        const bounds = node.getBoundingClientRect();
        return Math.hypot(bounds.x + bounds.width / 2 - anchor.x, bounds.y + bounds.height / 2 - anchor.y);
      });
    });
    for (const distance of distances) expect(distance).toBeLessThan(1);
    await atlas.getByRole("button", { name: "Zoom out map", exact: true }).click();
    const zoomedDistance = await ring.evaluate(node => {
      const anchor = new DOMPoint(0, 0).matrixTransform((node.closest(".atlas-city") as SVGGraphicsElement).getScreenCTM()!);
      const bounds = node.getBoundingClientRect();
      return Math.hypot(bounds.x + bounds.width / 2 - anchor.x, bounds.y + bounds.height / 2 - anchor.y);
    });
    expect(zoomedDistance).toBeLessThan(1);
  }
});

test("sourced city territory highlights from map clicks and clears when returning to the province", async ({ page, request }) => {
  await page.goto("/explore");
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  const atlas = page.getByRole("region", { name: "Interactive map of Liaoning" });
  await expect(atlas).toHaveAttribute("data-terrain-ready", "true");
  const response = await request.get("/folkverse/maps/liaoning-cities.geojson");
  expect(response.ok()).toBe(true);
  const data = await response.json();
  expect(data.features).toHaveLength(14);
  expect(data.features.every((f: { properties: { admin_level: number }; geometry: { type: string } }) => f.properties.admin_level === 5 && f.geometry.type === "MultiPolygon")).toBe(true);
  const territory = atlas.locator('.atlas-district[data-city-id="liaoning-shenyang"]');
  await territory.scrollIntoViewIfNeeded();
  const point = await territory.evaluate(node => {
    const b = node.getBoundingClientRect();
    for (let y = 1; y < 10; y++) for (let x = 1; x < 10; x++) {
      const px = b.x + b.width * x / 10, py = b.y + b.height * y / 10;
      if (document.elementFromPoint(px, py) === node) return { x: px, y: py };
    }
    return null;
  });
  expect(point).not.toBeNull();
  await page.mouse.click(point!.x, point!.y);
  const highlight = atlas.locator(".atlas-district-selected");
  await expect(highlight).toHaveAttribute("data-city-id", "liaoning-shenyang");
  await expect(highlight).toHaveAttribute("d", (await territory.getAttribute("d"))!);
  await expect(page.getByLabel("Region", { exact: true })).toHaveText("Shenyang");
  await expect(atlas.locator(".atlas-marker-shell")).toHaveCount(14);
  expect(await highlight.evaluate(node => Number.parseFloat(getComputedStyle(node).strokeWidth))).toBeGreaterThan(2);
  await atlas.getByRole("button", { name: "Select Dalian", exact: true }).click();
  await expect(highlight).toHaveAttribute("data-city-id", "liaoning-dalian");
  await atlas.getByRole("button", { name: "Back to all Liaoning" }).click();
  await expect(highlight).toHaveCount(0);
});

test("all cities remain selectable and searchable in Chinese at phone size", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/explore");
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  await page.getByRole("button", { name: "Switch to Chinese" }).click();
  const atlas = page.getByRole("region", { name: "辽宁交互地图" });
  await expect(atlas.locator(".atlas-city-grid button")).toHaveCount(14);
  await atlas.getByLabel("搜索辽宁城市").fill("丹东");
  await expect(atlas.locator(".atlas-city-grid button")).toHaveCount(1);
  await atlas.getByRole("button", { name: "选择丹东", exact: true }).click();
  await expect(atlas.locator(".atlas-location strong")).toHaveText("丹东");
  await expect(page.getByLabel("地区", { exact: true })).toHaveText("丹东");
  await atlas.getByLabel("搜索辽宁城市").fill("");
  await atlas.getByRole("button", { name: "选择大连", exact: true }).click();
  await expect(page.getByRole("button", { name: /复州皮影戏/ })).toBeVisible();
  await atlas.getByRole("button", { name: "显示全省", exact: true }).click();
  await expect(atlas).toHaveAttribute("data-terrain-ready", "true");
  await expect(page.locator(".collection-results [role=status]")).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: `${evidenceDir}/liaoning-atlas-phone-zh.png`, fullPage: true, animations: "disabled" });
});

test("touch pinch changes the map camera without scrolling the page", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await page.goto("/explore");
  await page.getByRole("button", { name: "Explore map", exact: true }).click();
  const world = page.locator(".atlas-world"); await world.scrollIntoViewIfNeeded();
  const bounds = await world.boundingBox(); expect(bounds).not.toBeNull();
  const x=bounds!.x+bounds!.width/2, y=bounds!.y+bounds!.height/2;
  const scrollBefore = await page.evaluate(() => window.scrollY);
  const cdp=await page.context().newCDPSession(page);
  await cdp.send("Input.dispatchTouchEvent", { type:"touchStart", touchPoints:[{x:x-30,y,id:0},{x:x+30,y,id:1}] });
  await cdp.send("Input.dispatchTouchEvent", { type:"touchMove", touchPoints:[{x:x-65,y,id:0},{x:x+65,y,id:1}] });
  await cdp.send("Input.dispatchTouchEvent", { type:"touchEnd", touchPoints:[] });
  await expect.poll(async () => Number(await world.getAttribute("data-zoom"))).toBeGreaterThan(1.5);
  expect(await page.evaluate(() => window.scrollY)).toBe(scrollBefore);
});
