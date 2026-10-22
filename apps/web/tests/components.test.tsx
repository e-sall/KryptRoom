import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import {
  Badge,
  Button,
  ButtonLink,
  Card,
  StatusView,
  TextField,
} from "../src/components/ui";
import { Brand } from "../src/components/brand";
import {
  modules,
  findModule,
  moduleHref,
  workspaceConnection,
} from "../src/lib/navigation";
import { ModulePlaceholder } from "../src/components/module-placeholder";

describe("foundation components", () => {
  it.each(["primary", "secondary", "ghost"] as const)(
    "renders the %s action variant",
    async (variant) => {
      const onClick = vi.fn();
      render(
        <Button variant={variant} onClick={onClick}>
          Example action
        </Button>,
      );
      const button = screen.getByRole("button", { name: "Example action" });
      expect(button).toHaveClass(`button-${variant}`);
      await userEvent.click(button);
      expect(onClick).toHaveBeenCalledOnce();
    },
  );
  it.each(["disabled", "loading"] as const)(
    "prevents %s actions",
    async (state) => {
      const onClick = vi.fn();
      render(
        <Button
          disabled={state === "disabled"}
          loading={state === "loading"}
          onClick={onClick}
        >
          Example
        </Button>,
      );
      const button = screen.getByRole("button");
      expect(button).toBeDisabled();
      if (state === "loading")
        expect(button).toHaveAttribute("aria-busy", "true");
      await userEvent.click(button);
      expect(onClick).not.toHaveBeenCalled();
    },
  );
  it("labels fields and preserves native validation semantics", () => {
    render(
      <TextField
        id="test"
        label="Label"
        hint="Example only"
        aria-invalid
        required
      />,
    );
    expect(screen.getByLabelText("Label")).toHaveAccessibleDescription(
      "Example only",
    );
    expect(screen.getByLabelText("Label")).toBeRequired();
    expect(screen.getByLabelText("Label")).toHaveAttribute(
      "aria-invalid",
      "true",
    );
  });
  it("renders links, brand and cards without fake backend data", () => {
    render(
      <Card>
        <Brand />
        <ButtonLink href="/app/rooms">Workspace</ButtonLink>
        <Badge status="not-assessed" />
      </Card>,
    );
    expect(
      screen.getByRole("link", { name: "KryptRoom home" }),
    ).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "Workspace" })).toHaveAttribute(
      "href",
      "/app/rooms",
    );
    expect(screen.getByText("Not assessed")).toBeVisible();
  });
  it.each(["empty", "loading", "blocked", "error", "unavailable"] as const)(
    "announces %s without claiming success",
    (state) => {
      render(<StatusView state={state} />);
      expect(
        screen.getByRole(state === "error" ? "alert" : "status"),
      ).toBeVisible();
      expect(
        screen.queryByText(/verified|finalized|computation succeeded/i),
      ).not.toBeInTheDocument();
    },
  );
});

describe("module boundary", () => {
  it("has unique routes and a closed unavailable connection", () => {
    expect(new Set(modules.map((item) => item.id)).size).toBe(modules.length);
    expect(findModule("invented")).toBeUndefined();
    expect(workspaceConnection.status).toBe("unavailable");
    for (const item of modules)
      expect(moduleHref(item.id)).toBe(`/app/${item.id}`);
  });
  it.each(modules)("keeps $id explicitly disconnected", (item) => {
    render(<ModulePlaceholder module={item} />);
    expect(
      screen.getByRole("heading", { level: 1, name: item.title }),
    ).toBeVisible();
    expect(screen.getByText("Unavailable", { exact: true })).toBeVisible();
    expect(screen.queryByText(/verified|finalized/i)).not.toBeInTheDocument();
    if (item.id === "rooms")
      expect(
        screen.getByRole("button", { name: "Create Room" }),
      ).toBeDisabled();
  });
});
