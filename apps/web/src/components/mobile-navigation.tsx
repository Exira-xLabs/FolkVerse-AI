"use client";

import Link from "next/link";
import { useEffect, useId, useRef, useState } from "react";
import { navigation, routes, type PageKey } from "@/lib/routes";
import { lockDocumentScroll, trapDialogTab } from "@/lib/dialog";
import { useLocale } from "./locale-provider";

const navigationIcons: Record<PageKey, string> = {
  home: "m3 10 9-7 9 7M5 9v12h14V9M9 21v-7h6v7",
  explore: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm4 5-2 6-6 2 2-6 6-2Z",
  journey: "M7 4a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm10 12a2 2 0 1 0 0 4 2 2 0 0 0 0-4ZM7 8v3a4 4 0 0 0 4 4h2a4 4 0 0 1 4 3",
  stories: "M12 6C9 4 6 4 3 5v14c3-1 6-1 9 1 3-2 6-2 9-1V5c-3-1-6-1-9 1Zm0 0v14",
  lens: "M8 3H3v5m13-5h5v5M3 16v5h5m8 0h5v-5M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10Z",
  guide: "M20 11a8 8 0 0 1-8 8H5l-3 3V11a9 9 0 0 1 18 0ZM7 10h8m-8 4h5",
  dna: "m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z",
  sources: "M6 3h9l4 4v14H6V3Zm8 0v5h5M9 12h7m-7 4h5M3 7v14",
  status: "M3 12h4l3-7 4 14 3-7h4",
};

export function MobileNavigation({ page }: { page: PageKey }) {
  const { locale, setLocale, t } = useLocale();
  const zh = locale !== "en";
  const [open, setOpen] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const dialogId = useId();
  const titleId = useId();
  const links: PageKey[] = ["home", ...navigation, "sources", "status"];

  useEffect(() => {
    const node = dialog.current;
    if (!node || !open) return;
    const trigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    node.showModal();
    const unlock = lockDocumentScroll();
    return () => { node.close(); unlock(); trigger?.focus({ preventScroll: true }); };
  }, [open]);
  useEffect(() => {
    const query = window.matchMedia("(max-width: 700px)");
    const closeOnDesktop = () => { if (!query.matches) setOpen(false); };
    query.addEventListener("change", closeOnDesktop);
    return () => query.removeEventListener("change", closeOnDesktop);
  }, []);

  return <>
    <button className="mobile-menu-toggle" aria-label={zh ? "打开导航菜单" : "Open navigation menu"} aria-expanded={open} aria-controls={dialogId} aria-haspopup="dialog" onClick={() => setOpen(true)}>
      <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"><path d="M4 6h16M4 12h16M4 18h16" /></svg>
    </button>
    <dialog ref={dialog} id={dialogId} className="mobile-menu" aria-labelledby={titleId} aria-modal="true" onKeyDown={trapDialogTab} onCancel={event => { event.preventDefault(); setOpen(false); }} onClick={event => {
      if (event.target !== event.currentTarget) return;
      const bounds = event.currentTarget.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) setOpen(false);
    }}>
      <header><h2 id={titleId}>{zh ? "探索 FolkVerse" : "Explore FolkVerse"}</h2><button className="mobile-menu-close" autoFocus onClick={() => setOpen(false)} aria-label={zh ? "关闭导航菜单" : "Close navigation menu"}>×</button></header>
      <nav aria-label={zh ? "手机主导航" : "Mobile main navigation"}>{links.map(key => <Link key={key} href={routes[key].href} prefetch={false} aria-current={page === key ? "page" : undefined} onClick={() => setOpen(false)}><span className="mobile-menu-icon"><svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d={navigationIcons[key]} /></svg></span><span>{t.nav[key]}</span></Link>)}</nav>
      <footer><span>{zh ? "语言" : "Language"}</span><button className="outline-button" aria-label={t.language} onClick={() => setLocale(zh ? "en" : "zh-CN")}>{zh ? "中文 / EN" : "EN / 中文"}</button></footer>
    </dialog>
  </>;
}
