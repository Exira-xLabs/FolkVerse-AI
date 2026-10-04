"use client";

import Image from "next/image";
import Link from "next/link";
import { useState, type ReactNode } from "react";
import { routes, type PageKey } from "@/lib/routes";
import { useLocale } from "./locale-provider";
import { ServiceStatus } from "./service-status";
import { GlassTabs } from "./museum-ui";
import { MuseumExperiences } from "./museum-experiences";

function DiscoveryArrow() {
  return <svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M4 14 14 4M4 4h10v10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>;
}

export function MuseumScene({ page, simple, children }: { page: PageKey; simple: boolean; children: ReactNode }) {
  return <div className={`museum-scene scene-${page} ${simple ? "reduced-graphics" : ""}`}>{children}</div>;
}

export function MuseumShell({ page, mode }: { page: PageKey; mode: "demo" | "live" }) {
  const { locale, setLocale, t } = useLocale();
  const [simple, setSimple] = useState(false);
  const demoLabel = mode === "demo" ? (locale === "en" ? "Interactive demo" : "交互演示") : (locale === "en" ? "Live mode · features unavailable" : "实时模式 · 功能尚未开放");
  const route = routes[page];
  const cards = ["journey", "stories", "lens", "guide"] as const;
  return <MuseumScene page={page} simple={simple}>
    <Image className="scene-art" src={`/folkverse/${route.asset}`} alt="" fill priority sizes="100vw" />
    <div className="scene-shade" />
    <a className="skip-link" href="#main">{t.skip}</a>
    <header className="museum-nav glass-panel">
      <Link className="brand" href="/" aria-label="FolkVerse China"><span>FolkVerse</span><small>CHINA / AI</small></Link>
      <GlassTabs page={page} />
      <button className="language-switch nav-tab" aria-label={t.language}
        onClick={() => setLocale(locale === "en" ? "zh-CN" : "en")}>{locale === "en" ? "EN / 中文" : "中文 / EN"}</button>
    </header>
    <main id="main" tabIndex={-1} className="museum-main">
      <div className="hero-copy">
        <p className="kicker">{page === "home" ? t.kicker : `${String(Object.keys(routes).indexOf(page)).padStart(2, "0")} / ${t.nav[page].toUpperCase()}`}</p>
        <h1>{t.titles[page]}</h1>
        <p className="subtitle">{t.subtitles[page]}</p>
      </div>
      {page === "home" ? <div className="discovery-cards">
        {cards.map((key, index) => <article className={`glass-panel discovery-card card-${key}`} key={key}>
          <h2>{t.homeCards[index]}</h2>
          <div className="card-art">
            <Image src={`/folkverse/${key === "guide" ? "09_ai_guide_character.png" : routes[key].asset}`}
              alt="" fill sizes="(max-width: 700px) 80vw, 25vw" className={key === "guide" ? "portrait-art" : ""} />
          </div>
          <Link className={index === 0 || index === 3 ? "gold-button" : "outline-button"}
            href={routes[key].href}>{t.homeActions[index]}<DiscoveryArrow /></Link>
        </article>)}
      </div> : page === "status" ? <ServiceStatus /> : <MuseumExperiences page={page} mode={mode} />}
    </main>
    <footer className="museum-footer">
      <span className="preview-label"><span aria-hidden="true" className="preview-dot" />{demoLabel}</span>
      <div><button className="graphics-toggle" aria-pressed={simple} onClick={() => setSimple(!simple)}>{locale === "en" ? (simple ? "Full atmosphere" : "Simplify graphics") : (simple ? "完整氛围" : "简化图形")}</button><Link href="/sources">{t.nav.sources}</Link><Link href="/status">{t.nav.status}</Link></div>
    </footer>
  </MuseumScene>;
}
