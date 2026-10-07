import { expect, test, type Page, type TestInfo } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { checkedHybrid } from "../../apps/web/src/lib/guide-hybrid-checks";
import type { GuideAnswer, GuideEvidence } from "@folkverse/contracts";
const frame = (event: string, value: unknown) => `event: ${event}\ndata: ${JSON.stringify(value)}\n\n`;
async function capture(page: Page, info: TestInfo, name: string) {
  const filename = info.outputPath(name);
  await page.screenshot({ path: filename });
  await info.attach(name, { path: filename });
}
function fixture(zh = false, lookup = false) {
  const text = zh ? "复州皮影戏列入传统戏剧，地区为瓦房店。" : "Fuzhou shadow puppetry is listed as traditional theatre in Wafangdian.";
  const p = { passage_id: "lookup_fixture", source_id: "source_fixture", text, language: zh ? "zh-CN" : "en", locator: "Synthetic row", rights_basis: "Synthetic fixture", institution: "Fixture institution", source_title: "Fixture inventory", canonical_url: "https://www.ln.gov.cn/fixture", fetched_at: "2026-10-07T00:00:00Z", reviewed_at: lookup ? null : "2026-10-07T00:00:00Z", reviewer: lookup ? "" : "Fixture reviewer", review_id: lookup ? "not_editorially_reviewed" : "review_fixture", content_hash: "fixture_hash", exhibit_ids: lookup ? [] : ["exhibit_fixture"], region_ids: [], evidence_origin: lookup ? "official_lookup" : "reviewed_corpus", classification: "source_statement", statement_variants: lookup ? [text] : [], required_support_ids: [] } as GuideEvidence;
  const general = zh ? "可以把皮影想象成会动的剪影。灯光、影偶和故事一起帮助观众理解表演。" : "Think of shadow puppetry as moving silhouettes. Light, puppets and storytelling work together to make the performance understandable.";
  const sections = [{ section_id: "evidence", kind: "evidence", text, claim_ids: ["claim_1"], support_label: lookup ? "official_lookup" : "sources_checked" }, { section_id: "general", kind: "general", text: general, claim_ids: [], support_label: "general_unverified" }];
  const answer = { answer_id: "hybrid_fixture", locale: p.language, depth: "beginner", status: "answered", uncertainty: "partial", reason: "supported_explanation", answer_text: `${text}\n\n${general}`, coverage_limit: "This is synthetic browser test evidence.", claims: [{ claim_id: "claim_1", text, passage_ids: [p.passage_id], source_ids: [p.source_id], kind: "source_statement", support_method: lookup ? "official_metadata_projection_v1" : "complete_reviewed_passage", support_version: "deterministic-support-v1" }], answer_claim_ids: ["claim_1"], context_claim_ids: [], evidence_ids: [p.passage_id], related_exhibit_ids: p.exhibit_ids, mode: "live", retrieval_mode: "lexical_only", corpus_version: "fixture", contract_version: "hybrid_sections_v1", presentation_version: "hybrid_sections_v1", sections } as GuideAnswer;
  return { p, answer };
}
test("Chinese single sentence keeps complete-passage support", () => {
  const { p, answer } = fixture(true);
  expect(checkedHybrid(answer, [p])).toBe(true);
});
test("machine-assessed official summaries preserve their support identity", () => {
  const { p, answer } = fixture(false, true);
  p.review_id = "machine_source_assessed_v1";
  answer.claims[0].support_method = "machine_source_summary_v1";
  expect(checkedHybrid(answer, [p])).toBe(true);
  answer.claims[0].support_method = "official_metadata_projection_v1";
  expect(checkedHybrid(answer, [p])).toBe(false);
});
for (const attack of ["display", "claim", "classification", "support", "general_date", "label", "missing_support", "diagnostic"] as const) test(`hybrid browser rejects ${attack}`, () => {
  const { p, answer } = fixture();
  expect(checkedHybrid(answer, [p])).toBe(true);
  if (attack === "display") answer.answer_text += " Founded in 1644.";
  if (attack === "claim") answer.claims[0].text = "Invented origin.";
  if (attack === "classification") answer.claims[0].kind = "folklore";
  if (attack === "support") answer.claims[0].support_method = "model_self_assessment";
  if (attack === "general_date") answer.sections![1].text += " Founded in 1644.";
  if (attack === "label") answer.sections![1].support_label = "sources_checked";
  if (attack === "missing_support") p.required_support_ids = ["missing_source"];
  if (attack === "diagnostic") p.evidence_origin = "diagnostic_candidate";
  expect(checkedHybrid(answer, [p])).toBe(false);
});
for (const zh of [false, true]) test(`hybrid ${zh ? "Chinese phone" : "English desktop"} labels and source withdrawal`, async ({ page }, testInfo) => {
  const { p, answer } = fixture(zh, true);
  p.review_id = "machine_source_assessed_v1";
  answer.claims[0].support_method = "machine_source_summary_v1";
  let withdrawn = false;
  if (zh) await page.setViewportSize({ width: 390, height: 844 });
  await page.route("**/api/v1/session", route => route.fulfill({ json: { session_id: "fixture_visit" } }));
  await page.route("**/api/v1/exhibits?*", route => route.fulfill({ json: { items: [], total: 0, next_cursor: null } }));
  await page.route("**/api/v1/guide/evidence/lookup_fixture", route => route.fulfill({ json: { current: !withdrawn, passage: withdrawn ? null : p } }));
  await page.route("**/api/v1/guide", route => route.fulfill({ contentType: "text/event-stream", body: frame("answer", answer) + frame("sources", { answer_id: answer.answer_id, items: [p] }) + frame("done", { answer_id: answer.answer_id }) }));
  await page.goto("http://127.0.0.1:3102/guide");
  if (zh) {
    await page.getByRole("button", { name: "Open navigation menu", exact: true }).click();
    await page.getByRole("button", { name: "Switch to Chinese", exact: true }).click();
    await page.getByRole("button", { name: "关闭导航菜单", exact: true }).click();
  }
  await page.getByRole("button", { name: zh ? "打开锦瑶聊天" : "Open Jinyao chat", exact: true }).click();
  await page.getByRole("combobox", { name: zh ? "解释深度" : "Explanation depth" }).selectOption("beginner");
  await page.getByRole("textbox").fill(zh ? "解释皮影戏" : "Explain shadow puppetry");
  await page.getByRole("textbox").press("Enter");
  await expect(page.getByRole("log")).toContainText(p.text);
  await expect(page.getByRole("log")).toContainText(zh ? "一般说明" : "General explanation");
  await expect(page.getByRole("log")).toContainText(zh ? "官方来源" : "Official source");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  const chatAudit = await new AxeBuilder({ page }).include(".jinyao-messenger").withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  await testInfo.attach("chat-accessibility.json", { body: JSON.stringify(chatAudit, null, 2), contentType: "application/json" });
  expect(chatAudit.violations).toEqual([]);
  await capture(page, testInfo, `chat-${zh ? "zh-phone" : "en-desktop"}.png`);
  await page.getByRole("button", { name: zh ? "查看回答来源" : "Inspect answer sources" }).click();
  await expect(page.getByRole("dialog", { name: zh ? "回答所依据的资料" : "Evidence behind this answer" })).toContainText(p.text);
  await expect(page.getByRole("dialog", { name: zh ? "回答所依据的资料" : "Evidence behind this answer" })).toContainText(zh ? "未经人工审核" : "no human review");
  const sourceAudit = await new AxeBuilder({ page }).include(".source-drawer").withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
  await testInfo.attach("sources-accessibility.json", { body: JSON.stringify(sourceAudit, null, 2), contentType: "application/json" });
  expect(sourceAudit.violations).toEqual([]);
  await capture(page, testInfo, `sources-${zh ? "zh-phone" : "en-desktop"}.png`);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("button", { name: zh ? "查看回答来源" : "Inspect answer sources" })).toBeFocused();
  withdrawn = true;
  await page.getByRole("button", { name: zh ? "查看回答来源" : "Inspect answer sources" }).click();
  await expect(page.getByRole("log")).not.toContainText(p.text);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("textbox")).toBeFocused();
});

test("reading older messages does not jump when an answer arrives", async ({ page }) => {
  const { p, answer } = fixture();
  const explanation = "Puppets and light help tell a story. The screen lets the audience follow the movement. ".repeat(10);
  answer.sections![1].text = explanation;
  answer.answer_text = `${p.text}\n\n${explanation}`;
  let release: (() => void) | undefined;
  let requests = 0;
  await page.route("**/api/v1/session", r => r.fulfill({ json: { session_id: "fixture_visit" } }));
  await page.route("**/api/v1/exhibits?*", r => r.fulfill({ json: { items: [], total: 0, next_cursor: null } }));
  await page.route("**/api/v1/guide", async r => {
    if (++requests === 2) await new Promise<void>(resolve => { release = resolve; });
    await r.fulfill({ contentType: "text/event-stream", body: frame("answer", answer) + frame("sources", { answer_id: answer.answer_id, items: [p] }) + frame("done", { answer_id: answer.answer_id }) });
  });
  await page.goto("http://127.0.0.1:3102/guide");
  await page.getByRole("button", { name: "Open Jinyao chat", exact: true }).click();
  await page.getByRole("combobox", { name: "Explanation depth" }).selectOption("beginner");
  await page.getByRole("textbox").fill("First question"); await page.getByRole("textbox").press("Enter");
  await expect(page.locator(".jinyao-chat-turn").last()).toHaveAttribute("data-status", "ready");
  await page.getByRole("textbox").fill("Another question"); await page.getByRole("textbox").press("Enter");
  await expect(page.getByRole("button", { name: "Stop reply" })).toBeVisible();
  await page.getByRole("log").evaluate(node => { node.scrollTop = 0; node.dispatchEvent(new Event("scroll")); });
  await expect(page.getByRole("button", { name: "Jump to latest messages" })).toBeVisible();
  await expect.poll(() => !!release).toBe(true); release!();
  await expect(page.locator(".jinyao-chat-turn").last()).toHaveAttribute("data-status", "ready");
  expect(await page.getByRole("log").evaluate(node => node.scrollTop)).toBeLessThan(5);
  await page.getByRole("button", { name: "Jump to latest messages" }).click();
  await expect.poll(() => page.getByRole("log").evaluate(node => node.scrollHeight - node.clientHeight - node.scrollTop)).toBeLessThan(5);
  await expect(page.getByRole("textbox")).toHaveAttribute("aria-describedby", "jinyao-composer-help");
});

for (const viewport of [{ width: 1600, height: 900 }, { width: 390, height: 844 }, { width: 768, height: 1024 }, { width: 800, height: 450 }]) test(`chat keyboard and readable reflow ${viewport.width}x${viewport.height}`, async ({ page }) => {
  await page.setViewportSize(viewport);
  await page.goto("http://127.0.0.1:3102/guide");
  await page.getByRole("button", { name: "Open Jinyao chat", exact: true }).click();
  const close = page.getByRole("button", { name: "Close Jinyao chat", exact: true });
  await expect(close).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  const activeInDialog = await page.evaluate(() => !!document.activeElement?.closest(".jinyao-messenger"));
  expect(activeInDialog).toBe(true);
  await page.keyboard.press("Tab"); await expect(close).toBeFocused();
  const dialog = page.getByRole("dialog", { name: "Jinyao", exact: true });
  expect(await dialog.evaluate(node => node.scrollWidth <= node.clientWidth)).toBe(true);
  await page.getByRole("textbox").focus();
  const bounds = await page.getByRole("textbox").boundingBox();
  expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(viewport.height);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("button", { name: "Open Jinyao chat", exact: true })).toBeFocused();
});
