import { useId } from "react";
import { Badge, Button } from "@/components/ui";
import type { Graph, GraphState } from "./model";
export type InspectorTab = "Overview" | "Inputs" | "Outputs" | "Metadata";

export function GraphInspector({ state, graph, detailed, tab, onTab, onSelect, blocked = false }: {
  state?: GraphState; graph: Graph; detailed: boolean; tab: InspectorTab;
  onTab: (tab: InspectorTab) => void; onSelect: (id: string) => void; blocked?: boolean;
}) {
  const id = useId();
  if (!state) return <div className="graph-inspector"><p className="eyebrow">STATE INSPECTOR</p>
    <h2>No state selected</h2><p className="caption">Select an example node to inspect its metadata. No real RoomState is loaded.</p></div>;
  const relations = <><dt>Parents · ordered</dt><dd>{state.parent_state_ids.length
    ? state.parent_state_ids.map((p) => <button className="graph-relation" key={p} onClick={() => onSelect(p)}>Inspect parent {p}</button>) : "None · root state"}</dd>
    <dt>Children</dt><dd>{graph.edges.filter((e) => e.parent === state.id).map((e) =>
      <button className="graph-relation" key={e.child} onClick={() => onSelect(e.child)}>Inspect child {e.child}</button>)}
      {!graph.edges.some((e) => e.parent === state.id) && "None"}</dd></>;
  return <div className="graph-inspector">
    <p className="eyebrow">STATE INSPECTOR · SYNTHETIC</p>
    <p className="graph-state-id">STATE {state.id}</p><h2>{state.title}</h2>
    <span className="badge badge-preview">Sample state · not a runtime record</span>
    {blocked && <p className="graph-blocked">Disclosure restricted · example. No permission grant is available.</p>}
    {detailed && <div className="graph-tabs" role="tablist" aria-label="State details"
      onKeyDown={(event) => {
        const tabs: InspectorTab[] = ["Overview", "Inputs", "Outputs", "Metadata"];
        const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
        if (step || event.key === "Home" || event.key === "End") {
          event.preventDefault();
          const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tabs.indexOf(tab) + step + 4) % 4;
          onTab(tabs[next]);
          (event.currentTarget.children[next] as HTMLElement).focus();
        }
      }}>
      {(["Overview", "Inputs", "Outputs", "Metadata"] as const).map((t) =>
        <button key={t} role="tab" id={`${id}-${t}`} aria-controls={`${id}-panel`}
          tabIndex={t === tab ? 0 : -1} aria-selected={t === tab} onClick={() => onTab(t)}>{t}</button>)}
    </div>}
    <div role={detailed ? "tabpanel" : undefined} id={`${id}-panel`} aria-labelledby={detailed ? `${id}-${tab}` : undefined}>
      {(!detailed || tab === "Overview") && <dl className="graph-facts">
        <dt>State ID</dt><dd>{state.id}</dd>{relations}
        <dt>Transition</dt><dd>{state.operation}</dd>
        <dt>Protection</dt><dd>Illustrative only · no payload loaded</dd>
        <dt>Proof verification</dt><dd><Badge status="not-assessed" /></dd>
        <dt>Chain anchor</dt><dd>Unavailable · no chain record</dd>
      </dl>}
      {detailed && tab === "Inputs" && <><dl className="graph-facts">{relations}</dl>
        <p className="caption">Ordered dependencies only. No source data or private input content is displayed.</p></>}
      {detailed && tab === "Outputs" && <><h3>Protected reference labels</h3>
        <ul>{state.artifactLabels.map((a) => <li key={a}><code>{a}</code></li>)}</ul>
        {!state.artifactLabels.length && <p>No example artifact references.</p>}
        <p className="caption">Fictional opaque labels, not resolvable artifact URIs. No result attached.</p></>}
      {detailed && tab === "Metadata" && <dl className="graph-facts">
        <dt>CryptoContext</dt><dd>{state.contextLabel}</dd>
        <dt>StatePolicy</dt><dd>Disclosure denied · no authoritative grant</dd>
        <dt>StateCommitment</dt><dd>Unavailable · no digest fabricated</dd>
        <dt>Provenance</dt><dd>P03/P04 synthetic presentation fixture</dd>
        <dt>Immutability</dt><dd>View-only; prior states are never edited</dd>
      </dl>}
    </div>
    {!detailed && <p className="caption">Detailed view includes context and protected reference labels.</p>}
    <Button disabled>Authorized result unavailable</Button>
    <p className="caption">A commitment is not a verified proof. Proofs &amp; Provenance and Activity are reserved for PR5.</p>
  </div>;
}
