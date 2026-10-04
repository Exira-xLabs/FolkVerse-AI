"use client";

import Image from "next/image";
import Link from "next/link";
import { motion, useReducedMotion } from "motion/react";
import { navigation, routes, type PageKey } from "@/lib/routes";
import { useLocale } from "./locale-provider";
import { ServiceStatus } from "./service-status";

function DiscoveryArrow() {
  return <svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M4 14 14 4M4 4h10v10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>;
}

export function MuseumShell({ page }: { page: PageKey }) {
  const { locale, setLocale, t } = useLocale();
  const reducedMotion = useReducedMotion();
  const route = routes[page];
  const cards = ["journey", "stories", "lens", "guide"] as const;
  return <div className={`museum-scene scene-${page}`}>
    <Image className="scene-art" src={`/folkverse/${route.asset}`} alt="" fill priority sizes="100vw" />
    <div className="scene-shade" />
    <a className="skip-link" href="#main">{t.skip}</a>
    <header className="museum-nav glass-panel">
      <Link className="brand" href="/" aria-label="FolkVerse China"><span>FolkVerse</span><small>CHINA / AI</small></Link>
      <nav aria-label={locale === "en" ? "Main navigation" : "主导航"} className="nav-tabs">
        {navigation.map(key => <Link key={key} href={routes[key].href} prefetch={false}
          className={`nav-tab ${page === key ? "selected" : ""}`}
          aria-current={page === key ? "page" : undefined}>{t.nav[key]}</Link>)}
      </nav>
      <button className="language-switch nav-tab" aria-label={t.language}
        onClick={() => setLocale(locale === "en" ? "zh-CN" : "en")}>{locale === "en" ? "EN / 中文" : "中文 / EN"}</button>
    </header>
    <main id="main" tabIndex={-1} className="museum-main">
      <div className="hero-copy">
        <p className="kicker">{page === "home" ? t.kicker : t.nav[page].toUpperCase()}</p>
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
      </div> : page === "status" ? <ServiceStatus /> :
        <motion.section className={`glass-panel experience-panel ${page === "guide" ? "guide-panel" : ""}`}
          initial={false} animate={{ opacity: 1 }} transition={{ duration: reducedMotion ? 0 : 0.2 }}>
          <p className="panel-label">{t.preview}</p>
          <h2>{t.unavailable}</h2>
          <p>{t.empty[page]}</p>
          <Link href="/" className="outline-button">{t.returnExplore}<DiscoveryArrow /></Link>
        </motion.section>}
      {page === "guide" && <div className="guide-portrait" aria-hidden="true">
        <Image src="/folkverse/09_ai_guide_character.png" alt="" fill sizes="(max-width: 700px) 80vw, 32vw" className="portrait-art" />
      </div>}
    </main>
    <footer className="museum-footer">
      <span className="preview-label"><span aria-hidden="true" className="preview-dot" />{t.preview}</span>
      <div><Link href="/sources">{t.nav.sources}</Link><Link href="/status">{t.nav.status}</Link></div>
    </footer>
  </div>;
}
