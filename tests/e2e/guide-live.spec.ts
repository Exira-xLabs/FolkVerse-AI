import { expect, test, type Page } from "@playwright/test";
import policy from "../../packages/contracts/src/jinyao-policy.json";
// Synthetic reviewed text and responses exercise presentation, not provider quality.
const evidence = (zh = false) => ({ passage_id: "passage_fixture", source_id: "source_fixture", text: zh ? "复州皮影戏在瓦房店名录中列为传统戏剧。" : "Fuzhou shadow puppetry is listed as traditional theatre in Wafangdian.", language: zh ? "zh-CN" : "en", locator: "Fixture row 1", rights_basis: "Synthetic test evidence", institution: "Fixture institution", source_title: "Fixture inventory", canonical_url: "https://example.org/inventory", fetched_at: "2026-10-06T00:00:00Z", reviewed_at: "2026-10-06T00:00:00Z", reviewer: "Fixture reviewer", review_id: "review_fixture", content_hash: "fixture_hash", exhibit_ids: ["exhibit_fixture"], region_ids: [] });
const event = (name: string, body: unknown) => `event: ${name}\r\ndata: ${JSON.stringify(body)}\r\n\r\n`;
type InvalidPublication = "display" | "empty_support" | "claim_reference" | "source_reference" | "source_language" | "unused_source";
function socialReply(inventedFact = false) {
  const answer = { answer_id: "social_fixture", locale: "en", depth: "concise", status: "conversational",
    uncertainty: "insufficient", reason: "social_turn", answer_text: policy.social.greeting.en +
      (inventedFact ? " It originated in 1644." : ""), coverage_limit: "", social_intent: "greeting",
    personality_version: policy.version, claims: [], answer_claim_ids: [], context_claim_ids: [],
    evidence_ids: [], related_exhibit_ids: [], mode: "live", corpus_version: "not_applicable" };
  return event("answer", answer) + event("sources", { answer_id: answer.answer_id, items: [] }) + event("done", { answer_id: answer.answer_id });
}
function reply(zh: boolean, depth: string, insufficient = false, hybrid = false, invalid?: InvalidPublication) {
  const p = evidence(zh);
  const answer = { answer_id: "answer_fixture", locale: zh ? "zh-CN" : "en", depth, status: insufficient ? "insufficient" : "answered", uncertainty: insufficient ? "insufficient" : "partial", reason: insufficient ? "coverage_gap" : "reviewed_excerpt", answer_text: insufficient ? (zh ? "审核资料不足，无法回答。" : "Reviewed evidence is insufficient to answer.") : p.text, coverage_limit: zh ? "仅支持名录信息。" : "Only inventory information is supported.", claims: insufficient ? [] : [{ claim_id: "claim_1", text: p.text, passage_ids: [p.passage_id], source_ids: [p.source_id], kind: "source_statement", support_method: "complete_reviewed_passage" }], answer_claim_ids: insufficient ? [] : ["claim_1"], context_claim_ids: [], evidence_ids: insufficient ? [] : [p.passage_id], related_exhibit_ids: insufficient ? [] : p.exhibit_ids, mode: "live", retrieval_mode: hybrid ? "hybrid" : "lexical_only", corpus_version: "fixture_corpus", context_token: "fixture_signed_context" };
  if (!insufficient) answer.answer_text = `${zh ? "经过审核的来源这样记载：" : "Here is what the reviewed source says:"}\n\n${p.source_title} (${p.institution}):\n${p.text}`;
  const sources = insufficient ? [] : [p];
  if (invalid === "display") answer.answer_text += "\nInvented origin in 1644.";
  if (invalid === "empty_support") { answer.claims[0].passage_ids = []; answer.claims[0].source_ids = []; }
  if (invalid === "claim_reference") answer.answer_claim_ids = ["invented_claim"];
  if (invalid === "source_reference") answer.claims[0].source_ids = ["invented_source"];
  if (invalid === "source_language") p.language = zh ? "en" : "zh-CN";
  if (invalid === "unused_source") { sources.push({ ...p, passage_id: "unused_passage" }); answer.evidence_ids.push("unused_passage"); }
  return event("meta", { mode: "live" }) + event("status", { stage: "validating" }) + event("answer", answer) + event("sources", { answer_id: answer.answer_id, items: sources }) + event("done", { answer_id: answer.answer_id });
}
async function fixtures(page: Page, options: { zh?: boolean; failure?: string; delay?: number; truncated?: boolean; sourceWithdrawn?: boolean; insufficient?: boolean; corrupt?: boolean; hybrid?: boolean; invalid?: InvalidPublication } = {}) {
  await page.route("**/api/v1/session", route => route.fulfill({ json: { session_id: "fixture_visit" } }));
  await page.route("**/api/v1/exhibits?*", route => route.fulfill({ json: { items: [{ id: "exhibit_fixture", title: options.zh ? "复州皮影戏" : "Fuzhou shadow puppetry" }], total: 1, next_cursor: null } }));
  await page.route("**/api/v1/sources/source_fixture", route => {
    const p = evidence(options.zh);
    return options.sourceWithdrawn ? route.fulfill({ status: 404, json: { error: { code: "unavailable" } } }) : route.fulfill({ json: { id: p.source_id, institution: p.institution, title: p.source_title, canonical_url: p.canonical_url, passages: [{ id: p.passage_id, text: p.text, language: p.language, locator: p.locator, rights_basis: p.rights_basis, review: { reviewer: p.reviewer, reviewed_at: p.reviewed_at } }] } });
  });
  await page.route("**/api/v1/guide", async route => {
    if (options.delay) await new Promise(resolve => setTimeout(resolve, options.delay));
    const body = route.request().postDataJSON();
    let data = options.failure ? event("error", { error: { code: options.failure } }) : reply(options.zh ?? false, body.depth, options.insufficient, options.hybrid, options.invalid);
    if (options.corrupt) data = data.replaceAll("passage_fixture", "invented_passage").replace("\"evidence_ids\":[\"invented_passage\"]", "\"evidence_ids\":[\"unmapped_passage\"]");
    await route.fulfill({ contentType: "text/event-stream", body: options.truncated ? data.slice(0, data.lastIndexOf("event: done")) : data }).catch(() => undefined);
  });
}
async function open(page: Page, zh = false) {
  await page.goto("http://127.0.0.1:3102/guide");
  if (zh) {
    await page.getByRole("button", { name: "Switch to Chinese", exact: true }).click();
  }
  await page.getByRole("button", { name: zh ? "打开锦瑶聊天" : "Open Jinyao chat", exact: true }).click();
}
for (const zh of [false, true]) {
  test(`live ${zh ? "Chinese phone" : "English desktop"} answer, consent, sources and retained history`, async ({ page }) => {
    const errors: string[] = []; page.on("pageerror", error => errors.push(error.message));
    if (zh) await page.setViewportSize({ width: 390, height: 844 });
    await fixtures(page, { zh });
    if (zh) { await page.goto("http://127.0.0.1:3102/guide"); await page.getByRole("button", { name: "Open navigation menu", exact: true }).click(); await page.getByRole("button", { name: "Switch to Chinese", exact: true }).click(); await page.getByRole("button", { name: "关闭导航菜单", exact: true }).click(); await page.getByRole("button", { name: "打开锦瑶聊天", exact: true }).click(); } else await open(page);
    await page.getByRole("checkbox").check();
    await page.getByRole("combobox", { name: zh ? "解释深度" : "Explanation depth" }).selectOption("beginner");
    const request = page.waitForRequest(r => r.url().endsWith("/api/v1/guide"));
    await page.getByRole("button", { name: zh ? "复州皮影戏" : "Fuzhou shadow puppetry", exact: true }).click();
    expect((await request).postDataJSON()).toMatchObject({ context_consent: true, depth: "beginner", locale: zh ? "zh-CN" : "en" });
    await expect(page.getByRole("log")).toContainText(evidence(zh).text);
    await expect(page.getByRole("log")).not.toContainText(zh ? "检索：" : "Search:");
    await page.getByRole("button", { name: zh ? "查看回答来源" : "Inspect answer sources" }).click();
    const drawer = page.getByRole("dialog", { name: zh ? "回答所依据的资料" : "Evidence behind this answer" });
    await expect(drawer).toContainText("Fixture inventory");
    await expect(drawer).toContainText(evidence(zh).text);
    await expect(drawer.getByRole("link")).toHaveAttribute("href", "https://example.org/inventory");
    await page.keyboard.press("Escape");
    await expect(page.getByRole("button", { name: zh ? "查看回答来源" : "Inspect answer sources" })).toBeFocused();
    await page.getByRole("textbox").fill(zh ? "有什么依据" : "Where is it listed?");
    const followup = page.waitForRequest(r => r.url().endsWith("/api/v1/guide"));
    await page.getByRole("button", { name: zh ? "发送消息" : "Send message", exact: true }).click();
    expect((await followup).postDataJSON().context_token).toBe("fixture_signed_context");
    await expect(page.locator(".jinyao-chat-turn")).toHaveCount(2);
    await expect(page.getByRole("button", { name: zh ? "查看回答来源" : "Inspect answer sources" })).toHaveCount(2);
    await page.keyboard.press("Escape");
    await page.getByRole("button", { name: zh ? "打开锦瑶聊天" : "Open Jinyao chat", exact: true }).click();
    await expect(page.locator(".jinyao-chat-turn")).toHaveCount(2);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(errors).toEqual([]);
  });
}
for (const failure of ["provider_timeout", "budget_exhausted", "rate_limited", "invalid_context"]) {
  test(`live ${failure} is retryable without facts`, async ({ page }) => {
    await fixtures(page, { failure }); await open(page);
    await page.getByRole("textbox").fill("Where is Fuzhou shadow puppetry listed?"); await page.getByRole("button", { name: "Send message", exact: true }).click();
    await expect(page.getByRole("button", { name: "Retry question" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Inspect answer sources" })).toHaveCount(0);
    await expect(page.getByRole("log")).not.toContainText(evidence().text);
  });
}
test("truncated stream discards the whole answer", async ({ page }) => {
  await fixtures(page, { truncated: true }); await open(page);
  await page.getByRole("textbox").fill("Question"); await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByRole("button", { name: "Retry question" })).toBeVisible();
  await expect(page.getByRole("log")).not.toContainText(evidence().text);
});
test("stop and retry cancel pending answer", async ({ page }) => {
  await fixtures(page, { delay: 800 }); await open(page);
  await page.getByRole("textbox").fill("Question"); await page.getByRole("button", { name: "Send message", exact: true }).click();
  await page.getByRole("button", { name: "Stop reply" }).click();
  await expect(page.getByRole("log")).toContainText("Reply stopped.");
  await page.waitForTimeout(1000); await expect(page.getByRole("log")).not.toContainText(evidence().text);
  await page.getByRole("button", { name: "Retry question" }).click();
  await expect(page.getByRole("log")).toContainText(evidence().text);
});
test("withdrawn source has no inspectable stale evidence", async ({ page }) => {
  await fixtures(page, { sourceWithdrawn: true }); await open(page);
  await page.getByRole("textbox").fill("Question"); await page.getByRole("button", { name: "Send message", exact: true }).click();
  await page.getByRole("button", { name: "Inspect answer sources" }).click();
  const drawer = page.getByRole("dialog", { name: "Evidence behind this answer" });
  await expect(drawer).toContainText("The evidence changed");
  await expect(drawer).not.toContainText(evidence().text);
});
for (const zh of [false, true]) test(`insufficiency ${zh ? "ZH" : "EN"} displays no citations or factual latency`, async ({ page }) => {
  await fixtures(page, { zh, insufficient: true }); await open(page, zh);
  await page.getByRole("textbox").fill("Unsupported dynasty question"); await page.getByRole("button", { name: zh ? "发送消息" : "Send message", exact: true }).click();
  await expect(page.getByRole("log")).toContainText(zh ? "审核资料不足" : "Reviewed evidence is insufficient");
  await expect(page.getByRole("button", { name: zh ? "查看回答来源" : "Inspect answer sources" })).toHaveCount(0);
  await expect(page.getByRole("log")).not.toContainText("received in");
});

test("mismatched evidence stream never publishes factual text", async ({ page }) => {
  await fixtures(page, { corrupt: true }); await open(page);
  await page.getByRole("textbox").fill("Question"); await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByRole("button", { name: "Retry question" })).toBeVisible();
  await expect(page.getByRole("log")).not.toContainText(evidence().text);
});

test("hybrid answers identify semantic retrieval while retaining citations", async ({ page }) => {
  await fixtures(page, { hybrid: true }); await open(page);
  await page.getByRole("textbox").fill("Question"); await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByRole("log")).not.toContainText("Search:");
  await expect(page.getByRole("button", { name: "Inspect answer sources" })).toBeVisible();
});

for (const invalid of ["display", "empty_support", "claim_reference", "source_reference", "source_language", "unused_source"] as const) {
  test(`invalid ${invalid} publication is discarded before display`, async ({ page }) => {
    await fixtures(page, { invalid }); await open(page);
    await page.getByRole("textbox").fill("Question");
    await page.getByRole("button", { name: "Send message", exact: true }).click();
    await expect(page.getByRole("button", { name: "Retry question" })).toBeVisible();
    await expect(page.getByRole("log")).not.toContainText(evidence().text);
    await expect(page.getByRole("log")).not.toContainText("Invented origin");
    await expect(page.getByRole("button", { name: "Inspect answer sources" })).toHaveCount(0);
  });
}

for (const invented of [false, true]) test(`social policy ${invented ? "rejects injected facts" : "preserves consented topic"}`, async ({ page }) => {
  await fixtures(page); await open(page);
  await page.getByRole("checkbox").check();
  await page.getByRole("textbox").fill("Where is Fuzhou shadow puppetry listed?");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByRole("button", { name: "Inspect answer sources" })).toBeVisible();
  await page.unroute("**/api/v1/guide");
  await page.route("**/api/v1/guide", route => route.fulfill({ contentType: "text/event-stream", body: socialReply(invented) }));
  await page.getByRole("textbox").fill("Hello!");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  if (invented) {
    await expect(page.getByRole("button", { name: "Retry question" })).toBeVisible();
    await expect(page.getByRole("log")).not.toContainText("1644");
  } else {
    await expect(page.getByRole("log")).toContainText(policy.social.greeting.en);
    await page.unroute("**/api/v1/guide");
    await page.route("**/api/v1/guide", route => route.fulfill({ contentType: "text/event-stream", body: reply(false, "beginner") }));
    const request = page.waitForRequest(r => r.url().endsWith("/api/v1/guide"));
    await page.getByRole("textbox").fill("Explain that simply");
    await page.getByRole("button", { name: "Send message", exact: true }).click();
    expect((await request).postDataJSON()).toMatchObject({ context_token: "fixture_signed_context", depth: "beginner" });
  }
});

test("open answer inspector clears evidence after source withdrawal revalidation", async ({ page }) => {
  await page.clock.install();
  await fixtures(page); await open(page);
  await page.getByRole("textbox").fill("Where is Fuzhou shadow puppetry listed?");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await page.getByRole("button", { name: "Inspect answer sources" }).click();
  const drawer = page.getByRole("dialog", { name: "Evidence behind this answer" });
  await expect(drawer).toContainText(evidence().text);
  await page.unroute("**/api/v1/sources/source_fixture");
  await page.route("**/api/v1/sources/source_fixture", route => route.fulfill({ status: 404, json: { error: { code: "unavailable" } } }));
  await page.clock.fastForward(16000);
  await expect(drawer).toContainText("The evidence changed");
  await expect(drawer).not.toContainText(evidence().text);
});
