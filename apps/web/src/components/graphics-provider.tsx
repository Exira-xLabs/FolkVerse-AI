"use client";

import { createContext, useContext, useEffect, useState } from "react";

const GraphicsContext = createContext<{ simple: boolean; setSimple: (value: boolean) => void; lowData: boolean; setLowData: (value: boolean) => void }>({ simple: false, setSimple: () => {}, lowData: false, setLowData: () => {} });

export function GraphicsProvider({ children, initialSimple, initialLowData = false }: { children: React.ReactNode; initialSimple: boolean; initialLowData?: boolean }) {
  const [lowData, setLowData] = useState(initialLowData);
  const [simple, setSimple] = useState(initialSimple);
  useEffect(() => {
    document.cookie = `folkverse_graphics=${simple ? "simple" : "full"}; Path=/; Max-Age=31536000; SameSite=Lax`;
  }, [simple]);
  useEffect(() => { document.cookie = `folkverse_data=${lowData ? "low" : "full"}; Path=/; Max-Age=31536000; SameSite=Lax`; }, [lowData]);
  return <GraphicsContext.Provider value={{ simple, setSimple, lowData, setLowData }}>{children}</GraphicsContext.Provider>;
}

export function useGraphics() { return useContext(GraphicsContext); }
