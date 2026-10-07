"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type ExhibitDetail } from "@folkverse/contracts";
import { useLocale } from "./locale-provider";
import { useVisit } from "./visit-provider";
import type { PageKey } from "@/lib/routes";
export function ExhibitContext({ page, identifier, canDraft = false }: { page: PageKey; identifier?: string; canDraft?: boolean }) {
  const { locale } = useLocale(); const zh = locale !== "en"; const { setGuide } = useVisit();
  const [record, setRecord] = useState<{ id: string; locale: string; data: ExhibitDetail | null } | null>(null);
  const [reload, setReload] = useState(0);
  useEffect(() => {
    if (!identifier) return;
    const controller = new AbortController();
    let latest = 0;
    const load = async () => {
      const request = ++latest;
      try { const result = await api.GET("/api/v1/exhibits/{identifier}", { params: { path: { identifier }, query: { locale } }, cache: "no-store", signal: controller.signal });
        if (!controller.signal.aborted && request === latest) setRecord({ id: identifier, locale, data: result.data ?? null });
      } catch { if (!controller.signal.aborted && request === latest) setRecord({ id: identifier, locale, data: null }); }
    }; void load();
    const refresh = () => void load(); window.addEventListener("focus", refresh); const timer = setInterval(refresh, 15000);
    return () => { controller.abort(); clearInterval(timer); window.removeEventListener("focus", refresh); };
  }, [identifier, locale, reload]);
  if (!identifier) return null;
  const loaded = record?.id === identifier && record.locale === locale;
  const data = loaded ? record.data : null;
  return <section className="exhibit-context glass-panel" aria-label={zh ? "展览上下文" : "Exhibit context"}><p className="eyebrow">{zh ? "继续探索" : "CONTINUE EXPLORING"}</p>
    {!loaded ? <p role="status">{zh ? "正在检查展览…" : "Checking exhibit…"}</p> : !data ? <><p role="alert">{zh ? "展览已撤回或暂时不可用。" : "The exhibit was withdrawn or is currently unavailable."}</p><button className="outline-button" onClick={() => setReload(n => n + 1)}>{zh ? "重试" : "Try again"}</button></> : <><h2>{data.title}</h2><p>{data.summary}</p><p className="fine-print">{data.estimated_minutes} {zh ? "分钟 · 已审核展览" : "min · reviewed exhibit"}</p>
      <Link className="outline-button" href={`/explore?exhibit=${encodeURIComponent(identifier)}`}>{zh ? "返回展览与来源" : "Return to exhibit & sources"} ↗︎</Link>
      {page === "guide" && canDraft && <button className="gold-button" onClick={() => {
        setGuide(previous => ({ ...previous, draft: (zh ? `关于《${data.title}》，有哪些经审核的资料？` : `What reviewed evidence is available about ${data.title}?`).slice(0, 2000) }));
        const preview = document.querySelector<HTMLDetailsElement>(".optional-preview");
        if (preview) preview.open = true;
        requestAnimationFrame(() => document.querySelector<HTMLTextAreaElement>("#guide-question")?.focus());
      }}>{zh ? "以此展览起草问题" : "Draft a question about this exhibit"}</button>}
    </>}
    <p className="fine-print">{page === "guide" ? (canDraft ? (zh ? "此处保留您选择的展览。预设对话示例不会基于此记录生成真实回答。" : "Your selected exhibit stays in context. Scripted conversation examples do not generate real answers from this record.") : (zh ? "向锦瑶提问时会携带此展览编号；仅在资料仍符合条件时使用，不会自动发送问题。" : "Questions to Jinyao carry this exhibit ID and use it only while its evidence remains eligible. No question is sent automatically.")) : page === "journey" ? (zh ? "生成路线时会请求以此展览为起点；仅在仍符合条件及时长限制时加入。每站的向导链接会保留展览上下文。" : "Creating a route requests this exhibit as its starting stop, only if it remains eligible and fits the time limit. Each stop’s guide link preserves exhibit context.") : page === "stories" ? (zh ? "故事生成尚未连接。下方原创虚构故事是独立示例，并非此展览的文化改编。" : "Story generation is not connected. The original fictional story below is a separate example, not an adaptation of this exhibit.") : (zh ? "此展览是探索的起点；不会自动改变您的兴趣。推荐 API 尚未连接。" : "Use this exhibit as a starting point; it does not automatically change your interests. The recommendation API is not connected.")}</p>
  </section>;
}
