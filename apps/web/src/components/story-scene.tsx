"use client";
import { useEffect, useId, useRef, useState } from "react";
import { useLocale } from "./locale-provider";

/** Code-drawn scenery for the original fictional endings; never documentary evidence. */
export function StoryScene({ node }: { node: string }) {
  const { locale } = useLocale(); const zh = locale !== "en"; const key = useId().replace(/:/g, ""); const river = node === "river";
  return <figure className="story-ending-art"><svg viewBox="0 0 600 240" role="img" aria-label={zh ? (river ? "虚构河流与灯笼插画" : "虚构山间与灯笼插画") : (river ? "Fictional river and lantern illustration" : "Fictional mountain and lantern illustration")}><defs><linearGradient id={`${key}-night`} x2="0" y2="1"><stop stopColor="#0b1722"/><stop offset="1" stopColor={river ? "#244954" : "#3a3447"}/></linearGradient></defs><rect width="600" height="240" fill={`url(#${key}-night)`}/>{[90, 175, 290, 405, 510].map((x, i) => <circle key={x} cx={x} cy={25 + i % 3 * 18} r="2" fill="#f6d697"/>)}{river ? <><path d="M0 190Q150 140 300 190T600 190V240H0Z" fill="#396774"/><path d="M90 185Q300 50 510 185M90 165Q300 30 510 165" fill="none" stroke="#cbb588" strokeWidth="9"/><path d="M230 215Q300 205 370 215M245 230H355" fill="none" stroke="#f6d697" strokeWidth="3"/></> : <><path d="M0 240L170 100 290 240Z" fill="#364843"/><path d="M150 240L340 65 560 240Z" fill="#506054"/><path d="M295 108L340 65 390 105 353 97 340 82 326 104Z" fill="#d3d8ce"/></>}<path d="M300 105V132" stroke="#f6d697" strokeWidth="2"/><rect x="286" y="133" width="28" height="39" rx="8" fill="#f6d697"/><path d="M286 141H314M286 163H314M300 172V184" stroke="#ab7545" strokeWidth="3"/></svg><figcaption>{zh ? "原创虚构故事插画 · 非文化证据" : "Original fictional scenery · not cultural evidence"}</figcaption></figure>;
}

export function StorySoundscape() {
  const { locale } = useLocale(); const zh = locale !== "en"; const [enabled, setEnabled] = useState(false); const [error, setError] = useState(false); const stop = useRef<(() => void) | null>(null); const starting = useRef(false); const generation = useRef(0);
  useEffect(() => () => { generation.current++; stop.current?.(); stop.current = null; }, []);
  const toggle = async () => {
    if (starting.current) return;
    if (enabled) { stop.current?.(); stop.current = null; setEnabled(false); return; }
    starting.current = true; const current = ++generation.current;
    try { const context = new AudioContext(); const volume = context.createGain(); volume.gain.value = .018; volume.connect(context.destination); const tones = [110, 165, 220].map(frequency => { const oscillator = context.createOscillator(); oscillator.type = "sine"; oscillator.frequency.value = frequency; oscillator.connect(volume); oscillator.start(); return oscillator; }); stop.current = () => { tones.forEach(tone => tone.stop()); void context.close(); }; await context.resume(); if (current !== generation.current) { void context.close(); return; } if (context.state !== "running") throw new Error(); setError(false); setEnabled(true); } catch { stop.current?.(); stop.current = null; setEnabled(false); setError(true); } finally { starting.current = false; }
  };
  return <div className="story-soundscape"><button className="outline-button" aria-pressed={enabled} onClick={() => void toggle()}>{zh ? (enabled ? "关闭环境音" : "开启轻柔环境音") : (enabled ? "Stop soundscape" : "Play soft soundscape")}</button><p className="fine-print">{error ? (zh ? "无法播放环境音，文字仍可阅读。" : "Soundscape unavailable. Reading remains available.") : (zh ? "合成环境音 · 自愿播放，不会自动播放。离开故事后停止。" : "Synthetic ambience · optional, never autoplayed. Stops when leaving the story.")}</p></div>;
}
