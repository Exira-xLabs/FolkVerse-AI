import { applicationMode } from "@/lib/app-mode";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const unavailable = (status = 503, code = "api_unavailable") => Response.json({
  error: { code, message: "The guide is temporarily unavailable.", retryable: status === 503 },
}, { status, headers: { "Cache-Control": "no-store" } });

export async function POST(request: Request) {
  if (applicationMode() !== "live") return unavailable(503, "guide_unavailable");
  // Next may use its bind hostname in request.url; Host retains the browser origin.
  const origin = request.headers.get("origin");
  let sameOrigin = false;
  try {
    const supplied = new URL(origin ?? "");
    sameOrigin = supplied.origin === origin && supplied.host === request.headers.get("host") && supplied.protocol === new URL(request.url).protocol;
  } catch { /* Missing or malformed origins fail closed. */ }
  if (!sameOrigin) return unavailable(403, "origin_denied");
  if (!request.headers.get("content-type")?.includes("application/json")) return unavailable(415, "invalid_input");
  const controller = new AbortController();
  const signal = AbortSignal.any([request.signal, controller.signal, AbortSignal.timeout(150000)]);
  try {
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
    const body = new Uint8Array(bytes);
    let offset = 0;
    for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.length; }
    const headers = new Headers({ "Content-Type": "application/json", "Accept": request.headers.get("accept") ?? "application/json" });
    const cookie = request.headers.get("cookie")?.split(";").find(v => v.trim().startsWith("folkverse_session="));
    if (cookie) headers.set("cookie", cookie.trim());
    headers.set("origin", request.headers.get("origin")!);
    const upstream = await fetch(new URL("/api/v1/guide", process.env.API_BASE_URL ?? "http://127.0.0.1:8000"), {
      method: "POST", headers, body: new TextDecoder("utf-8", { fatal: true }).decode(body),
      signal, cache: "no-store", redirect: "error",
    });
    const type = upstream.headers.get("content-type") ?? "";
    if (!upstream.body || (!type.includes("application/json") && !type.includes("text/event-stream"))) return unavailable();
    const output = new Headers({ "Content-Type": type, "Cache-Control": "no-store", "X-Accel-Buffering": "no" });
    const requestId = upstream.headers.get("x-request-id");
    if (requestId) output.set("X-Request-ID", requestId);
    const source = upstream.body.getReader();
    const stream = new ReadableStream<Uint8Array>({
      async pull(target) {
        try {
          const { value, done } = await source.read();
          if (done) { target.close(); source.releaseLock(); }
          else target.enqueue(value);
        } catch { controller.abort(); target.error(new Error("Guide connection interrupted")); }
      },
      async cancel() { controller.abort(); try { await source.cancel(); } catch { /* Already disconnected. */ } },
    });
    return new Response(stream, { status: upstream.status, headers: output });
  } catch { controller.abort(); return unavailable(); }
}
