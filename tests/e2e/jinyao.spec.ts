import { expect, test } from "@playwright/test";

test("Jinyao cinematic hero responds to scrolling and replaces the previous scene", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/guide");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Jinyao");
  await expect(page.locator('.scene-art')).toHaveCount(0);
  const image = page.locator('.jinyao-cinematic-image');
  const before = await image.evaluate(node => getComputedStyle(node).transform);
  await page.evaluate(() => window.scrollTo(0, 550));
  await expect.poll(() => image.evaluate(node => getComputedStyle(node).transform)).not.toBe(before);
  await expect(page.locator('.jinyao-chapters article')).toHaveCount(3);
  await expect(page.locator('.jinyao-example-window li')).toHaveCount(4);
  expect(errors).toEqual([]);
});

test("Messenger preview keeps messages local, cancels replies and restores keyboard focus", async ({ page }) => {
  const outgoing: string[] = [];
  const errors: string[] = [];
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", error => errors.push(error.message));
  page.on("request", request => { if (request.method() === "POST") outgoing.push(request.url()); });
  await page.goto("/guide");
  const launcher = page.getByRole("button", { name: "Open Jinyao chat", exact: true });
  await launcher.click();
  const dialog = page.getByRole("dialog", { name: "Jinyao", exact: true });
  await expect(dialog).toBeVisible();
  const close = page.getByRole("button", { name: "Close Jinyao chat", exact: true });
  await expect(close).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(page.getByRole("textbox", { name: "Message Jinyao", exact: true })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(close).toBeFocused();
  await page.getByRole("button", { name: "Where do I begin?", exact: true }).click();
  await expect(dialog.getByRole("log")).toContainText("Start with one reviewed exhibit.");
  await page.getByRole("textbox", { name: "Message Jinyao", exact: true }).fill("An uncertain question");
  await page.getByRole("button", { name: "Send example message", exact: true }).click();
  await page.getByRole("button", { name: "Stop reply", exact: true }).click();
  await expect(dialog.getByRole("log")).toContainText("Reply stopped.");
  await page.waitForTimeout(750);
  await expect(dialog.getByRole("log")).not.toContainText("Thank you for asking.");
  await expect(page.getByRole("button", { name: "Clear chat", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Send example message", exact: true })).toHaveCSS("border-radius", "12px");
  await expect(page.locator('.jinyao-chat-turn')).toHaveCount(2);
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(launcher).toBeFocused();
  await launcher.click();
  await expect(dialog.getByRole("log")).toContainText("An uncertain question");
  await page.keyboard.press("Escape");
  expect(await page.evaluate(() => document.body.style.position)).toBe("");
  expect(outgoing).toEqual([]);
  expect(errors).toEqual([]);
});

test("mobile Chinese chat fits the viewport and reduced motion unpins the hero", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/guide");
  await expect(page.locator('.jinyao-cinematic-stage')).toHaveCSS("position", "relative");
  await page.getByRole("button", { name: "Open navigation menu", exact: true }).click();
  await page.getByRole("dialog", { name: "Explore FolkVerse", exact: true }).getByRole("button", { name: "Switch to Chinese", exact: true }).click();
  await page.getByRole("button", { name: "关闭导航菜单", exact: true }).click();
  await expect(page.getByRole("heading", { level: 1 })).toContainText("锦瑶");
  await page.getByRole("button", { name: "打开锦瑶聊天", exact: true }).click();
  await page.getByRole("button", { name: "从哪里开始？", exact: true }).click();
  await expect(page.getByRole("log")).toContainText("从一件审核展览开始吧");
  await page.setViewportSize({ width: 390, height: 420 });
  await page.getByRole("textbox", { name: "给锦瑶的消息", exact: true }).focus();
  await expect(page.getByRole("textbox", { name: "给锦瑶的消息", exact: true })).toBeInViewport();
  await expect(page.getByRole("button", { name: "发送示例消息", exact: true })).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test("low data loads no Jinyao images", async ({ page, context, baseURL }) => {
  await context.addCookies([{ name: "folkverse_data", value: "low", url: baseURL! }]);
  const imageRequests: string[] = [];
  page.on("request", request => { if (request.url().includes("jinyao/") || request.url().includes("jinyao%2F")) imageRequests.push(request.url()); });
  await page.goto("/guide");
  await expect(page.locator('.jinyao-experience img')).toHaveCount(0);
  await page.getByRole("button", { name: "Open Jinyao chat", exact: true }).click();
  await expect(page.locator('.jinyao-messenger img')).toHaveCount(0);
  expect(imageRequests).toEqual([]);
});
