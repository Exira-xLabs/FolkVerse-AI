"use client";

import Link from "next/link";
import { useEffect, useId, useRef, useState } from "react";
import { lockDocumentScroll, trapDialogTab } from "@/lib/dialog";
import { useGuideKeyboard } from "@/lib/use-guide-keyboard";
import { useLocale } from "./locale-provider";
import { ArrowIcon } from "./arrow-icon";
import { JinyaoAvatar } from "./jinyao-avatar";

const prompts = [
  { id: "begin", en: "Where do I begin?", zh: "从哪里开始？", answer: ["Start with one reviewed exhibit. Open the collection, pick something that catches your eye, and follow its sources. We can take it one story at a time.", "从一件审核展览开始吧。打开馆藏，选择让您感兴趣的内容，再循着来源探索。我们可以一次了解一个故事。"], href: "/explore", link: ["Explore the collection", "探索馆藏"] },
  { id: "sources", en: "Can I see the sources?", zh: "能看看资料来源吗？", answer: ["Of course. Sources belong alongside the story. The Sources page lets you inspect published evidence. This example reply itself is scripted, rather than a cited AI answer.", "当然。故事与来源应该相伴。来源页面可查看已发布的证据。这条示例回复是预设脚本，并非带引用的 AI 回答。"], href: "/sources", link: ["Meet the sources", "了解来源"] },
  { id: "unsure", en: "What if you’re unsure?", zh: "如果您不确定呢？", answer: ["Then I should say so, and help you find a narrower question or a source to read. In this preview I use prepared examples; live evidence-backed conversation is still being built.", "那我应该坦诚说明，并帮助您缩小问题范围或寻找可阅读的来源。此预览使用准备好的示例；真实的循证对话仍在建设中。"] },
] as const;

type Turn = { id: number; question: string; prompt?: string; status: "pending" | "ready" | "cancelled" };

export function JinyaoChat({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { locale } = useLocale();
  const zh = locale !== "en";
  const language = zh ? 1 : 0;
  const titleId = useId();
  const dialog = useRef<HTMLDialogElement>(null);
  const history = useRef<HTMLDivElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const nextId = useRef(0);
  const [draft, setDraft] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const pending = turns.some(turn => turn.status === "pending");
  useGuideKeyboard();

  useEffect(() => {
    const node = dialog.current;
    if (!node || !open) return;
    const trigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    node.showModal();
    const unlock = lockDocumentScroll();
    return () => { node.close(); unlock(); trigger?.focus({ preventScroll: true }); };
  }, [open]);
  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, []);
  useEffect(() => {
    if (open && history.current) history.current.scrollTop = history.current.scrollHeight;
  }, [turns, open]);

  const send = (question = draft, prompt?: string) => {
    const text = question.trim().slice(0, 2000);
    if (!text || pending || turns.length >= 20) return;
    const id = ++nextId.current;
    setDraft("");
    setTurns(previous => [...previous, { id, question: text, prompt, status: "pending" }]);
    timer.current = setTimeout(() => {
      setTurns(previous => previous.map(turn => turn.id === id && turn.status === "pending" ? { ...turn, status: "ready" } : turn));
      timer.current = null;
    }, 650);
  };
  const stop = () => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
    setTurns(previous => previous.map(turn => turn.status === "pending" ? { ...turn, status: "cancelled" } : turn));
  };

  return <dialog ref={dialog} className="jinyao-messenger" aria-labelledby={titleId} aria-modal="true" onKeyDown={trapDialogTab}
    onCancel={event => { event.preventDefault(); onClose(); }} onClick={event => {
      if (event.target !== event.currentTarget) return;
      const bounds = event.currentTarget.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) onClose();
    }}>
    <header className="jinyao-chat-header"><JinyaoAvatar size={52} /><div><h2 id={titleId}>{zh ? "锦瑶 · Jinyao" : "Jinyao"}</h2><p>{zh ? "您的文化伙伴 · 示例对话" : "Your cultural companion · example chat"}</p></div><button className="jinyao-close" autoFocus onClick={onClose} aria-label={zh ? "关闭锦瑶聊天" : "Close Jinyao chat"}>×</button></header>
    <p className="jinyao-chat-notice">{zh ? "预设示例 · 未连接真实 AI · 不会发送消息" : "Scripted preview · no live AI · messages are not sent"}</p>
    <div ref={history} className="jinyao-chat-history" role="log" aria-label={zh ? "与锦瑶的示例对话" : "Example conversation with Jinyao"} aria-live="polite" aria-relevant="additions text" aria-busy={pending}>
      <div className="jinyao-message from-jinyao"><JinyaoAvatar size={32} /><div><span className="sr-only">Jinyao: </span><p>{zh ? "您好，我是锦瑶。想从哪里开始探索？选择下方的问题，试试和我聊天的感觉。" : "Hi, I’m Jinyao. What are you curious about today? Try a question below to see how a conversation could feel."}</p></div></div>
      {turns.map(turn => {
        const response = prompts.find(prompt => prompt.id === turn.prompt);
        return <div className="jinyao-chat-turn" key={turn.id}>
          <div className="jinyao-message from-visitor"><span className="sr-only">{zh ? "您：" : "You: "}</span><p>{turn.question}</p></div>
          <div className="jinyao-message from-jinyao"><JinyaoAvatar size={32} /><div><span className="sr-only">Jinyao: </span><p>{turn.status === "pending" ? (zh ? "正在准备示例回复…" : "Preparing an example reply…") : turn.status === "cancelled" ? (zh ? "回复已停止。您可以尝试另一个问题。" : "Reply stopped. You can try another question.") : response ? response.answer[language] : (zh ? "谢谢您的问题。此处只能展示预设对话，暂时无法依据证据回答自由输入的问题。您可以尝试上方的示例问题，或浏览审核馆藏。" : "Thank you for asking. I can only show prepared conversations here, so I cannot answer your question from evidence yet. Try a suggested question, or explore the reviewed collection.")}</p>{turn.status === "ready" && response && "href" in response && <Link href={response.href} onClick={onClose}>{response.link[language]} <ArrowIcon direction="diagonal" /></Link>}</div></div>
        </div>;
      })}
    </div>
    <div className="jinyao-chat-prompts">{prompts.map(prompt => <button key={prompt.id} disabled={pending || turns.length >= 20} onClick={() => send(zh ? prompt.zh : prompt.en, prompt.id)}>{zh ? prompt.zh : prompt.en}</button>)}</div>
    <form className="jinyao-chat-composer" onSubmit={event => { event.preventDefault(); send(); }}><label className="sr-only" htmlFor="jinyao-question">{zh ? "给锦瑶的消息" : "Message Jinyao"}</label><textarea id="jinyao-question" rows={2} maxLength={2000} value={draft} onChange={event => setDraft(event.target.value)} placeholder={zh ? "输入示例消息…" : "Write an example message…"} /><button className="gold-button" type="submit" disabled={!draft.trim() || pending || turns.length >= 20} aria-label={zh ? "发送示例消息" : "Send example message"}><ArrowIcon direction="up" /></button></form>
    <footer className="jinyao-chat-footer"><span>{draft.length} / 2000</span>{pending ? <button onClick={stop}>{zh ? "停止回复" : "Stop reply"}</button> : <span>{zh ? "本页访问中的对话" : "Conversation for this page visit"}</span>}</footer>
    {turns.length >= 20 && <p className="jinyao-chat-limit" role="status">{zh ? "此预览已达到20轮。" : "This preview has reached 20 turns."}</p>}
  </dialog>;
}
