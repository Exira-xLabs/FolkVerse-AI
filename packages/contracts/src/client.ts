import createClient from "openapi-fetch";
import type { paths, components } from "./schema";

export const api = createClient<paths>();
export type Health = components["schemas"]["HealthResponse"];
export type AnonymousSession = components["schemas"]["SessionResponse"];
export type ApiError = components["schemas"]["ErrorEnvelope"];
export type RegionList = components["schemas"]["RegionList"];
export type ExhibitPage = components["schemas"]["ExhibitPage"];
export type ExhibitDetail = components["schemas"]["ExhibitDetail"];
export type SourceCard = components["schemas"]["SourceCard"];
export type SourceList = components["schemas"]["SourceList"];
