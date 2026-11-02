"use client";
import Link from "next/link";
import { useId, type ReactNode } from "react";
import { Button, StatusView, type ViewState } from "@/components/ui";
import { exampleRooms } from "@/features/rooms/preview-model";
import { graphFixture } from "@/features/graph/fixtures";
import { previewRoomPath } from "./presentation";

export type DisplayScenario = "normal" | ViewState;
export function RoomChooser({ roomId, screen }: { roomId: string; screen: "computations" | "results" | "proofs" | "activity" }) {
  return <details className="operation-room-chooser"><summary>Change example Room</summary>
    <nav aria-label="Example Room selection">{exampleRooms.map((r) => <Link prefetch={false} key={r.id}
      aria-current={r.id === roomId ? "page" : undefined} href={previewRoomPath(r.id, screen)}>{r.name}</Link>)}</nav>
  </details>;
}
export function RoomTrail({ roomId, screen, selectedStateId }: { roomId: string; screen: "computations" | "results" | "proofs" | "activity"; selectedStateId?: string }) {
  const state = graphFixture(roomId).find((s) => s.id === selectedStateId);
  const suffix = state ? "/" + encodeURIComponent(state.id) : "";
  return <nav className="operation-trail" aria-label="Room preview journey">
    <Link prefetch={false} href="/preview/rooms">Rooms</Link><span aria-hidden="true">/</span>
    <Link prefetch={false} href={`/preview/rooms/${roomId}`}>Room details</Link><span aria-hidden="true">/</span>
    <Link prefetch={false} href={previewRoomPath(roomId, "workspace") + suffix}>Graph Workspace</Link><span aria-hidden="true">/</span>
    <Link prefetch={false} href={previewRoomPath(roomId, "computations")} aria-current={screen === "computations" ? "page" : undefined}>Computations</Link>
    <span aria-hidden="true">/</span><Link prefetch={false} href={previewRoomPath(roomId, "results")} aria-current={screen === "results" ? "page" : undefined}>Results</Link>
    <span aria-hidden="true">/</span><Link prefetch={false} href={previewRoomPath(roomId, "proofs") + suffix} aria-current={screen === "proofs" ? "page" : undefined}>Proofs &amp; Provenance</Link>
    <span aria-hidden="true">/</span><Link prefetch={false} href={previewRoomPath(roomId, "activity") + suffix} aria-current={screen === "activity" ? "page" : undefined}>Activity</Link>
  </nav>;
}
export function PreviewTabs<T extends string>({ label, options, value, onChange, children }: {
  label: string; options: readonly T[]; value: T; onChange: (value: T) => void; children: ReactNode;
}) {
  const id = useId();
  return <><div className="operation-tabs" role="tablist" aria-label={label} onKeyDown={(e) => {
    const delta = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
    if (!delta && e.key !== "Home" && e.key !== "End") return;
    e.preventDefault();
    const index = e.key === "Home" ? 0 : e.key === "End" ? options.length - 1 : (options.indexOf(value) + delta + options.length) % options.length;
    onChange(options[index]); (e.currentTarget.children[index] as HTMLElement).focus();
  }}>{options.map((option) => <button key={option} role="tab" id={`${id}-${option}`} aria-controls={`${id}-panel`}
    aria-selected={value === option} tabIndex={value === option ? 0 : -1} onClick={() => onChange(option)}>{option}</button>)}</div>
    <div role="tabpanel" id={`${id}-panel`} aria-labelledby={`${id}-${value}`}>{children}</div></>;
}
export function DisplayExamples({ value, onChange }: { value: DisplayScenario; onChange: (value: DisplayScenario) => void }) {
  return <details className="operation-examples"><summary>Display examples · not service responses</summary>
    <div className="segmented-control" role="group" aria-label="Display state">{(["normal", "empty", "loading", "blocked", "error", "unavailable"] as const).map((s) =>
      <button key={s} aria-pressed={s === value} onClick={() => onChange(s)}>{s}</button>)}</div>
  </details>;
}
export function UnavailableDisplay({ value, onReset }: { value: Exclude<DisplayScenario, "normal">; onReset: () => void }) {
  return <div className="operation-panel operation-unavailable"><StatusView state={value}
    title={value === "empty" ? "No examples in this view" : value === "unavailable" ? "Workspace service unavailable" : undefined}
    description={value === "empty" ? "This Room has no illustrative state references. Choose another example Room; no output is invented here." : undefined}
    action={<Button onClick={onReset}>Reset display example</Button>} /></div>;
}
