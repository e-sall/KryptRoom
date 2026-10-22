import type { Graph } from "./model";
export type Position = { x: number; y: number; width: number; height: number };
export type Viewport = { x: number; y: number; scale: number };
export function layoutGraph(graph: Graph, detailed = false, vertical = false) {
  const width = vertical ? 142 : detailed ? 184 : 158;
  const height = detailed ? 144 : 88;
  const lanes = new Map<number, string[]>();
  for (const s of graph.states) {
    const rank = graph.ranks.get(s.id)!;
    lanes.set(rank, [...(lanes.get(rank) ?? []), s.id]);
  }
  const maxLanes = Math.max(1, ...Array.from(lanes.values(), (lane) => lane.length));
  const positions = new Map<string, Position>();
  for (const [rank, lane] of lanes) {
    lane.forEach((id, i) => {
      const offset = i + (maxLanes - lane.length) / 2;
      positions.set(id, {
        x: 24 + (vertical ? offset * (width + 24) : rank * (width + 110)),
        y: 24 + (vertical ? rank * (height + 64) : offset * (height + 90)),
        width, height,
      });
    });
  }
  return {
    positions, vertical,
    width: Math.max(1, ...Array.from(positions.values(), (p) => p.x + p.width + 24)),
    height: Math.max(1, ...Array.from(positions.values(), (p) => p.y + p.height + 24)),
  };
}
export function edgePath(a: Position, b: Position, vertical: boolean) {
  if (vertical) {
    const x1 = a.x + a.width / 2, y1 = a.y + a.height;
    const x2 = b.x + b.width / 2, y2 = b.y;
    return `M${x1} ${y1} C${x1} ${(y1+y2)/2} ${x2} ${(y1+y2)/2} ${x2} ${y2}`;
  }
  const x1 = a.x + a.width, y1 = a.y + a.height / 2;
  const x2 = b.x, y2 = b.y + b.height / 2;
  return `M${x1} ${y1} C${(x1+x2)/2} ${y1} ${(x1+x2)/2} ${y2} ${x2} ${y2}`;
}
export function fitViewport(width: number, height: number, graphWidth: number, graphHeight: number): Viewport {
  const scale = Math.max(0.02, Math.min(1, (width - 24) / graphWidth, (height - 24) / graphHeight));
  return { x: (width - graphWidth * scale) / 2, y: (height - graphHeight * scale) / 2, scale };
}
export function zoomViewport(view: Viewport, factor: number, x: number, y: number): Viewport {
  const scale = Math.max(0.02, Math.min(2, view.scale * factor));
  return { x: x - (x - view.x) * scale / view.scale, y: y - (y - view.y) * scale / view.scale, scale };
}
