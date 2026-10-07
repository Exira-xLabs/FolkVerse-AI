"use client";
import { useEffect, useState } from "react";
import { api, type GuideEvidence } from "@folkverse/contracts";
import { SourceDrawer } from "./museum-ui";
import { useLocale } from "./locale-provider";

export function GuideSourceInspector({ evidence, onClose, onInvalid }: { evidence: GuideEvidence[] | null; onClose: () => void; onInvalid?: (evidence: GuideEvidence[]) => void }) {
  const { locale } = useLocale(); const zh = locale !== "en";
  const [checked, setChecked] = useState<{ evidence: GuideEvidence[]; current: boolean } | null>(null);
  useEffect(() => {
    if (!evidence) return;
    const controller = new AbortController();
    let checking = false;
    const revalidate = async () => {
      if (checking) return;
      checking = true;
      try {
        const results = await Promise.all(evidence.map(async p => {
          if (p.evidence_origin === "official_lookup" || p.evidence_origin === "reviewed_unit") {
            const result = await api.GET("/api/v1/guide/evidence/{identifier}", { params: { path: { identifier: p.passage_id } }, cache: "no-store", signal: controller.signal });
            const current = result.data?.passage;
            return !!result.data?.current && !!current && current.content_hash === p.content_hash && current.text === p.text && current.canonical_url === p.canonical_url && current.rights_basis === p.rights_basis && current.review_id === p.review_id && current.language === p.language && current.classification === p.classification;
          }
          const result = await api.GET("/api/v1/sources/{identifier}", { params: { path: { identifier: p.source_id } }, cache: "no-store", signal: controller.signal });
          return !!result.data && result.data.canonical_url === p.canonical_url && result.data.title === p.source_title && result.data.institution === p.institution && result.data.passages.some(current => current.id === p.passage_id && current.text === p.text && current.language === p.language && current.locator === p.locator && current.rights_basis === p.rights_basis && current.review.reviewer === p.reviewer && current.review.reviewed_at === p.reviewed_at);
        }));
        if (!controller.signal.aborted) { setChecked({ evidence, current: results.every(Boolean) }); if (!results.every(Boolean)) onInvalid?.(evidence); }
      } catch { if (!controller.signal.aborted) { setChecked({ evidence, current: false }); onInvalid?.(evidence); } }
      finally { checking = false; }
    };
    void revalidate();
    const interval = setInterval(() => void revalidate(), 15000);
    window.addEventListener("focus", revalidate);
    return () => { clearInterval(interval); window.removeEventListener("focus", revalidate); controller.abort(); };
  }, [evidence, onInvalid]);
  const ready = checked?.evidence === evidence;
  return <SourceDrawer open={!!evidence} onClose={onClose} title={zh ? "回答所依据的资料" : "Evidence behind this answer"}>
    {!ready ? <p role="status">{zh ? "正在检查来源是否仍可用…" : "Checking current source availability…"}</p> : !checked?.current ? <p role="alert">{zh ? "来源已改变、撤回或暂时不可用。请重新提问以检查最新证据。" : "The evidence changed, was withdrawn or is currently unavailable. Ask again to check current evidence."}</p> : evidence?.map(p => {
      let href: string | undefined;
      try { const url = new URL(p.canonical_url); if (["https:", "http:"].includes(url.protocol) && !url.username && !url.password) href = url.href; } catch { /* Unusable URL remains plain text. */ }
      return <article className="source-record" key={p.passage_id}><p className="eyebrow">{p.institution}</p><h3>{p.source_title}</h3><p className="fine-print">{({ source_statement: zh ? "来源记述" : "Source statement", history: zh ? "历史证据" : "Historical evidence", interpretation: zh ? "解释观点" : "Interpretation", folklore: zh ? "民间传说或信仰" : "Folklore or belief", creative_adaptation: zh ? "创作改编" : "Creative adaptation" })[p.classification ?? "source_statement"]}</p><blockquote lang={p.language}><p>{p.text}</p><small>{p.locator}</small></blockquote><p>{p.rights_basis}</p><p>{p.evidence_origin === "official_lookup" ? (p.review_id === "machine_source_assessed_v1" ? (zh ? "Codex 已比对原始来源与中英文摘要；未经人工审核。" : "Codex compared the original source and bilingual summary; no human review.") : (zh ? "官方页面在线查询，尚无编辑审核。" : "Official page lookup; editorial review is pending.")) : <>{zh ? "编辑审核" : "Editorial review"}: {p.reviewer} · {p.reviewed_at && new Date(p.reviewed_at).toLocaleDateString(locale, { timeZone: "Asia/Shanghai" })}</>}</p><p>{zh ? "获取时间" : "Fetched"}: {new Date(p.fetched_at).toLocaleString(locale, { timeZone: "Asia/Shanghai" })}</p>{href && <a href={href} target="_blank" rel="noopener noreferrer">{zh ? "打开原始来源" : "Open original source"}</a>}</article>;
    })}
  </SourceDrawer>;
}
