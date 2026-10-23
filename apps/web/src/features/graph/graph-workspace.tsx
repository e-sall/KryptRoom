"use client";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Button, ButtonLink, StatusView, type ViewState } from "@/components/ui";
import type { ExampleRoom } from "@/features/rooms/preview-model";
import { graphFixture, longGraph } from "./fixtures";
import { buildGraph, type GraphMode } from "./model";
import { StateCanvas } from "./state-canvas";
import { GraphInspector, type InspectorTab } from "./graph-inspector";
import "./graph.css";

export function GraphWorkspace({ room, initialSelected }: { room: ExampleRoom; initialSelected?: string }) {
  const [mode, setMode] = useState<GraphMode>("classic");
  const [previousMode, setPreviousMode] = useState<"classic" | "detailed">("classic");
  const [selected, setSelected] = useState<string | null>(() =>
    graphFixture(room.id).find((s) => s.id === initialSelected)?.id ?? graphFixture(room.id).at(-1)?.id ?? null);
  const [tab, setTab] = useState<InspectorTab>("Overview");
  const [scenario, setScenario] = useState<"normal" | ViewState>("normal");
  const [stress, setStress] = useState(false);
  const graph = useMemo(() => buildGraph(stress ? longGraph : graphFixture(room.id)), [room.id, stress]);
  const visible = (scenario === "normal" || scenario === "blocked") && graph.states.length > 0;
  const state = visible ? graph.states.find((s) => s.id === selected) : undefined;
  function changeMode(next: GraphMode) {
    if (next === "focus" && mode !== "focus") setPreviousMode(mode);
    if (next === "focus" && !selected) setSelected(graph.states.at(-1)?.id ?? null);
    setMode(next);
  }
  const inspector = <GraphInspector graph={graph} state={state} detailed={mode === "detailed"}
    tab={tab} onTab={setTab} onSelect={setSelected} blocked={scenario === "blocked"} />;
  return <AppShell preview activeModule="graph" previewRoomId={room.id} graphHref={`/preview/rooms/${room.id}/workspace`}
    contextLabel={state ? `${state.id} · ${state.title} · synthetic` : "No state selected"}
    inspector={inspector} pageHeader={<div className="graph-header">
      <div><p className="eyebrow">{room.name} · SYNTHETIC PREVIEW</p>
        <h1>State Graph</h1><p>RoomState lineage and contextual inspection</p></div>
      <div className="segmented-control" role="group" aria-label="Graph mode">
        {(["classic", "detailed", "focus"] as const).map((m) =>
          <button key={m} aria-pressed={mode === m} onClick={() => changeMode(m)}>{m[0].toUpperCase() + m.slice(1)}</button>)}
      </div>
    </div>}>
    <div className="graph-workspace">
      <div className="graph-navigation"><ButtonLink href={`/preview/rooms/${room.id}`}>Back to Room details</ButtonLink>
        <ButtonLink href="/preview/rooms">All example Rooms</ButtonLink>
        <ButtonLink href={`/preview/rooms/${room.id}/computations`}>Explore Computations</ButtonLink>
        <ButtonLink href={`/preview/rooms/${room.id}/results`}>Explore Results</ButtonLink>
        {mode === "focus" && <Button onClick={() => setMode(previousMode)}>Return to full view</Button>}
        <Button disabled>Proofs &amp; Provenance · PR5</Button><Button disabled>Activity · PR5</Button></div>
      <p className="caption">Illustrative topology, not M1–M7 runtime lineage. No computation, proof or transaction.</p>
      {visible ? <StateCanvas graph={graph} selected={selected} onSelect={setSelected} mode={mode} /> :
        <div className="graph-panel graph-system-state"><StatusView
          state={scenario === "normal" ? "empty" : scenario}
          title={scenario === "normal" || scenario === "empty" ? "Your graph starts here." : scenario === "unavailable" ? "Workspace service unavailable" : undefined}
          description={scenario === "normal" || scenario === "empty" ? "No synthetic states in this view. No real operation can be created here." : undefined}
          action={<Button onClick={() => setScenario("normal")}>Reset display example</Button>} /></div>}
      <p className="sr-only" role="status">{state ? `Selected ${state.id}: ${state.title}` : "No state selected"}</p>
      <details className="scenario-controls">
        <summary>Graph display examples</summary>
        <div className="segmented-control" role="group" aria-label="Graph system states">
          {(["normal", "empty", "loading", "blocked", "error", "unavailable"] as const).map((s) =>
            <button key={s} aria-pressed={scenario === s} onClick={() => setScenario(s)}>{s}</button>)}
        </div>
        <label className="graph-stress"><input type="checkbox" checked={stress} onChange={(e) => {
          setStress(e.target.checked); setSelected(null); setScenario("normal");
        }} />Long DAG · 24 synthetic states</label>
        <p className="caption">Display scenarios only. No service response, permission or operation is simulated as authoritative.</p>
      </details>
    </div>
  </AppShell>;
}
