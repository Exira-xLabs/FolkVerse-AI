import type { Page } from "@playwright/test";

export async function setLocale(page: Page, locale: "en" | "zh-CN") {
  if (await page.locator("html").getAttribute("lang") === locale) return;
  const name = locale === "en" ? "Switch to English" : "Switch to Chinese";
  const button = page.getByRole("button", { name, exact: true });
  const phoneMenu = !await button.isVisible();
  if (phoneMenu) await page.getByRole("button", { name: /Open navigation menu|打开导航菜单/, exact: true }).click();
  await button.click();
  if (phoneMenu) await page.getByRole("button", { name: /Close navigation menu|关闭导航菜单/, exact: true }).click();
}
