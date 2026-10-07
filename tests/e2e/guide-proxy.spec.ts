import { expect, test } from "@playwright/test";
const live = "http://127.0.0.1:3102";
test("BFF forwards owned cookie and typed body, preserves status, and refuses demo/origin/oversize", async ({ request }) => {
  const headers = { Origin: live, Cookie: "unrelated=private; folkverse_session=fixture_cookie", Authorization: "Bearer fixture_not_forwarded" };
  const body = { question: "fixture", locale: "en", depth: "concise" };
  const response = await request.post(`${live}/api/v1/guide`, { headers, data: body });
  expect(response.status()).toBe(200);
  expect(response.headers()["cache-control"]).toBe("no-store");
  expect(response.headers()["x-request-id"]).toBe("fixture_request");
  expect((await response.json()).received).toEqual({ cookie: "folkverse_session=fixture_cookie", origin: live, authorization: null, path: "/api/v1/guide", payload: body });
  expect((await request.post(`${live}/api/v1/guide`, { headers, data: { question: "limit_fixture" } })).status()).toBe(429);
  expect((await request.post(`${live}/api/v1/guide`, { headers: { Origin: "https://attacker.example" }, data: body })).status()).toBe(403);
  expect((await request.post(`${live}/api/v1/guide`, { headers, data: { question: "x".repeat(65536) } })).status()).toBe(413);
  expect((await request.post("http://127.0.0.1:3100/api/v1/guide", { headers: { Origin: "http://127.0.0.1:3100" }, data: body })).status()).toBe(503);
});
test("BFF stream cancellation closes the upstream fixture connection", async ({ page, request }) => {
  const before = (await (await request.get("http://127.0.0.1:3210")).json()).cancelled;
  await page.goto(`${live}/guide`);
  await page.evaluate(async () => {
    const controller = new AbortController();
    const response = await fetch("/api/v1/guide", { method: "POST", signal: controller.signal, headers: { "Content-Type": "application/json", Accept: "text/event-stream" }, body: JSON.stringify({ question: "cancel_fixture" }) });
    const reader = response.body!.getReader();
    await reader.read(); controller.abort(); await reader.cancel().catch(() => undefined);
  });
  await expect.poll(async () => (await (await request.get("http://127.0.0.1:3210")).json()).cancelled).toBe(before + 1);
});

test("evidence BFF forwards only the owned cookie and never caches", async ({ request }) => {
  const response = await request.get(`${live}/api/v1/guide/evidence/lookup_fixture`, { headers: { Cookie: "other=private; folkverse_session=fixture_cookie", Authorization: "Bearer not_forwarded" } });
  expect(response.status()).toBe(200);
  expect(response.headers()["cache-control"]).toBe("no-store");
  expect((await response.json()).received).toEqual({ cookie: "folkverse_session=fixture_cookie", authorization: null, path: "/api/v1/guide/evidence/lookup_fixture" });
  expect((await request.get("http://127.0.0.1:3100/api/v1/guide/evidence/lookup_fixture")).status()).toBe(404);
});

test("configured HTTPS preview behind HTTP preserves exact origin and Host checks", async ({ request }) => {
  const body = { question: "fixture", locale: "en", depth: "concise" };
  const headers = { Host: "preview.fixture.test", Origin: "https://preview.fixture.test" };
  const response = await request.post(`${live}/api/v1/guide`, { headers, data: body });
  expect(response.status()).toBe(200);
  expect((await response.json()).received.origin).toBe(headers.Origin);
  for (const invalid of [
    { ...headers, Origin: "http://preview.fixture.test" },
    { ...headers, Origin: "https://attacker.example" },
    { ...headers, Host: "attacker.example" },
    { ...headers, Origin: "https://preview.fixture.test/" },
  ]) expect((await request.post(`${live}/api/v1/guide`, { headers: invalid, data: body })).status()).toBe(403);
});
