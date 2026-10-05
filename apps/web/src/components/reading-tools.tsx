"use client";
import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { api, type ExhibitDetail } from "@folkverse/contracts";
import { useLocale } from "./locale-provider";
import { useReadingVisit } from "./visit-provider";

export function Bookmark({ identifier }: { identifier: string }) {
  const { locale } = useLocale(); const zh = locale !== "en"; const { reading, setReading } = useReadingVisit(); const selected = reading.saved.includes(identifier);
  return <button className="outline-button" disabled={!reading.saving || (!selected && reading.saved.length >= 50)} aria-pressed={selected} onClick={() => setReading(previous => ({ ...previous, saved: selected ? previous.saved.filter(id => id !== identifier) : [...previous.saved, identifier] }))}>{zh ? (selected ? "移除本次访问书签" : "为本次访问添加书签") : (selected ? "Remove visit bookmark" : "Bookmark for this visit")}</button>;
}

function SavedRecord({ identifier }: { identifier: string }) {
  const { locale } = useLocale(); const zh = locale !== "en"; const { setReading } = useReadingVisit();
  const [result, setResult] = useState<{ locale: string; data: ExhibitDetail | null } | null>(null); const [retry, setRetry] = useState(0);
  useEffect(() => { const controller = new AbortController(); let latest = 0;
    const load = async () => { const request = ++latest; try { const { data } = await api.GET("/api/v1/exhibits/{identifier}", { params: { path: { identifier }, query: { locale } }, cache: "no-store", signal: controller.signal }); if (!controller.signal.aborted && request === latest) setResult({ locale, data: data ?? null }); } catch { if (!controller.signal.aborted && request === latest) setResult({ locale, data: null }); } };
    void load(); const refresh = () => void load(); window.addEventListener("focus", refresh); const timer = setInterval(refresh, 15000); return () => { controller.abort(); window.removeEventListener("focus", refresh); clearInterval(timer); };
  }, [identifier, locale, retry]);
  return <li>{result?.locale !== locale ? <p role="status">{zh ? "正在检查书签…" : "Checking bookmark…"}</p> : result.data ? <Link className="outline-button" href={`/explore?exhibit=${encodeURIComponent(identifier)}`}>{result.data.title} ↗︎</Link> : <><p role="status">{zh ? "此书签暂时不可用或已撤回。" : "This bookmark is unavailable or withdrawn."}</p><button className="outline-button" onClick={() => setRetry(n => n + 1)}>{zh ? "重试书签" : "Retry bookmark"}</button></>}<button className="outline-button" onClick={() => setReading(previous => ({ ...previous, saved: previous.saved.filter(id => id !== identifier) }))}>{zh ? "移除书签" : "Remove bookmark"}</button></li>;
}

export function VisitReading({ home = false }: { home?: boolean }) {
  const { locale } = useLocale(); const zh = locale !== "en"; const { reading, setReading } = useReadingVisit();
  return <section className="glass-panel visit-reading" aria-label={zh ? "本次访问阅读" : "Visit reading"}>
    {home && reading.lastRead && <div className="compact-actions"><Link className="gold-button" href={`/explore?exhibit=${encodeURIComponent(reading.lastRead)}`}>{zh ? "继续探索" : "Continue exploring"} ↗︎</Link><button className="outline-button" onClick={() => setReading(previous => ({ ...previous, lastRead: null }))}>{zh ? "重置继续探索" : "Reset continuation"}</button></div>}
    <details><summary><span>{zh ? "本次访问书签" : "Bookmarks for this visit"}{reading.saved.length ? ` · ${reading.saved.length}` : ""}</span><svg className="bookmark-chevron" aria-hidden="true" width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="m5 7.5 5 5 5-5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" /></svg></summary><p>{zh ? "可自愿在此访问的内存中保留最多50个审核展览的编号。不会发送给服务器或写入浏览器存储；刷新或关闭后清除。关闭此选项会立即移除全部书签。" : "Optionally keep up to 50 reviewed exhibit IDs in memory for this visit. Nothing is sent to a server or written to browser storage; reload or close clears them. Turning this off removes all bookmarks immediately."}</p>
      <label className="visit-consent"><input type="checkbox" checked={reading.saving} onChange={event => setReading(previous => ({ ...previous, saving: event.target.checked, saved: event.target.checked ? previous.saved : [] }))} />{zh ? "允许本次访问内存书签" : "Enable in-memory visit bookmarks"}</label>
      {reading.saved.length ? <><ul className="saved-records">{reading.saved.map(id => <SavedRecord key={id} identifier={id} />)}</ul><button className="outline-button" onClick={() => setReading(previous => ({ ...previous, saved: [] }))}>{zh ? "清除全部书签" : "Clear all bookmarks"}</button></> : <p>{zh ? "暂无书签。启用后可在审核展览的阅读面板添加书签。" : "No bookmarks yet. Once enabled, add one from a reviewed exhibit’s reading panel."}</p>}
    </details>
  </section>;
}

export function ReadingSurface({ children }: { children: ReactNode }) {
  const { locale } = useLocale(); const zh = locale !== "en"; const [light, setLight] = useState(false); const [size, setSize] = useState("normal"); const [progress, setProgress] = useState(0); const root = useRef<HTMLDivElement>(null);
  useEffect(() => { const dialog = root.current?.closest("dialog"); if (!dialog) return; const update = () => setProgress(dialog.scrollHeight <= dialog.clientHeight ? 100 : Math.round(dialog.scrollTop / (dialog.scrollHeight - dialog.clientHeight) * 100)); update(); dialog.addEventListener("scroll", update); const observer = new ResizeObserver(update); observer.observe(dialog); if (root.current) observer.observe(root.current); return () => { dialog.removeEventListener("scroll", update); observer.disconnect(); }; }, []);
  return <div ref={root} className={`reading-surface reading-${size} ${light ? "reading-light" : ""}`}><div className="reading-toolbar" role="group" aria-label={zh ? "阅读偏好" : "Reading preferences"}><button className="outline-button" aria-pressed={light} onClick={() => setLight(!light)}>{zh ? "浅色阅读面板" : "Light reading surface"}</button><label>{zh ? "文字大小" : "Text size"}<select aria-label={zh ? "文字大小" : "Text size"} value={size} onChange={event => setSize(event.target.value)}><option value="normal">{zh ? "标准" : "Standard"}</option><option value="large">{zh ? "大" : "Large"}</option><option value="larger">{zh ? "更大" : "Larger"}</option></select></label><label className="reading-progress">{zh ? "阅读进度" : "Reading progress"}<progress max="100" value={progress} />{progress}%</label></div>{children}</div>;
}
