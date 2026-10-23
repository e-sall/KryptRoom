import type { GraphState } from "@/features/graph/model";
import { operations, phases, type OperationId, type Phase } from "./presentation";

/** Navigation through an explanation, never computation progress. */
export function WorkflowDiagram({ inputs, operation, phase, onPhase }: {
  inputs: readonly GraphState[]; operation: OperationId; phase: Phase; onPhase: (phase: Phase) => void;
}) {
  const item = operations[operation];
  return <div className="workflow-diagram" data-phase={phase} aria-label="Hypothetical transition diagram">
    <div className={`workflow-sources${phase === 0 ? " workflow-highlight" : ""}`}>
      {inputs.map((state, i) => <button key={state.id} className="workflow-source" onClick={() => onPhase(0)}>
        <span className="eyebrow">PARENT {i + 1} · SAMPLE</span><strong>{state.id} · {state.title}</strong>
        <span className="caption">Depends on: {state.parent_state_ids.join(" · ") || "No parent"}</span>
      </button>)}
      {!inputs.length && <p className="caption">Select illustrative parent states to trace a transition.</p>}
    </div>
    <div className={`workflow-connector${phase >= 1 ? " emphasized" : ""}`} aria-hidden="true">↓</div>
    <button className={`workflow-operation${phase === 1 ? " workflow-highlight" : ""}`} onClick={() => onPhase(1)}>
      <span className="eyebrow">PRIVATE OPERATION · CONCEPT</span><strong>{item.title}</strong><code>{item.code}</code>
      <span className="workflow-dots" aria-hidden="true">• — • — • — • — •</span>
      <span className="caption">No execution started</span>
    </button>
    <div className={`workflow-connector dashed${phase === 2 ? " emphasized" : ""}`} aria-hidden="true">↓</div>
    <button className={`workflow-output${phase === 2 ? " workflow-highlight" : ""}`} onClick={() => onPhase(2)}>
      <span className="eyebrow">HYPOTHETICAL · NOT CREATED</span><strong>New immutable RoomState</strong>
      <span className="caption">Potential output: {item.output}</span>
    </button>
    <p className="caption workflow-disclosure">{item.restriction}. A separate disclosure decision would still be required.</p>
    <p className="sr-only" role="status">Presentation phase: {phases[phase]}. Ordered parent references: {inputs.map((s) => s.id).join(", ") || "none"}. No state is created.</p>
  </div>;
}
