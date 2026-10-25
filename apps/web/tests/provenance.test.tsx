import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { readFileSync, readdirSync } from "node:fs";
import { exampleRooms } from "../src/features/rooms/preview-model";
import { graphFixture } from "../src/features/graph/fixtures";
import { ProofsWorkspace } from "../src/features/provenance/proofs-workspace";
import { ActivityWorkspace } from "../src/features/provenance/activity-workspace";
import { activityExamples, filterEvents, stages, transitionLabel, provenancePath } from "../src/features/provenance/presentation";
vi.mock("next/navigation", () => ({ usePathname: () => "/preview/rooms/supply-chain/proofs" }));
const room = exampleRooms[0];
const inspector = () => within(screen.getByLabelText("Context inspector"));
const main = () => within(screen.getByRole("main"));
describe("P09 P10 isolated presentation", () => {
  it("derives events exclusively from immutable PR3 states, preserving ordered parents", () => {
    const states = graphFixture(room.id), before = JSON.stringify(states), events = activityExamples(room.id);
    expect(transitionLabel(states.find((s) => s.id === "S4")!)).toBe("S2 + S3 → S4");
    expect(Object.isFrozen(events)).toBe(true);
    events.forEach((e) => {
      expect(Object.isFrozen(e)).toBe(true);
      expect(states.some((s) => s.id === e.stateId && transitionLabel(s) === e.transition)).toBe(true);
      expect(e.status).toBe("Illustrative");
      expect(Object.keys(e)).not.toEqual(expect.arrayContaining(["timestamp", "actor", "hash", "proof"]));
    });
    expect(JSON.stringify(states)).toBe(before);
    expect(provenancePath("a/b", "proofs", "S/1")).toBe("/preview/rooms/a%2Fb/proofs/S%2F1");
  });
  it("filters by type AND state, and returns no invented event for an empty Room", () => {
    const events = activityExamples(room.id);
    expect(filterEvents(events, "Security", "S4")).toHaveLength(2);
    expect(filterEvents(events, "Security", "S1")).toEqual([]);
    expect(activityExamples("research")).toEqual([]);
    expect(filterEvents(events, "All", "S2").every((e) => e.stateId === "S2")).toBe(true);
  });
  it("selects S1–S4, updates inspector, preserves source and correct state links", async () => {
    const before = JSON.stringify(graphFixture(room.id)), user = userEvent.setup();
    render(<ProofsWorkspace room={room} initialSelected="S2" />);
    const picker = within(screen.getByRole("group", { name: "RoomState selection" }));
    for (const state of graphFixture(room.id)) {
      await user.click(picker.getByRole("button", { name: new RegExp("^" + state.id) }));
      expect(inspector().getByRole("heading", { name: state.id + " · " + state.title })).toBeInTheDocument();
      expect(inspector().getByRole("link", { name: "Open " + state.id + " in Graph" })).toHaveAttribute("href", "/preview/rooms/supply-chain/workspace/" + state.id);
      expect(inspector().getByRole("link", { name: "Activity for " + state.id })).toHaveAttribute("href", "/preview/rooms/supply-chain/activity/" + state.id);
      expect(within(screen.getByRole("navigation", { name: "Workspace navigation" })).getByRole("link", { name: "Graph" })).toHaveAttribute("href", "/preview/rooms/supply-chain/workspace/" + state.id);
    }
    expect(JSON.stringify(graphFixture(room.id))).toBe(before);
  });
  it("navigates all four stages without performing checks or claiming success", async () => {
    const user = userEvent.setup();
    render(<ProofsWorkspace room={room} />);
    const rail = within(screen.getByRole("navigation", { name: "Provenance stages" }));
    for (const stage of stages) {
      await user.click(rail.getByRole("button", { name: new RegExp(stage) }));
      expect(screen.getByRole("region", { name: stage + " illustration" })).toBeInTheDocument();
      expect(inspector().getByText(stage, { exact: true })).toBeInTheDocument();
      expect(inspector().getByText("No verification performed")).toBeInTheDocument();
      expect(screen.queryByText(/^(Verified|Finalized|Pending)$/)).not.toBeInTheDocument();
    }
    expect(main().getByRole("button", { name: "Next stage" })).toBeDisabled();
    await user.click(main().getByRole("button", { name: "Previous stage" }));
    expect(screen.getByRole("region", { name: "Verification illustration" })).toBeInTheDocument();
    expect(inspector().getByRole("button", { name: /Verify proof/ })).toBeDisabled();
    expect(inspector().getByRole("button", { name: /Anchor state/ })).toBeDisabled();
    expect(inspector().getByRole("button", { name: /Download evidence/ })).toBeDisabled();
  });
  it("shows exact DAG edges, ordered parents and child navigation", async () => {
    const user = userEvent.setup();
    render(<ProofsWorkspace room={room} />);
    await user.click(screen.getByRole("button", { name: /01Lineage/ }));
    const parents = inspector().getByRole("list", { name: "Ordered parents" });
    expect(within(parents).getAllByRole("button").map((b) => b.textContent)).toEqual(["S2 · Private Join", "S3 · Analytics"]);
    expect(document.querySelectorAll('.lineage-edges path[data-child="S4"]')).toHaveLength(2);
    await user.click(within(parents).getByRole("button", { name: "S2 · Private Join" }));
    expect(inspector().getByRole("heading", { name: "S2 · Private Join" })).toBeInTheDocument();
    await user.click(within(inspector().getByRole("list", { name: "Children" })).getByRole("button", { name: "S4 · Private Analytics" }));
    expect(inspector().getByRole("heading", { name: "S4 · Private Analytics" })).toBeInTheDocument();
  });
  it("distinguishes evidence categories and explains unavailable artifacts", async () => {
    const user = userEvent.setup();
    render(<ProofsWorkspace room={room} />);
    await user.click(screen.getByRole("button", { name: /02Evidence/ }));
    const categories = within(screen.getByRole("group", { name: "Evidence categories" }));
    await user.click(categories.getByRole("button", { name: /Proof artifact/ }));
    expect(inspector().getByText("Proof artifact · Cryptographic artifact")).toBeInTheDocument();
    expect(inspector().getByText(/No proof artifact is supplied/)).toBeInTheDocument();
    await user.click(categories.getByRole("button", { name: /Artifact references/ }));
    expect(inspector().getByText("Artifact references · Metadata")).toBeInTheDocument();
    expect(screen.getByText("Evidence availability is not verification.")).toBeInTheDocument();
  });
  it("separates structural, Layer B and Layer C without executing a verifier", async () => {
    const user = userEvent.setup();
    render(<ProofsWorkspace room={room} />);
    await user.click(main().getByRole("button", { name: /Document consistency/ }));
    expect(inspector().getByText(/Consistency is not Groth16 validity/)).toBeInTheDocument();
    await user.click(main().getByRole("button", { name: /Cryptographic proof/ }));
    expect(inspector().getByText(/No verifier service is connected or invoked/)).toBeInTheDocument();
  });
  it("keeps sample sequence distinct from real telemetry and selects exact state events", async () => {
    const user = userEvent.setup();
    render(<ActivityWorkspace room={room} initialSelected="S2" />);
    expect(screen.getByRole("tab", { name: "List", selected: true })).toBeInTheDocument();
    expect(within(screen.getByRole("list", { name: "Sample timeline" })).getAllByRole("button")).toHaveLength(1);
    expect(inspector().getByText(/sample sequence is not a timestamp/)).toBeInTheDocument();
    await user.click(inspector().getByRole("tab", { name: "Context" }));
    expect(inspector().getByText("S1 → S2")).toBeInTheDocument();
    await user.click(inspector().getByRole("tab", { name: "Diagnostic" }));
    expect(inspector().getByText(/No runtime diagnostic/)).toBeInTheDocument();
    expect(inspector().getByRole("button", { name: /Approve action/ })).toBeDisabled();
  });
  it("preserves event selection across List/Graph, filters conservatively and clears stale inspector", async () => {
    const user = userEvent.setup();
    render(<ActivityWorkspace room={room} />);
    await user.click(screen.getByRole("group", { name: "Activity type" }).querySelector('button:nth-child(4)')!);
    const timeline = within(screen.getByRole("list", { name: "Sample timeline" }));
    expect(timeline.getAllByRole("button")).toHaveLength(2);
    await user.click(timeline.getByRole("button", { name: /Approval requirement/ }));
    await user.click(screen.getByRole("tab", { name: "Graph" }));
    expect(inspector().getByRole("heading", { name: "Approval requirement example" })).toBeInTheDocument();
    await user.selectOptions(screen.getByRole("combobox", { name: "Related state" }), "S1");
    expect(screen.getByRole("heading", { name: "No matching examples" })).toBeInTheDocument();
    expect(inspector().getByRole("heading", { name: "No event selected" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Clear activity filters" }));
    expect(inspector().getByRole("heading", { name: "Disclosure boundary example" })).toBeInTheDocument();
  });
  for (const [name, Component] of [["proofs", ProofsWorkspace], ["activity", ActivityWorkspace]] as const) {
    it(name + " hides stale selection in every system state", async () => {
      const user = userEvent.setup();
      render(<Component room={room} />);
      await user.click(screen.getByText("Display examples · not service responses"));
      const controls = within(screen.getByRole("group", { name: "Display state" }));
      for (const value of ["empty", "loading", "blocked", "error", "unavailable"]) {
        await user.click(controls.getByRole("button", { name: value }));
        expect(inspector().getByRole("heading", { name: /No (state|event) selected/ })).toBeInTheDocument();
        expect(inspector().queryByRole("navigation", { name: "Selected state destinations" })).not.toBeInTheDocument();
      }
      await user.click(screen.getByRole("button", { name: "Reset display example" }));
      expect(inspector().queryByRole("heading", { name: /No (state|event) selected/ })).not.toBeInTheDocument();
    });
  }
  it("contains no network, storage, cryptographic engine, historical proof or private data adapter", () => {
    const files = readdirSync("src/features/provenance").filter((f) => /\.tsx?$/.test(f));
    for (const file of files) {
      const source = readFileSync("src/features/provenance/" + file, "utf8");
      expect(source).not.toMatch(/\bfetch\s*\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage|indexedDB|use server|crypto\.subtle|createHash/);
      expect(source).not.toMatch(/from\s+["'][^"']*(?:engines|nodes|tests\/|chain_anchor|state_proof)/);
      expect(source).not.toMatch(/0x[0-9a-fA-F]{40,}|[0-9a-f]{64}|file:\/\//);
      expect(source).not.toMatch(/(?:privateKey|secretShare|patientId|matchedIdentifiers)\s*:/);
    }
  });
});
