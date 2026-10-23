import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { readFileSync, readdirSync } from "node:fs";
import { exampleRooms } from "../src/features/rooms/preview-model";
import { graphFixture } from "../src/features/graph/fixtures";
import { ComputationsWorkspace } from "../src/features/operations/computations-workspace";
import { ResultsWorkspace } from "../src/features/operations/results-workspace";
import { isOperation, operationIds, presentationReadiness, resultContext, sampleAggregates, sampleCardinality, selectedInputs } from "../src/features/operations/presentation";
vi.mock("next/navigation", () => ({ usePathname: () => "/preview/rooms/supply-chain/computations" }));
const room = exampleRooms[0];
const inspector = () => within(screen.getByLabelText("Context inspector"));

describe("isolated operation presentation", () => {
  it("preserves parent order and source immutability, rejects unknown/duplicate inputs for readiness", () => {
    const states = graphFixture(room.id), before = JSON.stringify(states);
    expect(selectedInputs(states, ["S3", "S2"]).map((s) => s.id)).toEqual(["S3", "S2"]);
    for (const ids of [[], ["missing"], ["S1", "S1"], ["S1", "missing"]])
      expect(presentationReadiness(states, ids).presentationComplete).toBe(false);
    const decision = presentationReadiness(states, ["S2", "S3"]);
    expect(decision.presentationComplete).toBe(true);
    expect([decision.execute, decision.approve, decision.persist, decision.reveal]).toEqual([false, false, false, false]);
    expect(JSON.stringify(states)).toBe(before);
    expect(states.find((s) => s.id === "S4")?.parent_state_ids).toEqual(["S2", "S3"]);
  });
  it("uses the existing graph labels instead of silently adopting conflicting P08 state IDs", () => {
    expect(resultContext(room.id, "join").associated?.id).toBe("S2");
    expect(resultContext(room.id, "analytics").associated?.id).toBe("S4");
    expect(resultContext(room.id, "analytics").sources.map((s) => s.id)).toEqual(["S2", "S3"]);
    expect(resultContext(room.id, "psi").hypothetical).toBe(true);
    expect(resultContext("insights", "psi").associated?.title).toBe("PSI");
    for (const op of operationIds) expect(resultContext("research", op).available).toBe(false);
  });
  it("has a closed operation set and frozen fixed display values only", () => {
    expect(operationIds).toEqual(["psi", "join", "analytics"]);
    expect(isOperation("fhe" )).toBe(false); expect(isOperation("__proto__")).toBe(false);
    expect(sampleCardinality).toBe(1248);
    expect(sampleAggregates.map((x) => x.value)).toEqual([42, 68, 55, 81]);
    expect(Object.isFrozen(sampleAggregates)).toBe(true);
    for (const value of sampleAggregates) { expect(Object.isFrozen(value)).toBe(true); expect(Object.keys(value)).toEqual(["cohort", "value"]); }
  });
});
describe("P07 Clean workflow", () => {
  it("selects inputs and operators, traverses all phases and resets without enabling execution", async () => {
    const user = userEvent.setup(); render(<ComputationsWorkspace room={room} />);
    await user.click(screen.getByRole("checkbox", { name: /S2 · Private Join/ }));
    await user.click(screen.getByRole("checkbox", { name: /S3 · Analytics/ }));
    await user.click(within(screen.getByRole("group", { name: "Operation example" })).getByRole("button", { name: /PSI Cardinality/ }));
    expect(inspector().getByRole("heading", { name: "PSI Cardinality" })).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Next phase" }));
    expect(screen.getByText(/This visual step does not execute psi_cardinality/)).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Next phase" }));
    expect(inspector().getByRole("tab", { name: "Review" })).toHaveAttribute("aria-selected", "true");
    expect(inspector().getByText("S1 → S2 → S3")).toBeVisible();
    expect(screen.getByRole("link", { name: "Explore fixed result example" })).toHaveAttribute("href", "/preview/rooms/supply-chain/results/psi");
    for (const name of [/Run computation/, /Approve/, /Save transition/]) expect(inspector().getByRole("button", { name })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Previous phase" }));
    await user.click(screen.getByRole("button", { name: "Reset preview" }));
    expect(screen.getByRole("checkbox", { name: /S1 · Initial State/ })).toBeChecked();
    expect(screen.getByRole("checkbox", { name: /S2 · Private Join/ })).not.toBeChecked();
    expect(inspector().getByRole("heading", { name: "Private Join" })).toBeVisible();
  });
  it("reports absent inputs, supports direct phase selection and keyboard inspector tabs", async () => {
    const user = userEvent.setup(); render(<ComputationsWorkspace room={room} />);
    await user.click(screen.getByRole("checkbox", { name: /S1 · Initial State/ }));
    await user.click(screen.getByRole("button", { name: "Next phase" }));
    expect(screen.getByRole("alert")).toHaveTextContent("Select at least one illustrative input");
    await user.click(screen.getByRole("checkbox", { name: /S4 · Private Analytics/ }));
    expect(screen.getByText("Parents: S2 · S3")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "03New State & Review" }));
    const tab = inspector().getByRole("tab", { name: "Review" });
    await user.click(tab); await user.keyboard("{Home}");
    expect(inspector().getByRole("tab", { name: "Readiness" })).toHaveFocus();
    expect(inspector().getByText("No authoritative permission decision")).toBeVisible();
  });
  it("clears inspector and diagram for every system state without stale authority", async () => {
    const user = userEvent.setup(); render(<ComputationsWorkspace room={room} />);
    await user.click(screen.getByText("Display examples · not service responses"));
    for (const value of ["empty", "loading", "blocked", "error", "unavailable"]) {
      await user.click(screen.getByRole("button", { name: value }));
      expect(screen.queryByLabelText("Hypothetical transition diagram")).toBeNull();
      expect(inspector().getByRole("heading", { name: "No operation context" })).toBeVisible();
      expect(inspector().getByRole("button", { name: /Run computation/ })).toBeDisabled();
    }
  });
});
describe("P08 editorial result views", () => {
  it.each(operationIds)("renders only the selected %s result and denies real actions", (operation) => {
    render(<ResultsWorkspace room={room} operation={operation} />);
    expect(screen.getAllByRole("article")).toHaveLength(1);
    expect(inspector().getByRole("button", { name: /Reveal result/ })).toBeDisabled();
    expect(inspector().getByRole("button", { name: /Download result/ })).toBeDisabled();
    for (const status of ["Ready", "Authorized", "Completed", "Verified", "Finalized"]) expect(screen.queryByText(status, { exact: true })).toBeNull();
    if (operation === "join") { expect(screen.queryByRole("table")).toBeNull(); expect(screen.queryByText("1,248")).toBeNull(); }
    if (operation === "psi") expect(screen.getByText("1,248")).toBeVisible();
  });
  it("switches the same analytics values between accessible chart/table and opens progressive details", async () => {
    const user = userEvent.setup(); render(<ResultsWorkspace room={room} operation="analytics" />);
    expect(screen.getByRole("img", { name: /Illustrative aggregate units/ })).toBeVisible();
    await user.click(screen.getByRole("tab", { name: "Table" }));
    const table = within(screen.getByRole("table"));
    expect(table.getAllByRole("cell").map((e) => e.textContent)).toEqual(["42", "68", "55", "81"]);
    await user.click(screen.getByText("Explore result details"));
    expect(screen.getByText(/arbitrary example units/)).toBeVisible();
    expect(inspector().getByRole("link", { name: /Inspect S4/ })).toHaveAttribute("href", "/preview/rooms/supply-chain/workspace/S4");
    expect(inspector().getByRole("link", { name: /Source S2/ })).toHaveAttribute("href", "/preview/rooms/supply-chain/workspace/S2");
    await user.click(screen.getByRole("tab", { name: "Table" })); await user.keyboard("{Home}");
    expect(screen.getByRole("tab", { name: "Chart" })).toHaveFocus();
  });
  it("removes all example values and state context when display becomes blocked", async () => {
    const user = userEvent.setup(); render(<ResultsWorkspace room={room} />);
    await user.click(screen.getByText("Display examples · not service responses"));
    for (const value of ["empty", "loading", "blocked", "error", "unavailable"]) {
      await user.click(screen.getByRole("button", { name: value }));
      expect(screen.queryByText("1,248")).toBeNull(); expect(screen.queryByRole("article")).toBeNull();
      expect(inspector().getByRole("heading", { name: "No result selected" })).toBeVisible();
    }
  });
  it("does not invent results for an empty Room", () => {
    render(<ResultsWorkspace room={exampleRooms[1]} operation="analytics" />);
    expect(screen.queryByRole("article")).toBeNull(); expect(screen.queryByRole("img")).toBeNull();
    expect(screen.getByText("No examples in this view")).toBeVisible();
  });
  it("keeps production modules disconnected and rejects storage, network and crypto imports", () => {
    for (const file of readdirSync("src/features/operations").filter((p) => /\.tsx?$/.test(p))) {
      const source = readFileSync("src/features/operations/" + file, "utf8");
      expect(source).not.toMatch(/\b(fetch|WebSocket|XMLHttpRequest|sendBeacon)\s*\(|localStorage|sessionStorage|indexedDB|use server/);
      expect(source).not.toMatch(/from ["'].*(?:engines|chain\/|nodes\/|node:)/);
      expect(source).not.toMatch(/0x[a-f0-9]{40}|[a-f0-9]{64}|file:\/\//i);
    }
    expect(readFileSync("src/app/app/[module]/page.tsx", "utf8")).not.toMatch(/ResultsWorkspace|ComputationsWorkspace|resultContext/);
  });
});
