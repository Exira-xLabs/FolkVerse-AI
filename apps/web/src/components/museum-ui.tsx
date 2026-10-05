"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useId, useRef, useState, type ReactNode, type ButtonHTMLAttributes } from "react";
import { useLocale } from "./locale-provider";
import { navigation, routes, type PageKey } from "@/lib/routes";
import { museumArt, museumArtFocus } from "@/lib/museum-art";
import { lockDocumentScroll, trapDialogTab } from "@/lib/dialog";

export function GlassPanel({ children, className = "", id }: { children: ReactNode; className?: string; id?: string }) {
  return <section id={id} className={`glass-panel reading-panel ${className}`}>{children}</section>;
}
export function GoldButton(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} className={`gold-button ${props.className ?? ""}`} />;
}
export function ThemeChip({ children, active, onClick }: { children: ReactNode; active: boolean; onClick: () => void }) {
  return <button className={`theme-chip ${active ? "selected" : ""}`} aria-pressed={active} onClick={onClick}>{children}</button>;
}
export function GlassTabs({ page }: { page: PageKey }) {
  const { t, locale } = useLocale();
  const nav = useRef<HTMLElement>(null);
  useEffect(() => {
    const row = nav.current, current = row?.querySelector<HTMLElement>("[aria-current=page]");
    if (!row || !current) return;
    const reveal = () => { const a = row.getBoundingClientRect(), b = current.getBoundingClientRect();
      if (b.left < a.left) row.scrollLeft -= a.left - b.left + 6;
      else if (b.right > a.right) row.scrollLeft += b.right - a.right + 6;
    };
    reveal(); const observer = new ResizeObserver(reveal); observer.observe(row);
    return () => observer.disconnect();
  }, [page, locale]);
  return <nav ref={nav} aria-label={locale === "en" ? "Main navigation" : "主导航"} className="nav-tabs">
    {navigation.map(key => <Link key={key} href={routes[key].href} prefetch={false}
      className={`nav-tab ${page === key ? "selected" : ""}`} aria-current={page === key ? "page" : undefined}>{t.nav[key]}</Link>)}
  </nav>;
}
export function GuidePortrait() {
  const { locale } = useLocale();
  return <div className="guide-identity portrait-card"><div className="portrait-frame">
    <Image src={museumArt("09_ai_guide_character.png")} alt="" fill quality={90} sizes="72px" className="portrait-art" />
    </div><p>{locale === "en" ? "Your museum companion" : "您的博物馆伙伴"}<small>{locale === "en" ? "A fictional character" : "虚构角色"}</small></p></div>;
}

export type DemoExhibit = { id: string; title: [string, string]; region: [string, string]; theme: string; minutes: number; asset: string };
export const demoExhibits: DemoExhibit[] = [
  { id: "screen", title: ["Behind the illuminated screen", "光影幕后的世界"], region: ["Shaanxi", "陕西"], theme: "Craft", minutes: 6, asset: "04_shadow_puppetry.png" },
  { id: "table", title: ["A place at the tea table", "茶桌旁的一席"], region: ["Fujian", "福建"], theme: "Food", minutes: 5, asset: "03_cultural_journey.png" },
  { id: "song", title: ["An evening of melodies", "旋律中的夜晚"], region: ["Guangdong", "广东"], theme: "Music", minutes: 7, asset: "07_folklore_dna.png" },
];
export function ExhibitCard({ exhibit, onOpen }: { exhibit: DemoExhibit; onOpen: () => void }) {
  const { locale } = useLocale(); const n = locale === "en" ? 0 : 1;
  return <button className="exhibit-card" onClick={onOpen}><span className="exhibit-thumb">
    <Image src={museumArt(exhibit.asset)} alt="" fill quality={90} sizes="64px" style={{ objectPosition: museumArtFocus(exhibit.asset, "thumbnail") }} />
    </span><span><small>{exhibit.region[n]} · {exhibit.minutes} {n === 0 ? "min" : "分钟"}</small><strong>{exhibit.title[n]}</strong><span className="card-caption">{n === 0 ? "Illustrative exhibit · view notes ↗︎" : "示例展览 · 查看说明 ↗︎"}</span></span></button>;
}

export function SourceDrawer({ open, onClose, title, children }: { open: boolean; onClose: () => void; title?: string; children?: ReactNode }) {
  const titleId = useId();
  const dialog = useRef<HTMLDialogElement>(null);
  const { locale } = useLocale(); const zh = locale !== "en";
  useEffect(() => {
    const node = dialog.current;
    if (!node || !open) return;
    const trigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    node.showModal();
    const unlock = lockDocumentScroll();
    return () => { node.close(); unlock(); trigger?.focus({ preventScroll: true }); };
  }, [open]);
  return <dialog ref={dialog} className="source-drawer glass-panel" aria-labelledby={titleId} aria-modal="true"
    onCancel={event => { event.preventDefault(); onClose(); }} onClick={event => {
      if (event.target !== event.currentTarget) return;
      const bounds = event.currentTarget.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) onClose();
    }} onKeyDown={trapDialogTab}>
    <div className="drawer-top"><span className="eyebrow">{zh ? "来源与使用说明" : "SOURCES & CONTEXT"}</span><button className="icon-button" autoFocus onClick={onClose} aria-label={zh ? "关闭来源" : "Close sources"}>×</button></div>
    <h2 id={titleId}>{title || (zh ? "了解您所看到的内容" : "Know what you are seeing")}</h2>
    {children ?? <><span className="demo-tag">{zh ? "演示内容 · 尚未审核" : "Demo material · not reviewed"}</span>
    <p>{zh ? "这些展览、故事和回答是用于测试界面的编辑示例，不是已发布的文化资料。尚无审核人或审核日期。" : "These exhibits, stories and responses are editorial UI fixtures, not published cultural evidence. No reviewer or review date is claimed."}</p>
    <dl><div><dt>{zh ? "图像用途" : "Artwork role"}</dt><dd>{zh ? "原始生成场景，仅作装饰" : "Supplied generated scenery; decorative only"}</dd></div><div><dt>{zh ? "识别参考" : "Recognition references"}</dt><dd>{zh ? "未导入" : "None imported"}</dd></div><div><dt>{zh ? "内容权利" : "Content rights"}</dt><dd>{zh ? "示例文本为项目原创；外部资料未导入" : "Original project fixture text; no external passages imported"}</dd></div></dl>
    <p>{zh ? "真实展览发布前，需要出处、使用权限和人工审核。" : "Real exhibits require source records, rights decisions and human review before publication."}</p>
    <Link className="outline-button" href="/sources" onClick={onClose}>{zh ? "浏览知识链" : "Explore the evidence chain"} ↗︎</Link></>}
  </dialog>;
}

export function NarrationTranscript() {
  const { locale } = useLocale(); const zh = locale !== "en";
  return <details className="narration-transcript"><summary>{zh ? "英语录音文字稿与中文翻译" : "English audio transcript & Chinese translation"}</summary><p lang="en">A lantern drifts beyond the screen. In this fictional tale, you may follow its light toward the mountain, or take the bridge across the river. Which path will you choose?</p><p lang="zh-CN">一盏灯笼飘出幕布。在这个虚构故事里，您可以追随灯火走向山间，或从桥梁跨过河流。您将选择哪条道路？</p></details>;
}

export function AudioControls() {
  const audio = useRef<HTMLAudioElement>(null);
  const [narration, setNarration] = useState("en");
  const [playing, setPlaying] = useState(false); const [time, setTime] = useState(0); const [duration, setDuration] = useState(0); const [error, setError] = useState(false);
  const { locale } = useLocale(); const zh = locale !== "en";
  useEffect(() => {
    const node = audio.current;
    const frame = requestAnimationFrame(() => {
      if (node?.error) setError(true);
      if (node && node.readyState >= 1 && Number.isFinite(node.duration)) setDuration(node.duration);
    });
    return () => { cancelAnimationFrame(frame); node?.pause(); };
  }, []);
  const clock = (value: number) => `${Math.floor(value / 60)}:${String(Math.floor(value % 60)).padStart(2, "0")}`;
  return <div className="narration-panel"><label className="field">{zh ? "旁白语言" : "Narration language"}<select value={narration} onChange={event => { setNarration(event.target.value); audio.current?.pause(); }}><option value="en">{zh ? "英语录音" : "English recording"}</option><option value="off">{zh ? "仅文字 · 中文音频尚未开放" : "Text only · Chinese audio unavailable"}</option></select></label>
    <NarrationTranscript />
    <div className="audio-controls">
    <audio ref={audio} src="/folkverse/audio/lantern-demo.mp3" preload="metadata" onTimeUpdate={() => setTime(audio.current?.currentTime ?? 0)}
      onLoadedMetadata={() => setDuration(audio.current?.duration ?? 0)} onDurationChange={() => { if (audio.current && Number.isFinite(audio.current.duration)) setDuration(audio.current.duration); }} onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)} onEnded={() => setPlaying(false)} onError={() => setError(true)} />
    <button className="icon-button" disabled={error || duration <= 0 || narration === "off"} aria-label={playing ? (zh ? "暂停旁白" : "Pause narration") : (zh ? "播放旁白" : "Play narration")}
      onClick={() => { if (playing) audio.current?.pause(); else void audio.current?.play().catch(() => setError(true)); }}>{playing ? "Ⅱ" : "▶︎"}</button>
    <label className="audio-timeline"><span className="sr-only">{zh ? "旁白位置" : "Narration position"}</span><input type="range" min="0" max={duration || 1} step="0.1" disabled={narration === "off" || error} value={time} onChange={e => { const value = Number(e.target.value); if (audio.current) audio.current.currentTime = value; setTime(value); }} /></label>
    <span role={error ? "alert" : duration <= 0 ? "status" : undefined}>{error ? (zh ? "音频不可用，请阅读文字稿。" : "Audio unavailable. Read the transcript.") : duration <= 0 ? (zh ? "正在加载旁白…" : "Loading narration…") : `${clock(time)} / ${clock(duration)}`}</span><small>{error ? (zh ? "音频不可用" : "Audio unavailable") : (zh ? "预录合成英语旁白" : "Recorded synthetic EN narration")}</small>
  </div></div>;
}

export function InterestChart({ weights }: { weights: number[] }) {
  const { locale } = useLocale(); const names = locale === "en" ? ["Craft", "Legends", "Music", "Food culture"] : ["工艺", "传说", "音乐", "饮食文化"];
  const points = weights.map((v, i) => { const angle = -Math.PI / 2 + i * Math.PI / 2; return `${100 + Math.cos(angle) * v * .7},${100 + Math.sin(angle) * v * .7}`; }).join(" ");
  return <div className="interest-chart"><svg viewBox="0 0 200 200" aria-hidden="true">
    {[25, 50, 75].map(r => <circle key={r} cx="100" cy="100" r={r} className="chart-ring" />)}
    <path d="M100 20V180M20 100H180" className="chart-ring" /><polygon points={points} className="chart-area" />
    {weights.map((v, i) => { const angle = -Math.PI / 2 + i * Math.PI / 2; return <circle key={i} cx={100 + Math.cos(angle) * v * .7} cy={100 + Math.sin(angle) * v * .7} r="4" fill="var(--accent-gold)" />; })}
    </svg><dl>{names.map((name, i) => <div key={name}><dt>{name}</dt><dd>{weights[i]} / 100<span className="interest-bar" aria-hidden="true"><span style={{ width: `${weights[i]}%` }} /></span></dd></div>)}</dl></div>;
}
