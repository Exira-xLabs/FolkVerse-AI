import { applicationMode } from "@/lib/app-mode";

export const dynamic = "force-dynamic";
export async function GET(request: Request, { params }: { params: Promise<{ identifier: string }> }) {
  const { identifier } = await params;
  const headers = { "Cache-Control": "no-store", "Content-Type": "application/json" };
  if (applicationMode() !== "live" || !/^[a-zA-Z0-9_-]{1,100}$/.test(identifier))
    return Response.json({ current: false, passage: null }, { status: 404, headers });
  const forwarded = new Headers();
  const cookie = request.headers.get("cookie")?.split(";").find(value => value.trim().startsWith("folkverse_session="));
  if (cookie) forwarded.set("cookie", cookie.trim());
  try {
    const upstream = await fetch(new URL(`/api/v1/guide/evidence/${identifier}`, process.env.API_BASE_URL ?? "http://127.0.0.1:8000"), {
      headers: forwarded, cache: "no-store", redirect: "error",
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(12000)]),
    });
    if (!upstream.headers.get("content-type")?.includes("application/json")) throw new Error("Invalid upstream");
    return new Response(await upstream.text(), { status: upstream.status, headers });
  } catch {
    return Response.json({ current: false, passage: null }, { status: 503, headers });
  }
}
