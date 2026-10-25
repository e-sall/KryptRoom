"use client";
import Link from "next/link";
import { useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Badge, Button } from "@/components/ui";
import type { ExampleRoom } from "@/features/rooms/preview-model";
import { operations, operationIds, previewRoomPath, resultContext, statePath, type OperationId } from "./presentation";
import { DisplayExamples, UnavailableDisplay, RoomChooser, RoomTrail, PreviewTabs, type DisplayScenario } from "./preview-controls";
import { AnalyticsChart, AnalyticsTable, JoinResult, PsiResult } from "./result-visuals";
import "./operations.css";
import { provenancePath } from "@/features/provenance/presentation";

function ContextLinks({ roomId, operation }: { roomId: string; operation: OperationId }) {
  const context = resultContext(roomId, operation);
  return <>
    {context.associated && <Link href={statePath(roomId, context.associated.id)}>Inspect {context.associated.id} · {context.associated.title} in Graph</Link>}
    {context.associated && <Link href={provenancePath(roomId, "proofs", context.associated.id)}>Provenance of {context.associated.id}</Link>}
    {context.associated && <Link href={provenancePath(roomId, "activity", context.associated.id)}>Activity for {context.associated.id}</Link>}
    {context.sources.map((s) => <Link key={s.id} href={statePath(roomId, s.id)}>Source {s.id} · {s.title}</Link>)}
  </>;
}
function ResultInspector({ roomId, operation, visible }: { roomId: string; operation: OperationId; visible: boolean }) {
  const context = resultContext(roomId, operation), item = operations[operation];
  return <div className="operation-inspector"><p className="eyebrow">DISCLOSURE INSPECTOR · SAMPLE</p>
    <h2>{visible ? item.title : "No result selected"}</h2><Badge status="not-assessed" />
    {visible ? <dl className="operation-facts">
      <dt>Output example</dt><dd>{item.output}</dd>
      <dt>Disclosure restriction</dt><dd>{item.restriction}</dd>
      <dt>Actual authorization</dt><dd>Unavailable · no disclosure grant</dd>
      <dt>Associated state</dt><dd>{context.associated ? `${context.associated.id} · ${context.associated.title} · synthetic` : "Hypothetical output only · no state created"}</dd>
      <dt>State context</dt><dd className="result-context-links"><ContextLinks roomId={roomId} operation={operation} /></dd>
      <dt>Provenance</dt><dd>P08 fixed design fixture · not a runtime receipt</dd>
      <dt>Proof verification</dt><dd>Not assessed</dd><dt>Chain anchor / commitment</dt><dd>Unavailable · no record or digest</dd>
    </dl> : <p className="caption">No values or stale disclosure metadata are available in this display state.</p>}
    <p className="operation-caution">Viewing a sample grants no access to real outputs.</p>
    <div className="operation-denied"><Button disabled>Reveal result · unavailable</Button><Button disabled>Download result · unavailable</Button></div>
  </div>;
}
export function ResultsWorkspace({ room, operation = "psi" }: { room: ExampleRoom; operation?: OperationId }) {
  const [view, setView] = useState<"Chart" | "Table">("Chart");
  const [scenario, setScenario] = useState<DisplayScenario>("normal");
  const context = resultContext(room.id, operation), item = operations[operation];
  const visible = scenario === "normal" && context.available;
  return <AppShell preview previewRoomId={room.id} previewStateId={visible ? context.associated?.id : undefined} activeModule="results"
    contextLabel={visible ? `${item.title} · ${context.id} · illustrative` : "No result selected"}
    pageHeader={<div className="operation-header"><p className="eyebrow">{room.name} · SYNTHETIC PREVIEW</p><h1>Results</h1>
      <p>Only the intended insight. Never the underlying records.</p><RoomChooser roomId={room.id} screen="results" /></div>}
    inspector={<ResultInspector roomId={room.id} operation={operation} visible={visible} />}>
    <RoomTrail roomId={room.id} screen="results" selectedStateId={visible ? context.associated?.id : undefined} />
    <p className="operation-boundary">Fixed design examples, not engine outputs. No real computation or authorized disclosure has occurred.</p>
    <nav className="operation-picker result-picker" aria-label="Result category">{operationIds.map((id) => <Link key={id}
      aria-current={id === operation ? "page" : undefined} href={`${previewRoomPath(room.id, "results")}/${id}`}>
      <span className="eyebrow">{operations[id].number} · SAMPLE</span><strong>{operations[id].title}</strong>
      <span className="caption">{operations[id].output}</span></Link>)}</nav>
    {visible ? <article className="operation-panel result-article" aria-label={`${item.title} sample result`}>
      <div className="operation-panel-heading"><span className="eyebrow">{item.number} / {item.title.toUpperCase()} · SAMPLE</span><code>{context.id}</code></div>
      {operation === "psi" && <PsiResult />}
      {operation === "join" && <JoinResult stateLabel={context.associated?.id ?? "Hypothetical state"} />}
      {operation === "analytics" && <><h2 className="result-editorial-title">The signal, without the rows.</h2>
        <p className="caption">Four fixed illustrative aggregates. No computation produced these values.</p>
        <div className="analytics-lead"><div><p className="eyebrow">LARGEST SAMPLE · COHORT D</p><p className="result-number">81</p></div>
          <div className="analytics-context"><span className="caption">Associated example state</span><strong>{context.associated?.id ?? "Hypothetical"}</strong></div></div>
        <h3>Illustrative breakdown</h3>
        <PreviewTabs label="Analytics display" options={["Chart", "Table"]} value={view} onChange={setView}>
          {view === "Chart" ? <AnalyticsChart /> : <AnalyticsTable />}
        </PreviewTabs></>}
      <details className="result-details"><summary>Explore result details</summary>
        <dl className="operation-facts"><dt>Selected example</dt><dd>{context.id} · {item.title}</dd>
          <dt>Source context · not canonical runtime lineage</dt><dd className="result-context-links"><ContextLinks roomId={room.id} operation={operation} /></dd>
          <dt>Protected reference labels</dt><dd>{context.sources.flatMap((s) => s.artifactLabels).join(" · ") || "No artifact label on the example root"}</dd>
          <dt>Transition interpretation</dt><dd>{context.hypothetical ? "Hypothetical only; no corresponding state is created." : "Existing synthetic graph illustration; not proof of a persisted transition."}</dd>
          <dt>Method / date / receipt</dt><dd>Unavailable · fixed P08 presentation data, no run or timestamp</dd>
          <dt>Disclosure limits</dt><dd>{item.restriction}. Real disclosure remains unavailable.</dd>
        </dl>
        {operation === "analytics" && <p className="caption">These are arbitrary example units, not patient counts, model metrics or statistical claims. No individual-level drill-down exists.</p>}
      </details>
    </article> : <UnavailableDisplay value={scenario === "normal" ? "empty" : scenario} onReset={() => setScenario("normal")} />}
    <DisplayExamples value={scenario} onChange={setScenario} />
  </AppShell>;
}
