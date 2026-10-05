"use client";

import Link from "next/link";
import { useState } from "react";
import { useLocale } from "./locale-provider";
import { AudioControls, demoExhibits, ExhibitCard, GlassPanel, GoldButton, GuidePortrait, InterestChart, SourceDrawer, ThemeChip } from "./museum-ui";
import { CatalogExperience } from "./catalog-explorer";
import { useVisit } from "./visit-provider";
import { ExhibitContext } from "./exhibit-context";
import { MuseumSelect } from "./museum-select";
import type { PageKey } from "@/lib/routes";

function useCopy() {
  const { locale } = useLocale();
  return (en: string, zh: string) => locale === "en" ? en : zh;
}
type OpenSource = (title?: string) => void;

function ExperiencePreview({ page, children }: { page: "journey" | "lens" | "guide"; children: React.ReactNode }) {
  const c = useCopy();
  const copy = {
    journey: ["A little time, a new discovery", "用一点时间，发现新的文化", "Personal routes are being prepared. Start with the reviewed Liaoning collection, or try a separate example tour of Shaanxi, Fujian and Guangdong.", "个性化路线正在准备中。您可以先浏览审核后的辽宁馆藏，或尝试陕西、福建和广东的独立示例游览。", "Preview a learning route", "预览学习路线"],
    lens: ["Curious about an object?", "想了解眼前的物件？", "Photo recognition is being prepared. Explore reviewed exhibits and their sources while you wait. The optional example below shows how results could look.", "照片识别正在准备中。您可以先探索审核展览及其来源。下方的可选示例展示未来结果的呈现方式。", "Preview Object Lens", "预览识物体验"],
    guide: ["Welcome to the museum", "欢迎来到博物馆", "Source-backed conversation is being prepared. Discover a reviewed exhibit today, or try a clearly labelled conversation example.", "有来源依据的对话正在准备中。您可以先探索审核展览，或尝试明确标注的对话示例。", "Preview a conversation", "预览对话体验"],
  }[page];
  return <div className="experience-preview"><GlassPanel className="experience-intro">
    {page === "guide" && <GuidePortrait />}
    <p className="eyebrow">{c("COMING SOON", "即将开放")}</p><h2>{c(copy[0], copy[1])}</h2><p>{c(copy[2], copy[3])}</p>
    <Link href="/explore" className="gold-button">{c("Explore the collection", "探索馆藏")} ↗︎</Link>
  </GlassPanel><details className="optional-preview"><summary>{c(copy[4], copy[5])}<span>{c("Optional example", "可选示例")}</span></summary>
    <p className="preview-explanation">{c("This preview uses scripted examples. It does not connect to live AI services.", "此预览使用预设示例，未连接真实 AI 服务。")}</p>{children}
  </details></div>;
}

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
  const c = useCopy(); const { journey, setJourney } = useVisit();
  const { duration, theme, appliedDuration, appliedTheme } = journey;
  const stops = journey.ids.map(id => demoExhibits.find(e => e.id === id)!).filter(Boolean);
  const setStops = (next: typeof stops) => setJourney(previous => ({ ...previous, ids: next.map(e => e.id) }));
  const setDuration = (duration: number) => setJourney(previous => ({ ...previous, duration }));
  const setTheme = (theme: string) => setJourney(previous => ({ ...previous, theme }));
  const dirty = duration !== appliedDuration || theme !== appliedTheme;
  const regenerate = () => { let total = 0; const next = demoExhibits.filter(e => { if (theme !== "all" && e.theme !== theme) return false; if (total + e.minutes > duration) return false; total += e.minutes; return true; }); setJourney(previous => ({ ...previous, ids: next.map(e => e.id), appliedDuration: duration, appliedTheme: theme })); };
  const move = (index: number, direction: number) => { const next = [...stops]; [next[index], next[index + direction]] = [next[index + direction], next[index]]; setStops(next); };
  const total = stops.reduce((sum, e) => sum + e.minutes, 0);
  return <div className="journey-layout"><div className="journey-controls">
    <MuseumSelect compact label={c("Interests", "兴趣")} value={theme} onChange={setTheme} options={[{ value: "all", label: c("All interests", "所有兴趣") }, ...[["Craft", "工艺"], ["Music", "音乐"], ["Food", "饮食"]].map(([value, zh]) => ({ value, label: c(value, zh) }))]} />
    <MuseumSelect compact label={c("Time", "时长")} value={String(duration)} onChange={value => setDuration(Number(value))} options={[5, 10, 20, 30].map(value => ({ value: String(value), label: `${value} ${c("minutes", "分钟")}` }))} />
    <GoldButton onClick={regenerate}>{c("Apply — Shape my route", "应用 — 生成我的路线")} ↗︎</GoldButton>
  </div><GlassPanel className="journey-route"><div className="panel-heading"><h2>{c("Your next discoveries", "您的下一站发现")}</h2><span className="demo-tag" aria-live="polite">{stops.length} {c("stops", "站")} · {total} / {appliedDuration} {c("min", "分钟")}</span></div>
    {dirty && <p role="status" className="journey-draft">{c("Draft criteria changed. This route still uses the last applied time and interests; apply to update it.", "草稿条件已修改。当前路线仍使用上次应用的时长与兴趣，请应用以更新。")}</p>}
    <p className="fine-print">{c("Separate example tour: Shaanxi, Fujian and Guangdong. This is not a Liaoning route. The plan stays in memory during this visit; reload or close clears it. Durable saving is not connected.", "独立示例游览：陕西、福建和广东。这不是辽宁路线。计划仅在本次访问的内存中保留，刷新或关闭后清除。持久保存尚未连接。")}</p>
    <button className="text-button" onClick={() => setJourney({ ids: demoExhibits.map(e => e.id), duration: 20, theme: "all", appliedDuration: 20, appliedTheme: "all" })}>{c("Reset example plan", "重置示例计划")}</button>
    <p className="fine-print">{c("A digital learning route · illustrative stops, not physical travel directions.", "数字学习路线 · 示例站点，不是实际旅行导航。")}</p>
    {!stops.length ? <p className="empty-state">{c("Not enough time for an eligible demo stop. Increase the duration or change your interests.", "没有符合时长的演示站点，请增加时长或更换兴趣。")}</p> : <ol className="journey-stops">{stops.map((e, i) => <li key={e.id}><span className="stop-number">{String(i + 1).padStart(2, "0")}</span><h3>{c(e.region[0], e.region[1])}</h3><button className="text-button" onClick={() => open(c(e.title[0], e.title[1]))}>{c(e.title[0], e.title[1])} ↗︎</button><span className="fine-print">{e.minutes} {c("min", "分钟")}</span><div className="stop-actions"><button className="icon-button" aria-label={`${c("Move up", "上移")} ${e.id}`} disabled={i === 0} onClick={() => move(i, -1)}>↑</button><button className="icon-button" aria-label={`${c("Move down", "下移")} ${e.id}`} disabled={i === stops.length - 1} onClick={() => move(i, 1)}>↓</button><button className="text-button" aria-label={`${c("Remove", "移除")} ${e.id}`} onClick={() => setStops(stops.filter(s => s.id !== e.id))}>{c("Remove", "移除")}</button></div></li>)}</ol>}
    {total > appliedDuration && <p role="status">{c("This route exceeds your selected time. Regenerate or remove a stop.", "路线超出所选时长，请重新生成或删除站点。")}</p>}
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
    <MuseumSelect label={c("Choose a demo scenario", "选择演示场景")} value={state} onChange={setState} options={[["related", "Related object class", "相关物件类别"], ["unknown", "Unknown object", "未知物件"], ["poor", "Insufficient image", "图像不足"], ["denied", "Permission denied", "权限被拒绝"], ["unavailable", "Service unavailable", "服务不可用"]].map(([value, en, zh]) => ({ value, label: c(en, zh) }))} />
    <div className="lens-result" aria-live="polite" aria-busy={busy}><span className="lens-symbol" aria-hidden="true">{busy ? "◌" : state === "related" ? "◇" : "?"}</span><h3>{busy ? c("Comparing demo…", "正在比较演示…") : c(...message[state])}</h3><p>{state === "related" ? c("Visible silhouette and articulated shapes suggest a puppet-like object in this scripted example. Similarity is not identity or authentication.", "在此脚本示例中，轮廓和关节形状提示类似偶人的物件。相似性不代表身份或鉴定。") : state === "poor" ? c("Try a clear, well-lit photograph of the object and its label when capture is available.", "拍摄功能开放后，请提供清晰、光线充足的物件及标签照片。") : state === "denied" ? c("Camera access is not requested by this demo. This is a permission-error preview.", "本演示不会请求相机权限，此处仅预览权限错误。") : c("No live recognition is connected. This demo does not upload images or claim a catalog identity.", "尚未连接真实识别服务，本演示不会上传图像或宣称目录身份。")}</p></div>
    <GoldButton disabled={busy} onClick={() => void compare()}>{c("Replay simulation", "重播模拟")} ↻</GoldButton><button className="text-button" onClick={() => open()}>{c("Inspect catalog requirements", "查看目录要求")} ↗︎</button>
  </GlassPanel>;
}

function Guide({ open }: { open: OpenSource }) {
  const c = useCopy(); const { guide, setGuide } = useVisit(); const question = guide.draft;
  const busy = guide.turns.some(turn => turn.pending);
  const send = async () => {
    if (!question.trim() || busy || guide.turns.length >= 20) return;
    const id = crypto.randomUUID();
    setGuide(previous => ({ draft: "", turns: [...previous.turns, { id, question: question.trim(), pending: true }] }));
    await new Promise(resolve => setTimeout(resolve, 500));
    setGuide(previous => ({ ...previous, turns: previous.turns.map(turn => turn.id === id ? { ...turn, pending: false } : turn) }));
  };
  return <div className="guide-layout"><GlassPanel className="chat-panel"><span className="demo-tag">{c("SCRIPTED DEMO · NO MODEL CALL", "脚本演示 · 无模型调用")}</span>
    <p className="fine-print">{c("Draft and up to 20 turns stay in memory while you navigate this visit. Reload, close or Clear conversation removes them. Nothing is sent to a model or saved on a server; scripted replies do not use conversation history as AI context.", "草稿与最多20轮对话仅在本次访问的内存中保留。刷新、关闭或清除对话后移除。内容不会发送给模型或保存到服务器；脚本回答不会将历史作为 AI 上下文。")}</p>
    <button className="text-button" onClick={() => setGuide({ draft: "", turns: [] })}>{c("Clear conversation", "清除对话")}</button>
    <div className="chat-history" aria-live="polite" aria-busy={busy}>{!guide.turns.length && <p className="chat-answer">{c("Explore a reviewed exhibit, or try this conversation preview. Answers here are scripted examples.", "探索审核展览，或尝试此对话预览。此处回答均为预设示例。")}</p>}{guide.turns.map(turn => <article className="chat-turn" key={turn.id}><p className="eyebrow">{c("YOU", "您")}</p><div className="chat-question">{turn.question}</div><p className="eyebrow">{c("GUIDE", "向导")}</p><p className="chat-answer">{turn.pending ? c("Loading the scripted response…", "正在加载脚本回答…") : c("This is a recorded UI demonstration, so I cannot answer your question from evidence yet. Browse the reviewed collection, or inspect the source requirements below.", "这是预设界面演示，目前无法根据证据回答您的问题。您可以浏览审核馆藏，或查看下方来源要求。")}</p></article>)}<button className="source-pill" onClick={() => open()}>{c("Demo provenance & source requirements", "演示出处与来源要求")} ↗︎</button></div>
    {guide.turns.length >= 20 && <p role="status">{c("This preview has reached 20 turns. Clear the conversation to start again.", "此预览已达到20轮。请清除对话以重新开始。")}</p>}
    <form className="guide-composer" onSubmit={e => { e.preventDefault(); void send(); }}><label className="sr-only" htmlFor="guide-question">{c("Ask the guide", "向向导提问")}</label><textarea id="guide-question" maxLength={2000} rows={2} value={question} onChange={e => setGuide(previous => ({ ...previous, draft: e.target.value }))} placeholder={c("Ask about a tradition…", "询问文化传统…")} /><GoldButton type="submit" disabled={!question.trim() || busy || guide.turns.length >= 20}>{c("Send", "发送")} ↑</GoldButton></form>
    <div className="composer-bottom"><small>{question.length} / 2000</small><button className="text-button" disabled aria-describedby="voice-availability">{c("Voice — unavailable", "语音 — 尚未开放")} ◉</button></div><p id="voice-availability" className="fine-print">{c("Live microphone transcription is unavailable. Type your question instead.", "实时麦克风转写尚未开放，请输入您的问题。")}</p>
  </GlassPanel></div>;
}

function Dna({ open }: { open: OpenSource }) {
  const c = useCopy(); const [weights, setWeights] = useState([0, 0, 0, 0]); const [editing, setEditing] = useState(false); const [example, setExample] = useState(false);
  const names = [["Craft", "工艺"], ["Legends", "传说"], ["Music", "音乐"], ["Food culture", "饮食文化"]]; const strongest = weights.indexOf(Math.max(...weights));
  return <div className="dna-layout"><GlassPanel className="dna-panel"><h2>{c("Your cultural constellation", "您的文化星图")}</h2>
    {example && <p className="demo-tag">{c("Example interests · not your profile", "示例兴趣 · 非您的档案")}</p>}
    {weights.every(v => v === 0) && <p className="interest-intro">{c("Nothing selected yet. Choose a little, a lot, or leave any theme open.", "尚未选择兴趣。您可以选择不同程度，也可以保留任何主题为空。")}</p>}
    <InterestChart weights={weights} /><p className="fine-print">{c("Only the preferences you choose here. Changes stay on this page; no tracking or profile is saved.", "仅使用您在此选择的偏好。修改保留在此页面，不会追踪或保存个人档案。")}</p>
    <div className="compact-actions"><GoldButton onClick={() => setEditing(!editing)} aria-expanded={editing}>{editing ? c("Done", "完成") : c("Edit interests", "编辑兴趣")}</GoldButton><button className="outline-button" onClick={() => { setWeights([0, 0, 0, 0]); setExample(false); }}>{c("Reset", "重置")}</button></div>
    {editing && <fieldset className="interest-edit"><legend>{c("How curious are you?", "您对哪些主题感到好奇？")}</legend>{names.map(([en, zh], i) => <label key={en}>{c(en, zh)}<input type="range" min="0" max="100" value={weights[i]} onChange={e => { setExample(false); setWeights(weights.map((v, j) => i === j ? Number(e.target.value) : v)); }} /><output>{weights[i]}</output></label>)}</fieldset>}
    <button className="text-button" onClick={() => { setWeights([78, 64, 53, 41]); setExample(true); }}>{c("Try example interests", "尝试示例兴趣")}</button>
  </GlassPanel><GlassPanel className="recommendation-panel"><p className="eyebrow">{c(example ? "EXAMPLE DISCOVERY" : "A DIRECTION TO EXPLORE", example ? "示例探索方向" : "探索方向")}</p><h2>{weights.every(v => v === 0) ? c("Begin with curiosity", "从好奇开始") : c(names[strongest][0], names[strongest][1])}</h2><p>{weights.every(v => v === 0) ? c("The collection is open to everyone. Choose interests whenever you like.", "馆藏向所有人开放。您可以随时选择兴趣。") : c("Your strongest selected interest offers a starting direction. Browse the reviewed collection to see what is available.", "您选择的最强兴趣提供探索方向。浏览审核馆藏，了解现有展览。")}</p><Link className="gold-button" href="/explore">{c("Browse reviewed exhibits", "浏览审核展览")} ↗︎</Link><button className="text-button" onClick={() => open(c("About these interests", "关于这些兴趣"))}>{c("About this preview", "关于此预览")} ↗︎</button></GlassPanel></div>;
}

function Sources({ open }: { open: OpenSource }) {
  const c = useCopy(); const steps = [["Community voice", "社群声音", "Attribution + consent", "署名与同意"], ["Reviewed record", "审核记录", "Claims + media rights", "事实与媒体权利"], ["AI experience", "AI 体验", "Citations + uncertainty", "引用与不确定性"], ["Visitor", "访客", "Explore and ask", "探索与提问"]];
  return <div className="sources-layout"><div className="source-summary"><span className="demo-tag">{c("0 published sources", "0 条已发布来源")}</span><span className="demo-tag">{c("EN / 中文", "中文 / EN")}</span><span className="demo-tag">{c("Human review required", "需要人工审核")}</span></div><GlassPanel className="evidence-panel"><h2>{c("How an answer is built", "答案如何形成")}</h2><div className="evidence-chain">{steps.map(([en, zh, note, zn], i) => <button key={en} onClick={() => open(c(en, zh))}><span className="eyebrow">0{i + 1}</span><h3>{c(en, zh)}</h3><p>{c(note, zn)}</p><span aria-hidden="true">↗︎</span></button>)}</div><p className="fine-print">{c("No reviewed records are published yet. Inspect a stage to learn its requirements.", "尚未发布经审核的记录。查看任一阶段以了解其要求。")}</p></GlassPanel></div>;
}

export function MuseumExperiences({ page, mode, initialExhibitId }: { page: PageKey; mode: "demo" | "live"; initialExhibitId?: string }) {
  const c = useCopy(); const [source, setSource] = useState<string | null>(null); const open: OpenSource = title => setSource(title || "");
  if (page === "explore" || page === "sources") return <><CatalogExperience page={page} mode={mode} initialExhibitId={initialExhibitId} fixture={<div className="fixture-content">{page === "explore" ? <Explore open={open} /> : <Sources open={open} />}</div>} /><SourceDrawer open={source !== null} title={source || undefined} onClose={() => setSource(null)} /></>;
  if (mode !== "demo") return <><ExhibitContext page={page} identifier={initialExhibitId} /><GlassPanel className="experience-panel"><p className="eyebrow">{c("LIVE MODE", "实时模式")}</p><h2>{c("This experience is not available yet.", "此功能尚未开放。")}</h2><p>{c("This capability’s live API is not connected. Published exhibits and sources are available in Explore. Demo fixtures are disabled in live mode.", "此功能的真实 API 尚未连接。探索页面提供已发布展览与来源。实时模式不提供演示资料。")}</p><Link href="/status" className="outline-button">{c("Check services", "检查服务")}</Link></GlassPanel></>;
  const screens: Partial<Record<PageKey, React.ReactNode>> = { explore: <Explore open={open} />, journey: <Journey open={open} />, stories: <Stories open={open} />, lens: <Lens open={open} />, guide: <Guide open={open} />, dna: <Dna open={open} />, sources: <Sources open={open} /> };
  return <><ExhibitContext page={page} identifier={initialExhibitId} canDraft /><div className="fixture-content">{page === "journey" || page === "lens" || page === "guide" ? <ExperiencePreview page={page}>{screens[page]}</ExperiencePreview> : screens[page]}</div><SourceDrawer open={source !== null} title={source || undefined} onClose={() => setSource(null)} /></>;
}
