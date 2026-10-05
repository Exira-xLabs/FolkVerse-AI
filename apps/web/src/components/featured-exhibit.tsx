"use client";

import Link from "next/link";
import { useReadingVisit } from "./visit-provider";
import { useEffect, useState } from "react";
import { api, type ExhibitPage } from "@folkverse/contracts";
import { useLocale } from "./locale-provider";

type Feature = { locale: string; state: "ready" | "loading" | "error"; exhibit: ExhibitPage["items"][number] | null };

/** Published text only: decorative museum scenery is not an exhibit photograph. */
export function FeaturedExhibit() {
  const { setReading } = useReadingVisit();
  const { locale } = useLocale();
  const zh = locale !== "en";
  const [feature, setFeature] = useState<Feature | null>(null);
  const [reload, setReload] = useState(0);
  useEffect(() => {
    let controller: AbortController | undefined;
    const load = async () => {
      controller?.abort();
      const requestController = new AbortController();
      controller = requestController;
      const signal = AbortSignal.any([requestController.signal, AbortSignal.timeout(7000)]);
      setFeature({ locale, state: "loading", exhibit: null });
      try {
        const { data } = await api.GET("/api/v1/exhibits", {
          params: { query: { locale, region_id: "liaoning", limit: 1 } }, signal, cache: "no-store",
        });
        if (!data) throw new Error("Collection unavailable");
        if (!requestController.signal.aborted) setFeature({ locale, state: "ready", exhibit: data.items[0] ?? null });
      } catch {
        if (!requestController.signal.aborted) setFeature({ locale, state: "error", exhibit: null });
      }
    };
    const refresh = () => { void load(); };
    refresh();
    window.addEventListener("focus", refresh);
    const timer = setInterval(refresh, 15000);
    return () => { controller?.abort(); clearInterval(timer); window.removeEventListener("focus", refresh); };
  }, [locale, reload]);
  const current = feature?.locale === locale ? feature : null;
  const exhibit = current?.exhibit;
  return <section className="featured-exhibit reading-panel glass-panel" aria-labelledby="featured-title" aria-busy={!current || current.state === "loading"}>
    <div className="featured-heading"><p className="eyebrow">{zh ? "从审核馆藏开始" : "START WITH THE REVIEWED COLLECTION"}</p>
      <h2 id="featured-title">{zh ? "认识一项辽宁传统" : "Meet a Liaoning tradition"}</h2></div>
    {!current || current.state === "loading" ? <p role="status">{zh ? "正在查找已发布展览…" : "Finding a published exhibit…"}</p>
      : current.state === "error" ? <div><p role="alert">{zh ? "暂时无法读取推荐展览，请重试或浏览馆藏。" : "The featured exhibit is temporarily unavailable. Try again or browse the collection."}</p>
        <button className="outline-button" onClick={() => setReload(n => n + 1)}>{zh ? "重试" : "Try again"}</button></div>
        : exhibit ? <article className="featured-record"><span className="demo-tag">{zh ? "人工编辑审核 · 辽宁" : "Human editorial review · Liaoning"}</span>
          <h3>{exhibit.title}</h3><p>{exhibit.summary}</p>
          <Link className="gold-button" onClick={() => setReading(previous => ({ ...previous, lastRead: exhibit.id }))} href={`/explore?exhibit=${encodeURIComponent(exhibit.id)}`}>{zh ? "阅读展览与来源" : "Read exhibit & sources"} ↗︎</Link></article>
          : <p role="status">{zh ? "目前没有可推荐的已发布展览，资料完成审核后会在这里出现。" : "No published exhibit is available to feature yet. Records appear here after review."}</p>}
    {!exhibit && <Link className="text-button" href="/explore">{zh ? "浏览馆藏" : "Browse the collection"} ↗︎</Link>}
  </section>;
}
