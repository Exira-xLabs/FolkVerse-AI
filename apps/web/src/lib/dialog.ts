/** Visible keyboard targets, including native disclosures and SVG controls. */
export function tabbableElements(root: Element) {
  return [...root.querySelectorAll<HTMLElement>("button, a[href], input, select, textarea, summary, [tabindex]")]
    .filter(node => node.tabIndex >= 0 && !node.matches(":disabled") && !node.closest("[inert], [hidden]")
      && node.getClientRects().length > 0 && getComputedStyle(node).visibility !== "hidden");
}

export function trapDialogTab(event: { key: string; shiftKey: boolean; preventDefault: () => void; currentTarget: Element }) {
  if (event.key !== "Tab") return;
  const items = tabbableElements(event.currentTarget), first = items[0], last = items.at(-1);
  if (!first || !last) return;
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
}

let locks = 0;
let restore: (() => void) | undefined;
/** Fix the document in place while a modal scrolls; nested modals share the lock. */
export function lockDocumentScroll() {
  if (locks++ === 0) {
    const body = document.body, html = document.documentElement;
    const x = window.scrollX, y = window.scrollY;
    const properties = ["position", "top", "left", "right", "width", "overflow"] as const;
    const previous = properties.map(key => [key, body.style[key]] as const);
    const htmlOverflow = html.style.overflow;
    body.style.position = "fixed"; body.style.top = `${-y}px`; body.style.left = `${-x}px`;
    body.style.right = "0"; body.style.width = "100%"; body.style.overflow = "hidden";
    html.style.overflow = "hidden";
    restore = () => {
      for (const [key, value] of previous) body.style[key] = value;
      html.style.overflow = htmlOverflow;
      window.scrollTo({ left: x, top: y, behavior: "instant" });
    };
  }
  let released = false;
  return () => { if (!released) { released = true; if (--locks === 0) { restore?.(); restore = undefined; } } };
}
