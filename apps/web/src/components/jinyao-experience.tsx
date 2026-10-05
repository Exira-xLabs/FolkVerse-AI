"use client";

import Image from "next/image";
import Link from "next/link";
import { motion, useScroll, useTransform } from "motion/react";
import { useRef, useState, useSyncExternalStore, type ReactNode } from "react";
import { useLocale } from "./locale-provider";
import { useGraphics } from "./graphics-provider";
import { ArrowIcon } from "./arrow-icon";
import { JinyaoAvatar } from "./jinyao-avatar";
import { JinyaoChat } from "./jinyao-chat";

const motionQuery = "(prefers-reduced-motion: reduce)";
function subscribeMotionPreference(onChange: () => void) {
  const query = window.matchMedia(motionQuery);
  query.addEventListener("change", onChange);
  return () => query.removeEventListener("change", onChange);
}
const motionPreference = () => window.matchMedia(motionQuery).matches;
// Keep the server and first client render static; animate after hydration.
const serverMotionPreference = () => true;
const phoneQuery = "(max-width: 700px)";
function subscribePhonePreference(onChange: () => void) {
  const query = window.matchMedia(phoneQuery);
  query.addEventListener("change", onChange);
  return () => query.removeEventListener("change", onChange);
}
const phonePreference = () => window.matchMedia(phoneQuery).matches;
const serverPhonePreference = () => false;

function ChatSymbol() {
  return <svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M20 11.5a8 8 0 0 1-8 8H5l-3 3v-11a9 9 0 0 1 18 0Z" /><path d="M7 11h8M7 15h5" /></svg>;
}

export function JinyaoExperience({ mode, children }: { mode: "demo" | "live"; children?: ReactNode }) {
  const { locale } = useLocale();
  const zh = locale !== "en";
  const c = (en: string, cn: string) => zh ? cn : en;
  const { simple, lowData } = useGraphics();
  const reducedMotion = useSyncExternalStore(subscribeMotionPreference, motionPreference, serverMotionPreference);
  const phone = useSyncExternalStore(subscribePhonePreference, phonePreference, serverPhonePreference);
  const animate = !simple && !reducedMotion;
  const hero = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: hero, offset: ["start start", "end end"] });
  const imageY = useTransform(scrollYProgress, [0, 1], ["0%", "-5%"]);
  const imageScale = useTransform(scrollYProgress, [0, 1], [1, 1.1]);
  const copyY = useTransform(scrollYProgress, [0, 1], [0, -36]);
  const [chatOpen, setChatOpen] = useState(false);
  const chapters = [
    ["01", "A friendly face, a curious mind.", "温柔相伴，一起好奇。", "I’m Jinyao, your fictional museum companion. A detail, a question, a story—every visit can begin somewhere small.", "我是锦瑶，您的虚构博物馆伙伴。一个细节、一个问题、一个故事——每次探索，都可以从小小的好奇开始。"],
    ["02", "Follow the story. Keep the source.", "循着故事，也循着来源。", "Explore reviewed exhibits at your own pace. Open the evidence alongside each story, and make room for what we don’t yet know.", "按照自己的节奏探索审核展览。阅读故事时，也打开它的证据，并为未知保留空间。"],
    ["03", "A conversation, at your pace.", "您的节奏，您的对话。", "Ask a little. Look closer. Take a different path. The example below shows how chatting with me could feel.", "提出一个问题，仔细观察，或选择另一条路。下方的示例展示与我聊天的感觉。"],
  ];
  const examples = [
    { who: "visitor", text: c("I have five minutes. Where should I start?", "我有五分钟，可以从哪里开始？") },
    { who: "jinyao", text: c("Let’s begin with one reviewed exhibit. Pick something that catches your eye, and we’ll follow its story and sources together.", "先从一件审核展览开始吧。选择让您感兴趣的内容，我们一起循着故事与来源探索。") },
    { who: "visitor", text: c("And if something isn’t certain?", "如果有不确定的地方呢？") },
    { who: "jinyao", text: c("Then we leave room for the unknown. A good question can be the next step—not a reason to invent an answer.", "那就为未知保留空间。一个好问题可以成为下一步，而不是编造答案的理由。") },
  ];

  return <div className="jinyao-experience">
    <section ref={hero} className="jinyao-cinematic" aria-labelledby="page-title">
      <div className="jinyao-cinematic-stage">
        {!lowData && <motion.div className="jinyao-cinematic-image" style={animate ? { y: imageY, scale: imageScale } : undefined}><Image src="/folkverse/jinyao/cinematic.webp" alt={c("Jinyao, a fictional guide in a red embroidered robe, welcomes you into an illustrated museum.", "身穿红色刺绣服饰的虚构向导锦瑶，在插画博物馆中欢迎您。")} fill priority quality={90} sizes="100vw" /></motion.div>}
        <div className="jinyao-cinematic-shade" />
        <motion.div className="jinyao-hero-copy" style={animate && !phone ? { y: copyY } : undefined}>
          <div className="jinyao-headline"><p className="eyebrow">{c("YOUR CULTURAL COMPANION", "您的文化伙伴")}</p>
          <h1 id="page-title">{c("Hi, I’m", "你好，我是")}<span>{c("Jinyao.", "锦瑶。")}</span></h1>
          <p className="jinyao-hero-subtitle">{c("Your curiosity has company.", "让好奇心，有人相伴。")}</p></div>
          <div className="jinyao-hero-details"><p className="jinyao-hero-description">{c("A fictional cultural guide for the stories, details, and little discoveries that make a museum yours.", "一位虚构的文化向导，陪您发现故事、细节，以及属于您的博物馆时刻。")}</p>
          <div className="hero-actions"><button className="gold-button" onClick={() => setChatOpen(true)} disabled={mode !== "demo"}><ChatSymbol />{c("Chat with Jinyao", "与锦瑶聊天")}</button><Link className="text-button" href="/explore">{c("Explore the collection", "探索馆藏")} <ArrowIcon direction="diagonal" /></Link></div>
          <p className="jinyao-preview-note">{c("Fictional companion · scripted chat preview · live AI not connected", "虚构伙伴 · 预设聊天预览 · 未连接真实 AI")}</p></div>
        </motion.div>
        <a className="jinyao-scroll-cue" href="#meet-jinyao" onClick={event => { event.preventDefault(); document.getElementById("meet-jinyao")?.scrollIntoView({ behavior: animate ? "smooth" : "instant" }); }}>{c("Scroll to get to know me", "向下滚动，认识锦瑶")} <ArrowIcon direction="down" /></a>
        <motion.div className="jinyao-scroll-progress" aria-hidden="true" style={{ scaleX: animate ? scrollYProgress : 0 }} />
      </div>
    </section>

    <section id="meet-jinyao" className="jinyao-story" aria-label={c("Meet Jinyao", "认识锦瑶")}>
      <figure className="jinyao-story-portrait">{!lowData && <Image src="/folkverse/jinyao/welcome.webp" alt={c("Jinyao offers a welcoming hand, wearing her red and gold robe.", "身穿红金服饰的锦瑶伸出手，欢迎您的到来。")} width={960} height={1440} sizes="(max-width: 700px) 100vw, 40vw" quality={90} />}<figcaption><span>{c("Jinyao / 锦瑶", "锦瑶 / Jinyao")}</span>{c("Your cultural companion", "您的文化伙伴")}</figcaption></figure>
      <div className="jinyao-chapters">{chapters.map(([number, title, titleZh, text, textZh]) => <article key={number} className="jinyao-chapter"><p className="eyebrow">{number} / {c("GET TO KNOW ME", "认识锦瑶")}</p><h2>{c(title, titleZh)}</h2><p>{c(text, textZh)}</p><span className="jinyao-chapter-line" aria-hidden="true" /></article>)}</div>
    </section>

    {mode === "demo" && <section className="jinyao-conversation" aria-labelledby="jinyao-example-title"><div className="jinyao-example-intro"><p className="eyebrow">{c("A GLIMPSE OF THE CONVERSATION", "看看对话会是什么样")}</p><h2 id="jinyao-example-title">{c("A question becomes a beginning.", "一个问题，开启一段探索。")}</h2><p>{c("A prepared example of the tone and flow. No messages are sent to an AI service.", "一段预先准备的对话，展示语气与交流方式。不会向 AI 服务发送消息。")}</p><button className="gold-button" onClick={() => setChatOpen(true)}>{c("Try the chat preview", "试试聊天预览")} <ChatSymbol /></button></div>
      <div className="jinyao-example-window"><header><JinyaoAvatar size={56} /><div><h3>{c("Jinyao", "锦瑶")}</h3><p>{c("Example conversation", "示例对话")}</p></div><span className="jinyao-example-label">{c("PREVIEW", "预览")}</span></header><ol>{examples.map((message, index) => <li key={index} className={`jinyao-message from-${message.who}`}><span className="sr-only">{message.who === "visitor" ? c("You: ", "您：") : "Jinyao: "}</span>{message.who === "jinyao" && <JinyaoAvatar size={32} />}<p>{message.text}</p></li>)}</ol><p className="jinyao-example-footnote">{c("Scripted illustration · not a factual AI answer", "预设对话示例 · 非真实 AI 事实回答")}</p></div>
    </section>}
    {children}
    {mode === "demo" ? <><button className="jinyao-chat-launcher" onClick={() => setChatOpen(true)} aria-label={c("Open Jinyao chat", "打开锦瑶聊天")} aria-haspopup="dialog" aria-expanded={chatOpen}><JinyaoAvatar size={44} /><span>{c("Chat with Jinyao", "与锦瑶聊天")}</span><ChatSymbol /></button><JinyaoChat open={chatOpen} onClose={() => setChatOpen(false)} /></> : <section className="glass-panel experience-panel"><h2>{c("This experience is not available yet.", "此功能尚未开放。")}</h2><p>{c("Chat is unavailable in live mode. Explore the published collection while the guide is being built.", "实时模式下聊天尚未开放。您可以先探索已发布馆藏。")}</p><Link className="outline-button" href="/explore">{c("Explore the collection", "探索馆藏")} <ArrowIcon direction="diagonal" /></Link></section>}
  </div>;
}
