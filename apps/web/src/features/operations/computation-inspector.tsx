import { Badge, Button } from "@/components/ui";
import type { GraphState } from "@/features/graph/model";
import { operations, phases, type OperationId, type Phase } from "./presentation";
import { PreviewTabs } from "./preview-controls";
export function ComputationInspector({ operation, inputs, phase, tab, onTab, visible }: {
  operation: OperationId; inputs: readonly GraphState[]; phase: Phase;
  tab: "Readiness" | "Review"; onTab: (tab: "Readiness" | "Review") => void; visible: boolean;
}) {
  return <div className="operation-inspector"><p className="eyebrow">READINESS &amp; REVIEW · PREVIEW</p>
    <h2>{visible ? operations[operation].title : "No operation context"}</h2>
    <Badge status="unavailable" />
    {visible ? <PreviewTabs label="Computation inspector" options={["Readiness", "Review"]} value={tab} onChange={onTab}>
      <dl className="operation-facts">{tab === "Readiness" ? <>
        <dt>Presentation prerequisites</dt><dd>{inputs.length ? `${inputs.length} example reference(s) selected` : "Select at least one example state"}</dd>
        <dt>Input availability</dt><dd>Labels only · local connections not assessed</dd>
        <dt>State policy</dt><dd>No authoritative permission decision</dd>
        <dt>Participant approvals</dt><dd>Required · unavailable</dd>
        <dt>Execution authority</dt><dd>Unavailable · never granted by this checklist</dd>
        <dt>Disclosure permission</dt><dd>Denied by default · separate exact-output grant required</dd>
        <dt>Backend capability</dt><dd>No Workspace service connected</dd>
      </> : <>
        <dt>Presentation phase</dt><dd>{phases[phase]}</dd>
        <dt>Ordered parent references</dt><dd>{inputs.map((s) => s.id).join(" → ") || "None"}</dd>
        <dt>Proposed operation</dt><dd>{operations[operation].code} · conceptual</dd>
        <dt>Transition status</dt><dd>Hypothetical · not computed, signed, committed or persisted</dd>
        <dt>Potential output</dt><dd>{operations[operation].output}</dd>
        <dt>Actual result</dt><dd>Unavailable · no execution</dd>
        <dt>Proof / chain</dt><dd>Not assessed / unavailable</dd>
      </>}</dl>
    </PreviewTabs> : <p className="caption">Display example only. No stale input, transition or result is presented.</p>}
    <p className="operation-caution">Presentation choices are not permissions.</p>
    <div className="operation-denied"><Button disabled>Run computation · unavailable</Button><Button disabled>Approve · unavailable</Button><Button disabled>Save transition · unavailable</Button></div>
  </div>;
}
