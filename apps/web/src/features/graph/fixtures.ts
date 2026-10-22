import { exampleRooms } from "@/features/rooms/preview-model";
import type { GraphState } from "./model";

/** P03 labels retained. S4 extends its illustrative branch, not M1–M7 lineage. */
export function graphFixture(roomId: string): readonly GraphState[] {
  const room = exampleRooms.find((r) => r.id === roomId);
  const states: GraphState[] = (room?.states ?? []).map((s) => ({
    demo: true, id: s.id, title: s.label === "Initial" ? "Initial State" : s.label,
    parent_state_ids: [...s.parent_state_ids],
    operation: s.id === "S1" ? "room_initialize (example)" : "private_operation (example)",
    contextLabel: "Illustrative protected context · not runtime parameters",
    artifactLabels: s.id === "S1" ? [] : [`example-${s.id.toLowerCase()}-protected-ref`],
  }));
  if (roomId === "supply-chain") states.push({
    demo: true, id: "S4", title: "Private Analytics", parent_state_ids: ["S2", "S3"],
    operation: "private_analytics (example)", contextLabel: "Illustrative protected context · not runtime parameters",
    artifactLabels: ["example-s4-protected-ref"],
  });
  return Object.freeze(states.map((s) => Object.freeze({
    ...s, parent_state_ids: Object.freeze([...s.parent_state_ids]),
    artifactLabels: Object.freeze([...s.artifactLabels]),
  })));
}

/** Display-only stress scenario; no persisted state or operation is created. */
export const longGraph: readonly GraphState[] = Object.freeze(Array.from({ length: 24 }, (_, i) =>
  Object.freeze({
    demo: true as const, id: `L${i + 1}`, title: `Example state ${i + 1}`,
    parent_state_ids: Object.freeze(i === 0 ? [] : i > 2 && i % 4 === 0 ? [`L${i}`, `L${i-2}`] : [`L${i}`]),
    operation: "display_transition (example)", contextLabel: "Unavailable · display-only stress scenario",
    artifactLabels: Object.freeze([] as string[]),
  })));
