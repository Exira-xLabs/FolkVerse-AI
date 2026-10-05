"use client";
import { createContext, useContext, useState, type Dispatch, type SetStateAction } from "react";
export type CatalogVisit = { query: string; region: string; theme: string; view: "collection" | "map" };
export type GuideVisit = { draft: string; turns: { id: string; question: string; pending: boolean; runId?: string; outcome?: "cancelled" | "error" | "insufficient" }[] };
export type JourneyVisit = { ids: string[]; duration: number; theme: string; appliedDuration: number; appliedTheme: string };
const VisitContext = createContext<{ guide: GuideVisit; setGuide: Dispatch<SetStateAction<GuideVisit>>; catalog: CatalogVisit; setCatalog: Dispatch<SetStateAction<CatalogVisit>>; journey: JourneyVisit; setJourney: Dispatch<SetStateAction<JourneyVisit>> } | null>(null);
export function VisitProvider({ children }: { children: React.ReactNode }) {
  const [catalog, setCatalog] = useState<CatalogVisit>({ query: "", region: "", theme: "", view: "collection" });
  const [guide, setGuide] = useState<GuideVisit>({ draft: "", turns: [] });
  const [journey, setJourney] = useState<JourneyVisit>({ ids: ["screen", "table", "song"], duration: 20, theme: "all", appliedDuration: 20, appliedTheme: "all" });
  return <VisitContext.Provider value={{ guide, setGuide, journey, setJourney, catalog, setCatalog }}>{children}</VisitContext.Provider>;
}
export function useVisit() { const visit = useContext(VisitContext); if (!visit) throw new Error("VisitProvider required"); return visit; }
