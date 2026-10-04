"use client";

import Link from "next/link";
import { useState } from "react";
import { useLocale } from "./locale-provider";
import { AudioControls, demoExhibits, ExhibitCard, GlassPanel, GoldButton, GuidePortrait, InterestChart, SourceDrawer, ThemeChip } from "./museum-ui";
import type { PageKey } from "@/lib/routes";

function useCopy() {
  const { locale } = useLocale();
  return (en: string, zh: string) => locale === "en" ? en : zh;
}
type OpenSource = (title?: string) => void;

function Explore({ open }: { open: OpenSource }) {
  const c = useCopy(); const [query, setQuery] = useState(""); const [theme, setTheme] = useState("Craft"); const [selected, setSelected] = useState("screen");
  const themes = [["Craft", "工艺"], ["Legends", "传说"], ["Music", "音乐"], ["Food", "饮食"]];
  const results = demoExhibits.filter(e => (!theme || e.theme === theme) && [...e.title, ...e.region].join(" ").toLowerCase().includes(query.toLowerCase()));
  const exhibit = demoExhibits.find(e => e.id === selected)!;
  return <div className="explore-layout"><GlassPanel className="filter-panel">
    <h2>{c("Find your culture", "寻找您的文化")}</h2>
    <label className="field"><span className="sr-only">{c("Search regions and exhibits", "搜索地区与展览")}</span><input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder={c("Region, tradition, craft…", "地区、传统、工艺…")} /></label>
    <p className="eyebrow">{c("EXPLORE THEMES", "探索主题")}</p><div className="theme-grid">{themes.map(([en, zh]) => <ThemeChip key={en} active={theme === en} onClick={() => setTheme(theme === en ? "" : en)}>{c(en, zh)}</ThemeChip>)}</div>
    <div className="filtered-exhibits" aria-live="polite">{results.length ? results.map(e => <ExhibitCard key={e.id} exhibit={e} onOpen={() => { setSelected(e.id); open(c(e.title[0], e.title[1])); }} />) : <p className="empty-state">{c("No demo exhibits match. Try another theme or clear your search.", "没有符合条件的演示展览。请更换主题或清除搜索。")}</p>}</div>
    <p className="fine-print">{c("Illustrative scenery. Use the list to explore; no reviewed map geometry is available.", "地图仅作示意，请使用列表探索。尚无经审核的地理数据。")}</p>
  </GlassPanel><GlassPanel className="region-preview"><div><p className="eyebrow">{c("A PLACE TO BEGIN", "探索的起点")}</p><h2>{c(exhibit.region[0], exhibit.region[1])} {c("is calling", "在呼唤")}</h2><p>{c(exhibit.title[0], exhibit.title[1])}</p></div><GoldButton onClick={() => open(c(exhibit.title[0], exhibit.title[1]))}>{c("Explore", "探索")} ↗︎</GoldButton></GlassPanel></div>;
}

function Journey({ open }: { open: OpenSource }) {
  const c = useCopy(); const [stops, setStops] = useState(demoExhibits); const [duration, setDuration] = useState(20); const [theme, setTheme] = useState("all");
  const regenerate = () => { let total = 0; setStops(demoExhibits.filter(e => { if (theme !== "all" && e.theme !== theme) return false; if (total + e.minutes > duration) return false; total += e.minutes; return true; })); };
  const move = (index: number, direction: number) => setStops(previous => { const next = [...previous]; [next[index], next[index + direction]] = [next[index + direction], next[index]]; return next; });
  const total = stops.reduce((sum, e) => sum + e.minutes, 0);
  return <div className="journey-layout"><div className="journey-controls">
    <label className="select-pill">{c("Interests", "兴趣")}<select aria-label={c("Interests", "兴趣")} value={theme} onChange={e => setTheme(e.target.value)}><option value="all">{c("Performance + craft", "表演与工艺")}</option><option value="Craft">{c("Craft", "工艺")}</option><option value="Music">{c("Music", "音乐")}</option><option value="Food">{c("Food", "饮食")}</option></select></label>
    <label className="select-pill">{c("Time", "时长")}<select aria-label={c("Time", "时长")} value={duration} onChange={e => setDuration(Number(e.target.value))}>{[5, 10, 20, 30].map(v => <option key={v} value={v}>{v} {c("minutes", "分钟")}</option>)}</select></label>
    <GoldButton onClick={regenerate}>{c("Shape my route", "生成我的路线")} ↗︎</GoldButton>
  </div><GlassPanel className="journey-route"><div className="panel-heading"><h2>{c("Your next discoveries", "您的下一站发现")}</h2><span className="demo-tag" aria-live="polite">{stops.length} {c("stops", "站")} · {total} / {duration} {c("min", "分钟")}</span></div>
    <p className="fine-print">{c("A digital learning route · illustrative stops, not physical travel directions.", "数字学习路线 · 示例站点，不是实际旅行导航。")}</p>
    {!stops.length ? <p className="empty-state">{c("Not enough time for an eligible demo stop. Increase the duration or change your interests.", "没有符合时长的演示站点，请增加时长或更换兴趣。")}</p> : <ol className="journey-stops">{stops.map((e, i) => <li key={e.id}><span className="stop-number">{String(i + 1).padStart(2, "0")}</span><h3>{c(e.region[0], e.region[1])}</h3><button className="text-button" onClick={() => open(c(e.title[0], e.title[1]))}>{c(e.title[0], e.title[1])} ↗︎</button><span className="fine-print">{e.minutes} {c("min", "分钟")}</span><div className="stop-actions"><button className="icon-button" aria-label={`${c("Move up", "上移")} ${e.id}`} disabled={i === 0} onClick={() => move(i, -1)}>↑</button><button className="icon-button" aria-label={`${c("Move down", "下移")} ${e.id}`} disabled={i === stops.length - 1} onClick={() => move(i, 1)}>↓</button><button className="text-button" aria-label={`${c("Remove", "移除")} ${e.id}`} onClick={() => setStops(stops.filter(s => s.id !== e.id))}>{c("Remove", "移除")}</button></div></li>)}</ol>}
    {total > duration && <p role="status">{c("This route exceeds your selected time. Regenerate or remove a stop.", "路线超出所选时长，请重新生成或删除站点。")}</p>}
  </GlassPanel></div>;
}

function Stories({ open }: { open: OpenSource }) {
  const c = useCopy(); const [node, setNode] = useState("start");
  const story = node === "start" ? ["A shadow beyond the screen", "幕后的影子", "A lantern drifts into the night. Which trail will you follow?", "一盏灯笼飘入夜色。您将选择哪条道路？"] : node === "mountain" ? ["The mountain light", "山间的灯火", "You climb toward a quiet light. At the summit, your lantern becomes one of the stars.", "您向静谧的灯火攀登。到达山顶时，灯笼化作群星中的一颗。"] : ["The river bridge", "河上的桥", "You cross the bridge. Below, the lantern's reflection carries your story downstream.", "您走过桥梁。水中的灯影带着您的故事顺流而下。"];
  return <GlassPanel className="story-panel"><p className="eyebrow">{c("CHAPTER", "章节")} {node === "start" ? "01" : "02"}</p><h2>{c(story[0], story[1])}</h2><p className="story-text" aria-live="polite">{c(story[2], story[3])}</p><span className="demo-tag">{c("Original fictional adaptation · demo", "原创虚构故事 · 演示")}</span>
    {node === "start" ? <><AudioControls /><GoldButton onClick={() => setNode("mountain")}>{c("Follow the mountain light", "追随山间的灯火")} ›</GoldButton><button className="outline-button" onClick={() => setNode("river")}>{c("Cross the river bridge", "走过河上的桥")} ›</button></> : <><p className="ending-label">{c("Your lantern rests. The tale is yours to begin again.", "灯笼停歇了，您可以重新开始这个故事。")}</p><GoldButton onClick={() => setNode("start")}>{c("Begin again", "重新开始")} ↻</GoldButton></>}
    <button className="text-button" onClick={() => open()}>{c("Context & captions", "背景与字幕")} ↗︎</button>
  </GlassPanel>;
}

function Lens({ open }: { open: OpenSource }) {
  const c = useCopy(); const [state, setState] = useState("related"); const [busy, setBusy] = useState(false);
  const compare = async () => { setBusy(true); await new Promise(resolve => setTimeout(resolve, 500)); setBusy(false); };
  const message: Record<string, [string, string]> = {
    related: ["A related object class", "相关物件类别"], unknown: ["No eligible catalog match", "没有符合条件的目录匹配"], poor: ["More detail is needed", "需要更多细节"], denied: ["Camera permission denied", "相机权限被拒绝"], unavailable: ["Recognition service unavailable", "识别服务不可用"],
  };
  return <GlassPanel className="lens-panel"><h2>{c("Look closer", "仔细看看")}</h2><span className="demo-tag">{c("SIMULATED RESULT · NO RECOGNITION", "模拟结果 · 非真实识别")}</span>
    <label className="field"><span>{c("Choose a demo scenario", "选择演示场景")}</span><select value={state} onChange={e => setState(e.target.value)}><option value="related">{c("Related object class", "相关物件类别")}</option><option value="unknown">{c("Unknown object", "未知物件")}</option><option value="poor">{c("Insufficient image", "图像不足")}</option><option value="denied">{c("Permission denied", "权限被拒绝")}</option><option value="unavailable">{c("Service unavailable", "服务不可用")}</option></select></label>
    <div className="lens-result" aria-live="polite" aria-busy={busy}><span className="lens-symbol" aria-hidden="true">{busy ? "◌" : state === "related" ? "◇" : "?"}</span><h3>{busy ? c("Comparing demo…", "正在比较演示…") : c(...message[state])}</h3><p>{state === "related" ? c("Visible silhouette and articulated shapes suggest a puppet-like object in this scripted example. Similarity is not identity or authentication.", "在此脚本示例中，轮廓和关节形状提示类似偶人的物件。相似性不代表身份或鉴定。") : state === "poor" ? c("Try a clear, well-lit photograph of the object and its label when capture is available.", "拍摄功能开放后，请提供清晰、光线充足的物件及标签照片。") : state === "denied" ? c("Camera access is not requested by this demo. This is a permission-error preview.", "本演示不会请求相机权限，此处仅预览权限错误。") : c("No live recognition is connected. This demo does not upload images or claim a catalog identity.", "尚未连接真实识别服务，本演示不会上传图像或宣称目录身份。")}</p></div>
    <GoldButton disabled={busy} onClick={() => void compare()}>{c("Replay simulation", "重播模拟")} ↻</GoldButton><button className="text-button" onClick={() => open()}>{c("Inspect catalog requirements", "查看目录要求")} ↗︎</button>
  </GlassPanel>;
}

function Guide({ open }: { open: OpenSource }) {
  const c = useCopy(); const [question, setQuestion] = useState(""); const [asked, setAsked] = useState(""); const [state, setState] = useState("ready"); const [notice, setNotice] = useState("");
  const send = async () => { if (!question.trim() || state === "loading") return; setAsked(question.trim()); setQuestion(""); setState("loading"); await new Promise(resolve => setTimeout(resolve, 500)); setState("answered"); };
  return <div className="guide-layout"><GlassPanel className="chat-panel"><span className="demo-tag">{c("SCRIPTED DEMO · NO MODEL CALL", "脚本演示 · 无模型调用")}</span><div className="chat-history" aria-live="polite" aria-busy={state === "loading"}><p className="eyebrow">{c("YOU", "您")}</p><div className="chat-question">{asked || c("What can I discover here?", "我能在这里发现什么？")}</div><p className="eyebrow">{c("GUIDE", "向导")}</p><p className="chat-answer">{state === "loading" ? c("Loading the scripted response…", "正在加载脚本回答…") : asked ? c("This is a recorded UI demonstration, so I cannot answer your question from evidence yet. Explore a demo exhibit, or inspect the source requirements below.", "这是预设界面演示，目前无法根据证据回答您的问题。您可以探索示例展览，或查看下方来源要求。") : c("Follow a lantern, shape a learning route, or explore your cultural interests. These interactive previews use demo material; reviewed cultural answers are coming in a later phase.", "追随灯笼、规划学习路线，或探索文化兴趣。这些交互预览使用演示资料，经过审核的文化问答将在后续阶段上线。")}</p><button className="source-pill" onClick={() => open()}>{c("Demo provenance & source requirements", "演示出处与来源要求")} ↗︎</button></div>
    <form className="guide-composer" onSubmit={e => { e.preventDefault(); void send(); }}><label className="sr-only" htmlFor="guide-question">{c("Ask the guide", "向向导提问")}</label><textarea id="guide-question" maxLength={2000} rows={2} value={question} onChange={e => setQuestion(e.target.value)} placeholder={c("Ask about a tradition…", "询问文化传统…")} /><GoldButton type="submit" disabled={!question.trim() || state === "loading"}>{c("Send", "发送")} ↑</GoldButton></form>
    <div className="composer-bottom"><small>{question.length} / 2000</small><button className="text-button" onClick={() => setNotice(c("Live microphone transcription is unavailable. Type your question instead.", "实时麦克风转写尚未开放，请输入您的问题。"))}>{c("Voice", "语音")} ◉</button></div>{notice && <p role="status" className="fine-print">{notice}</p>}
  </GlassPanel><GuidePortrait /></div>;
}

function Dna({ open }: { open: OpenSource }) {
  const c = useCopy(); const [weights, setWeights] = useState([78, 64, 53, 41]); const [editing, setEditing] = useState(false); const [paused, setPaused] = useState(true);
  const names = [["Craft", "工艺"], ["Legends", "传说"], ["Music", "音乐"], ["Food culture", "饮食文化"]]; const strongest = weights.indexOf(Math.max(...weights));
  return <div className="dna-layout"><GlassPanel className="dna-panel"><h2>{c("Your cultural constellation", "您的文化星图")}</h2><InterestChart weights={weights} /><p className="fine-print">{c("Sample interests, not ancestry. Changes stay in this page; no tracking or profile is saved.", "示例兴趣，不代表血统。修改仅保留在此页面，不会追踪或保存个人档案。")}</p>
    <div className="compact-actions"><GoldButton onClick={() => setEditing(!editing)} aria-expanded={editing}>{editing ? c("Done", "完成") : c("Edit interests", "编辑兴趣")}</GoldButton><button className="outline-button" onClick={() => setWeights([0, 0, 0, 0])}>{c("Reset", "重置")}</button></div>
    {editing && <fieldset className="interest-edit"><legend>{c("Set your own weights", "设置您的兴趣权重")}</legend>{names.map(([en, zh], i) => <label key={en}>{c(en, zh)}<input type="range" min="0" max="100" value={weights[i]} onChange={e => setWeights(weights.map((v, j) => i === j ? Number(e.target.value) : v))} /><output>{weights[i]}</output></label>)}</fieldset>}
    <button className="text-button" aria-pressed={!paused} onClick={() => setPaused(!paused)}>{paused ? c("Preview tracking opt-in", "预览追踪同意") : c("Pause demo tracking", "暂停演示追踪")}</button><small className="fine-print">{paused ? c("Tracking is off.", "追踪已关闭。") : c("Opt-in preview only; no events are collected.", "仅预览同意状态，不收集事件。")}</small>
  </GlassPanel><GlassPanel className="recommendation-panel"><p className="eyebrow">{c("RECOMMENDED FOR YOUR DEMO", "为您的演示推荐")}</p><h2>{weights.every(v => v === 0) ? c("Begin with curiosity", "从好奇开始") : c(names[strongest][0], names[strongest][1])}</h2><p>{weights.every(v => v === 0) ? c("Choose an interest to shape a suggestion.", "选择一项兴趣来获得建议。") : c("Based on your strongest explicit demo interest.", "根据您设置的最强演示兴趣。")}</p><button className="text-button" onClick={() => open()}>{c("Why this suggestion?", "为什么推荐？")} ↗︎</button></GlassPanel></div>;
}

function Sources({ open }: { open: OpenSource }) {
  const c = useCopy(); const steps = [["Community voice", "社群声音", "Attribution + consent", "署名与同意"], ["Reviewed record", "审核记录", "Claims + media rights", "事实与媒体权利"], ["AI experience", "AI 体验", "Citations + uncertainty", "引用与不确定性"], ["Visitor", "访客", "Explore and ask", "探索与提问"]];
  return <div className="sources-layout"><div className="source-summary"><span className="demo-tag">{c("0 published sources", "0 条已发布来源")}</span><span className="demo-tag">{c("EN / 中文", "中文 / EN")}</span><span className="demo-tag">{c("Human review required", "需要人工审核")}</span></div><GlassPanel className="evidence-panel"><h2>{c("How an answer is built", "答案如何形成")}</h2><div className="evidence-chain">{steps.map(([en, zh, note, zn], i) => <button key={en} onClick={() => open(c(en, zh))}><span className="eyebrow">0{i + 1}</span><h3>{c(en, zh)}</h3><p>{c(note, zn)}</p><span aria-hidden="true">↗︎</span></button>)}</div><p className="fine-print">{c("No reviewed records are published yet. Inspect a stage to learn its requirements.", "尚未发布经审核的记录。查看任一阶段以了解其要求。")}</p></GlassPanel></div>;
}

export function MuseumExperiences({ page, mode }: { page: PageKey; mode: "demo" | "live" }) {
  const c = useCopy(); const [source, setSource] = useState<string | null>(null); const open: OpenSource = title => setSource(title || "");
  if (mode !== "demo") return <GlassPanel className="experience-panel"><p className="eyebrow">{c("LIVE MODE", "实时模式")}</p><h2>{c("This experience is not available yet.", "此功能尚未开放。")}</h2><p>{c("Live content and providers are not connected. Demo fixtures are disabled in live mode.", "尚未连接真实内容及服务，实时模式不提供演示资料。")}</p><Link href="/status" className="outline-button">{c("Check services", "检查服务")}</Link></GlassPanel>;
  const screens: Partial<Record<PageKey, React.ReactNode>> = { explore: <Explore open={open} />, journey: <Journey open={open} />, stories: <Stories open={open} />, lens: <Lens open={open} />, guide: <Guide open={open} />, dna: <Dna open={open} />, sources: <Sources open={open} /> };
  return <><div className="fixture-content">{screens[page]}</div><SourceDrawer open={source !== null} title={source || undefined} onClose={() => setSource(null)} /></>;
}
