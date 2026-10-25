"use client";
import Link from "next/link";
import { useId } from "react";
import type { Graph, GraphState } from "@/features/graph/model";
import { statePath } from "@/features/operations/presentation";
import { provenancePath, transitionLabel } from "./presentation";

export function StateLinks({ roomId, state }: { roomId: string; state: GraphState }) {
  return <nav className="provenance-links" aria-label="Selected state destinations">
    <Link href={statePath(roomId, state.id)}>Open {state.id} in Graph</Link>
    <Link href={provenancePath(roomId, "proofs", state.id)}>Provenance of {state.id}</Link>
    <Link href={provenancePath(roomId, "activity", state.id)}>Activity for {state.id}</Link>
  </nav>;
}
export function StateRelations({ graph, state, onSelect }: { graph: Graph; state: GraphState; onSelect: (id: string) => void }) {
  const children = graph.states.filter((s) => s.parent_state_ids.includes(state.id));
  return <div className="provenance-relations">
    <p className="caption">Ordered parents</p><ol aria-label="Ordered parents">{state.parent_state_ids.map((id) => <li key={id}><button onClick={() => onSelect(id)}>{id} · {graph.states.find((s) => s.id === id)?.title}</button></li>)}</ol>
    {!state.parent_state_ids.length && <p className="caption">Root · no parent</p>}
    <p className="caption">Children</p><ul aria-label="Children">{children.map((s) => <li key={s.id}><button onClick={() => onSelect(s.id)}>{s.id} · {s.title}</button></li>)}</ul>
    {!children.length && <p className="caption">No child in this example</p>}
  </div>;
}
/** Semantic HTML nodes and relationship text; decorative SVG connectors never carry unique data. */
export function LineageMap({ graph, selected, onSelect }: { graph: Graph; selected: string; onSelect: (id: string) => void }) {
  const id = useId();
  const ranks = [...new Set(graph.ranks.values())];
  const positions = new Map(graph.states.map((s) => {
    const rank = graph.ranks.get(s.id)!;
    const peers = graph.states.filter((p) => graph.ranks.get(p.id) === rank);
    return [s.id, { x: 1000 * (peers.indexOf(s) + 0.5) / peers.length, y: rank * 184 }];
  }));
  return <figure className="provenance-lineage" aria-labelledby={id}>
    <figcaption id={id}>Illustrative lineage · {selected} selected</figcaption>
    <div className="lineage-dag">
      <svg className="lineage-edges" viewBox={`0 0 1000 ${ranks.length * 184 - 44}`} preserveAspectRatio="none" aria-hidden="true">
        {graph.edges.map((edge) => {
          const a = positions.get(edge.parent)!, b = positions.get(edge.child)!;
          return <path key={edge.parent + edge.child} data-parent={edge.parent} data-child={edge.child}
            data-selected={edge.child === selected || edge.parent === selected}
            d={`M${a.x} ${a.y + 140} C${a.x} ${a.y + 162} ${b.x} ${b.y - 22} ${b.x} ${b.y}`} />;
        })}
      </svg>
    {ranks.map((rank) => <div key={rank} className="lineage-rank">
      <div className="lineage-nodes">{graph.states.filter((s) => graph.ranks.get(s.id) === rank).map((s) =>
        <button key={s.id} aria-pressed={selected === s.id} aria-label={`Select ${s.id} · ${s.title}`} onClick={() => onSelect(s.id)}>
          <span className="eyebrow">{s.id} · SAMPLE</span><strong>{s.title}</strong><small>{transitionLabel(s)}</small>
        </button>)}</div>
    </div>)}</div>
    <p className="caption">Lines show existing parent relationships, not execution. Each node lists its ordered incoming relationship.</p>
  </figure>;
}
