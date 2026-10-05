"use client";

import Link from "next/link";
import { useCallback, useEffect, useState, type ReactNode } from "react";
import { api, type ExhibitDetail, type ExhibitPage, type RegionList, type SourceCard, type SourceList } from "@folkverse/contracts";
import { useLocale } from "./locale-provider";
import { LiaoningAtlas, atlasCities } from "./liaoning-atlas";
import { GlassPanel, GoldButton, SourceDrawer } from "./museum-ui";
import { useVisit } from "./visit-provider";
import { MuseumSelect } from "./museum-select";

const themeNames: Record<string, [string, string]> = { performance: ["Performance", "表演"], craft: ["Craft", "工艺"], music: ["Music", "音乐"], custom: ["Customs", "民俗"], learning: ["Learning", "学习"], food: ["Food", "饮食"] };

function SourceRecord({ source }: { source: SourceCard }) {
  const { locale } = useLocale(); const zh = locale !== "en";
  return <article id={`source-${source.id}`} className="source-record"><p className="eyebrow">{source.institution}</p><h3>{source.title}</h3>
    <p>{source.rights_basis}</p><dl><div><dt>{zh ? "资料获取时间" : "Retrieved"}</dt><dd>{new Date(source.fetched_at).toLocaleDateString(locale)}</dd></div><div><dt>{zh ? "编辑审核" : "Editorial review"}</dt><dd>{source.review.reviewer} · {new Date(source.review.reviewed_at).toLocaleDateString(locale)}</dd></div></dl>
    {source.passages.filter(p => p.language === locale).map(p => <blockquote key={p.id}><p>{p.text}</p><small>{p.locator} · {p.rights_basis}</small></blockquote>)}
    {source.canonical_url.startsWith("https://") && <a className="outline-button" href={source.canonical_url} target="_blank" rel="noopener noreferrer">{zh ? "查看机构来源" : "Visit institutional source"} ↗︎</a>}
    <details><summary>{zh ? "记录完整性" : "Record integrity"}</summary><code>{source.raw_hash}</code><p>{source.review.notes}</p></details>
  </article>;
}

export function CatalogExperience({ page, mode, fixture, initialExhibitId }: { page: "explore" | "sources"; mode: "demo" | "live"; fixture: ReactNode; initialExhibitId?: string }) {
  const { locale } = useLocale(); const zh = locale !== "en";
  const [preview, setPreview] = useState(false);
  const { catalog, setCatalog } = useVisit(); const { query, region, theme, view } = catalog;
  const setQuery = (query: string) => setCatalog(previous => ({ ...previous, query }));
  const setRegion = (region: string) => setCatalog(previous => ({ ...previous, region }));
  const setTheme = (theme: string) => setCatalog(previous => ({ ...previous, theme }));
  const setView = (view: "collection" | "map") => setCatalog(previous => ({ ...previous, view }));
  const clearFilters = () => { setCatalog(previous => ({ ...previous, query: "", region: "", theme: "" })); setCursor(undefined); };
  const [regions, setRegions] = useState<RegionList["items"]>([]); const [exhibits, setExhibits] = useState<ExhibitPage | null>(null); const [sources, setSources] = useState<SourceList["items"]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading"); const [reload, setReload] = useState(0); const [cursor, setCursor] = useState<string | undefined>();
  const [selection, setSelection] = useState<{ kind: "exhibit" | "source"; id: string } | null>(() => initialExhibitId ? { kind: "exhibit", id: initialExhibitId } : null);
  const [detail, setDetail] = useState<ExhibitDetail | SourceCard | null>(null); const [detailError, setDetailError] = useState(false);
  const refresh = useCallback(() => setReload(n => n + 1), [setReload]);
  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setState("loading");
      try {
        if (page === "explore") {
          const [r, e] = await Promise.all([
            api.GET("/api/v1/regions", { params: { query: { locale } }, signal: controller.signal, cache: "no-store" }),
            api.GET("/api/v1/exhibits", { params: { query: { locale, q: query, region_id: region || "liaoning", themes: theme || undefined, cursor, limit: 12 } }, signal: controller.signal, cache: "no-store" }),
          ]);
          if (!r.data || !e.data) throw new Error();
          setRegions(r.data.items); setExhibits(e.data);
        } else {
          const result = await api.GET("/api/v1/sources", { signal: controller.signal, cache: "no-store" });
          if (!result.data) throw new Error(); setSources(result.data.items);
        }
        setState("ready");
      } catch { if (!controller.signal.aborted) { setState("error"); setExhibits(null); setSources([]); } }
    }, 150);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [page, locale, query, region, theme, cursor, reload]);
  useEffect(() => {
    if (!selection) return;
    const controller = new AbortController();
    const load = async () => {
      try {
        const result = selection.kind === "exhibit"
          ? await api.GET("/api/v1/exhibits/{identifier}", { params: { path: { identifier: selection.id }, query: { locale } }, signal: controller.signal, cache: "no-store" })
          : await api.GET("/api/v1/sources/{identifier}", { params: { path: { identifier: selection.id } }, signal: controller.signal, cache: "no-store" });
        if (!result.data) throw new Error();
        if (!controller.signal.aborted) { setDetail(result.data); setDetailError(false); }
      } catch { if (!controller.signal.aborted) { setDetail(null); setDetailError(true); } }
    };
    void load(); return () => controller.abort();
  }, [selection, locale, reload]);
  // Revalidate visible records on focus and periodically: withdrawal must not leave a stale drawer.
  useEffect(() => {
    window.addEventListener("focus", refresh); const timer = setInterval(refresh, 15000);
    return () => { window.removeEventListener("focus", refresh); clearInterval(timer); };
  }, [refresh]);
  const open = (kind: "exhibit" | "source", id: string) => { setDetail(null); setDetailError(false); setSelection({ kind, id }); };
  const title = detail?.title ?? (detailError ? (zh ? "记录已不可用" : "Record no longer available") : (zh ? "正在加载展览…" : "Loading collection record…"));
  return <div className="collection-experience"><div className="collection-mode" aria-label={zh ? "馆藏模式" : "Collection mode"}>
    <button className={`theme-chip ${!preview ? "selected" : ""}`} aria-pressed={!preview} onClick={() => setPreview(false)}>{zh ? "已发布馆藏" : "Published collection"}</button>
    {mode === "demo" && <button className={`theme-chip ${preview ? "selected" : ""}`} aria-pressed={preview} onClick={() => setPreview(true)}>{zh ? "预览示例体验" : "Preview examples"}</button>}
  </div>{preview ? fixture : <>
    {page === "explore" && <><div className="collection-view-switch" aria-label={zh ? "探索方式" : "Explore view"}>
      <button className={`theme-chip ${view === "collection" ? "selected" : ""}`} aria-pressed={view === "collection"} onClick={() => setView("collection")}>{zh ? "浏览馆藏" : "Browse collection"}</button>
      <button className={`theme-chip ${view === "map" ? "selected" : ""}`} aria-pressed={view === "map"} onClick={() => setView("map")}>{zh ? "探索地图" : "Explore map"}</button>
    </div><div hidden={view !== "map"}><LiaoningAtlas selectedId={region} onSelect={id => { setRegion(id); setCursor(undefined); }} availableIds={regions.map(r => r.id)} availability={state} /></div></>}
    {page === "explore" && <div className="active-filters" aria-label={zh ? "当前筛选" : "Active filters"}><strong>{zh ? "当前筛选：" : "Showing:"}</strong><span>{atlasCities.find(city => city.id === region)?.names[locale] ?? (zh ? "辽宁全省" : "All Liaoning")}</span>{query && <span>{zh ? "搜索" : "Search"}: {query}</span>}{theme && <span>{themeNames[theme]?.[zh ? 1 : 0] ?? theme}</span>}<button className="outline-button" disabled={!query && !region && !theme} onClick={clearFilters}>{zh ? "清除筛选" : "Clear filters"}</button>{region && <button className="outline-button" onClick={() => { setRegion(""); setCursor(undefined); }}>{zh ? "返回辽宁全省" : "Return to all Liaoning"}</button>}<p className="fine-print">{zh ? "城市、视图与筛选仅在本次访问中保留；刷新后清除。重新进入时地图以所选城市为中心。" : "City, view and filters stay during this visit; reload clears them. Reopening the map fits the selected city."}</p></div>}
    <div className="collection-layout">
<GlassPanel className="collection-results" id={page === "explore" ? "liaoning-city-collection" : undefined}><div className="panel-heading"><h2>{page === "explore" && region.startsWith("liaoning-") ? atlasCities.find(c => c.id === region)?.names[locale] : zh ? "馆藏中的相遇" : "Meet the collection"}</h2><span className="demo-tag">{zh ? "人工编辑审核" : "Human editorial review"}</span></div>
      {state === "loading" && <p role="status" className="empty-state">{zh ? "正在加载馆藏…" : "Loading the collection…"}</p>}
      {state === "error" && <div role="alert" className="empty-state"><p>{zh ? "暂时无法读取馆藏，请重试。" : "The collection is temporarily unavailable. Please try again."}</p><GoldButton onClick={refresh}>{zh ? "重试" : "Try again"}</GoldButton></div>}
      {(state === "ready" || (state === "loading" && (page === "explore" ? exhibits !== null : sources.length > 0))) && (page === "explore" ? <><p className="fine-print" aria-live="polite">{exhibits?.total ?? 0} {zh ? "个已发布展览" : exhibits?.total === 1 ? "published exhibit" : "published exhibits"}</p>{!exhibits?.items.length && <div className="empty-state"><p>{zh ? "暂无符合筛选条件的已发布展览。" : "No published exhibits match these filters."}</p><button className="outline-button" onClick={clearFilters}>{zh ? "清除筛选并浏览辽宁" : "Clear filters and browse Liaoning"}</button>{region.startsWith("liaoning-") && <p className="city-review-note">{zh ? "这座城市已纳入辽宁图鉴。文化资料需完成审核后才会发布。" : "This city is part of the Liaoning atlas. Cultural records appear after editorial review."}</p>}</div>}
        <div className="published-cards">{exhibits?.items.map(e => <button className="published-card" key={e.id} onClick={() => open("exhibit", e.id)}><span className="eyebrow">{e.estimated_minutes} {zh ? "分钟 · 已审核" : "MIN · REVIEWED"}</span><h3>{e.title}</h3><p>{e.summary}</p><span className="text-button">{zh ? "打开展览与来源" : "Open exhibit & sources"} ↗︎</span></button>)}</div>
        <div className="compact-actions">{cursor && <button className="outline-button" onClick={() => setCursor(undefined)}>{zh ? "返回首页" : "First page"}</button>}{exhibits?.next_cursor && <button className="outline-button" onClick={() => setCursor(exhibits.next_cursor ?? undefined)}>{zh ? "下一页" : "Next page"}</button>}</div></> : <><p className="fine-print">{sources.length} {zh ? "条已发布来源" : sources.length === 1 ? "published source" : "published sources"}</p>{!sources.length && <p className="empty-state">{zh ? "尚无已发布来源。" : "No reviewed sources have been published yet."}</p>}<div className="published-cards">{sources.map(s => <button className="published-card" key={s.id} onClick={() => open("source", s.id)}><span className="eyebrow">{s.institution}</span><h3>{s.title}</h3><span className="text-button">{zh ? "查看来源记录" : "Inspect source record"} ↗︎</span></button>)}</div></>)}
    </GlassPanel>
    <GlassPanel className="collection-controls"><p className="eyebrow">{zh ? "循着来源探索" : "FOLLOW THE EVIDENCE"}</p><h2>{page === "explore" ? (zh ? "走进辽宁" : "Discover Liaoning") : (zh ? "出处与记录" : "Sources, in the open")}</h2>
      {page === "explore" && <><label className="field"><span>{zh ? "搜索已发布展览" : "Search published exhibits"}</span><input type="search" maxLength={200} value={query} onChange={e => { setQuery(e.target.value); setCursor(undefined); }} placeholder={zh ? "光影、工艺、传承…" : "Light, craft, heritage…"} /></label>
        <MuseumSelect label={zh ? "地区" : "Region"} value={region} onChange={value => { setRegion(value); setCursor(undefined); }} options={[{ value: "", label: zh ? "辽宁全省" : "All Liaoning" }, ...atlasCities.map(r => ({ value: r.id, label: r.names[locale] }))]} />
        <MuseumSelect label={zh ? "主题" : "Theme"} value={theme} onChange={value => { setTheme(value); setCursor(undefined); }} options={[{ value: "", label: zh ? "所有主题" : "All themes" }, ...[["performance", "Performance", "表演"], ["craft", "Craft", "工艺"], ["music", "Music", "音乐"], ["custom", "Customs", "民俗"], ["learning", "Learning", "学习"]].map(([value, en, cn]) => ({ value, label: zh ? cn : en }))]} /></>}
      <p className="fine-print">{page === "explore" ? (zh ? "全省14个地级市是馆藏采集范围。选择城市，查看已有审核展览。" : "Select a city to explore reviewed exhibits across Liaoning’s 14 cities.") : (zh ? "浏览已发布来源记录，打开记录查看获准摘录、机构署名、编辑审核与使用权限。" : "Browse published source records. Open a record to read permitted excerpts, institution attribution, editorial review and rights.")}</p>
      <button className="text-button" onClick={refresh}>{zh ? "刷新馆藏" : "Refresh collection"} ↻</button>
    </GlassPanel></div></>}
    <SourceDrawer open={selection !== null} title={title} onClose={() => setSelection(null)}>{detailError ? <div><p role="alert">{zh ? "此记录已撤回或暂时无法访问。请关闭并刷新馆藏。" : "This record was withdrawn or cannot currently be reached. Close this drawer and refresh the collection."}</p><button className="outline-button" onClick={refresh}>{zh ? "重试记录" : "Retry record"}</button><button className="outline-button" onClick={() => { setSelection(null); setView("collection"); }}>{zh ? "返回馆藏" : "Back to collection"}</button></div> : detail ? <>{"summary" in detail && <><section className="exhibit-reading" aria-label={zh ? "展览阅读" : "Exhibit reading"}><span className="demo-tag">{zh ? "已发布展览" : "Published exhibit"}</span><h3>{zh ? "关于此展览" : "About this exhibit"}</h3><dl><div><dt>{zh ? "城市" : "City"}</dt><dd>{detail.region_ids.map(id => atlasCities.find(city => city.id === id)?.names[locale]).filter(Boolean).join(" · ") || (zh ? "辽宁" : "Liaoning")}</dd></div><div><dt>{zh ? "主题" : "Themes"}</dt><dd>{detail.themes.map(theme => themeNames[theme]?.[zh ? 1 : 0] ?? theme).join(" · ")}</dd></div></dl><p>{detail.summary}</p><nav aria-label={zh ? "展览引用" : "Exhibit citations"}>{detail.sources.map((source, index) => <a key={source.id} className="source-pill" href={`#source-${source.id}`}>[{index + 1}] {source.institution}</a>)}</nav><div className="compact-actions"><button className="outline-button" onClick={() => { setSelection(null); setView("collection"); }}>{zh ? "返回馆藏" : "Back to collection"}</button><a className="outline-button" href={`/explore?exhibit=${encodeURIComponent(detail.id)}`}>{zh ? "此展览的分享链接" : "Shareable exhibit link"}</a></div></section><p className="fine-print">{zh ? "审核人" : "Reviewed by"}: {detail.review.reviewer}</p><nav className="exhibit-next" aria-label={zh ? "继续探索此展览" : "Continue with this exhibit"}>{[["/guide", "Ask about this exhibit", "询问此展览"], ["/journey", "Learn from this exhibit", "从此展览开始学习"], ["/stories/lantern-path", "Explore story options", "探索故事选项"], ["/dna", "Explore interests", "探索兴趣"]].map(([href, en, cn]) => <Link className="outline-button" key={href} href={`${href}?exhibit=${encodeURIComponent(detail.id)}`}>{zh ? cn : en} ↗︎</Link>)}</nav><p className="fine-print">{zh ? "展览上下文会随链接保留；AI 问答、个性化路线与故事生成尚未连接。" : "These links carry the exhibit context. AI answers, personalized routes and story generation are not connected."}</p></>}<section className="exhibit-evidence" aria-label={zh ? "来源证据" : "Source evidence"}><h3>{zh ? "来源与证据" : "Sources & evidence"}</h3>{("sources" in detail ? detail.sources : [detail]).map(s => <SourceRecord key={s.id} source={s} />)}</section></> : <p role="status">{zh ? "正在读取审核记录…" : "Reading the reviewed record…"}</p>}</SourceDrawer>
  </div>;
}
