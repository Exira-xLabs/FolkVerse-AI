"use client";
import { useEffect, useState } from "react";
import { api, type GuideEvidence } from "@folkverse/contracts";
import { SourceDrawer } from "./museum-ui";
import { useLocale } from "./locale-provider";

export function GuideSourceInspector({ evidence, onClose }: { evidence: GuideEvidence[] | null; onClose: () => void }) {
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
          const result = await api.GET("/api/v1/sources/{identifier}", { params: { path: { identifier: p.source_id } }, cache: "no-store", signal: controller.signal });
          return !!result.data && result.data.canonical_url === p.canonical_url && result.data.title === p.source_title && result.data.institution === p.institution && result.data.passages.some(current => current.id === p.passage_id && current.text === p.text && current.language === p.language && current.locator === p.locator && current.rights_basis === p.rights_basis && current.review.reviewer === p.reviewer && current.review.reviewed_at === p.reviewed_at);
        }));
        if (!controller.signal.aborted) setChecked({ evidence, current: results.every(Boolean) });
      } catch { if (!controller.signal.aborted) setChecked({ evidence, current: false }); }
      finally { checking = false; }
    };
    void revalidate();
    const interval = setInterval(() => void revalidate(), 15000);
    window.addEventListener("focus", revalidate);
    return () => { clearInterval(interval); window.removeEventListener("focus", revalidate); controller.abort(); };
  }, [evidence]);
  const ready = checked?.evidence === evidence;
  return <SourceDrawer open={!!evidence} onClose={onClose} title={zh ? "回答所依据的资料" : "Evidence behind this answer"}>
    {!ready ? <p role="status">{zh ? "正在检查来源是否仍可用…" : "Checking current source availability…"}</p> : !checked?.current ? <p role="alert">{zh ? "来源已改变、撤回或暂时不可用。请重新提问以检查最新证据。" : "The evidence changed, was withdrawn or is currently unavailable. Ask again to check current evidence."}</p> : evidence?.map(p => {
      let href: string | undefined;
      try { const url = new URL(p.canonical_url); if (["https:", "http:"].includes(url.protocol) && !url.username && !url.password) href = url.href; } catch { /* Unusable URL remains plain text. */ }
      return <article className="source-record" key={p.passage_id}><p className="eyebrow">{p.institution}</p><h3>{p.source_title}</h3><blockquote><p>{p.text}</p><small>{p.locator}</small></blockquote><p>{p.rights_basis}</p><p>{zh ? "编辑审核" : "Editorial review"}: {p.reviewer} · {new Date(p.reviewed_at).toLocaleDateString(locale, { timeZone: "Asia/Shanghai" })}</p><p><small>{p.passage_id}</small></p>{href && <a href={href} target="_blank" rel="noopener noreferrer">{zh ? "打开原始来源" : "Open original source"}</a>}</article>;
    })}
  </SourceDrawer>;
}
