"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { lockDocumentScroll, trapDialogTab } from "@/lib/dialog";
import geography from "@/lib/maps/liaoning-geography.json";
import cityBoundaries from "@/lib/maps/liaoning-city-boundaries.json";
import { useLocale } from "./locale-provider";

export const atlasCities = geography.cities;
const WIDTH = 1120, HEIGHT = 880;
const [west, south, east, north] = geography.bounds;
const cosine = Math.cos((south + north) / 2 * Math.PI / 180);
const unit = Math.min((WIDTH - 200) / ((east - west) * cosine), (HEIGHT - 150) / (north - south));
const left = (WIDTH - (east - west) * cosine * unit) / 2;
function project(coordinates: number[]) {
  return { x: left + (coordinates[0] - west) * cosine * unit, y: 75 + (north - coordinates[1]) * unit };
}
function geometryPath(coordinates: number[][][][]) {
  return coordinates.map(polygon => polygon.map(ring => ring.map((point, i) => {
  const p = project(point); return `${i ? "L" : "M"}${p.x.toFixed(2)},${p.y.toFixed(2)}`;
}).join(" ") + "Z").join(" ")).join(" ");
}
const outline = geometryPath(geography.geometry.coordinates);
const districts = cityBoundaries.features.map(feature => ({ ...feature.properties, path: geometryPath(feature.geometry.coordinates) }));
const terrainPath = "/folkverse/maps/liaoning-terrain-v2-lossless.webp";
const positions = atlasCities.map(city => ({ ...city, ...project(city.coordinates) }));
const offsets: Record<string, [number, number, number]> = {
  dalian: [65, -32, 126], shenyang: [-60, -57, 140], anshan: [-5, 48, 118], fushun: [101, -15, 120],
  benxi: [94, 5, 110], dandong: [76, 22, 132], jinzhou: [-54, -38, 118], yingkou: [-55, 57, 130],
  fuxin: [-35, -48, 110], liaoyang: [-30, -38, 130], tieling: [40, -45, 118], chaoyang: [-35, -60, 140],
  panjin: [-20, -48, 110], huludao: [-80, 37, 138],
};
type Camera = { x: number; y: number; zoom: number };
const home: Camera = { x: WIDTH / 2, y: HEIGHT / 2, zoom: 1 };
const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));
function bound(camera: Camera): Camera {
  return { x: clamp(camera.x, -120, WIDTH + 120), y: clamp(camera.y, -100, HEIGHT + 100), zoom: clamp(camera.zoom, 1, 4.5) };
}

function fittedCamera(id: string): Camera {
  const district = districts.find(city => city.id === id);
  if (!district) return home;
  const [w, s, e, n] = district.land_bounds;
  const a = project([w, n]), b = project([e, s]);
  const zoom = clamp(Math.min((WIDTH - 280) / (b.x - a.x), (HEIGHT - 180) / (b.y - a.y)), 1, 3.3);
  return bound({ x: (a.x + b.x) / 2 - 90 / zoom, y: (a.y + b.y) / 2, zoom });
}

export function LiaoningAtlas({ selectedId, onSelect, availableIds, availability }: { selectedId: string; onSelect: (id: string) => void; availableIds: string[]; availability: "loading" | "ready" | "error" }) {
  const { locale } = useLocale(); const zh = locale !== "en";
  const [cameraState, setCameraState] = useState(() => ({ selection: selectedId, camera: fittedCamera(selectedId) }));
  if (cameraState.selection !== selectedId) {
    setCameraState({ selection: selectedId, camera: fittedCamera(selectedId) });
  }
  const camera = cameraState.selection === selectedId ? cameraState.camera : fittedCamera(selectedId);
  const setCamera = useCallback((update: Camera | ((camera: Camera) => Camera)) => {
    setCameraState(previous => {
      const current = previous.selection === selectedId ? previous.camera : fittedCamera(selectedId);
      return { selection: selectedId, camera: typeof update === "function" ? update(current) : update };
    });
  }, [selectedId]);
  const [stageSize, setStageSize] = useState({ width: WIDTH, height: HEIGHT });
  const [full, setFull] = useState(false);
  const [terrainReady, setTerrainReady] = useState(false);
  const [cityQuery, setCityQuery] = useState("");
  const root = useRef<HTMLElement>(null); const svg = useRef<SVGSVGElement>(null);
  const modal = useRef<HTMLDialogElement>(null);
  const expandTrigger = useRef<HTMLElement | null>(null);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const drag = useRef<{ x: number; y: number; camera: Camera; moved: boolean } | null>(null);
  const pinch = useRef<{ distance: number; camera: Camera } | null>(null);
  const suppressClick = useRef(false);
  const key = useId().replace(/:/g, "");
  const selected = positions.find(city => city.id === selectedId);
  const selectedDistrict = districts.find(city => city.id === selectedId);
  const zoom = useCallback((factor: number) => setCamera(c => bound({ ...c, zoom: c.zoom * factor })), [setCamera]);
  const view = { x: camera.x - WIDTH / camera.zoom / 2, y: camera.y - HEIGHT / camera.zoom / 2, width: WIDTH / camera.zoom, height: HEIGHT / camera.zoom };
  const labelScale = 1 / Math.max(.001, Math.min(stageSize.width / WIDTH, stageSize.height / HEIGHT) * camera.zoom);
  const choose = (id: string) => {
    if (suppressClick.current) return;
    onSelect(id);
    setCameraState({ selection: id, camera: fittedCamera(id) });
  };
  useEffect(() => {
    const node = svg.current;
    if (!node) return;
    const resize = () => {
      const { width, height } = node.getBoundingClientRect();
      setStageSize(previous => previous.width === width && previous.height === height ? previous : { width, height });
    };
    resize(); const observer = new ResizeObserver(resize); observer.observe(node);
    return () => observer.disconnect();
  }, [full]);
  useEffect(() => {
    const artwork = new Image(); let cancelled = false;
    artwork.src = terrainPath;
    void artwork.decode().then(() => { if (!cancelled) setTerrainReady(true); }).catch(() => {});
    return () => { cancelled = true; };
  }, []);
  useEffect(() => {
    const node = svg.current;
    if (!node) return;
    const wheel = (event: WheelEvent) => {
      event.preventDefault();
      const matrix = node.getScreenCTM(); if (!matrix) return;
      const anchor = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse());
      setCamera(c => { const next = clamp(c.zoom * (event.deltaY > 0 ? .87 : 1.15), 1, 4.5);
        return bound({ zoom: next, x: anchor.x + (c.x-anchor.x)*c.zoom/next,
          y: anchor.y + (c.y-anchor.y)*c.zoom/next }); });
    };
    node.addEventListener("wheel", wheel, { passive: false });
    return () => node.removeEventListener("wheel", wheel);
  }, [full, setCamera]);
  useEffect(() => {
    const node = modal.current;
    if (!full || !node) return;
    node.showModal();
    const unlock = lockDocumentScroll();
    return () => {
      node.close(); unlock();
      requestAnimationFrame(() => {
        const trigger = expandTrigger.current?.isConnected ? expandTrigger.current : document.querySelector<HTMLButtonElement>(".atlas-expand-button");
        trigger?.focus({ preventScroll: true });
      });
    };
  }, [full]);
  const atlas = <section ref={root} className={`liaoning-atlas ${full ? "atlas-expanded" : ""}`} aria-label={zh ? "辽宁交互地图" : "Interactive map of Liaoning"} data-terrain-ready={terrainReady}>
    <div className="atlas-topbar"><div><span className="eyebrow">{zh ? "探索图鉴 / 辽宁" : "EXPLORER’S ATLAS / LIAONING"}</span><h2>{zh ? "十四座城，无数种相遇。" : "Fourteen cities. A world to discover."}</h2></div><span className="atlas-edition">{zh ? "辽宁省 · 01" : "LIAONING · 01"}</span></div>
    <div className="atlas-stage">
      <svg ref={svg} className="atlas-world" viewBox={`${view.x} ${view.y} ${view.width} ${view.height}`} tabIndex={0} role="group" aria-label={zh ? "拖动地图，缩放并选择城市" : "Drag map, zoom and choose a city"} data-zoom={camera.zoom.toFixed(2)}
        onKeyDown={event => {
          if (event.target !== event.currentTarget) return;
          const direction: Record<string, [number, number]> = { ArrowLeft: [-70, 0], ArrowRight: [70, 0], ArrowUp: [0, -70], ArrowDown: [0, 70] };
          if (direction[event.key]) { event.preventDefault(); const [x,y] = direction[event.key]; setCamera(c => bound({ ...c, x: c.x+x/c.zoom, y: c.y+y/c.zoom })); }
          if (["+", "="].includes(event.key)) { event.preventDefault(); zoom(1.2); }
          if (event.key === "-") { event.preventDefault(); zoom(1/1.2); }
          if (event.key === "Home") { event.preventDefault(); setCamera(home); }
        }}
        onDoubleClick={event => { if (!(event.target as Element).closest(".atlas-map-target")) zoom(1.5); }}
        onPointerDown={event => {
          if (event.button !== 0) return;
          pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
          if (!(event.target as Element).closest(".atlas-map-target")) svg.current?.setPointerCapture(event.pointerId);
          if (pointers.current.size === 1) { suppressClick.current = false; drag.current = { x: event.clientX, y: event.clientY, camera, moved: false }; }
          if (pointers.current.size === 2) { const [a,b] = [...pointers.current.values()]; pinch.current = { distance: Math.hypot(a.x-b.x, a.y-b.y), camera }; }
        }}
        onPointerMove={event => {
          if (!pointers.current.has(event.pointerId)) return;
          pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
          if (pointers.current.size === 2 && pinch.current) { const [a,b] = [...pointers.current.values()]; const distance = Math.hypot(a.x-b.x,a.y-b.y); setCamera(bound({ ...pinch.current.camera, zoom: pinch.current.camera.zoom * distance / Math.max(pinch.current.distance,1) })); suppressClick.current = true; return; }
          const initial = drag.current; const bounds = svg.current?.getBoundingClientRect(); if (!initial || !bounds) return;
          const dx = event.clientX-initial.x, dy = event.clientY-initial.y;
          if (Math.hypot(dx,dy) > 5) { svg.current?.setPointerCapture(event.pointerId); initial.moved = true; suppressClick.current = true; const scale = Math.min(bounds.width/WIDTH, bounds.height/HEIGHT)*initial.camera.zoom; setCamera(bound({ ...initial.camera, x: initial.camera.x-dx/scale, y: initial.camera.y-dy/scale })); }
        }}
        onPointerUp={event => { pointers.current.delete(event.pointerId); pinch.current = null; drag.current = null; if (svg.current?.hasPointerCapture(event.pointerId)) svg.current.releasePointerCapture(event.pointerId); }}
        onPointerCancel={() => { pointers.current.clear(); pinch.current = null; drag.current = null; }}>
        <defs>
          <clipPath id={`${key}-land`}><path d={outline} fillRule="evenodd" /></clipPath>
          <linearGradient id={`${key}-edge`} x1="0" y1="0" x2="0" y2="1"><stop stopColor="#a7803c"/><stop offset="1" stopColor="#24362f"/></linearGradient>
          <linearGradient id={`${key}-light`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#ffde8c" stopOpacity=".1"/><stop offset="1" stopColor="#082e25" stopOpacity=".32"/></linearGradient>
          <pattern id={`${key}-grid`} width="80" height="80" patternUnits="userSpaceOnUse"><path d="M80 0H0V80" stroke="#95c3c7" strokeOpacity=".08" fill="none"/></pattern>
          <filter id={`${key}-shadow`} x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="22" stdDeviation="20" floodColor="#000" floodOpacity=".6"/></filter>
          <filter id={`${key}-glow`} x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="8"/></filter>
          <radialGradient id={`${key}-marker`} cx=".35" cy=".25" r=".8"><stop stopColor="#466c75"/><stop offset="1" stopColor="#071a23"/></radialGradient>
        </defs>
        <rect x="-2000" y="-2000" width="6000" height="6000" fill={`url(#${key}-grid)`}/>
        <g className="atlas-landscape" filter={`url(#${key}-shadow)`}>
          <path d={outline} transform="translate(0 15)" fill={`url(#${key}-edge)`} stroke="#6f743f" strokeWidth="3" fillRule="evenodd"/>
          <path d={outline} fill="#5b7047"/>
          <g clipPath={`url(#${key}-land)`}><image onLoad={() => setTerrainReady(true)} href={terrainPath} x={left} y="75" width={(east-west)*cosine*unit} height={(north-south)*unit} preserveAspectRatio="none"/><rect x="0" y="0" width={WIDTH} height={HEIGHT} fill={`url(#${key}-light)`}/></g>
          <path className="atlas-coast" d={outline} fill="none" stroke="#edd898" strokeWidth="1.8" vectorEffect="non-scaling-stroke" strokeOpacity=".8"/>
        </g>
        <g clipPath={`url(#${key}-land)`} className="atlas-districts">
          {districts.map(city => <path key={city.id} className="atlas-district atlas-map-target" d={city.path} data-city-id={city.id} fillRule="evenodd" onClick={() => choose(city.id)}><title>{city.names[locale]}</title></path>)}
          {selectedDistrict && <path className="atlas-district-selected" data-city-id={selectedDistrict.id} d={selectedDistrict.path} fillRule="evenodd" aria-hidden="true"/>}
        </g>
        <text className={`atlas-province-name ${selected ? "is-muted" : ""}`} x="350" y="170">{zh ? "辽 宁" : "L I A O N I N G"}</text>
        {positions.map(city => {
          const id = city.id.replace("liaoning-", ""); const [dx,dy,width] = offsets[id]; const picked = city.id === selectedId; const available = availability === "ready" && availableIds.includes(city.id); const label = city.names[locale];
          return <g key={city.id} className={`atlas-city atlas-map-target ${picked ? "is-selected" : ""} ${["dalian", "shenyang"].includes(id) ? "is-major" : ""} ${available ? "has-exhibits" : ""}`} data-city-id={city.id} transform={`translate(${city.x} ${city.y})`} tabIndex={0} role="button" aria-label={zh ? `探索${label}` : `Explore ${label}`} aria-pressed={picked}
            onClick={() => choose(city.id)} onKeyDown={event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); suppressClick.current = false; choose(city.id); } }}>
            <title>{label}</title><g transform={`scale(${1/Math.sqrt(camera.zoom)})`}><circle className="atlas-hit" r="32" fill="transparent"/>
            {picked && <><circle r="30" fill="#ffdf93" opacity=".5" filter={`url(#${key}-glow)`}/><circle className="atlas-selection-ring" r="26" fill="none" stroke="#ffe0a1" strokeWidth="2"/></>}
            <circle className="atlas-marker-shell" r="15" fill={`url(#${key}-marker)`} stroke={picked ? "#ffe2a2" : "#d6e8e8"} strokeWidth="1.6"/>
            <circle r="9" fill="none" stroke="#d6e8e8" strokeOpacity=".3" strokeWidth=".8"/>
            <circle className="atlas-marker-core" r="5" fill={picked || available ? "#ffe1a0" : "#a1e4db"}/>
            </g><g className="atlas-label" transform={`scale(${labelScale})`}><path d={`M0 0L${dx} ${dy}`} fill="none" stroke="#fff0c5" strokeOpacity=".55" strokeWidth="1"/>
              <rect x={dx-width/2} y={dy-22} width={width} height="44" rx="11" fill="#071f22" fillOpacity=".94" stroke={picked ? "#ffe1a0" : "#bfd0ad"} strokeOpacity={picked ? "1" : ".45"}/>
              <text x={dx} y={dy+7} textAnchor="middle" className="atlas-city-name">{label}</text>
              {available && <circle cx={dx+width/2-8} cy={dy-16} r="4" fill="#ffdb8f"/>}
            </g>
          </g>;
        })}
      </svg>
      <div className="atlas-compass" aria-hidden="true"><span>N</span><svg viewBox="0 0 40 54"><path d="M20 4 8 42 20 32Z" fill="#eddaa6"/><path d="M20 4 32 42 20 32Z" fill="#6b8c86"/></svg></div>
      <div className="atlas-camera-controls" aria-label={zh ? "地图控制" : "Map controls"}><button aria-label={zh ? "放大地图" : "Zoom in map"} onClick={() => zoom(1.3)} disabled={camera.zoom >= 4.5}>+</button><button aria-label={zh ? "缩小地图" : "Zoom out map"} onClick={() => zoom(1/1.3)} disabled={camera.zoom <= 1}>−</button><button aria-label={zh ? "显示全省" : "Fit Liaoning province"} onClick={() => setCamera(home)}>⌖</button><button className="atlas-expand-button" autoFocus={full} aria-label={zh ? (full ? "退出全屏地图" : "展开地图") : (full ? "Exit expanded map" : "Expand map")} aria-pressed={full} onClick={event => { if (!full) expandTrigger.current = event.currentTarget; setFull(!full); }}>⛶</button></div>
      <button className="atlas-minimap" aria-label={zh ? "通过小地图重新定位" : "Recenter using minimap"} onClick={event => { const rect=event.currentTarget.getBoundingClientRect(); const x=(event.clientX-rect.left)/rect.width*WIDTH, y=(event.clientY-rect.top)/rect.height*HEIGHT; setCamera(c => bound({ ...c, x, y })); }} onKeyDown={event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setCamera(home); } }}><svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} aria-hidden="true"><path d={outline} fill="#76896a" stroke="#d4c48d" strokeWidth="10"/><rect x={view.x} y={view.y} width={view.width} height={view.height} fill="#e8d19833" stroke="#ffde95" strokeWidth="12"/></svg></button>
      <div className="atlas-map-hint">{zh ? "拖动探索 · 滚动或双指缩放" : "Drag to wander · scroll or pinch to zoom"}</div>
      {selected && <div className="atlas-location" aria-live="polite"><span className="eyebrow">{zh ? "您正在探索" : "YOU ARE EXPLORING"}</span><strong>{selected.names[locale]}</strong><span>{selected.coordinates[1].toFixed(2)}° N · {selected.coordinates[0].toFixed(2)}° E</span><p className="atlas-location-status">{availability === "loading" ? (zh ? "正在检查馆藏…" : "Checking collection…") : availability === "error" ? (zh ? "馆藏服务暂时不可用，请刷新重试。" : "Collection service unavailable. Refresh to try again.") : availableIds.includes(selected.id) ? (zh ? "已有审核展览，可循着来源探索。" : "Reviewed exhibits ready to explore.") : (zh ? "目前没有已发布展览。" : "No published exhibits currently available.")}</p><button onClick={() => { setFull(false); requestAnimationFrame(() => document.getElementById("liaoning-city-collection")?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth" })); }}>{zh ? "查看城市馆藏" : "See city collection"} ↓</button><button onClick={() => { onSelect(""); setCameraState({ selection: "", camera: home }); }}>{zh ? "返回辽宁全省" : "Back to all Liaoning"} ↗</button></div>}
    </div>
    <div className="atlas-bottom"><span><i className="atlas-legend-dot"/>{availability === "loading" ? (zh ? "正在检查馆藏…" : "Checking collection…") : availability === "error" ? (zh ? "馆藏服务暂时不可用" : "Collection service unavailable") : availableIds.some(id => atlasCities.some(city => city.id === id)) ? (zh ? "已有审核展览" : "Reviewed exhibits available") : (zh ? "目前没有已发布展览" : "No published exhibits currently available")}</span><span>{zh ? "真实省市边界 · 地形依高程资料生成，为近似表现。" : "Sourced city borders · AI terrain guided by elevation, approximate."}</span><span className="atlas-attribution"><a href="https://www.naturalearthdata.com/about/terms-of-use/" target="_blank" rel="noopener noreferrer">Natural Earth</a> · <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">© OpenStreetMap contributors</a> · <a href="https://github.com/tilezen/joerd/blob/master/docs/attribution.md" target="_blank" rel="noopener noreferrer">Mapzen / USGS / NOAA</a></span></div>
    <div className="atlas-city-directory"><div className="atlas-directory-heading"><span className="eyebrow">{zh ? "选择一座城市 / 14" : "CHOOSE A CITY / 14"}</span><label><span className="sr-only">{zh ? "搜索辽宁城市" : "Find a Liaoning city"}</span><input value={cityQuery} onChange={e => setCityQuery(e.target.value)} placeholder={zh ? "寻找城市…" : "Find a city…"}/></label></div><div className="atlas-city-grid">{positions.filter(city => `${city.names.en} ${city.names['zh-CN']}`.toLowerCase().includes(cityQuery.toLowerCase())).map(city => <button className={selectedId === city.id ? "selected" : ""} key={city.id} onClick={() => { suppressClick.current=false; choose(city.id); }} aria-label={zh ? `选择${city.names[locale]}` : `Select ${city.names[locale]}`} aria-pressed={selectedId === city.id}><span>{city.names[locale]}</span>{availability === "ready" && availableIds.includes(city.id) ? <i className="atlas-legend-dot"/> : <span className="atlas-city-arrow" aria-hidden="true">↗</span>}</button>)}</div>{!positions.some(city => `${city.names.en} ${city.names['zh-CN']}`.toLowerCase().includes(cityQuery.toLowerCase())) && <p className="fine-print" role="status">{zh ? "没有匹配的城市。" : "No cities match your search."}</p>}</div>
  </section>;
  return full ? createPortal(<dialog ref={modal} className="atlas-dialog" aria-label={zh ? "辽宁全屏交互地图" : "Expanded interactive map of Liaoning"} aria-modal="true"
    onCancel={event => { event.preventDefault(); setFull(false); }} onKeyDown={trapDialogTab}>{atlas}</dialog>, document.body) : atlas;
}
