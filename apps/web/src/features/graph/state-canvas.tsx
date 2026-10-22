"use client";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { Button } from "@/components/ui";
import { edgePath, fitViewport, layoutGraph, zoomViewport, type Viewport } from "./layout";
import { neighborhood, type Graph, type GraphMode } from "./model";

export function StateCanvas({ graph, selected, onSelect, mode }: {
  graph: Graph; selected: string | null; onSelect: (id: string | null) => void; mode: GraphMode;
}) {
  const canvas = useRef<HTMLDivElement>(null);
  const nodes = useRef(new Map<string, HTMLButtonElement>());
  const drag = useRef<{ x: number; y: number; view: Viewport; moved: boolean } | null>(null);
  const [size, setSize] = useState({ width: 700, height: 480 });
  const [manualView, setManualView] = useState<{ key: string; value: Viewport } | null>(null);
  const [hover, setHover] = useState<string | null>(null);
  const arrowId = useId().replaceAll(":", "");
  const helpId = useId();
  const layout = useMemo(() => layoutGraph(graph, mode === "detailed", size.width < 520), [graph, mode, size.width]);
  const viewKey = `${mode}:${size.width}:${size.height}:${layout.width}:${layout.height}:${mode === "focus" ? selected : ""}`;
  const focusPosition = mode === "focus" && selected ? layout.positions.get(selected) : undefined;
  const defaultView = focusPosition ? {
    x: size.width / 2 - (focusPosition.x + focusPosition.width / 2),
    y: size.height / 2 - (focusPosition.y + focusPosition.height / 2), scale: 1,
  } : fitViewport(size.width, size.height, layout.width, layout.height);
  const view = manualView?.key === viewKey ? manualView.value : defaultView;
  function setView(update: Viewport | ((previous: Viewport) => Viewport)) {
    setManualView((previous) => ({ key: viewKey, value: typeof update === "function"
      ? update(previous?.key === viewKey ? previous.value : defaultView) : update }));
  }
  const related = neighborhood(graph, selected);
  const fit = () => setView(fitViewport(size.width, size.height, layout.width, layout.height));
  const center = (id: string, scale = view.scale) => {
    const p = layout.positions.get(id);
    if (p) setView({ x: size.width / 2 - (p.x + p.width / 2) * scale,
      y: size.height / 2 - (p.y + p.height / 2) * scale, scale });
  };
  useEffect(() => {
    const element = canvas.current;
    if (!element) return;
    const observer = new ResizeObserver(([entry]) => setSize({
      width: entry.contentRect.width, height: entry.contentRect.height,
    }));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  const zoom = (factor: number) => setView((v) => zoomViewport(v, factor, size.width / 2, size.height / 2));
  function selectAndCenter(id: string) {
    onSelect(id); center(id, Math.max(0.8, view.scale));
    canvas.current?.scrollIntoView({ block: "center" });
    nodes.current.get(id)?.focus({ preventScroll: true });
  }
  return <section className="graph-panel" aria-label="Interactive synthetic lineage">
    <div className="graph-caption"><span className="eyebrow">ROOMSTATE LINEAGE</span><span>{graph.states.length} SAMPLE STATES</span></div>
    <div ref={canvas} className="graph-canvas" role="region" aria-label="State graph canvas"
      aria-describedby={helpId} tabIndex={0}
      onPointerDown={(e) => {
        if (e.button !== 0 || (e.target as HTMLElement).closest("button")) return;
        e.currentTarget.focus({ preventScroll: true });
        e.currentTarget.setPointerCapture(e.pointerId);
        drag.current = { x: e.clientX, y: e.clientY, view, moved: false };
      }}
      onPointerMove={(e) => {
        const start = drag.current;
        if (!start) return;
        const dx = e.clientX - start.x, dy = e.clientY - start.y;
        if (Math.abs(dx) + Math.abs(dy) > 4) start.moved = true;
        setView({ ...start.view, x: start.view.x + dx, y: start.view.y + dy });
      }}
      onPointerUp={() => { if (drag.current && !drag.current.moved) onSelect(null); drag.current = null; }}
      onPointerCancel={() => { drag.current = null; }}
      onLostPointerCapture={() => { drag.current = null; }}
      onWheel={(e) => {
        // Modifier zoom leaves ordinary page scrolling and browser zoom available.
        if (e.altKey) zoom(e.deltaY < 0 ? 1.12 : 1 / 1.12);
      }}
      onKeyDown={(e) => {
        if ((e.target as HTMLElement).closest("button")) return;
        if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(e.key)) {
          e.preventDefault();
          setView((v) => ({ ...v, x: v.x + (e.key === "ArrowLeft" ? 40 : e.key === "ArrowRight" ? -40 : 0),
            y: v.y + (e.key === "ArrowUp" ? 40 : e.key === "ArrowDown" ? -40 : 0) }));
        } else if (e.key === "+" || e.key === "=") { e.preventDefault(); zoom(1.2); }
        else if (e.key === "-") { e.preventDefault(); zoom(1/1.2); }
        else if (e.key.toLowerCase() === "f") { e.preventDefault(); fit(); }
        else if (e.key === "Escape") onSelect(null);
      }}>
      <div className="graph-plane" data-testid="graph-plane" style={{
        width: layout.width, height: layout.height, transform: `translate(${view.x}px, ${view.y}px) scale(${view.scale})`,
      }}>
        <svg width={layout.width} height={layout.height} className="graph-edges" aria-hidden="true">
          <defs><marker id={arrowId} markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
            <path d="M0 0 L7 3.5 L0 7" fill="context-stroke" /></marker></defs>
          {graph.edges.map((edge) => <path key={`${edge.parent}-${edge.child}`}
            data-edge={`${edge.parent}-${edge.child}`} data-parent-index={edge.parentIndex}
            className={`graph-edge${[selected, hover].some((id) => id === edge.parent || id === edge.child) ? " highlighted" : ""}${mode === "focus" && ![edge.parent, edge.child].includes(selected ?? "") ? " subdued" : ""}`}
            d={edgePath(layout.positions.get(edge.parent)!, layout.positions.get(edge.child)!, layout.vertical)}
            markerEnd={`url(#${arrowId})`} />)}
        </svg>
        {graph.states.map((state, index) => {
          const p = layout.positions.get(state.id)!;
          const expanded = mode === "detailed";
          return <button key={state.id} ref={(el) => { if (el) nodes.current.set(state.id, el); else nodes.current.delete(state.id); }}
            className={`graph-node${expanded ? " detailed" : ""}${mode === "focus" && !related.has(state.id) ? " subdued" : ""}`}
            style={{ left: p.x, top: p.y, width: p.width, minHeight: p.height }}
            aria-label={`State ${state.id}: ${state.title}`} aria-pressed={selected === state.id}
            onMouseEnter={() => setHover(state.id)} onMouseLeave={() => setHover(null)}
            onFocus={() => {
              setHover(state.id);
              const left = view.x + p.x * view.scale, top = view.y + p.y * view.scale;
              if (left < 0 || top < 0 || left + p.width * view.scale > size.width || top + p.height * view.scale > size.height)
                center(state.id, Math.max(0.8, view.scale));
            }}
            onBlur={() => setHover(null)}
            onClick={() => onSelect(selected === state.id ? null : state.id)}
            onKeyDown={(e) => {
              let target: string | undefined;
              if (e.key === "ArrowLeft") target = state.parent_state_ids[0];
              if (e.key === "ArrowRight") target = graph.edges.find((edge) => edge.parent === state.id)?.child;
              if (e.key === "ArrowDown") target = graph.states[(index + 1) % graph.states.length]?.id;
              if (e.key === "ArrowUp") target = graph.states[(index - 1 + graph.states.length) % graph.states.length]?.id;
              if (e.key === "Home") target = graph.states[0]?.id;
              if (e.key === "End") target = graph.states.at(-1)?.id;
              if (target) { e.preventDefault(); e.stopPropagation(); selectAndCenter(target); }
              if (e.key === "Escape") { e.preventDefault(); onSelect(null); canvas.current?.focus(); }
            }}>
            <span className="graph-state-id">{state.id}</span><strong>{state.title}</strong>
            <span className="graph-sample">Sample</span>
            {expanded && <span className="graph-node-extra">{state.operation}<br />
              {state.parent_state_ids.length} parent references</span>}
            {!expanded && selected === state.id && view.scale >= 1.15 &&
              <span className="graph-node-peek">Parents: {state.parent_state_ids.join(" · ") || "None"}</span>}
          </button>;
        })}
      </div>
    </div>
    <div className="graph-controls">
      <span className="caption">{mode === "detailed" ? "Detailed · progressive metadata" : mode === "focus" ? "Focus · selected neighborhood" : "Classic · compact nodes"}</span>
      <div className="button-row" role="group" aria-label="Graph viewport">
        <Button aria-label="Zoom out" onClick={() => zoom(1/1.2)} disabled={view.scale <= 0.02}>−</Button>
        <output aria-label="Graph zoom">{Math.round(view.scale * 100)}%</output>
        <Button aria-label="Zoom in" onClick={() => zoom(1.2)} disabled={view.scale >= 2}>+</Button>
        <Button onClick={fit}>Fit View</Button>
        <Button disabled={!selected} onClick={() => selected && center(selected, 1)}>Center selected</Button>
      </div>
    </div>
    <p className="caption graph-help" id={helpId}>Drag the background to pan. Canvas: arrows pan, +/− zoom, F fits. Nodes: ← parent, → child, ↑/↓ browse, Escape deselects. Use the ordered list for every parent.</p>
    <details className="graph-accessible-list"><summary>Ordered state list · accessible navigation</summary>
      <ol>{graph.states.map((state) => <li key={state.id}>
        <button className="graph-relation" aria-pressed={selected === state.id} onClick={() => selectAndCenter(state.id)}>
          {state.id} · {state.title}</button><span className="caption">Parents: {state.parent_state_ids.join(", ") || "none"}</span>
      </li>)}</ol>
    </details>
  </section>;
}
