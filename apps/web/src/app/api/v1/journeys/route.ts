import { proxyJourney } from "@/lib/journey-proxy";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export const GET = (request: Request) => proxyJourney(request);
export const POST = (request: Request) => proxyJourney(request);
