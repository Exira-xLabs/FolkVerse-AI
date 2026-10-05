"use client";

import { useEffect, useId, useLayoutEffect, useRef, useState, type KeyboardEvent } from "react";
import { createPortal } from "react-dom";

type Option = { value: string; label: string };

export function MuseumSelect({ label, value, options, onChange, compact = false }: {
  label: string;
  value: string;
  options: Option[];
  onChange: (value: string) => void;
  compact?: boolean;
}) {
  const id = useId();
  const trigger = useRef<HTMLButtonElement>(null);
  const menu = useRef<HTMLDivElement>(null);
  const search = useRef({ text: "", time: 0 });
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const selected = Math.max(0, options.findIndex(option => option.value === value));
  const reveal = (index = selected) => { setActive(index); setOpen(true); };
  const choose = (index: number) => {
    onChange(options[index].value);
    setOpen(false);
    trigger.current?.focus({ preventScroll: true });
  };

  // Render outside glass panels so overflow and backdrop filters cannot clip the menu.
  useLayoutEffect(() => {
    if (!open) return;
    const position = () => {
      const button = trigger.current, popup = menu.current;
      if (!button || !popup) return;
      const rect = button.getBoundingClientRect();
      const width = Math.min(Math.max(rect.width, 240), window.innerWidth - 24);
      const below = window.innerHeight - rect.bottom - 20, above = rect.top - 20;
      const upward = below < Math.min(320, popup.scrollHeight) && above > below;
      popup.style.width = `${width}px`;
      popup.style.maxHeight = `${Math.min(320, Math.max(80, upward ? above : below))}px`;
      popup.style.left = `${Math.max(12, Math.min(rect.left, window.innerWidth - width - 12))}px`;
      popup.style.top = `${upward ? Math.max(12, rect.top - popup.getBoundingClientRect().height - 8) : rect.bottom + 8}px`;
      popup.classList.toggle("select-menu-simple", !!button.closest(".reduced-graphics"));
    };
    position();
    window.addEventListener("resize", position);
    window.addEventListener("scroll", position, true);
    const dismiss = (event: PointerEvent) => {
      if (!trigger.current?.contains(event.target as Node) && !menu.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("pointerdown", dismiss);
    return () => {
      window.removeEventListener("resize", position);
      window.removeEventListener("scroll", position, true);
      document.removeEventListener("pointerdown", dismiss);
    };
  }, [open]);

  useEffect(() => {
    if (open) document.getElementById(`${id}-option-${active}`)?.scrollIntoView({ block: "nearest" });
  }, [active, open, id]);

  const keyboard = (event: KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === "Tab") { setOpen(false); return; }
    if (event.key === "Escape") {
      if (open) { event.preventDefault(); event.stopPropagation(); setOpen(false); }
      return;
    }
    if (["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
      event.preventDefault();
      const next = event.key === "Home" ? 0 : event.key === "End" ? options.length - 1
        : Math.max(0, Math.min(options.length - 1, (open ? active : selected) + (event.key === "ArrowDown" ? 1 : -1)));
      reveal(next); return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (open) choose(active); else reveal();
      return;
    }
    if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      const now = Date.now();
      const text = (now - search.current.time < 700 ? search.current.text : "") + event.key.toLocaleLowerCase();
      search.current = { text, time: now };
      const query = [...text].every(character => character === text[0]) ? text[0] : text;
      const start = query.length === 1 ? (open ? active : selected) + 1 : 0;
      for (let offset = 0; offset < options.length; offset++) {
        const index = (start + offset) % options.length;
        if (options[index].label.toLocaleLowerCase().startsWith(query)) { reveal(index); break; }
      }
    }
  };

  return <div className={`museum-select ${compact ? "select-pill" : "field"}`}>
    <span id={`${id}-label`} className="select-label">{label}</span>
    <button ref={trigger} type="button" className="select-trigger" role="combobox"
      aria-labelledby={`${id}-label`} aria-expanded={open} aria-haspopup="listbox"
      aria-controls={open ? `${id}-list` : undefined} aria-activedescendant={open ? `${id}-option-${active}` : undefined}
      onClick={() => { if (open) setOpen(false); else reveal(); }} onKeyDown={keyboard}
      onBlur={event => { if (!menu.current?.contains(event.relatedTarget as Node)) setOpen(false); }}>
      <span className="select-value">{options[selected]?.label}</span>
      <svg className="select-chevron" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m5 7.5 5 5 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
    </button>
    {open && createPortal(<div ref={menu} id={`${id}-list`} className="select-menu" role="listbox" aria-labelledby={`${id}-label`}>
      {options.map((option, index) => <button type="button" key={option.value} id={`${id}-option-${index}`} role="option"
        aria-selected={option.value === value} tabIndex={-1} className={`select-option ${active === index ? "is-active" : ""}`}
        onMouseDown={event => event.preventDefault()} onPointerMove={() => setActive(index)} onClick={() => choose(index)}>
        <span>{option.label}</span><svg className="select-check" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m4 10 4 4 8-8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>
      </button>)}
    </div>, document.body)}
  </div>;
}
