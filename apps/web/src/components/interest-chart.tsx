"use client";

import { useLocale } from "./locale-provider";

const themes = [
  { id: "craft", en: "Craft", zh: "工艺", icon: "M5 12 12 5l7 7-7 7-7-7Zm0 0h14M12 5v14" },
  { id: "legends", en: "Legends", zh: "传说", icon: "M12 7c-3-2-6-2-9-2v13c3 0 6 0 9 2 3-2 6-2 9-2V5c-3 0-6 0-9 2Zm0 0v13" },
  { id: "music", en: "Music", zh: "音乐", icon: "M9 17V6l10-2v11M9 9l10-2M9 17c0 2-5 3-5 0s5-3 5 0Zm10-2c0 2-5 3-5 0s5-3 5 0Z" },
  { id: "food", en: "Food culture", zh: "饮食文化", icon: "M3 11h18c0 6-4 9-9 9s-9-3-9-9Zm4-6v2m5-4v4m5-2v2M7 21h10" },
] as const;

const center = { x: 160, y: 132 };
const orbitRadius = 92;
const nodeRadius = 18;
const nodeCircumference = 2 * Math.PI * nodeRadius;

function orbitPoint(index: number, radius: number) {
  const angle = -3 * Math.PI / 4 + index * Math.PI / 2;
  return { x: center.x + Math.cos(angle) * radius, y: center.y + Math.sin(angle) * radius };
}

function ThemeIcon({ path, size = 22, x, y }: { path: string; size?: number; x?: number; y?: number }) {
  return <svg aria-hidden="true" x={x} y={y} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d={path} /></svg>;
}

export function InterestChart({ weights, onChange }: { weights: number[]; onChange?: (index: number, value: number) => void }) {
  const { locale } = useLocale();
  const zh = locale !== "en";
  const points = themes.map((_, index) => {
    const point = orbitPoint(index, 28 + weights[index] * .64);
    return `${point.x},${point.y}`;
  }).join(" ");

  return <div className="interest-chart">
    <div className="constellation-canvas">
      <span className="constellation-caption">{zh ? "好奇心，由您定义" : "CURIOSITY, SHAPED BY YOU"}</span>
      <svg className="constellation-map" viewBox="0 0 320 264" aria-hidden="true">
        <circle cx={center.x} cy={center.y} r="110" className="constellation-orbit outer-orbit" />
        <circle cx={center.x} cy={center.y} r={orbitRadius} className="constellation-orbit" />
        <circle cx={center.x} cy={center.y} r="56" className="constellation-orbit inner-orbit" />
        {themes.map((theme, index) => {
          const point = orbitPoint(index, orbitRadius);
          return <path key={theme.id} d={`M${center.x} ${center.y} ${point.x} ${point.y}`} className="constellation-ray" />;
        })}
        <polygon points={points} className="constellation-shape" />
        {themes.map((theme, index) => {
          const point = orbitPoint(index, orbitRadius);
          const label = orbitPoint(index, orbitRadius + 33);
          return <g key={theme.id} data-theme={theme.id} className="constellation-accent">
            <circle cx={point.x} cy={point.y} r={nodeRadius} className="constellation-node" />
            <circle cx={point.x} cy={point.y} r={nodeRadius} className="constellation-node-progress" strokeDasharray={`${weights[index] / 100 * nodeCircumference} ${nodeCircumference}`} transform={`rotate(-90 ${point.x} ${point.y})`} />
            <ThemeIcon path={theme.icon} size={20} x={point.x - 10} y={point.y - 10} />
            <text x={label.x} y={label.y + 4} textAnchor="middle" className="constellation-index">0{index + 1}</text>
          </g>;
        })}
        <circle cx={center.x} cy={center.y} r="22" className="constellation-center" />
        <path d="m160 117 4 11 11 4-11 4-4 11-4-11-11-4 11-4Z" className="constellation-spark" />
        {themes.map((theme, index) => {
          const angle = -Math.PI / 2 + index * Math.PI / 2;
          return <circle key={theme.id} cx={center.x + Math.cos(angle) * 110} cy={center.y + Math.sin(angle) * 110} r="2" data-theme={theme.id} className="constellation-accent constellation-dot" />;
        })}
      </svg>
      <p className="constellation-hint">{zh ? "四种兴趣，无限探索方向" : "Four interests. Endless paths to explore."}</p>
    </div>
    <dl className="constellation-themes">{themes.map((theme, index) => {
      const name = zh ? theme.zh : theme.en;
      const value = weights[index];
      return <div key={theme.id} className="constellation-theme" data-theme={theme.id}>
        <dt><button type="button" disabled={!onChange} aria-label={`${name} ${value} / 100 · ${zh ? "修改兴趣" : "Change interest"}`} onClick={() => onChange?.(index, value >= 100 ? 0 : Math.min(100, value + 25))}>
          <ThemeIcon path={theme.icon} /><span>{name}</span><span className="theme-add" aria-hidden="true">+</span>
        </button></dt>
        <dd>{value} / 100<span className="interest-bar" aria-hidden="true"><span style={{ width: `${value}%` }} /></span></dd>
      </div>;
    })}</dl>
    {onChange && <p className="theme-interaction-hint">{zh ? "点击主题增加兴趣，或编辑兴趣以精确调整。" : "Tap a theme to add interest, or edit for finer control."}</p>}
  </div>;
}
