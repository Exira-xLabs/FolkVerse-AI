"use client";
import { useEffect } from "react";
/** Adapt the composer to the visual viewport without claiming physical keyboard validation. */
export function useGuideKeyboard() {
  useEffect(() => {
    const viewport = window.visualViewport;
    const previous = document.documentElement.style.getPropertyValue("--guide-keyboard-inset");
    const update = () => {
      const focused = document.activeElement?.id === "guide-question";
      const inset = focused && viewport ? Math.max(0, innerHeight - viewport.height - viewport.offsetTop) : 0;
      document.documentElement.style.setProperty("--guide-keyboard-inset", `${inset}px`);
      if (focused && inset > 0) document.activeElement?.scrollIntoView({ block: "center", behavior: "instant" });
    };
    viewport?.addEventListener("resize", update); document.addEventListener("focusin", update); document.addEventListener("focusout", update);
    return () => { viewport?.removeEventListener("resize", update); document.removeEventListener("focusin", update); document.removeEventListener("focusout", update); document.documentElement.style.setProperty("--guide-keyboard-inset", previous); };
  }, []);
}
