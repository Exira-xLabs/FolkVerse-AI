import "server-only";
import { randomUUID } from "node:crypto";

export async function proxyFoundation(request: Request, resource: "health" | "session") {
  const headers = new Headers();
  const cookie = request.headers.get("cookie")?.split(";").find(value => value.trim().startsWith("folkverse_session="));
  if (cookie) headers.set("cookie", cookie.trim());
  const origin = request.headers.get("origin");
  if (origin) headers.set("origin", origin);
  const noStore = { "Cache-Control": "no-store", "Content-Type": "application/json" };
  try {
    const base = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
    const upstream = await fetch(new URL(`/api/v1/${resource}`, base), {
      method: request.method, headers, cache: "no-store", signal: AbortSignal.timeout(5000), redirect: "error",
    });
    if (!upstream.headers.get("content-type")?.includes("application/json")) throw new Error("Invalid upstream");
    const responseHeaders = new Headers(noStore);
    for (const value of upstream.headers.getSetCookie()) responseHeaders.append("Set-Cookie", value);
    const requestId = upstream.headers.get("x-request-id");
    if (requestId) responseHeaders.set("X-Request-ID", requestId);
    return new Response(await upstream.text(), { status: upstream.status, headers: responseHeaders });
  } catch {
    return Response.json({ error: { code: "api_unavailable", message: "The museum service is temporarily unavailable.", retryable: true }, request_id: `req_${randomUUID()}` }, { status: 503, headers: noStore });
  }
}
