"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type ExhibitPage } from "@folkverse/contracts";
import { useLocale } from "./locale-provider";
import { useVisit } from "./visit-provider";
export function ReviewedDiscovery({ action = "read", theme }: { action?: "read" | "question"; theme?: string }) {
  const { locale } = useLocale(); const zh = locale !== "en"; const { setGuide } = useVisit();
  const [result, setResult] = useState<{ locale: string; theme?: string; data: ExhibitPage | null } | null>(null);
  const [reload, setReload] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); let latest = 0;
    const load = async () => { const request = ++latest;
      try { const response = await api.GET("/api/v1/exhibits", { params: { query: { locale, region_id: "liaoning", themes: theme, limit: 12 } }, cache: "no-store", signal: controller.signal });
        if (!controller.signal.aborted && request === latest) setResult({ locale, theme, data: response.data ?? null });
      } catch { if (!controller.signal.aborted && request === latest) setResult({ locale, theme, data: null }); }
    }; void load(); const refresh = () => void load(); window.addEventListener("focus", refresh); const timer = setInterval(refresh, 15000);
    return () => { controller.abort(); window.removeEventListener("focus", refresh); clearInterval(timer); };
  }, [locale, theme, reload]);
  const loaded = result?.locale === locale && result.theme === theme;
  return <section className="reviewed-discovery" aria-label={zh ? "审核后的探索起点" : "Reviewed starting points"}><h3>{zh ? "从审核后的馆藏开始" : "Start with reviewed coverage"}</h3>
    {!loaded ? <p role="status">{zh ? "正在检查展览…" : "Checking exhibits…"}</p> : !result.data ? <><p role="alert">{zh ? "馆藏暂时不可用，请重试。" : "The collection is unavailable. Please try again."}</p><button className="outline-button" onClick={() => setReload(n => n + 1)}>{zh ? "重试馆藏" : "Retry collection"}</button></> : !result.data.items.length ? <p>{zh ? "此方向暂无符合条件的已发布展览，您仍可浏览全部辽宁馆藏。" : "No eligible published exhibit matches this direction yet. You can still browse all Liaoning."}</p> : <ul>{result.data.items.map(record => <li key={record.id}><Link className="outline-button" href={`/explore?exhibit=${encodeURIComponent(record.id)}`}>{record.title} · {record.estimated_minutes} {zh ? "分钟" : "min"} ↗︎</Link>{action === "question" && <button className="outline-button" onClick={() => { setGuide(previous => ({ ...previous, draft: (zh ? `关于《${record.title}》，有哪些经审核的资料？` : `What reviewed evidence is available about ${record.title}?`).slice(0, 2000) })); document.getElementById("guide-question")?.focus(); }}>{zh ? "起草相关问题" : "Draft a related question"}</button>}</li>)}</ul>}
    <Link className="text-button" href="/explore">{zh ? "浏览全部辽宁馆藏" : "Browse all Liaoning"} ↗︎</Link>
  </section>;
}
