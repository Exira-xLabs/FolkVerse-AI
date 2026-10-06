// Actual browser/BFF/API/provider walkthrough. No routing, mocked replies or fake reviews.
import { chromium } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

const output = process.env.FOLKVERSE_EVIDENCE_DIR ?? "report/evidence/phase03-completion";
mkdirSync(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, reducedMotion: "reduce" });
await page.addInitScript(() => {
  // Observe a clone: the app cancels its SSE reader after the validated done frame,
  // so Chrome cannot always supply the completed response body through DevTools.
  window.__guideResponses = [];
  const fetchOriginal = window.fetch.bind(window);
  window.fetch = async (...args) => {
    const response = await fetchOriginal(...args);
    if (response.url.endsWith("/api/v1/guide")) {
      const record = { status: response.status, body: null };
      window.__guideResponses.push(record);
      void response.clone().text().then(body => { record.body = body; });
    }
    return response;
  };
});
const results = { checkedAt: new Date().toISOString(), provenance: "real_browser_no_interception", conversations: [], checks: [], errors: [] };
page.on("pageerror", error => results.errors.push(error.message));
const check = (name, passed, details = null) => results.checks.push({ name, passed, details });
async function send(question, expected) {
  const started = performance.now();
  const responseIndex = await page.evaluate(() => window.__guideResponses.length);
  const responsePromise = page.waitForResponse(r => r.url().endsWith("/api/v1/guide") && r.request().method() === "POST", { timeout: 60000 });
  await page.getByRole("textbox").fill(question);
  await page.locator(".jinyao-chat-composer button[type=submit]").click();
  const response = await responsePromise;
  await page.waitForFunction(index => typeof window.__guideResponses[index]?.body === "string", responseIndex, { timeout: 60000 });
  const stream = await page.evaluate(index => window.__guideResponses[index].body, responseIndex);
  const frames = stream.split(/\r?\n\r?\n/).filter(Boolean).map(frame => {
    const lines = frame.split(/\r?\n/);
    return { event: lines.find(x => x.startsWith("event: "))?.slice(7), data: JSON.parse(lines.filter(x => x.startsWith("data: ")).map(x => x.slice(6)).join("\n")) };
  });
  const answer = frames.find(x => x.event === "answer")?.data;
  const error = frames.find(x => x.event === "error")?.data;
  const sources = frames.find(x => x.event === "sources")?.data.items;
  const done = frames.find(x => x.event === "done")?.data;
  if (answer) delete answer.context_token;
  results.conversations.push({ question, httpStatus: response.status(), answer, sources, error, done, browserRoundTripMs: Math.round(performance.now() - started) });
  await page.waitForFunction(() => !document.querySelector(".jinyao-chat-history[aria-busy=true]"), { timeout: 60000 });
  check(`turn: ${question}`, answer?.status === expected && !error);
  return answer;
}
try {
  const health = await page.request.get("http://127.0.0.1:3000/api/v1/health");
  check("web API PostgreSQL health", health.status() === 200, await health.json());
  await page.goto("http://127.0.0.1:3000/guide");
  await page.getByRole("button", { name: "Open Jinyao chat", exact: true }).click();
  await page.getByRole("checkbox").check();
  await send("Hello Jinyao!", "conversational");
  const first = await send("Where is Fuzhou shadow puppetry listed?", "answered");
  check("actual provider attempt recorded", !!first?.provider_attempt_id);
  if (first?.status === "answered") {
    await page.getByRole("button", { name: "Inspect answer sources" }).last().click();
    const drawer = page.getByRole("dialog", { name: "Evidence behind this answer" });
    await drawer.getByRole("link", { name: "Open original source" }).waitFor();
    check("current source inspector", (await drawer.innerText()).includes("Wafangdian"));
    await page.keyboard.press("Escape");
    check("source inspector restores focus", await page.getByRole("button", { name: "Inspect answer sources" }).last().evaluate(el => el === document.activeElement));
    await send("Explain that simply", "answered");
    await send("Go deeper", "answered");
    await send("Thank you", "conversational");
    const chinese = await send("Say that in Chinese", "answered");
    check("language switched with supported context", chinese?.locale === "zh-CN");
    await send("复州皮影戏起源于哪一年？", "insufficient");
    await send("为什么？", "insufficient");
  }
  const count = await page.locator(".jinyao-chat-turn").count();
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: /Open Jinyao chat|打开锦瑶聊天/, exact: true }).click();
  check("close reopen keeps page history", await page.locator(".jinyao-chat-turn").count() === count);
  for (const [width, height] of [[1600, 900], [390, 844], [768, 1024]]) {
    await page.setViewportSize({ width, height });
    await page.screenshot({ path: path.join(output, `live-chat-${width}.png`) });
    check(`no overflow ${width}`, await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    check(`composer reachable ${width}`, await page.locator(".jinyao-chat-composer").isVisible());
  }
  await page.setViewportSize({ width: 1600, height: 900 });
  await page.evaluate(() => { document.body.style.zoom = "2"; });
  check("200 percent CSS zoom has no document overflow", await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({ path: path.join(output, "live-chat-zoom-200.png") });
  await page.evaluate(() => { document.body.style.zoom = ""; });
  // Unscoped ambiguity uses the same real owned transport, without provider generation.
  const ambiguous = await page.evaluate(async () => {
    const r = await fetch("/api/v1/guide", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: "Explain more", locale: "en", depth: "concise" }) });
    return { status: r.status, body: await r.json() };
  });
  check("unscoped reference asks clarification", ambiguous.body.status === "clarification");
} catch (error) {
  results.errors.push(error.message);
} finally {
  await browser.close();
  writeFileSync(path.join(output, "live-browser.json"), JSON.stringify(results, null, 2) + "\n");
}
console.log(JSON.stringify({ checks: results.checks.length, failed: results.checks.filter(x => !x.passed).map(x => x.name), errors: results.errors }, null, 2));
process.exitCode = results.errors.length || results.checks.some(x => !x.passed) ? 1 : 0;
