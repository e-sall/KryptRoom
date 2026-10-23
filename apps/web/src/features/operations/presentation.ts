import { graphFixture } from "@/features/graph/fixtures";
import type { GraphState } from "@/features/graph/model";

/** Display vocabulary, not an operation catalog, API DTO or policy decision. */
export const operationIds = ["psi", "join", "analytics"] as const;
export type OperationId = (typeof operationIds)[number];
export const operations = Object.freeze({
  psi: Object.freeze({ title: "PSI Cardinality", code: "psi_cardinality", number: "01",
    output: "Single aggregate count", restriction: "Cardinality only; no matched identifiers",
    explanation: "Understand the size of an overlap without displaying who matches.",
    requirement: "Two participating organizations, compatible protected inputs and a cardinality disclosure decision." }),
  join: Object.freeze({ title: "Private Join", code: "private_join", number: "02",
    output: "Protected RoomState", restriction: "No plaintext joined rows",
    explanation: "Carry a protected relationship forward into an immutable state, not a spreadsheet.",
    requirement: "Compatible input references, participant approvals and an authorized private-state transition." }),
  analytics: Object.freeze({ title: "Private Analytics", code: "private_analytics", number: "03",
    output: "Four illustrative aggregates", restriction: "Only separately authorized aggregates; no underlying records",
    explanation: "Explore an aggregate view while the underlying records remain outside this interface.",
    requirement: "Eligible parent states, an allowed operator and a separate grant for each precise output." }),
});
export function isOperation(value: string): value is OperationId {
  return operationIds.some((id) => id === value);
}
export const phases = ["Protected Inputs", "Private Operation", "New State & Review"] as const;
export type Phase = 0 | 1 | 2;
export const previewRoomPath = (roomId: string, screen: "workspace" | "computations" | "results") =>
  `/preview/rooms/${encodeURIComponent(roomId)}/${screen}`;
export const statePath = (roomId: string, stateId: string) =>
  `${previewRoomPath(roomId, "workspace")}/${encodeURIComponent(stateId)}`;

export function selectedInputs(states: readonly GraphState[], ids: readonly string[]) {
  // Selection order is meaningful; never sort parents or mutate source states.
  return ids.filter((id, index) => ids.indexOf(id) === index)
    .flatMap((id) => { const state = states.find((s) => s.id === id); return state ? [state] : []; });
}
export function presentationReadiness(states: readonly GraphState[], ids: readonly string[]) {
  const valid = ids.length > 0 && ids.length === selectedInputs(states, ids).length;
  return Object.freeze({ presentationComplete: valid, execute: false as const,
    approve: false as const, persist: false as const, reveal: false as const,
    reason: "No authenticated execution or disclosure service. Presentation choices are not permissions." });
}

/** Fixed P08 display values: never derived from inputs or a private computation. */
export const sampleCardinality = 1248;
export const sampleAggregates = Object.freeze([
  Object.freeze({ cohort: "A", value: 42 }), Object.freeze({ cohort: "B", value: 68 }),
  Object.freeze({ cohort: "C", value: 55 }), Object.freeze({ cohort: "D", value: 81 }),
]);
export function resultContext(roomId: string, operation: OperationId) {
  const states = graphFixture(roomId);
  const associated = operation === "join" ? states.find((s) => s.title === "Private Join")
    : operation === "analytics" ? states.findLast((s) => s.title.includes("Analytics"))
    : states.find((s) => s.title === "PSI");
  return Object.freeze({ demo: true as const, id: `Sample R-${operations[operation].number}`,
    associated, sources: associated ? selectedInputs(states, associated.parent_state_ids) : states.slice(0, 1),
    hypothetical: !associated, available: states.length > 0 });
}
