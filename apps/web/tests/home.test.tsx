import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import Home from "../src/app/page";
import { HomeShowcase } from "../src/features/marketing/home-showcase";
import { demoGraph, demoScenes } from "../src/features/marketing/demo-model";

describe("founder-approved homepage", () => {
  it("preserves the locked order, original portrait and honest technical boundaries", () => {
    const { container } = render(<Home />);
    const order = [...container.querySelectorAll(".home-page > section")].map(s => s.getAttribute("aria-labelledby"));
    expect(order).toEqual(["home-title", "showcase-title", "why-title", "how-title", "persistent-title", "foundation-title", "founder-title", "final-title", "faq-title"]);
    expect(screen.getByAltText("Elimane Sall, founder of KryptRoom")).toHaveAttribute("src", "/images/elimane-sall.jpeg");
    expect(screen.getByText(/industrial engineering student at Polytechnique/)).toBeVisible();
    expect(screen.getByText(/no general malicious security/)).toBeVisible();
    expect(screen.getByText(/planned research and development direction/)).toBeInTheDocument();
    expect(container.querySelectorAll(".faq-questions details")).toHaveLength(10);
    expect(container.querySelector(".home-page > section:last-child")).toHaveAttribute("aria-labelledby", "faq-title");
  });
  it("keeps the no-motion fallback usable, scenes deterministic and the catalog immutable", async () => {
    const before = JSON.stringify(demoGraph.states);
    const user = userEvent.setup(); render(<HomeShowcase />);
    expect(screen.getByRole("button", { name: "Pause demo" })).toBeDisabled();
    const scenes = within(screen.getByRole("navigation", { name: "Homepage demo scenes" }));
    for (const [index, s] of demoScenes.entries()) {
      await user.click(scenes.getByRole("button", { name: `Show scene ${index + 1}: ${s.name}` }));
      expect(screen.getByLabelText("Homepage demo context")).toHaveTextContent(s.description);
    }
    await user.click(screen.getByRole("button", { name: "Replay demo" }));
    expect(scenes.getByRole("button", { name: /Show scene 1:/ })).toHaveAttribute("aria-current", "step");
    expect(screen.getByText("Not assessed")).toBeVisible(); expect(screen.getByText("Not anchored")).toBeVisible();
    expect(JSON.stringify(demoGraph.states)).toBe(before);
  });
});
