"use client";

import { api, type GuideAnswer, type GuideEvidence } from "@folkverse/contracts";
import { GuideError, sendGuide, type GuideStage } from "@/lib/guide-stream";
import { GuideSourceInspector } from "./guide-source-inspector";
import Link from "next/link";
import { useEffect, useId, useRef, useState } from "react";
import { lockDocumentScroll, trapDialogTab } from "@/lib/dialog";
import { useGuideKeyboard } from "@/lib/use-guide-keyboard";
import { useLocale } from "./locale-provider";
import { ArrowIcon } from "./arrow-icon";
import { JinyaoAvatar } from "./jinyao-avatar";

const MAX_VISIBLE_TURNS = 100;

const prompts = [
  { id: "begin", en: "Where do I begin?", zh: "从哪里开始？", answer: ["Start with one reviewed exhibit. Open the collection, pick something that catches your eye, and follow its sources. We can take it one story at a time.", "从一件审核展览开始吧。打开馆藏，选择让您感兴趣的内容，再循着来源探索。我们可以一次了解一个故事。"], href: "/explore", link: ["Explore the collection", "探索馆藏"] },
  { id: "sources", en: "Can I see the sources?", zh: "能看看资料来源吗？", answer: ["Of course. Sources belong alongside the story. The Sources page lets you inspect published evidence. This example reply itself is scripted, rather than a cited AI answer.", "当然。故事与来源应该相伴。来源页面可查看已发布的证据。这条示例回复是预设脚本，并非带引用的 AI 回答。"], href: "/sources", link: ["Meet the sources", "了解来源"] },
  { id: "unsure", en: "What if you’re unsure?", zh: "如果您不确定呢？", answer: ["Then I should say so, and help you find a narrower question or a source to read. In this preview I use prepared examples; live evidence-backed conversation is still being built.", "那我应该坦诚说明，并帮助您缩小问题范围或寻找可阅读的来源。此预览使用准备好的示例；真实的循证对话仍在建设中。"] },
] as const;

type Turn = { id: number; question: string; prompt?: string; status: "pending" | "ready" | "cancelled" | "error"; answer?: GuideAnswer; error?: string; stage?: GuideStage; firstContentMs?: number | null };

export function JinyaoChat({ open, onClose, mode = "demo", initialExhibitId }: { open: boolean; onClose: () => void; mode?: "demo" | "live"; initialExhibitId?: string }) {
  const live = mode === "live";
  const { locale, setLocale } = useLocale();
  const zh = locale !== "en";
  const language = zh ? 1 : 0;
  const titleId = useId();
  const dialog = useRef<HTMLDialogElement>(null);
  const history = useRef<HTMLDivElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const nextId = useRef(0);
  const controller = useRef<AbortController | null>(null);
  const context = useRef<string | null>(null);
  const [consent, setConsent] = useState(false);
  const [depth, setDepth] = useState<"concise" | "beginner" | "deeper">("concise");
  const [evidence, setEvidence] = useState<GuideEvidence[] | null>(null);
  const [topics, setTopics] = useState<{ locale: string; items: { id: string; title: string }[] } | null>(null);
  const [draft, setDraft] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [historyTrimmed, setHistoryTrimmed] = useState(false);
  const pending = turns.some(turn => turn.status === "pending");
  useGuideKeyboard();
  useEffect(() => {
    if (!live || !open) return;
    const abort = new AbortController();
    void api.GET("/api/v1/exhibits", { params: { query: { locale, limit: 5 } }, cache: "no-store", signal: abort.signal }).then(result => {
      if (!abort.signal.aborted) setTopics({ locale, items: result.data?.items.filter(item => !initialExhibitId || item.id === initialExhibitId) ?? [] });
    }).catch(() => { if (!abort.signal.aborted) setTopics({ locale, items: [] }); });
    return () => abort.abort();
  }, [live, open, locale, initialExhibitId]);

  useEffect(() => {
    const node = dialog.current;
    if (!node || !open) return;
    const trigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    node.showModal();
    const unlock = lockDocumentScroll();
    return () => { node.close(); unlock(); trigger?.focus({ preventScroll: true }); controller.current?.abort(); controller.current = null; setTurns(previous => previous.map(turn => turn.status === "pending" ? { ...turn, status: "cancelled" } : turn)); };
  }, [open]);
  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); controller.current?.abort(); }, []);
  useEffect(() => {
    if (open && history.current) history.current.scrollTop = history.current.scrollHeight;
  }, [turns, open]);

  const send = (question = draft, prompt?: string) => {
    const text = question.trim().slice(0, 2000);
    if (!text || pending || (live && controller.current)) return;
    const id = ++nextId.current;
    const normalized = text.toLocaleLowerCase().replace(/[?.!。！？]+$/, "");
    const replyLocale = ["say that in chinese", "用中文说"].includes(normalized) ? "zh-CN" :
      ["say that in english", "用英文说"].includes(normalized) ? "en" : locale;
    const replyDepth = ["explain that simply", "simplify that", "make it simpler", "解释得简单一点", "说简单一点"].includes(normalized) ? "beginner" :
      ["go deeper", "explain more", "详细一点"].includes(normalized) ? "deeper" : depth;
    if (live) { setLocale(replyLocale); setDepth(replyDepth); }
    setDraft("");
    if (turns.length >= MAX_VISIBLE_TURNS) setHistoryTrimmed(true);
    setTurns(previous => [...previous, { id, question: text, prompt, status: "pending" as const }].slice(-MAX_VISIBLE_TURNS));
    if (live) {
      const abort = new AbortController(); controller.current = abort;
      void sendGuide({ question: text, locale: replyLocale, depth: replyDepth, exhibit_id: initialExhibitId,
        context_consent: consent, context_token: consent ? context.current : null }, abort.signal,
        stage => { if (!abort.signal.aborted) setTurns(previous => previous.map(turn => turn.id === id ? { ...turn, stage } : turn)); })
        .then(reply => {
          if (abort.signal.aborted) return;
          context.current = consent ? reply.answer.context_token ??
            (reply.answer.reason === "evidence_changed" ? null : context.current) : null;
          setTurns(previous => previous.map(turn => turn.id === id ? { ...turn, status: "ready", answer: reply.answer, firstContentMs: reply.firstContentMs } : turn));
        }).catch(error => {
          if (abort.signal.aborted) return;
          const code = error instanceof GuideError ? error.code : "connection_interrupted";
          if (["invalid_context", "session_expired", "evidence_changed"].includes(code)) context.current = null;
          setTurns(previous => previous.map(turn => turn.id === id ? { ...turn, status: "error", error: code } : turn));
        }).finally(() => { if (controller.current === abort) controller.current = null; });
      return;
    }
    timer.current = setTimeout(() => {
      setTurns(previous => previous.map(turn => turn.id === id && turn.status === "pending" ? { ...turn, status: "ready" } : turn));
      timer.current = null;
    }, 650);
  };
  const stop = () => {
    controller.current?.abort(); controller.current = null;
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
    setTurns(previous => previous.map(turn => turn.status === "pending" ? { ...turn, status: "cancelled" } : turn));
  };

  const liveError = (code?: string) => {
    if (code === "budget_exhausted") return zh ? "今日向导预算已用完，请稍后再试。" : "The daily guide budget has been reached. Please try later.";
    if (code === "rate_limited" || code === "guide_busy") return zh ? "请求较多，请稍后再试。" : "The guide is busy. Please try again shortly.";
    if (code === "provider_timeout" || code === "guide_timeout") return zh ? "回复超时，请重试。" : "The guide timed out. Please retry.";
    if (code === "invalid_context" || code === "evidence_changed") return zh ? "上下文或证据已改变，请在新问题中提供展项名称。" : "Context or evidence changed. Include the exhibit name in a new question.";
    return zh ? "向导暂时不可用。您的问题未得到回答，请重试。" : "The guide is temporarily unavailable. Your question was not answered. Please retry.";
  };
  const stageText = (stage?: GuideStage) => ({ connecting: zh ? "正在连接…" : "Connecting…", retrieving: zh ? "正在查找审核资料…" : "Finding reviewed evidence…", generating: zh ? "正在准备回答…" : "Preparing an answer…", validating: zh ? "正在核验回答…" : "Checking the answer…" }[stage ?? "connecting"]);

  return <><dialog ref={dialog} className="jinyao-messenger" aria-labelledby={titleId} aria-modal="true" onKeyDown={trapDialogTab}
    onCancel={event => { event.preventDefault(); onClose(); }} onClick={event => {
      if (event.target !== event.currentTarget) return;
      const bounds = event.currentTarget.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) onClose();
    }}>
    <header className="jinyao-chat-header"><JinyaoAvatar size={52} /><div><h2 id={titleId}>{zh ? "锦瑶 · Jinyao" : "Jinyao"}</h2><p>{live ? (zh ? "您的文化伙伴 · 审核资料" : "Your cultural companion · reviewed evidence") : (zh ? "您的文化伙伴 · 示例对话" : "Your cultural companion · example chat")}</p></div><button className="jinyao-close" autoFocus onClick={onClose} aria-label={zh ? "关闭锦瑶聊天" : "Close Jinyao chat"}>×</button></header>
    <p className="jinyao-chat-notice">{live ? (zh ? "文化问题会发送至向导服务与配置的 AI 提供商。当前审核资料范围有限；对话仅保留在本页。" : "Cultural questions are sent to the guide service and configured AI provider. Reviewed coverage is limited; chat stays on this page.") : (zh ? "预设示例 · 未连接真实 AI · 不会发送消息" : "Scripted preview · no live AI · messages are not sent")}</p>
    <div ref={history} className="jinyao-chat-history" role="log" aria-label={live ? (zh ? "与锦瑶的对话" : "Conversation with Jinyao") : (zh ? "与锦瑶的示例对话" : "Example conversation with Jinyao")} aria-live="polite" aria-relevant="additions text" aria-busy={pending}>
      <div className="jinyao-message from-jinyao"><JinyaoAvatar size={32} /><div><span className="sr-only">Jinyao: </span><p>{live ? (zh ? "您好，我是锦瑶。请选择一件审核展项，或提出问题，我们一起查看资料。" : "Hi, I’m Jinyao. Choose a reviewed exhibit or ask a question, and we can inspect the evidence together.") : (zh ? "您好，我是锦瑶。想从哪里开始探索？选择下方的问题，试试和我聊天的感觉。" : "Hi, I’m Jinyao. What are you curious about today? Try a question below to see how a conversation could feel.")}</p></div></div>
      {turns.map(turn => {
        const response = prompts.find(prompt => prompt.id === turn.prompt);
        return <div className="jinyao-chat-turn" key={turn.id}>
          <div className="jinyao-message from-visitor"><span className="sr-only">{zh ? "您：" : "You: "}</span><p>{turn.question}</p></div>
          <div className="jinyao-message from-jinyao"><JinyaoAvatar size={32} /><div><span className="sr-only">Jinyao: </span><p>{turn.status === "pending" ? (live ? stageText(turn.stage) : (zh ? "正在准备示例回复…" : "Preparing an example reply…")) : turn.status === "cancelled" ? (zh ? "回复已停止。您可以尝试另一个问题。" : "Reply stopped. You can try another question.") : turn.status === "error" ? liveError(turn.error) : turn.answer ? turn.answer.answer_text : response ? response.answer[language] : (zh ? "谢谢您的问题。此处只能展示预设对话，暂时无法依据证据回答自由输入的问题。您可以尝试上方的示例问题，或浏览审核馆藏。" : "Thank you for asking. I can only show prepared conversations here, so I cannot answer your question from evidence yet. Try a suggested question, or explore the reviewed collection.")}</p>{live && turn.answer && turn.answer.status !== "conversational" && <><p className="fine-print">{turn.answer.coverage_limit}</p><span className="demo-tag">{turn.answer.uncertainty === "partial" ? (zh ? "有限证据" : "Limited evidence") : (zh ? "资料不足" : "Insufficient evidence")}</span>{(turn.answer.sources ?? []).length > 0 && <button className="outline-button" onClick={() => setEvidence(turn.answer!.sources ?? [])}>{zh ? "查看回答来源" : "Inspect answer sources"}</button>}</>}{live && (turn.status === "error" || turn.status === "cancelled") && <button className="outline-button" disabled={pending} onClick={() => send(turn.question)}>{zh ? "重试问题" : "Retry question"}</button>}{turn.status === "ready" && response && "href" in response && <Link href={response.href} onClick={onClose}>{response.link[language]} <ArrowIcon direction="diagonal" /></Link>}</div></div>
        </div>;
      })}
    </div>
    <div className="jinyao-chat-prompts">{live ? (topics?.locale === locale ? topics.items : []).map(topic => <button key={topic.id} disabled={pending} onClick={() => send(zh ? `介绍一下${topic.title}` : `What does the reviewed source say about ${topic.title}?`)}>{topic.title}</button>) : prompts.map(prompt => <button key={prompt.id} disabled={pending} onClick={() => send(zh ? prompt.zh : prompt.en, prompt.id)}>{zh ? prompt.zh : prompt.en}</button>)}</div>
    {live && <div className="jinyao-live-options"><label>{zh ? "解释深度" : "Explanation depth"}<select aria-label={zh ? "解释深度" : "Explanation depth"} value={depth} disabled={pending} onChange={event => setDepth(event.target.value as typeof depth)}><option value="concise">{zh ? "简短" : "Concise"}</option><option value="beginner">{zh ? "入门" : "Beginner"}</option><option value="deeper">{zh ? "深入" : "Deeper"}</option></select></label><label><input type="checkbox" checked={consent} disabled={pending} onChange={event => { setConsent(event.target.checked); if (!event.target.checked) context.current = null; }} />{zh ? "允许使用30分钟的展项与证据上下文进行追问" : "Use topic and evidence context for follow-ups for 30 minutes"}</label></div>}
    <form className="jinyao-chat-composer" onSubmit={event => { event.preventDefault(); send(); }}><label className="sr-only" htmlFor="jinyao-question">{zh ? "给锦瑶的消息" : "Message Jinyao"}</label><textarea id="jinyao-question" rows={1} maxLength={2000} value={draft} onChange={event => setDraft(event.target.value)} onKeyDown={event => {
      if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing && event.keyCode !== 229) {
        event.preventDefault(); send();
      }
    }} placeholder={live ? (zh ? "向锦瑶提问…" : "Ask Jinyao…") : (zh ? "输入示例消息…" : "Write an example message…")} /><button className="gold-button" type="submit" disabled={!draft.trim() || pending} aria-label={live ? (zh ? "发送消息" : "Send message") : (zh ? "发送示例消息" : "Send example message")}><ArrowIcon direction="up" /></button></form>
    <footer className="jinyao-chat-footer"><span>{draft.length} / 2000</span>{pending ? <button onClick={stop}>{zh ? "停止回复" : "Stop reply"}</button> : <span>{zh ? "本页访问中的对话" : "Conversation for this page visit"}</span>}</footer>
    {historyTrimmed && <p className="jinyao-chat-limit" role="status">{zh ? "仅显示最近100轮对话，您可以继续聊天。" : "Showing the latest 100 turns. You can keep chatting."}</p>}
  </dialog>{live && <GuideSourceInspector evidence={evidence} onClose={() => setEvidence(null)} />}</>;
}
