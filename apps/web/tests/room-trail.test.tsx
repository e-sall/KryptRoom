import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { RoomTrail } from "../src/features/operations/preview-controls";
import { ComputationsWorkspace } from "../src/features/operations/computations-workspace";
import { ResultsWorkspace } from "../src/features/operations/results-workspace";
import { ProofsWorkspace } from "../src/features/provenance/proofs-workspace";
import { ActivityWorkspace } from "../src/features/provenance/activity-workspace";
import { exampleRooms } from "../src/features/rooms/preview-model";

vi.mock("next/navigation", () => ({ usePathname: () => "/preview/rooms/supply-chain/proofs" }));
const room = exampleRooms[0];
const destinations = [["Graph Workspace", "workspace"], ["Proofs & Provenance", "proofs"], ["Activity", "activity"]] as const;
function expectTrail(roomId: string, stateId?: string) {
  const trail = within(screen.getByRole("navigation", { name: "Room preview journey" }));
  for (const [name, path] of destinations) {
    expect(trail.getByRole("link", { name })).toHaveAttribute("href", `/preview/rooms/${roomId}/${path}${stateId ? "/" + stateId : ""}`);
  }
  for (const name of ["Computations", "Results"]) expect(trail.getByRole("link", { name })).toHaveAttribute("href", `/preview/rooms/${roomId}/${name.toLowerCase()}`);
}

describe("RoomTrail state continuity", () => {
  it.each([undefined, "", "unknown", "S2/../S4"])("keeps generic destinations for absent or invalid state %s", (selectedStateId) => {
    render(<RoomTrail roomId={room.id} screen="proofs" selectedStateId={selectedStateId} />);
    expectTrail(room.id);
  });
  it("revalidates the selected ID against the destination Room catalog", () => {
    const { rerender } = render(<RoomTrail roomId={room.id} screen="proofs" selectedStateId="S4" />);
    expectTrail(room.id, "S4");
    rerender(<RoomTrail roomId="insights" screen="proofs" selectedStateId="S4" />);
    expectTrail("insights");
    rerender(<RoomTrail roomId="research" screen="activity" selectedStateId="S1" />);
    expectTrail("research");
  });
  it("propagates Proofs S2 and subsequent explicit selections", async () => {
    const user = userEvent.setup();
    render(<ProofsWorkspace room={room} initialSelected="S2" />);
    expectTrail(room.id, "S2");
    await user.click(within(screen.getByRole("group", { name: "RoomState selection" })).getByRole("button", { name: /^S4/ }));
    expectTrail(room.id, "S4");
  });
  it("propagates Activity S3 and S4, keeping empty event selection separate from a valid explicit filter", async () => {
    const user = userEvent.setup();
    render(<ActivityWorkspace room={room} initialSelected="S3" />);
    expectTrail(room.id, "S3");
    await user.selectOptions(screen.getByRole("combobox", { name: "Related state" }), "S4");
    expectTrail(room.id, "S4");
    await user.click(within(screen.getByRole("group", { name: "Activity type" })).getByRole("button", { name: "Security" }));
    await user.selectOptions(screen.getByRole("combobox", { name: "Related state" }), "S1");
    expectTrail(room.id, "S1");
    expect(screen.getByRole("heading", { name: "No matching examples" })).toBeInTheDocument();
    const inspector = within(screen.getByLabelText("Context inspector"));
    expect(inspector.getByRole("heading", { name: "No event selected" })).toBeInTheDocument();
    expect(inspector.queryByRole("navigation", { name: "Selected state destinations" })).not.toBeInTheDocument();
    expect(within(screen.getByRole("navigation", { name: "Workspace navigation" })).getByRole("link", { name: "Graph" })).toHaveAttribute("href", "/preview/rooms/supply-chain/workspace/S1");
    await user.click(screen.getByText("Display examples · not service responses"));
    await user.click(within(screen.getByRole("group", { name: "Display state" })).getByRole("button", { name: "unavailable" }));
    expectTrail(room.id);
  });
  it("leaves Computations generic even with multiple input selections", async () => {
    const user = userEvent.setup();
    render(<ComputationsWorkspace room={room} />);
    await user.click(screen.getByRole("checkbox", { name: /S2 · Private Join/ }));
    expectTrail(room.id);
  });
  it.each([["analytics", "S4"], ["join", "S2"], ["psi", undefined]] as const)("uses only the existing associated Results state for %s", (operation, stateId) => {
    render(<ResultsWorkspace room={room} operation={operation} />);
    expectTrail(room.id, stateId);
  });
});
