import { graphFixture } from "@/features/graph/fixtures";
import type { GraphState } from "@/features/graph/model";

/** Local display vocabulary only. Never a StateProof, ChainAnchor, grant or API DTO. */
export const stages = ["Lineage", "Evidence", "Verification", "Anchoring"] as const;
export type Stage = (typeof stages)[number];
export const stageTitles: Record<Stage, string> = {
  Lineage: "Where this state comes from.", Evidence: "What supports this state.",
  Verification: "Can the proof be verified?", Anchoring: "Is this state anchored?",
};
export const evidence = Object.freeze([
  Object.freeze({ id: "commitment", title: "State commitment", category: "Commitment", detail: "A commitment binds content; it is not a proof. No digest is supplied or calculated in this preview." }),
  Object.freeze({ id: "references", title: "Artifact references", category: "Metadata", detail: "Only presentation labels from the existing graph are shown. No artifact locator, content or access grant is available." }),
  Object.freeze({ id: "proof", title: "Proof artifact", category: "Cryptographic artifact", detail: "No proof artifact is supplied. A file or descriptor alone cannot establish cryptographic validity." }),
  Object.freeze({ id: "receipt", title: "Receipt reference", category: "Metadata", detail: "No runtime receipt is supplied. A receipt must be bound to the precise transition and independently assessed." }),
]);
export type Evidence = (typeof evidence)[number];
export const checks = Object.freeze([
  Object.freeze({ title: "Structural validation", detail: "Document shape and required fields. No document is loaded; no structural assessment has run." }),
  Object.freeze({ title: "Document consistency · Layer B", detail: "Binding the exact RoomState, transition and StateProof document. Consistency is not Groth16 validity; no assessment has run." }),
  Object.freeze({ title: "Cryptographic proof · Layer C", detail: "Separate, explicit M5 verification against the expected program and public claim. No verifier service is connected or invoked." }),
]);
export const anchorSteps = Object.freeze([
  Object.freeze({ title: "Prepared commitment", detail: "An exact subject and evidence binding would be needed. None is created here." }),
  Object.freeze({ title: "Published event", detail: "A transaction reference alone would not prove inclusion. No event is supplied." }),
  Object.freeze({ title: "Canonical inclusion", detail: "Layer A checks the matching event on the canonical chain. No chain is queried." }),
  Object.freeze({ title: "Finality", detail: "Layer A requires verified canonical finality. No finality assessment is available." }),
]);
export function provenancePath(roomId: string, screen: "proofs" | "activity", stateId?: string) {
  return `/preview/rooms/${encodeURIComponent(roomId)}/${screen}${stateId ? `/${encodeURIComponent(stateId)}` : ""}`;
}
export function transitionLabel(state: GraphState) {
  return `${state.parent_state_ids.join(" + ") || "Root"} → ${state.id}`;
}
export const activityTypes = ["All", "State", "Compute", "Security", "Access"] as const;
export type ActivityType = (typeof activityTypes)[number];
export type SampleEvent = Readonly<{
  id: string; sequence: number; type: Exclude<ActivityType, "All">;
  title: string; detail: string; stateId: string; transition: string; status: "Illustrative";
}>;
/** Derived from the unchanged PR3 catalog. Sequence is a display order, NOT audit time. */
export function activityExamples(roomId: string): readonly SampleEvent[] {
  const states = graphFixture(roomId);
  if (!states.length) return Object.freeze([]);
  const last = states.at(-1)!;
  const entries = states.map((s, i) => ({ type: (i === 0 || i === states.length - 1 ? "State" : "Compute") as SampleEvent["type"],
    title: `${s.title} · state relationship`, stateId: s.id, transition: transitionLabel(s),
    detail: `Illustrative ${s.operation} context. This is not a completed operation or a persistence receipt.` }));
  entries.push(
    { type: "Access", title: "Participation boundary example", stateId: states[0].id, transition: transitionLabel(states[0]), detail: "Conceptual participant context, not an invitation, membership grant or access decision." },
    { type: "Security", title: "Approval requirement example", stateId: last.id, transition: transitionLabel(last), detail: "An authorized service would need to evaluate the precise operation. No approval is recorded." },
    { type: "Security", title: "Disclosure boundary example", stateId: last.id, transition: transitionLabel(last), detail: "A disclosure request would require its own policy decision. No request, denial or reveal has occurred." },
  );
  return Object.freeze(entries.map((entry, i) => Object.freeze({ ...entry, id: `E${i + 1}`, sequence: i + 1, status: "Illustrative" as const })).reverse());
}
export function filterEvents(events: readonly SampleEvent[], type: ActivityType, stateId: string) {
  return events.filter((e) => (type === "All" || e.type === type) && (!stateId || e.stateId === stateId));
}
