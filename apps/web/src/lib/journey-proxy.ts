import "server-only";

const unavailable = (status = 503, code = "api_unavailable") => Response.json({
  error: { code, message: "The journey service is temporarily unavailable.", retryable: status === 503 },
}, { status, headers: { "Cache-Control": "no-store" } });

// Owned routes never accept an owner supplied by the browser. Forward only the signed session.
export async function proxyJourney(request: Request, identifier?: string) {
  if (identifier && !/^[A-Za-z0-9_.:-]{1,100}$/.test(identifier)) return unavailable(404, "not_found");
  const mutating = request.method !== "GET";
  if (mutating) {
    const origin = request.headers.get("origin");
    let sameOrigin = false;
    try {
      const supplied = new URL(origin ?? "");
      let protocol = new URL(request.url).protocol;
      const configured = process.env.PUBLIC_APP_ORIGIN;
      if (configured) {
        const publicOrigin = new URL(configured);
        if (publicOrigin.origin === configured && publicOrigin.protocol === "https:" &&
          publicOrigin.host === request.headers.get("host")) protocol = publicOrigin.protocol;
      }
      sameOrigin = supplied.origin === origin && supplied.host === request.headers.get("host") && supplied.protocol === protocol;
    } catch { /* Missing or malformed origins fail closed. */ }
    if (!sameOrigin) return unavailable(403, "origin_denied");
    if (!request.headers.get("content-type")?.includes("application/json")) return unavailable(415, "invalid_input");
  }
  try {
    let body: string | undefined;
    if (mutating) {
      const reader = request.body?.getReader();
      if (!reader) return unavailable(422, "invalid_input");
      const chunks: Uint8Array[] = [];
      let bytes = 0;
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        bytes += value.length;
        if (bytes > 65536) { await reader.cancel(); return unavailable(413, "context_too_large"); }
        chunks.push(value);
      }
      const joined = new Uint8Array(bytes);
      let offset = 0;
      for (const chunk of chunks) { joined.set(chunk, offset); offset += chunk.length; }
      body = new TextDecoder("utf-8", { fatal: true }).decode(joined);
    }
    const headers = new Headers({ "Accept": "application/json" });
    if (mutating) headers.set("Content-Type", "application/json");
    const cookie = request.headers.get("cookie")?.split(";").find(v => v.trim().startsWith("folkverse_session="));
    if (cookie) headers.set("cookie", cookie.trim());
    const origin = request.headers.get("origin");
    if (origin) headers.set("origin", origin);
    const path = `/api/v1/journeys${identifier ? `/${encodeURIComponent(identifier)}` : ""}`;
    const target = new URL(path, process.env.API_BASE_URL ?? "http://127.0.0.1:8000");
    const query = new URL(request.url).searchParams;
    const locale = query.get("locale");
    if (locale !== null) target.searchParams.set("locale", locale);
    if (request.method === "GET" && !identifier) {
      const limit = query.get("limit");
      if (limit !== null) target.searchParams.set("limit", limit);
    }
    const upstream = await fetch(target, {
      method: request.method, headers, body, cache: "no-store", redirect: "error",
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(45000)]),
    });
    if (!upstream.headers.get("content-type")?.includes("application/json")) return unavailable();
    const output = new Headers({ "Content-Type": "application/json", "Cache-Control": "no-store" });
    const requestId = upstream.headers.get("x-request-id");
    if (requestId) output.set("X-Request-ID", requestId);
    return new Response(await upstream.text(), { status: upstream.status, headers: output });
  } catch { return unavailable(); }
}
