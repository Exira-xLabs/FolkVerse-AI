import { proxyFoundation } from "@/lib/api-proxy";

export const dynamic = "force-dynamic";
export const GET = (request: Request) => proxyFoundation(request, "health");
