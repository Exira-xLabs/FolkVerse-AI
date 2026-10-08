import { proxyJourney } from "@/lib/journey-proxy";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
type Context = { params: Promise<{ identifier: string }> };
export async function GET(request: Request, context: Context) {
  return proxyJourney(request, (await context.params).identifier);
}
export async function PATCH(request: Request, context: Context) {
  return proxyJourney(request, (await context.params).identifier);
}
