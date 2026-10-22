import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, describe, expect, it, vi } from "vitest";
import { buildGraph, neighborhood, type GraphState } from "../src/features/graph/model";
import { graphFixture, longGraph } from "../src/features/graph/fixtures";
import { layoutGraph, fitViewport, zoomViewport, edgePath } from "../src/features/graph/layout";
import { GraphWorkspace } from "../src/features/graph/graph-workspace";
import { exampleRooms } from "../src/features/rooms/preview-model";
import { readFileSync, readdirSync } from "node:fs";

vi.mock("next/navigation", () => ({ usePathname: () => "/preview/rooms/supply-chain/workspace" }));
beforeAll(() => vi.stubGlobal("ResizeObserver", class { observe() {} disconnect() {} }));
const fixture = graphFixture("supply-chain");
describe("presentation DAG", () => {
  it("preserves every ordered parent edge and never mutates immutable source nodes", () => {
    const snapshot = JSON.stringify(fixture);
    const graph = buildGraph([...fixture].reverse());
    expect(graph.states.map((s) => s.id)).toEqual(["S1", "S3", "S2", "S4"]);
    expect(graph.edges.filter((e) => e.child === "S4")).toEqual([
      { parent: "S2", child: "S4", parentIndex: 0 }, { parent: "S3", child: "S4", parentIndex: 1 },
    ]);
    expect(graph.ranks.get("S4")).toBe(2);
    expect(JSON.stringify(fixture)).toBe(snapshot);
    expect(Object.isFrozen(fixture[0].parent_state_ids)).toBe(true);
  });
  it.each(["cycle", "missing", "duplicate", "duplicate-parent", "self"] as const)("rejects %s graphs", (kind) => {
    const states: GraphState[] = fixture.map((s) => ({ ...s }));
    if (kind === "cycle") states[0] = { ...states[0], parent_state_ids: ["S4"] };
    if (kind === "missing") states[1] = { ...states[1], parent_state_ids: ["unknown"] };
    if (kind === "duplicate") states.push(states[0]);
    if (kind === "duplicate-parent") states[3] = { ...states[3], parent_state_ids: ["S2", "S2"] };
    if (kind === "self") states[0] = { ...states[0], parent_state_ids: ["S1"] };
    expect(() => buildGraph(states)).toThrow();
  });
  it("handles empty graphs and multiple roots without inventing edges", () => {
    expect(buildGraph([]).edges).toEqual([]);
    expect(layoutGraph(buildGraph([])).positions.size).toBe(0);
    expect(buildGraph(fixture.map((s) => ({ ...s, parent_state_ids: [] }))).edges).toEqual([]);
  });
  it.each([false, true])("lays out branches deterministically, vertical=%s", (vertical) => {
    const graph = buildGraph(fixture);
    const layout = layoutGraph(graph, true, vertical);
    expect(layout).toEqual(layoutGraph(graph, true, vertical));
    for (const e of graph.edges) {
      const a = layout.positions.get(e.parent)!, b = layout.positions.get(e.child)!;
      expect(vertical ? b.y > a.y + a.height : b.x > a.x + a.width).toBe(true);
      expect(edgePath(a, b, vertical)).toMatch(/^M.+ C/);
    }
    const peers = ["S2", "S3"].map((id) => layout.positions.get(id)!);
    expect(vertical ? Math.abs(peers[1].x-peers[0].x) : Math.abs(peers[1].y-peers[0].y))
      .toBeGreaterThan(vertical ? peers[0].width : peers[0].height);
  });
  it("fits and navigates long chains with multi-parent branches", () => {
    const graph = buildGraph(longGraph), layout = layoutGraph(graph);
    expect(graph.states).toHaveLength(24);
    expect(graph.edges.some((e) => e.parentIndex === 1)).toBe(true);
    const fit = fitViewport(700, 480, layout.width, layout.height);
    expect(Number.isFinite(fit.scale)).toBe(true);
    expect(zoomViewport(fit, 100, 350, 240).scale).toBe(2);
    expect(zoomViewport(fit, 0.001, 350, 240).scale).toBe(0.02);
    expect(layout.width * fit.scale).toBeLessThanOrEqual(700);
    expect(neighborhood(buildGraph(fixture), "S2")).toEqual(new Set(["S2", "S1", "S4"]));
  });
  it("contains only explicitly synthetic display labels, no commitment or proof payload", () => {
    for (const room of exampleRooms) for (const state of graphFixture(room.id)) {
      expect(state.demo).toBe(true);
      expect(Object.keys(state).sort()).toEqual(["artifactLabels", "contextLabel", "demo", "id", "operation", "parent_state_ids", "title"]);
      expect(JSON.stringify(state)).not.toMatch(/[a-f0-9]{64}|file:\/\/|proof\.bin|patient|privateKey/i);
    }
  });
});
describe("interactive graph workspace", () => {
  it("selects, deselects and synchronizes inspector in all three modes", async () => {
    const user = userEvent.setup();
    render(<GraphWorkspace room={exampleRooms[0]} />);
    const inspector = within(screen.getByLabelText("Context inspector"));
    const node = screen.getByRole("button", { name: "State S2: Private Join" });
    await user.click(node);
    expect(node).toHaveAttribute("aria-pressed", "true");
    expect(inspector.getByRole("heading", { name: "Private Join" })).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Detailed" }));
    expect(inspector.getAllByRole("tab")).toHaveLength(4);
    await user.click(inspector.getByRole("tab", { name: "Inputs" }));
    await user.click(inspector.getByRole("button", { name: "Inspect parent S1" }));
    expect(screen.getByRole("button", { name: "State S1: Initial State" })).toHaveAttribute("aria-pressed", "true");
    await user.click(inspector.getByRole("tab", { name: "Outputs" }));
    expect(inspector.getByText("No example artifact references.")).toBeVisible();
    await user.click(inspector.getByRole("tab", { name: "Metadata" }));
    expect(inspector.getByText("Unavailable · no digest fabricated")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Focus" }));
    expect(inspector.queryByRole("tab")).toBeNull();
    await user.click(screen.getByRole("button", { name: "Return to full view" }));
    expect(screen.getByRole("button", { name: "Detailed" })).toHaveAttribute("aria-pressed", "true");
    await user.click(screen.getByRole("button", { name: "State S1: Initial State" }));
    expect(inspector.getByRole("heading", { name: "No state selected" })).toBeVisible();
  });
  it("handles empty and display error states without stale inspector metadata or success", async () => {
    const user = userEvent.setup();
    render(<GraphWorkspace room={exampleRooms[0]} />);
    await user.click(screen.getByText("Graph display examples"));
    for (const scenario of ["empty", "loading", "error", "unavailable"]) {
      await user.click(screen.getByRole("button", { name: scenario }));
      expect(screen.queryByRole("region", { name: "State graph canvas" })).toBeNull();
      expect(within(screen.getByLabelText("Context inspector")).getByRole("heading", { name: "No state selected" })).toBeVisible();
    }
    await user.click(screen.getByRole("button", { name: "blocked" }));
    expect(screen.getByRole("region", { name: "State graph canvas" })).toBeVisible();
    expect(within(screen.getByLabelText("Context inspector")).getByRole("button", { name: "Authorized result unavailable" })).toBeDisabled();
    expect(screen.queryByText("Verified", { exact: true })).toBeNull();
    expect(screen.queryByText("Finalized", { exact: true })).toBeNull();
  });
  it("rejects data access capabilities and keeps production routes disconnected", () => {
    for (const file of readdirSync("src/features/graph").filter((p) => /\.tsx?$/.test(p))) {
      const source = readFileSync("src/features/graph/" + file, "utf8");
      expect(source).not.toMatch(/\b(fetch|WebSocket|sendBeacon)\s*\(|localStorage|sessionStorage|indexedDB|use server/);
      expect(source).not.toMatch(/from ["'].*(?:engines|chain\/|node:)/);
    }
    expect(readFileSync("src/app/app/[module]/page.tsx", "utf8")).not.toMatch(/GraphWorkspace|graphFixture/);
  });
});
