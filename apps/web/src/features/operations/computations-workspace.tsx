"use client";
import Link from "next/link";
import { useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Button, ButtonLink } from "@/components/ui";
import type { ExampleRoom } from "@/features/rooms/preview-model";
import { graphFixture } from "@/features/graph/fixtures";
import { operationIds, operations, phases, selectedInputs, presentationReadiness, previewRoomPath, statePath, type OperationId, type Phase } from "./presentation";
import { RoomChooser, RoomTrail, DisplayExamples, UnavailableDisplay, type DisplayScenario } from "./preview-controls";
import { WorkflowDiagram } from "./workflow-diagram";
import { ComputationInspector } from "./computation-inspector";
import "./operations.css";

export function ComputationsWorkspace({ room }: { room: ExampleRoom }) {
  const states = graphFixture(room.id);
  const [operation, setOperation] = useState<OperationId>("join");
  const [ids, setIds] = useState<string[]>(states[0] ? [states[0].id] : []);
  const [phase, setPhase] = useState<Phase>(0);
  const [tab, setTab] = useState<"Readiness" | "Review">("Readiness");
  const [error, setError] = useState("");
  const [scenario, setScenario] = useState<DisplayScenario>("normal");
  const visible = scenario === "normal" && states.length > 0;
  const inputs = selectedInputs(states, ids);
  const readiness = presentationReadiness(states, ids);
  function go(next: Phase) {
    if (next > 0 && !readiness.presentationComplete) { setError("Select at least one illustrative input state. This is not an execution prerequisite check."); return; }
    setError(""); setPhase(next); setTab(next === 2 ? "Review" : "Readiness");
  }
  function reset() { setOperation("join"); setIds(states[0] ? [states[0].id] : []); setPhase(0); setTab("Readiness"); setError(""); setScenario("normal"); }
  return <AppShell preview previewRoomId={room.id} activeModule="computations"
    contextLabel={visible ? `${operations[operation].title} · ${phases[phase]} · preview only` : "No operation context"}
    pageHeader={<div className="operation-header"><p className="eyebrow">{room.name} · SYNTHETIC PREVIEW</p><h1>Computations</h1>
      <p>Protected inputs. A private operation. A new possibility.</p><RoomChooser roomId={room.id} screen="computations" /></div>}
    inspector={<ComputationInspector visible={visible} operation={operation} inputs={visible ? inputs : []} phase={phase} tab={tab} onTab={setTab} />}>
    <RoomTrail roomId={room.id} screen="computations" />
    <p className="operation-boundary">Explore a hypothetical workflow. No computation, state creation or disclosure occurs.</p>
    {visible ? <>
      <div className="operation-picker" role="group" aria-label="Operation example">
        {operationIds.map((id) => <button key={id} aria-pressed={operation === id} onClick={() => { setOperation(id); go(0); }}>
          <span className="eyebrow">{operations[id].number} · SAMPLE</span><strong>{operations[id].title}</strong>
        </button>)}
      </div>
      <section className="operation-panel" aria-label="Workflow preparation">
        <div className="operation-panel-heading"><span className="eyebrow">WORKFLOW PREVIEW</span><span className="caption">NOT EXECUTABLE</span></div>
        <ol className="workflow-phases" aria-label="Presentation phases">{phases.map((name, i) => <li key={name}>
          <button aria-current={phase === i ? "step" : undefined} onClick={() => go(i as Phase)}><span>0{i + 1}</span>{name}</button>
        </li>)}</ol>
        <WorkflowDiagram inputs={inputs} operation={operation} phase={phase} onPhase={go} />
        <div className="workflow-editor">
          <h2>{phases[phase]}</h2>
          {phase === 0 && <><p className="caption">Choose state references, not data. Selection order becomes the hypothetical parent order.</p>
            <fieldset aria-describedby="input-guidance"><legend>Illustrative input states</legend><div className="input-choices">{states.map((state) =>
              <label key={state.id}><input type="checkbox" checked={ids.includes(state.id)} onChange={(e) => { setIds(e.target.checked ? [...ids, state.id] : ids.filter((id) => id !== state.id)); setError(""); }} />
                <span><strong>{state.id} · {state.title}</strong><small>Parents: {state.parent_state_ids.join(" · ") || "None"}</small></span></label>)}</div></fieldset>
            <p className="caption" id="input-guidance">Fictional references are non-resolvable. No file upload, artifact lookup or local data connection.</p>
            <details><summary>Protected reference labels &amp; dependencies</summary><ul>{inputs.map((s) => <li key={s.id}>
              <Link href={statePath(room.id, s.id)}>{s.id} · inspect in Graph</Link><p className="caption">{s.artifactLabels.join(" · ") || "No artifact label on this root"}</p>
            </li>)}</ul></details></>}
          {phase === 1 && <><p>{operations[operation].explanation}</p><p className="caption">{operations[operation].requirement}</p>
            <p className="operation-caution">This visual step does not execute {operations[operation].code}. No timer, run ID or progress percentage exists.</p></>}
          {phase === 2 && <><p>These ordered parents could support a new immutable state under an authoritative policy.</p>
            <p className="caption">Parents: {ids.join(" → ")}. The dashed node is hypothetical, has no state ID or commitment, and is never added to the existing graph.</p>
            <ButtonLink href={`${previewRoomPath(room.id, "results")}/${operation}`}>Explore fixed result example</ButtonLink>
            <p className="caption">The result example is a separate fixed fixture, not produced from your selections.</p></>}
          {error && <p role="alert" className="operation-error">{error}</p>}
          <div className="workflow-actions"><Button disabled={phase === 0} onClick={() => go((phase - 1) as Phase)}>Previous phase</Button>
            {phase < 2 && <Button variant="primary" onClick={() => go((phase + 1) as Phase)}>Next phase</Button>}
            <Button onClick={reset}>Reset preview</Button></div>
        </div>
      </section>
    </> : <UnavailableDisplay value={scenario === "normal" ? "empty" : scenario} onReset={reset} />}
    <DisplayExamples value={scenario} onChange={(value) => { setScenario(value); setError(""); }} />
  </AppShell>;
}
