import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import {
  emptyDraft,
  exampleRooms,
  filterRooms,
  previewGate,
  validateStep,
} from "../src/features/rooms/preview-model";
import { RoomsPreviewProvider } from "../src/features/rooms/preview-context";
import { EasySetup, Readiness } from "../src/features/rooms/easy-setup";
import { RoomDetails } from "../src/features/rooms/room-details";

describe("isolated Rooms presentation", () => {
  it("searches names, descriptions and organizations without case or whitespace sensitivity", () => {
    expect(filterRooms("  RESEARCH ", "all").map((r) => r.id)).toEqual([
      "research",
    ]);
    expect(filterRooms("analytics", "all")).toHaveLength(1);
    expect(filterRooms("example organization", "all")).toHaveLength(3);
    expect(filterRooms("missing", "all")).toEqual([]);
  });
  it("intersects search with status and fails empty for unknown filters", () => {
    expect(filterRooms("", "Setup required").map((r) => r.id)).toEqual([
      "research",
    ]);
    expect(filterRooms("research", "Ready")).toEqual([]);
    expect(filterRooms("", "invented")).toEqual([]);
  });
  it("contains only explicit fixtures and list-valued, internal parent references", () => {
    for (const room of exampleRooms) {
      expect(room.demo).toBe(true);
      for (const state of room.states) {
        expect(Array.isArray(state.parent_state_ids)).toBe(true);
        for (const parent of state.parent_state_ids)
          expect(room.states.some((s) => s.id === parent)).toBe(true);
      }
    }
  });
  it("labels details and lineage as illustrative, without numeric results or proof claims", () => {
    render(<RoomDetails room={exampleRooms[0]} />);
    expect(screen.getByRole("img")).toHaveAccessibleName(
      /Illustrative lineage.*Not a runtime record/,
    );
    expect(screen.getByText("Unavailable")).toBeVisible();
    expect(screen.queryByText(/Verified|Finalized/)).not.toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Open Workspace" }),
    ).toHaveAttribute("href", "/preview/rooms/supply-chain/workspace");
  });
  it.each(["", "a", "  ", "x".repeat(81)])(
    "rejects invalid Room identity %s",
    (name) => {
      expect(validateStep(0, { ...emptyDraft, name })).toMatch(/3 and 80/);
    },
  );
  it("validates description, optional invitations and opaque references", () => {
    expect(
      validateStep(0, {
        ...emptyDraft,
        name: "Example",
        description: "x".repeat(281),
      }),
    ).toMatch(/280/);
    expect(validateStep(1, emptyDraft)).toBeNull();
    expect(validateStep(1, { ...emptyDraft, organization: "Example" })).toMatch(
      /email/,
    );
    expect(
      validateStep(1, {
        ...emptyDraft,
        organization: "Example",
        email: "a@example.invalid",
      }),
    ).toBeNull();
    expect(
      validateStep(2, { ...emptyDraft, source: "example-source-a" }),
    ).toBeNull();
    for (const source of [
      "C:\\private.csv",
      "https://example.invalid",
      "raw,row,values",
    ])
      expect(validateStep(2, { ...emptyDraft, source })).toMatch(
        /example-only/,
      );
  });
  it("keeps execution denied even when the draft is valid", () => {
    const draft = {
      ...emptyDraft,
      name: "Fictional",
      organization: "Example",
      email: "a@example.invalid",
      source: "example-source-a",
    };
    for (const step of [0, 1, 2, 3])
      expect(validateStep(step, draft)).toBeNull();
    expect(previewGate().allowed).toBe(false);
  });
  it("preserves fields across all four steps without enabling business mutations", async () => {
    const user = userEvent.setup();
    render(
      <RoomsPreviewProvider>
        <EasySetup />
        <Readiness />
      </RoomsPreviewProvider>,
    );
    await user.click(screen.getByRole("button", { name: "Continue preview" }));
    expect(screen.getByRole("alert")).toHaveTextContent(/Room name/);
    await user.type(screen.getByLabelText("Room name"), "Fictional room");
    await user.click(screen.getByRole("button", { name: "Continue preview" }));
    await user.type(
      screen.getByLabelText("Organization name (optional)"),
      "Example lab",
    );
    await user.type(
      screen.getByLabelText("Invite by organization email"),
      "a@example.invalid",
    );
    expect(
      screen.getByRole("button", { name: "Send invitation" }),
    ).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Continue preview" }));
    await user.type(
      screen.getByLabelText("Opaque example reference (optional)"),
      "example-source-a",
    );
    expect(
      screen.getByRole("button", { name: "Connect data source" }),
    ).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Continue preview" }));
    expect(
      screen.getByRole("button", { name: "Save Room policy" }),
    ).toBeDisabled();
    await user.click(
      screen.getByRole("button", { name: "Review example fields" }),
    );
    expect(screen.getByText(/Example fields reviewed/)).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Run Computation" }),
    ).toBeDisabled();
    for (let i = 0; i < 3; i++)
      await user.click(screen.getByRole("button", { name: "Back" }));
    expect(screen.getByLabelText("Room name")).toHaveValue("Fictional room");
    await user.click(
      screen.getByRole("button", { name: "Reset example fields" }),
    );
    expect(screen.getByLabelText("Room name")).toHaveValue("");
  });
  it("never exposes preview data through application modules or adds I/O/storage capabilities", () => {
    const app = readFileSync("src/app/app/[module]/page.tsx", "utf8");
    expect(app).not.toMatch(/exampleRooms|RoomsPreview/);
    const entries = readdirSync("src", {
      recursive: true,
      withFileTypes: true,
    }).filter((e) => e.isFile() && /\.tsx?$/.test(e.name));
    for (const entry of entries) {
      const code = readFileSync(resolve(entry.parentPath, entry.name), "utf8");
      expect(code).not.toMatch(
        /\b(sendBeacon|fetch|WebSocket|Worker)\s*\(|\b(localStorage|sessionStorage|indexedDB)\b|type=["']file["']|["']use server["']/,
      );
      expect(code).not.toMatch(
        /from ["'].*(?:engines|krypt-node|chain\/|node:fs|node:child_process)/,
      );
    }
  });
});
