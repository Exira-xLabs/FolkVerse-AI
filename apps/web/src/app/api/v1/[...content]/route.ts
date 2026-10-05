import { NextRequest } from "next/server";

export async function GET(request: NextRequest, { params }: { params: Promise<{ content: string[] }> }) {
  const { content } = await params;
  const [resource, id] = content;
  if (!resource || !["regions", "exhibits", "sources", "artifacts"].includes(resource) || content.length > 2 ||
      (id && (!["exhibits", "sources"].includes(resource) || !/^[a-zA-Z0-9_-]{1,100}$/.test(id)))) {
    return Response.json({ error: { code: "not_found", message: "Not found", retryable: false } }, { status: 404 });
  }
  const headers = { "Cache-Control": "no-store", "Content-Type": "application/json" };
  try {
    const url = new URL(`/api/v1/${content.join("/")}`, process.env.API_BASE_URL ?? "http://127.0.0.1:8000");
    for (const key of ["locale", "region_id", "themes", "q", "cursor", "limit"]) {
      const value = request.nextUrl.searchParams.get(key);
      if (value !== null) url.searchParams.set(key, value);
    }
    const upstream = await fetch(url, { cache: "no-store", redirect: "error", signal: AbortSignal.timeout(8000) });
    if (!upstream.headers.get("content-type")?.includes("application/json")) throw new Error("Invalid upstream");
    return new Response(await upstream.text(), { status: upstream.status, headers });
  } catch {
    return Response.json({ error: { code: "api_unavailable", message: "The collection is temporarily unavailable.", retryable: true } }, { status: 503, headers });
  }
}
