/** Read-only presentation projection. Not a RoomState serializer or API DTO.
 * A future authorized server adapter must explicitly select safe fields.
 * Never spread a core descriptor into this model or infer a proof from a digest.
 */
export type GraphState = Readonly<{
  demo: true;
  id: string;
  title: string;
  parent_state_ids: readonly string[];
  operation: string;
  contextLabel: string;
  artifactLabels: readonly string[];
}>;
export type GraphMode = "classic" | "detailed" | "focus";
export type GraphEdge = Readonly<{ parent: string; child: string; parentIndex: number }>;
export type Graph = Readonly<{
  states: readonly GraphState[];
  edges: readonly GraphEdge[];
  ranks: ReadonlyMap<string, number>;
}>;

/** Stable topological order; preserve each child's parent order exactly. */
export function buildGraph(states: readonly GraphState[]): Graph {
  const byId = new Map(states.map((s) => [s.id, s]));
  if (byId.size !== states.length || states.some((s) => !s.id))
    throw new Error("Duplicate or empty state identifier");
  const edges: GraphEdge[] = [];
  for (const s of states) {
    if (new Set(s.parent_state_ids).size !== s.parent_state_ids.length)
      throw new Error("Duplicate parent");
    for (const [parentIndex, parent] of s.parent_state_ids.entries()) {
      if (!byId.has(parent)) throw new Error("Missing parent");
      edges.push({ parent, child: s.id, parentIndex });
    }
  }
  const ranks = new Map<string, number>();
  const ordered: GraphState[] = [];
  const pending = new Set(states);
  while (pending.size) {
    let progress = false;
    for (const s of pending) {
      if (s.parent_state_ids.every((p) => ranks.has(p))) {
        ranks.set(s.id, Math.max(-1, ...s.parent_state_ids.map((p) => ranks.get(p)!)) + 1);
        ordered.push(s);
        pending.delete(s);
        progress = true;
      }
    }
    if (!progress) throw new Error("Cyclic graph");
  }
  return { states: ordered, edges, ranks };
}

export function neighborhood(graph: Graph, selected: string | null): Set<string> {
  return new Set(selected ? [selected, ...graph.edges.flatMap((e) =>
    e.parent === selected ? [e.child] : e.child === selected ? [e.parent] : [])] : []);
}
