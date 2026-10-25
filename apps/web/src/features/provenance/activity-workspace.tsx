"use client";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Badge, Button } from "@/components/ui";
import { graphFixture } from "@/features/graph/fixtures";
import { buildGraph, type Graph } from "@/features/graph/model";
import type { ExampleRoom } from "@/features/rooms/preview-model";
import { DisplayExamples, RoomChooser, RoomTrail, UnavailableDisplay, PreviewTabs, type DisplayScenario } from "@/features/operations/preview-controls";
import { activityExamples, activityTypes, filterEvents, type ActivityType, type SampleEvent } from "./presentation";
import { LineageMap, StateLinks, StateRelations } from "./shared";
import "@/features/operations/operations.css";
import "./provenance.css";

type InspectorTab = "Overview" | "Context" | "Diagnostic";
function ActivityInspector({ roomId, graph, event, tab, onTab, onState }: {
  roomId: string; graph: Graph; event?: SampleEvent; tab: InspectorTab; onTab: (tab: InspectorTab) => void; onState: (id: string) => void;
}) {
  const state = graph.states.find((s) => s.id === event?.stateId);
  return <div className="operation-inspector provenance-inspector"><p className="eyebrow">ACTIVITY INSPECTOR · SAMPLE</p><h2>{event?.title ?? "No event selected"}</h2><Badge status="not-assessed" />
    {event && state ? <><PreviewTabs label="Activity inspector" options={["Overview", "Context", "Diagnostic"]} value={tab} onChange={onTab}>
      {tab === "Overview" && <dl className="operation-facts"><dt>Sample reference</dt><dd>{event.id} · Illustrative</dd><dt>Category</dt><dd>{event.type}</dd><dt>Interpretation</dt><dd>{event.detail}</dd><dt>Audit time / actor / outcome</dt><dd>Unavailable · sample sequence is not a timestamp or execution order</dd></dl>}
      {tab === "Context" && <><dl className="operation-facts"><dt>RoomState</dt><dd>{state.id} · {state.title}</dd><dt>Transition relationship</dt><dd>{event.transition}</dd><dt>Operation label</dt><dd>{state.operation} · presentation only</dd></dl><StateRelations graph={graph} state={state} onSelect={onState} /></>}
      {tab === "Diagnostic" && <><p className="operation-caution">No runtime diagnostic. No approval, rejection or disclosure decision has been received.</p><dl className="operation-facts"><dt>Explanation</dt><dd>{event.detail}</dd><dt>Evidence / verification / chain status</dt><dd>Unavailable / Not assessed / Unavailable</dd><dt>Future source</dt><dd>Authorized activity service with field-filtered metadata. Local examples confer no permission.</dd></dl></>}
    </PreviewTabs><StateLinks roomId={roomId} state={state} /></> : <p className="caption">No stale event, diagnostic or permission is displayed.</p>}
    <p className="caption">Synthetic examples, not live telemetry or an audit log.</p>
    <div className="operation-denied"><Button disabled>Approve action · unavailable</Button><Button disabled>Download log · unavailable</Button></div>
  </div>;
}
export function ActivityWorkspace({ room, initialSelected }: { room: ExampleRoom; initialSelected?: string }) {
  const graph = useMemo(() => buildGraph(graphFixture(room.id)), [room.id]);
  const events = useMemo(() => activityExamples(room.id), [room.id]);
  const [view, setView] = useState<"List" | "Graph">("List");
  const [type, setType] = useState<ActivityType>("All");
  const [stateId, setStateId] = useState(initialSelected ?? "");
  const [selected, setSelected] = useState<string | undefined>();
  const [tab, setTab] = useState<InspectorTab>("Overview");
  const [scenario, setScenario] = useState<DisplayScenario>("normal");
  const filtered = filterEvents(events, type, stateId);
  const event = scenario === "normal" ? filtered.find((e) => e.id === selected) ?? filtered[0] : undefined;
  // A valid explicit filter remains navigation context even with no matching event.
  // It never supplies an event or inspector selection.
  const navigationStateId = scenario === "normal"
    ? graph.states.find((s) => s.id === (stateId || event?.stateId))?.id : undefined;
  function selectState(id: string) { setStateId(id); setSelected(undefined); }
  const index = filtered.findIndex((e) => e.id === event?.id);
  return <AppShell preview previewRoomId={room.id} previewStateId={navigationStateId} activeModule="activity"
    contextLabel={event ? `${event.id} · ${event.stateId} · illustrative` : "No event selected"}
    pageHeader={<div className="operation-header"><p className="eyebrow">{room.name} · SYNTHETIC PREVIEW</p><h1>Activity &amp; History</h1><p>A history connected to its states.</p><RoomChooser roomId={room.id} screen="activity" /></div>}
    inspector={<ActivityInspector roomId={room.id} graph={graph} event={event} tab={tab} onTab={setTab} onState={selectState} />}>
    <RoomTrail roomId={room.id} screen="activity" selectedStateId={navigationStateId} />
    <p className="operation-boundary">Illustrative relationships, not execution logs. Sample sequence numbers are not audit timestamps. No live telemetry.</p>
    {scenario === "normal" && events.length > 0 ? <section className="activity-workspace" aria-label="Illustrative activity">
      <div className="activity-controls"><div role="group" aria-label="Activity type" className="segmented-control">{activityTypes.map((t) => <button key={t} aria-pressed={type === t} onClick={() => { setType(t); setSelected(undefined); }}>{t}</button>)}</div>
        <label>Related state<select aria-label="Related state" value={stateId} onChange={(e) => selectState(e.target.value)}><option value="">All states</option>{graph.states.map((s) => <option key={s.id} value={s.id}>{s.id} · {s.title}</option>)}</select></label></div>
      <PreviewTabs label="Activity display" options={["List", "Graph"]} value={view} onChange={setView}>
        {view === "List" ? <ol className="activity-timeline" aria-label="Sample timeline">{filtered.map((e) => <li key={e.id}><button aria-pressed={e.id === event?.id} onClick={() => setSelected(e.id)}>
          <span className="timeline-sequence">{String(e.sequence).padStart(2, "0")}<small>SAMPLE</small></span><span className="timeline-body"><span className="eyebrow">{e.type} · ILLUSTRATIVE</span><strong>{e.title}</strong><span>{e.stateId} · {e.transition}</span></span><span className="timeline-marker" aria-hidden="true">↗</span>
        </button></li>)}</ol> : <><p className="caption">Full Room topology. Selecting a node filters related examples; type filters remain active.</p><LineageMap graph={graph} selected={event?.stateId ?? stateId} onSelect={selectState} /><div className="activity-graph-events" role="group" aria-label="Related sample events">{filtered.map((e) => <button key={e.id} aria-pressed={event?.id === e.id} onClick={() => setSelected(e.id)}>{e.id} · {e.title}</button>)}</div></>}
        {!filtered.length && <div role="status" className="provenance-explanation"><h2>No matching examples</h2><p>No event is invented for this combination.</p><Button onClick={() => { setType("All"); setStateId(""); setSelected(undefined); }}>Clear activity filters</Button></div>}
      </PreviewTabs>
      {event && <div className="activity-selection" aria-live="polite"><p className="eyebrow">SELECTED EXAMPLE · {event.id}</p><h2>{event.title}</h2><p>{event.detail}</p><StateLinks roomId={room.id} state={graph.states.find((s) => s.id === event.stateId)!} /><details><summary>Explore example context</summary><p>{event.transition} · illustrative transition reference, not a runtime transition identifier.</p><p>No actor, timestamp, permission decision or receipt is available.</p></details></div>}
      <div className="workflow-actions"><Button disabled={index <= 0} onClick={() => setSelected(filtered[index - 1]?.id)}>Previous example</Button><Button disabled={index < 0 || index >= filtered.length - 1} onClick={() => setSelected(filtered[index + 1]?.id)}>Next example</Button></div>
    </section> : <UnavailableDisplay value={scenario === "normal" ? "empty" : scenario} onReset={() => setScenario("normal")} />}
    <DisplayExamples value={scenario} onChange={setScenario} />
  </AppShell>;
}
