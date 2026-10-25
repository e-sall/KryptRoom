"use client";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Badge, Button } from "@/components/ui";
import { graphFixture } from "@/features/graph/fixtures";
import { buildGraph, type Graph, type GraphState } from "@/features/graph/model";
import type { ExampleRoom } from "@/features/rooms/preview-model";
import { DisplayExamples, RoomChooser, RoomTrail, UnavailableDisplay, type DisplayScenario } from "@/features/operations/preview-controls";
import { stages, stageTitles, evidence, checks, anchorSteps, transitionLabel, type Stage, type Evidence } from "./presentation";
import { LineageMap, StateLinks, StateRelations } from "./shared";
import "@/features/operations/operations.css";
import "./provenance.css";

function ProofInspector({ roomId, graph, state, stage, item, check, onSelect }: {
  roomId: string; graph: Graph; state?: GraphState; stage: Stage; item: Evidence; check: number; onSelect: (id: string) => void;
}) {
  return <div className="operation-inspector provenance-inspector"><p className="eyebrow">PROVENANCE INSPECTOR · SAMPLE</p>
    <h2>{state ? `${state.id} · ${state.title}` : "No state selected"}</h2><Badge status="not-assessed" />
    {state ? <><dl className="operation-facts"><dt>Current stage</dt><dd>{stage}</dd><dt>Transition context · illustrative</dt><dd>{transitionLabel(state)}<br />{state.operation}</dd>
      <dt>Assessment</dt><dd>No verification performed</dd>
      {stage === "Lineage" && <><dt>Lineage source</dt><dd>Existing PR3 presentation catalog · not a runtime receipt</dd></>}
      {stage === "Evidence" && <><dt>Selected evidence category</dt><dd>{item.title} · {item.category}</dd><dt>Availability</dt><dd>{item.id === "references" && state.artifactLabels.length ? `Sample labels only: ${state.artifactLabels.join(" · ")}` : "Unavailable"}</dd><dt>Meaning</dt><dd>{item.detail}</dd></>}
      {stage === "Verification" && <><dt>Selected check concept</dt><dd>{checks[check].title}</dd><dt>Assessment boundary</dt><dd>{checks[check].detail}</dd><dt>Run / verifier / time</dt><dd>Unavailable · no run</dd></>}
      {stage === "Anchoring" && <><dt>Chain record / inclusion / finality</dt><dd>Unavailable · no chain source connected</dd><dt>Historical acceptance evidence</dt><dd>Separate from these synthetic states. No historic transaction is attached here.</dd></>}
    </dl><StateRelations graph={graph} state={state} onSelect={onSelect} /><StateLinks roomId={roomId} state={state} /></> : <p className="caption">No stale evidence or assessment is shown in this display state.</p>}
    <p className="operation-caution">A visualization is not a verified proof. A commitment is not a finalized anchor.</p>
    <div className="operation-denied"><Button disabled>Verify proof · unavailable</Button><Button disabled>Anchor state · unavailable</Button><Button disabled>Download evidence · unavailable</Button></div>
    <p className="caption">Requires authorized services. Preview controls only change presentation.</p>
  </div>;
}
export function ProofsWorkspace({ room, initialSelected }: { room: ExampleRoom; initialSelected?: string }) {
  const graph = useMemo(() => buildGraph(graphFixture(room.id)), [room.id]);
  const [selected, setSelected] = useState(initialSelected ?? graph.states.at(-1)?.id ?? "");
  const [stage, setStage] = useState<Stage>("Verification");
  const [evidenceId, setEvidenceId] = useState("commitment");
  const [check, setCheck] = useState(0);
  const [scenario, setScenario] = useState<DisplayScenario>("normal");
  const state = scenario === "normal" ? graph.states.find((s) => s.id === selected) : undefined;
  const item = evidence.find((e) => e.id === evidenceId)!;
  const index = stages.indexOf(stage);
  return <AppShell preview previewRoomId={room.id} previewStateId={state?.id} activeModule="proofs"
    contextLabel={state ? `${state.id} · ${stage} · no verification performed` : "No state selected"}
    pageHeader={<div className="operation-header"><p className="eyebrow">{room.name} · SYNTHETIC PREVIEW</p><h1>Proofs &amp; Provenance</h1><p>Understand the evidence. Know its limits.</p><RoomChooser roomId={room.id} screen="proofs" /></div>}
    inspector={<ProofInspector roomId={room.id} graph={graph} state={state} stage={stage} item={item} check={check} onSelect={setSelected} />}>
    <RoomTrail roomId={room.id} screen="proofs" selectedStateId={state?.id} />
    <p className="operation-boundary">Illustrative states only. No verification performed, no transaction, no real proof or chain record supplied.</p>
    {state ? <><div className="provenance-state-picker" role="group" aria-label="RoomState selection">{graph.states.map((s) => <button key={s.id} aria-pressed={selected === s.id} onClick={() => setSelected(s.id)}>{s.id}<span>{s.title}</span></button>)}</div>
      <div className="provenance-workspace"><nav className="provenance-stages" aria-label="Provenance stages">{stages.map((s, i) => <button key={s} aria-current={s === stage ? "step" : undefined} onClick={() => setStage(s)}><span>0{i + 1}</span>{s}</button>)}</nav>
        <section className="provenance-scene" aria-label={`${stage} illustration`}><p className="eyebrow">0{index + 1} / {stage.toUpperCase()} · CONCEPTUAL</p><h2>{stageTitles[stage]}</h2><p className="provenance-selected">{state.id} · {state.title}<span>{transitionLabel(state)} · illustrative transition</span></p>
          {stage === "Lineage" && <><LineageMap graph={graph} selected={selected} onSelect={setSelected} /><StateRelations graph={graph} state={state} onSelect={setSelected} /></>}
          {stage === "Evidence" && <><div className="evidence-grid" role="group" aria-label="Evidence categories">{evidence.map((e) => <button key={e.id} aria-pressed={e.id === evidenceId} onClick={() => setEvidenceId(e.id)}><span className="eyebrow">{e.category}</span><strong>{e.title}</strong><span className="caption">{e.id === "references" && state.artifactLabels.length ? "Sample labels only" : "Unavailable"}</span></button>)}</div><div className="provenance-explanation" aria-live="polite"><h3>{item.title}</h3><p>{item.detail}</p><p>Relates to {state.id} via {transitionLabel(state)}. No documentary binding has been assessed.</p></div><p className="operation-caution">Evidence availability is not verification.</p></>}
          {stage === "Verification" && <><ol className="verification-flow" aria-label="Conceptual checks">{checks.map((c, i) => <li key={c.title}><button aria-pressed={check === i} onClick={() => setCheck(i)}><span className="eyebrow">0{i + 1} · NOT ASSESSED</span><strong>{c.title}</strong></button></li>)}</ol><div className="provenance-explanation" aria-live="polite"><h3>{checks[check].title}</h3><p>{checks[check].detail}</p></div><div className="verification-verdict"><Badge status="not-assessed" /><h3>No verdict.</h3><p>No verification performed. A coherent StateProofDocumentCommitment does not establish Groth16 validity.</p></div></>}
          {stage === "Anchoring" && <><ol className="anchor-flow" aria-label="Conceptual anchoring stages">{anchorSteps.map((step, i) => <li key={step.title}><span className="eyebrow">0{i + 1} · UNAVAILABLE</span><h3>{step.title}</h3><p>{step.detail}</p></li>)}</ol><p className="operation-caution">Layer A is chain inclusion/finality, not structural validation. Layer B is document consistency; Layer C is separate cryptographic verification. None has been assessed here.</p></>}
          <StateLinks roomId={room.id} state={state} />
          <div className="workflow-actions"><Button disabled={index === 0} onClick={() => setStage(stages[index - 1])}>Previous stage</Button><Button disabled={index === stages.length - 1} onClick={() => setStage(stages[index + 1])}>Next stage</Button></div>
        </section></div></> : <UnavailableDisplay value={scenario === "normal" ? "empty" : scenario} onReset={() => setScenario("normal")} />}
    <DisplayExamples value={scenario} onChange={setScenario} />
  </AppShell>;
}
