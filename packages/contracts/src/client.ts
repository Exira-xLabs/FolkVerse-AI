import createClient from "openapi-fetch";
import type { paths, components } from "./schema";

export const api = createClient<paths>();
export type Health = components["schemas"]["HealthResponse"];
export type AnonymousSession = components["schemas"]["SessionResponse"];
export type ApiError = components["schemas"]["ErrorEnvelope"];
