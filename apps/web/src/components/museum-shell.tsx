"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, type ReactNode } from "react";
import { routes, type PageKey } from "@/lib/routes";
import { museumArt, museumArtFocus } from "@/lib/museum-art";
import { useLocale } from "./locale-provider";
import { ServiceStatus } from "./service-status";
import { GlassTabs } from "./museum-ui";
import { MuseumExperiences } from "./museum-experiences";
import { FeaturedExhibit } from "./featured-exhibit";
import { useGraphics } from "./graphics-provider";

function DiscoveryArrow() {
  return <svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M4 14 14 4M4 4h10v10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>;
}

export function MuseumScene({ page, simple, children }: { page: PageKey; simple: boolean; children: ReactNode }) {
  return <div className={`museum-scene scene-${page} ${simple ? "reduced-graphics" : ""}`}>{children}</div>;
}

export function MuseumShell({ page, mode, initialExhibitId }: { page: PageKey; mode: "demo" | "live"; initialExhibitId?: string }) {
  const { locale, setLocale, t } = useLocale();
  const { simple, setSimple } = useGraphics();
  useEffect(() => { document.title = `${t.nav[page]} | FolkVerse China`; }, [page, t.nav]);
  const demoLabel = locale === "en" ? (mode === "demo" ? "Reviewed collection · optional previews" : "Published collection available · AI experiences not connected") : (mode === "demo" ? "审核馆藏 · 可选体验预览" : "已发布馆藏可用 · AI 体验尚未连接");
  const route = routes[page];
  const cards = ["explore", "stories", "journey", "guide"] as const;
  return <MuseumScene page={page} simple={simple}>
    <a className="skip-link" href="#main">{t.skip}</a>
    <header className="museum-nav glass-panel">
      <Link className="brand" href="/" aria-label="FolkVerse China"><span>FolkVerse</span><small>CHINA / AI</small></Link>
      <GlassTabs page={page} />
      <button className="language-switch nav-tab" aria-label={t.language}
        onClick={() => setLocale(locale === "en" ? "zh-CN" : "en")}>{locale === "en" ? "EN / 中文" : "中文 / EN"}</button>
    </header>
    <main id="main" tabIndex={-1} className="museum-main">
      <section className="scene-hero" aria-labelledby="page-title">
      <div className="scene-picture">
        <Image className="scene-art" src={museumArt(route.asset)} alt="" fill priority quality={90} sizes="(max-width: 700px) 100vw, 70vw" />
        <div className="scene-shade" />
      </div>
      <div className="hero-copy">
        <p className="kicker">{page === "home" ? t.kicker : `${String(Object.keys(routes).indexOf(page)).padStart(2, "0")} / ${t.nav[page].toUpperCase()}`}</p>
        <h1 id="page-title">{t.titles[page]}</h1>
        <p className="subtitle">{t.subtitles[page]}</p>
        {page === "home" && <div className="hero-actions"><Link className="gold-button" href="/explore">{locale === "en" ? "Explore Liaoning" : "探索辽宁"}<DiscoveryArrow /></Link><Link className="text-button" href="/sources">{locale === "en" ? "Meet the sources" : "了解资料来源"} ↗︎</Link></div>}
      </div></section>
      {page === "home" ? <><FeaturedExhibit /><div className="discovery-cards">
        {cards.map((key, index) => <article className={`glass-panel discovery-card card-${key}`} key={key}>
          <h2>{t.homeCards[index]}</h2>
          <p className="card-availability">{locale === "en" ? (index === 0 ? "Published collection" : key === "stories" ? "Original fiction · preview" : "Experience preview") : (index === 0 ? "已发布馆藏" : key === "stories" ? "原创虚构故事 · 预览" : "体验预览")}</p>
          <div className="card-art">
            <Image src={museumArt(key === "guide" ? "09_ai_guide_character.png" : routes[key].asset)}
              alt="" fill quality={90} sizes="(max-width: 700px) 100vw, (max-width: 1050px) 50vw, 25vw" className={key === "guide" ? "portrait-art" : ""}
              style={{ objectPosition: museumArtFocus(key === "guide" ? "09_ai_guide_character.png" : routes[key].asset, "card") }} />
          </div>
          <p className="art-caption">{locale === "en" ? (key === "guide" ? "Fictional companion" : "Decorative museum illustration") : (key === "guide" ? "虚构伙伴" : "装饰性博物馆插画")}</p>
          <Link className={index === 0 ? "gold-button" : "outline-button"}
            href={routes[key].href}>{t.homeActions[index]}<DiscoveryArrow /></Link>
        </article>)}
      </div></> : page === "status" ? <ServiceStatus /> : <MuseumExperiences page={page} mode={mode} initialExhibitId={initialExhibitId} />}
    </main>
    <footer className="museum-footer">
      <span className="preview-label"><span aria-hidden="true" className="preview-dot" />{demoLabel}</span>
      <div><button className="graphics-toggle" aria-pressed={simple} onClick={() => setSimple(!simple)}>{locale === "en" ? (simple ? "Full atmosphere" : "Simplify graphics") : (simple ? "完整氛围" : "简化图形")}</button><Link href="/sources">{t.nav.sources}</Link><Link href="/status">{t.nav.status}</Link></div>
    </footer>
  </MuseumScene>;
}
