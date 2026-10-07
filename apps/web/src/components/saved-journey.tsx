"use client";

import Link from "next/link";
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { api, type JourneyResponse } from "@folkverse/contracts";
import { useLocale } from "./locale-provider";
import { useVisit } from "./visit-provider";
import { GlassPanel, GoldButton, ThemeChip } from "./museum-ui";
import { MuseumSelect } from "./museum-select";
import { atlasCities } from "./liaoning-atlas";

const themes = [["craft", "Craft", "工艺"], ["custom", "Customs", "民俗"], ["music", "Music", "音乐"], ["performance", "Performance", "表演"], ["learning", "Learning", "学习"]];

let sessionFlight: Promise<string> | null = null;
async function visitorSession(): Promise<string> {
  if (!sessionFlight) {
    const create = async () => {
      // POST is idempotent for a valid cookie; serialize bootstrap across tabs where supported.
      const response = await api.POST("/api/v1/session", { signal: AbortSignal.timeout(10000) });
      if (!response.data) throw new Error("service");
      return response.data.session_id;
    };
    sessionFlight = (async () => navigator.locks
      ? await navigator.locks.request("folkverse-visitor-session", create)
      : await create())().finally(() => { sessionFlight = null; });
  }
  return sessionFlight;
}

export function SavedJourney({ initialExhibitId }: { initialExhibitId?: string }) {
  const { locale } = useLocale(); const zh = locale !== "en";
  const c = (en: string, cn: string) => zh ? cn : en;
  const { catalog } = useVisit();
  const [duration, setDuration] = useState(20);
  const [interests, setInterests] = useState<string[]>([]);
  const [region, setRegion] = useState(() => catalog.region || "liaoning");
  const [novelty, setNovelty] = useState(false);
  const [savedRoute, setRoute] = useState<JourneyResponse | null>(null);
  const route = savedRoute?.locale === locale ? savedRoute : null;
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<"service" | "session" | "stale" | null>(null);
  const [refresh, setRefresh] = useState(0);
  const operation = useRef(0); const applying = useRef(false);
  const activeId = useRef<string | null>(null); const initialized = useRef(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const stopList = useRef<HTMLOListElement>(null);
  const recovery = useRef<HTMLButtonElement>(null);
  const pendingFocus = useRef<{ kind: "stop"; id?: string } | { kind: "error" } | null>(null);
  useLayoutEffect(() => {
    if (busy || !pendingFocus.current) return;
    const target = pendingFocus.current;
    pendingFocus.current = null;
    if (target.kind === "error") { recovery.current?.focus({ preventScroll: true }); return; }
    const item = [...(stopList.current?.children ?? [])].find(node => (node as HTMLElement).dataset.exhibitId === target.id);
    const control = item?.querySelector<HTMLButtonElement>("button:not(:disabled)");
    if (control) control.focus({ preventScroll: true }); else heading.current?.focus({ preventScroll: true });
  }, [busy, savedRoute, error]);
  const sessionId = useRef<string | null>(null);
  const currentLocale = useRef(locale);
  useEffect(() => { currentLocale.current = locale; }, [locale]);
  const mounted = useRef(true);
  const [sessionReset, setSessionReset] = useState(false);
  useEffect(() => { mounted.current = true; return () => { mounted.current = false; }; }, []);

  const ensureSession = useCallback(async () => {
    const id = await visitorSession();
    if (sessionId.current && sessionId.current !== id) { activeId.current = null; setSessionReset(true); }
    sessionId.current = id;
  }, []);

  useEffect(() => {
    const controller = new AbortController(); let latest = 0;
    const load = async () => {
      if (applying.current) return;
      const request = ++latest; const generation = operation.current;
      try {
        await ensureSession();
        if (controller.signal.aborted) return;
        let result = activeId.current
          ? await api.GET("/api/v1/journeys/{identifier}", { params: { path: { identifier: activeId.current }, query: { locale } }, cache: "no-store", signal: controller.signal })
          : await api.GET("/api/v1/journeys", { params: { query: { locale } }, cache: "no-store", signal: controller.signal });
        if (!result.data && activeId.current && [403, 404].includes(result.response.status)) {
          activeId.current = null; setSessionReset(true);
          result = await api.GET("/api/v1/journeys", { params: { query: { locale } }, cache: "no-store", signal: controller.signal });
        }
        if (!result.data) throw new Error(result.response.status === 401 ? "session" : "service");
        if (controller.signal.aborted || request !== latest || generation !== operation.current || applying.current) return;
        const data = "items" in result.data ? result.data.items[0] ?? null : result.data;
        activeId.current = data?.id ?? null; setRoute(data); setState("ready"); setError(null);
        if (!initialized.current) {
          initialized.current = true;
          if (data) { setDuration(data.duration_minutes); setInterests(data.interests); if (!catalog.region) setRegion(data.region_id ?? ""); }
        }
      } catch (failure) {
        if (!controller.signal.aborted && request === latest && generation === operation.current && !applying.current) {
          // Fail closed: a withdrawn or expired route must not remain visibly authoritative.
          setRoute(null); setState("error"); setError(failure instanceof Error && failure.message === "session" ? "session" : "service");
        }
      }
    };
    void load();
    const focus = () => void load(); window.addEventListener("focus", focus);
    const timer = setInterval(focus, 15000);
    return () => { controller.abort(); window.removeEventListener("focus", focus); clearInterval(timer); };
  }, [locale, refresh, ensureSession, catalog.region]);

  const generate = async () => {
    if (applying.current) return;
    applying.current = true; const generation = ++operation.current; setBusy(true); setError(null);
    try {
      await ensureSession();
      const result = await api.POST("/api/v1/journeys", { body: {
        locale, interests, duration_minutes: duration, region_id: region || null,
        novelty_exhibit_ids: novelty ? route?.stops.map(stop => stop.exhibit_id) ?? [] : [],
        start_exhibit_id: initialExhibitId ?? null,
      } });
      if (!result.data) throw new Error(result.response.status === 401 ? "session" : "service");
      if (generation === operation.current && mounted.current) {
        activeId.current = result.data.id; setState("ready"); setSessionReset(false);
        if (currentLocale.current === locale) { setRoute(result.data); heading.current?.focus(); }
        else setRefresh(value => value + 1);
      }
    } catch (failure) {
      if (generation === operation.current && mounted.current) setError(failure instanceof Error && failure.message === "session" ? "session" : "service");
    } finally { if (generation === operation.current && mounted.current) { applying.current = false; setBusy(false); } }
  };

  const edit = async (ids: string[], focusId?: string) => {
    if (!route || applying.current) return;
    const previous = route;
    applying.current = true; const generation = ++operation.current; setBusy(true); setError(null);
    const stops = ids.map(id => previous.stops.find(stop => stop.exhibit_id === id)!);
    // Keep focus somewhere stable while an optimistic removal unmounts its activating button.
    heading.current?.focus({ preventScroll: true });
    setRoute({ ...previous, stops, total_minutes: stops.reduce((sum, stop) => sum + stop.estimated_minutes, 0) });
    try {
      const result = await api.PATCH("/api/v1/journeys/{identifier}", { params: { path: { identifier: previous.id }, query: { locale } }, body: { ordered_exhibit_ids: ids, expected_version: previous.version } });
      if (!result.data) throw new Error(result.response.status === 401 ? "session" : result.response.status === 409 ? "stale" : "service");
      if (generation === operation.current && mounted.current) {
        if (currentLocale.current === locale) {
          // Focus after the saved DOM and enabled controls commit, not on a racy animation frame.
          pendingFocus.current = { kind: "stop", id: focusId };
          setRoute(result.data);
        } else setRefresh(value => value + 1);
      }
    } catch (failure) {
      if (generation === operation.current && mounted.current) {
        pendingFocus.current = { kind: "error" };
        setRoute(null); setState("error");
        setError(failure instanceof Error && failure.message === "session" ? "session" : failure instanceof Error && failure.message === "stale" ? "stale" : "service");
      }
    } finally { if (generation === operation.current && mounted.current) { applying.current = false; setBusy(false); } }
  };
  const move = (index: number, direction: number) => {
    if (!route) return;
    const ids = route.stops.map(stop => stop.exhibit_id);
    [ids[index], ids[index + direction]] = [ids[index + direction], ids[index]];
    void edit(ids, route.stops[index].exhibit_id);
  };
  const dirty = route && (route.duration_minutes !== duration || (route.region_id ?? "") !== region || [...route.interests].sort().join(",") !== [...interests].sort().join(","));
  return <section className="saved-journey" aria-label={c("Saved learning journey", "已保存学习路线")}>
    <div className="journey-controls saved-journey-controls"><fieldset disabled={busy} className="saved-interests"><legend>{c("Learning interests", "学习兴趣")}</legend><div className="theme-grid">{themes.map(([id, en, cn]) => <ThemeChip key={id} active={interests.includes(id)} onClick={() => setInterests(current => current.includes(id) ? current.filter(value => value !== id) : [...current, id])}>{c(en, cn)}</ThemeChip>)}</div><p className="fine-print">{c("Leave interests open to explore all eligible themes.", "不选择兴趣即可探索所有符合条件的主题。")}</p></fieldset>
      <MuseumSelect compact label={c("Learning time", "学习时长")} value={String(duration)} onChange={value => setDuration(Number(value))} options={[5, 10, 20, 30, 45, 60].map(value => ({ value: String(value), label: `${value} ${c("minutes", "分钟")}` }))} />
      <MuseumSelect compact label={c("Learning region", "学习地区")} value={region} onChange={setRegion} options={[{ value: "", label: c("All published regions", "所有已发布地区") }, { value: "liaoning", label: c("All Liaoning", "辽宁全省") }, ...atlasCities.map(city => ({ value: city.id, label: city.names[locale] }))]} />
      <label className="saved-novelty"><input type="checkbox" checked={novelty} disabled={busy} onChange={event => setNovelty(event.target.checked)} />{c("Prefer different stops from this route", "优先选择不同于当前路线的展览")}</label>
      <GoldButton disabled={busy || state === "loading"} onClick={() => void generate()}>{busy ? c("Saving route…", "正在保存路线…") : route ? c("Apply — Regenerate & save", "应用 — 重新生成并保存") : c("Create & save my journey", "生成并保存学习路线")} ↗︎</GoldButton>
    </div>
    <GlassPanel className="saved-journey-route"><div className="panel-heading"><h2 ref={heading} tabIndex={-1}>{c("Your saved discoveries", "您保存的文化发现")}</h2><span className="demo-tag" aria-live="polite">{route ? `${route.stops.length} ${c("stops", "站")} · ${route.total_minutes} / ${route.duration_minutes} ${c("min", "分钟")}` : c("Published exhibits only", "仅限已发布展览")}</span></div>
      <p className="fine-print">{c("A digital learning route, not physical travel directions. Only published exhibit IDs and stored learning estimates are used. Decorative regional examples do not expand this collection.", "这是数字学习路线，并非实际旅行导航。仅使用已发布展览编号及存储的学习时长。装饰性地区示例不会扩大馆藏范围。")}</p>
      <p className="fine-print">{c("The latest route is restored on reload and is readable only while your signed visitor session remains valid. Deleting the session deletes its routes. Only preferences you explicitly choose are used; no passive tracking.", "刷新后会恢复最新路线，仅在签名访客会话有效期间可读取。删除会话将删除其路线。仅使用您主动选择的偏好，不进行被动追踪。")}</p>
      {initialExhibitId && <p className="fine-print">{c("Your selected exhibit is requested as the starting stop only if it remains eligible and fits your criteria and time.", "仅当所选展览仍符合条件、偏好及时间限制时，才会作为起点。")}</p>}
      {(state === "loading" || (savedRoute && !route)) && <p role="status">{c("Checking your saved journey…", "正在检查已保存路线…")}</p>}
      {error && <div role="alert" className="empty-state"><p>{error === "session" ? c("Your visitor session expired. Reload your saved routes or create a new journey.", "访客会话已过期。请重新读取保存路线，或创建新路线。") : error === "stale" ? c("The route changed or a stop is no longer published. Reload before editing again.", "路线已变化，或某个展览已撤回。请重新读取后再编辑。") : c("The route could not be saved or checked. No success is claimed; reload to see the database state.", "路线无法保存或验证。此次操作未显示为成功；请重新读取数据库状态。")}</p><button ref={recovery} className="outline-button" disabled={busy} onClick={() => { activeId.current = null; setRefresh(value => value + 1); }}>{c("Reload saved journey", "重新读取保存路线")}</button></div>}
      {dirty && <p role="status" className="saved-journey-draft">{c("Draft preferences changed. Apply to create a new saved route; this route’s saved time budget remains unchanged.", "草稿偏好已修改。应用后将创建新的保存路线；当前路线的时间预算尚未改变。")}</p>}
      {sessionReset && <p role="status">{c("The previous visitor session or route is no longer available. Only journeys owned by the current session are shown.", "此前的访客会话或路线已不可用。这里只显示当前会话拥有的路线。")}</p>}
      {route?.notice && <p role="status" className="saved-journey-notice">{route.notice}</p>}
      {state === "ready" && !savedRoute && <div className="empty-state"><p>{c("Choose your learning time and interests, then create your first saved route.", "选择学习时长与兴趣，然后生成您的第一条保存路线。")}</p><Link className="outline-button" href="/explore">{c("Explore the published collection", "探索已发布馆藏")} ↗︎</Link></div>}
      {route && <><p className="fine-print">{route.explanation_status === "generated" ? c("AI-selected reasons from validated, application-authored options. Stops and time are selected by the application.", "AI 从经验证的应用理由选项中选择。站点与时间由应用决定。") : route.explanation_status === "unavailable" ? c("AI explanations are unavailable; these are deterministic selection reasons. Your saved route still works.", "AI 说明暂不可用；以下为确定性选择理由。保存路线仍可使用。") : c("Deterministic selection reasons; no AI-generated explanation is claimed.", "确定性选择理由，未声称生成 AI 说明。")}</p>
        {!route.stops.length && <div className="empty-state"><p>{c("This saved route currently has no stops. You may have removed them, or no published stop fits. Regenerate with more time, broader interests or another region.", "当前保存路线没有站点：可能已被您移除，或没有已发布展览符合条件。请增加时长、拓宽兴趣或更换地区后重新生成。")}</p><Link className="outline-button" href="/explore">{c("Browse available exhibits", "浏览可用展览")} ↗︎</Link></div>}
        <ol ref={stopList} className="saved-journey-stops" aria-busy={busy}>{route.stops.map((stop, index) => <li key={stop.exhibit_id} data-exhibit-id={stop.exhibit_id}><span className="stop-number">{String(index + 1).padStart(2, "0")}</span><h3>{stop.title}</h3><p>{stop.summary}</p><span className="fine-print">{stop.estimated_minutes} {c("min", "分钟")} · {stop.reason}</span><div className="compact-actions"><Link className="text-button" href={`/explore?exhibit=${encodeURIComponent(stop.exhibit_id)}`}>{c("Read exhibit", "阅读展览")} ↗︎</Link><Link className="text-button" href={`/guide?exhibit=${encodeURIComponent(stop.exhibit_id)}`}>{c("Ask Jinyao", "询问锦瑶")} ↗︎</Link></div>
          <nav className="compact-actions" aria-label={`${c("Sources for", "展览来源：")} ${stop.title}`}>{stop.sources.map(source => source.canonical_url.startsWith("https://") && <a key={source.id} className="source-pill" href={source.canonical_url} target="_blank" rel="noopener noreferrer">{source.institution} · {source.title} ↗︎</a>)}</nav>
          <div className="stop-actions"><button className="icon-button" disabled={busy || index === 0} aria-label={`${c("Move saved stop up", "上移保存站点")} ${stop.title}`} onClick={() => move(index, -1)}>↑</button><button className="icon-button" disabled={busy || index === route.stops.length - 1} aria-label={`${c("Move saved stop down", "下移保存站点")} ${stop.title}`} onClick={() => move(index, 1)}>↓</button><button className="text-button" disabled={busy} aria-label={`${c("Remove saved stop", "移除保存站点")} ${stop.title}`} onClick={() => void edit(route.stops.filter(value => value.exhibit_id !== stop.exhibit_id).map(value => value.exhibit_id), route.stops[index + 1]?.exhibit_id ?? route.stops[index - 1]?.exhibit_id)}>{c("Remove", "移除")}</button></div>
        </li>)}</ol><p className="fine-print" role="status">{busy ? c("Saving changes…", "正在保存修改…") : c("Saved to this visitor session. Publication is rechecked on reload and while this page is open.", "已保存到本访客会话。刷新及页面打开期间会重新检查发布状态。")}</p></>}
    </GlassPanel>
  </section>;
}
