"use client";

import { createContext, useContext, useEffect, useState } from "react";

const GraphicsContext = createContext<{ simple: boolean; setSimple: (value: boolean) => void }>({ simple: false, setSimple: () => {} });

export function GraphicsProvider({ children, initialSimple }: { children: React.ReactNode; initialSimple: boolean }) {
  const [simple, setSimple] = useState(initialSimple);
  useEffect(() => {
    document.cookie = `folkverse_graphics=${simple ? "simple" : "full"}; Path=/; Max-Age=31536000; SameSite=Lax`;
  }, [simple]);
  return <GraphicsContext.Provider value={{ simple, setSimple }}>{children}</GraphicsContext.Provider>;
}

export function useGraphics() { return useContext(GraphicsContext); }
