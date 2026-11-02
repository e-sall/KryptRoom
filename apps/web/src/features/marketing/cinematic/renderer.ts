import artwork from "./artwork.json";
import * as originals from "./renderers.js";
import { clamp, duration, durations, ease, position } from "./timeline";

const NS = "http://www.w3.org/2000/svg";
type Art = { tag: string; attrs: Record<string, string>; text: string; children: Art[] };
type Shape = { key: string; tag: string; attrs: Record<string, string>; text: string; source: string };
type Frame = { shapes: Shape[]; cursor: { x: number; y: number; opacity: number } };
const factories = [originals.clip01, originals.clip02, originals.clip03, originals.clip04, originals.clip05,
  originals.clip06, originals.clip07, originals.clip08, originals.clip10, originals.clip11, originals.clip12];
const inherited = ["fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin", "font-family", "font-size", "font-weight", "letter-spacing", "text-anchor", "fill-opacity", "stroke-opacity"];
const geometry = ["x", "y", "cx", "cy", "width", "height", "rx", "ry", "r"];

function make(art: Art): SVGElement {
  const node = document.createElementNS(NS, art.tag === "svg" ? "g" : art.tag);
  for (const [name, value] of Object.entries(art.attrs)) {
    if (!/^(?:on|href|xmlns|viewBox)/i.test(name)) node.setAttribute(name, value);
  }
  if (art.text) node.textContent = art.text;
  art.children.forEach(child => node.append(make(child)));
  return node;
}
function attrs(node: Element) { return Object.fromEntries([...node.attributes].map(a => [a.name, a.value])); }
function distance(a: Shape, b: Shape) {
  if (a.tag !== b.tag || (a.tag === "text" && a.text !== b.text) || (a.tag === "path" && a.attrs.d !== b.attrs.d)) return Infinity;
  return geometry.reduce((s, k) => s + Math.abs(Number(a.attrs[k] || 0) - Number(b.attrs[k] || 0)), 0);
}
function interpolate(a: string, b: string, p: number): string {
  if (a === b) return b;
  if (/^#[0-9a-f]{6}$/i.test(a) && /^#[0-9a-f]{6}$/i.test(b)) {
    return "#" + [1, 3, 5].map(i => Math.round(parseInt(a.slice(i, i + 2), 16) * (1 - p) + parseInt(b.slice(i, i + 2), 16) * p).toString(16).padStart(2, "0")).join("");
  }
  const numbers = /-?\d*\.?\d+(?:e[-+]?\d+)?/gi;
  if (a.replace(numbers, "#") === b.replace(numbers, "#")) {
    const old = a.match(numbers) || []; let i = 0;
    return b.replace(numbers, n => String(Number(old[i++]) * (1 - p) + Number(n) * p));
  }
  return p < .5 ? a : b;
}

/** Attribute-level seam patch. Matching shapes retain identity; no full-frame fade or camera transform. */
function join(a: Shape[], b: Shape[], p: number): Shape[] {
  if (p <= 0) return a;
  if (p >= 1) return b;
  const before = new Map(a.map(s => [s.key, s]));
  const after = new Set(b.map(s => s.key));
  const result: Shape[] = a.filter(s => !after.has(s.key)).map(s => ({ ...s, attrs: { ...s.attrs, opacity: String(Number(s.attrs.opacity) * (1 - p)) } }));
  for (const shape of b) {
    const prior = before.get(shape.key);
    const next = { ...shape, attrs: { ...shape.attrs } };
    if (!prior) next.attrs.opacity = String(Number(shape.attrs.opacity) * p);
    else for (const name of new Set([...Object.keys(prior.attrs), ...Object.keys(shape.attrs)])) {
      const from = prior.attrs[name] ?? (name === "opacity" ? "1" : "0");
      const to = shape.attrs[name] ?? (name === "opacity" ? "1" : "0");
      next.attrs[name] = interpolate(from, to, p);
    }
    result.push(next);
  }
  return result;
}

export function createMovie(svg: SVGSVGElement) {
  const defs = document.createElementNS(NS, "defs"); defs.setAttribute("aria-hidden", "true");
  const paint = document.createElementNS(NS, "g"); paint.dataset.moviePaint = "true"; paint.setAttribute("aria-hidden", "true");
  const cursor = document.createElementNS(NS, "g"); cursor.dataset.movieCursor = "true"; cursor.setAttribute("aria-hidden", "true");
  const pointer = document.createElementNS(NS, "path");
  for (const [k, v] of Object.entries({ d: "M1 1 V24 L7 18 L12 30 L18 27 L13 16 L22 16 Z", fill: "#F1F0EB", stroke: "#101011", "stroke-width": "2", "stroke-linejoin": "round" })) pointer.setAttribute(k, v);
  // Scale the original vector around its authored tip (1,1), preserving its hotspot.
  pointer.setAttribute("transform", "translate(1 1) scale(.5) translate(-1 -1)");
  cursor.append(pointer); svg.append(defs, paint, cursor);
  const roots = (artwork as unknown as Art[]).map(a => { const root = make(a) as SVGGElement; defs.append(root); return root; });
  const renders = roots.map((root, i) => factories[i](root));
  // Exact source IDs stay in non-rendering definitions only. Public paint has stable, independent keys.
  const keyMaps = roots.map(() => new Map<string, string>());
  let keySequence = 0;
  function snapshot(sourceIndex: number, time: number): Frame {
    renders[sourceIndex](time);
    const root = roots[sourceIndex];
    const shapes: Shape[] = [];
    let mouse = { x: 680, y: 410, opacity: 0 };
    let leaf = 0;
    function walk(node: Element, parent: Record<string, string>, transform: string, opacity: number) {
      if (node.tagName === "defs") return;
      const own = attrs(node);
      const alpha = opacity * Number(own.opacity ?? 1);
      const combined = [transform, own.transform].filter(Boolean).join(" ");
      if (/cursor|pointer$/i.test(own.id || "")) {
        const xy = /translate\(([-\d.]+)[ ,]+([-\d.]+)/.exec(combined);
        if (xy) mouse = { x: Number(xy[1]), y: Number(xy[2]), opacity: alpha };
        return;
      }
      const style = { ...parent };
      inherited.forEach(k => { if (own[k] !== undefined) style[k] = own[k]; });
      if (node.children.length) { [...node.children].forEach(child => walk(child, style, combined, alpha)); return; }
      const source = `${sourceIndex}-${leaf++}`;
      // Original transparent click targets are never interactive or painted on the homepage.
      if (/hit/i.test(own.id || "") || own.fill === "transparent") return;
      const all: Record<string, string> = { ...style, ...own, opacity: String(alpha), transform: combined };
      delete all.id;
      delete all.style;
      const key = keyMaps[sourceIndex].get(source) || source;
      shapes.push({ key, source, tag: node.tagName, text: node.textContent || "", attrs: all });
    }
    walk(root, { "font-family": "Arial,Helvetica,sans-serif" }, "", 1);
    return { shapes, cursor: mouse };
  }
  // Bind matching artwork across clips once. Shared chrome and matching content keep the same DOM node.
  let previous: Shape[] = [];
  roots.forEach((_, i) => {
    const start = snapshot(i, 0).shapes;
    const available = previous.filter(s => Number(s.attrs.opacity) > .99);
    for (const shape of start) {
      let match = -1; let best = 45;
      if (Number(shape.attrs.opacity) > .99) available.forEach((candidate, index) => {
        const d = distance(candidate, shape);
        if (d < best) { best = d; match = index; }
      });
      const key = match >= 0 ? available.splice(match, 1)[0].key : `p12-${keySequence++}`;
      keyMaps[i].set(shape.source, key);
    }
    previous = snapshot(i, durations[i < 8 ? i : i + 1]).shapes;
  });
  const startFrames = roots.map((_, i) => snapshot(i, 0));
  const endFrames = roots.map((_, i) => snapshot(i, durations[i < 8 ? i : i + 1]));
  const panel = (s: Shape) => {
    const x = Number(s.attrs.x ?? s.attrs.cx ?? 0), y = Number(s.attrs.y ?? s.attrs.cy ?? 0);
    return (x >= 787 && y >= 317 && y <= 538) || (s.tag === "path" && /^M1035 511/.test(s.attrs.d || ""));
  };
  const overview = endFrames[7];
  const detail = startFrames[8];
  const detailFrame = [...overview.shapes.filter(s => !panel(s)), ...detail.shapes.filter(panel)];
  const painted = new Map<string, SVGElement>();
  function display(shapes: Shape[], mouse: Frame["cursor"]) {
    const visible = shapes.filter(s => Number(s.attrs.opacity) > .0001);
    const active = new Set(visible.map(s => s.key));
    for (const [key, element] of painted) if (!active.has(key)) element.setAttribute("display", "none");
    let previousElement: SVGElement | null = null;
    for (const shape of visible) {
      let element = painted.get(shape.key);
      if (!element) { element = document.createElementNS(NS, shape.tag); painted.set(shape.key, element); }
      element.removeAttribute("display");
      for (const attr of [...element.attributes]) if (!(attr.name in shape.attrs) && attr.name !== "data-shape") element.removeAttribute(attr.name);
      for (const [k, v] of Object.entries(shape.attrs)) if (element.getAttribute(k) !== v) element.setAttribute(k, v);
      element.dataset.shape = shape.key;
      if (element.textContent !== shape.text) element.textContent = shape.text;
      const expected: ChildNode | null = previousElement ? previousElement.nextSibling : paint.firstChild;
      if (expected !== element) paint.insertBefore(element, expected);
      previousElement = element;
    }
    cursor.setAttribute("transform", `translate(${mouse.x} ${mouse.y})`);
    cursor.setAttribute("opacity", String(mouse.opacity));
  }
  const startCursor = [0, 640, 480, 550, 550, 550, 0, 0, 400, 0, 410];
  function renderAt(ms: number) {
    const { index, local } = position(ms);
    let frame: Frame;
    if (index === 8) {
      // SPEC-ONLY adaptation: retain every overview pixel outside the right panel.
      const p = ease((local - 900) / 750);
      frame = { shapes: join(overview.shapes, detailFrame, p), cursor: { x: 930, y: 511, opacity: 1 } };
      const tap = clamp((local - 740) / 190);
      frame.shapes = [...frame.shapes, { key: "adaptation-click", source: "09-10-adaptation", tag: "circle", text: "", attrs: { cx: "930", cy: "511", r: String(9 + tap * 17), fill: "none", stroke: "#C4D8E5", "stroke-width": "1.5", opacity: String(local >= 740 && local < 930 ? (1 - tap) * .7 : 0) } }];
    } else {
      const i = index < 8 ? index : index - 1;
      frame = snapshot(i, local);
      if (index === 9) {
        // Preserve the complete 08→09 graph until the original Ask AI navigation occurs.
        const p = ease((local - 1600) / 350);
        frame.shapes = join(detailFrame, frame.shapes, p);
      }
      if (i > 0 && local < startCursor[i] && startCursor[i] > 0) {
        const before = i === 8 ? { x: 930, y: 511, opacity: 1 } : endFrames[i - 1].cursor;
        const p = ease(local / startCursor[i]);
        frame.cursor = { x: before.x + (frame.cursor.x - before.x) * p,
          y: before.y + (frame.cursor.y - before.y) * p - 12 * Math.sin(Math.PI * p), opacity: before.opacity + (frame.cursor.opacity - before.opacity) * p };
      }
      // Reconcile source-export differences during the existing ending hold, never at the time boundary.
      // The 08→09→10 dashboard is deliberately exempt: its stationary graph is retained verbatim.
      if (index < 11 && index !== 7 && local > durations[index] - 450) {
        const next = startFrames[i + 1];
        frame.shapes = join(frame.shapes, next.shapes, ease((local - durations[index] + 450) / 450));
      }
    }
    display(frame.shapes, frame.cursor);
    svg.dataset.time = String(Math.min(duration, Math.max(0, ms)));
    svg.dataset.clip = String(index + 1);
    return frame;
  }
  renderAt(0);
  return { renderAt, destroy() { defs.remove(); paint.remove(); cursor.remove(); } };
}
