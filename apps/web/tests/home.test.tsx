import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import Home from "../src/app/page";
import { HomeShowcase } from "../src/features/marketing/home-showcase";
import { businessScenes } from "../src/features/marketing/business-story";
import { demoGraph } from "../src/features/marketing/demo-model";

describe("founder-approved homepage", () => {
  it("preserves the locked order, original portrait and honest technical boundaries", () => {
    const { container } = render(<Home />);
    const order = [...container.querySelectorAll(".home-page > section")].map(s => s.getAttribute("aria-labelledby"));
    expect(order).toEqual(["home-title", "showcase-title", "why-title", "how-title", "persistent-title", "founder-title", "final-title", "faq-title"]);
    const portrait = screen.getByAltText("Elimane Sall, founder of KryptRoom");
    expect(portrait).toHaveAttribute("src", "/images/elimane-sall-768.webp");
    expect(portrait.closest("picture")?.querySelector("source")).toHaveAttribute("srcset", expect.stringContaining("1200w"));
    expect(portrait).toHaveAttribute("width", "3367"); expect(portrait).toHaveAttribute("height", "3958");
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
    for (const [index, s] of businessScenes.entries()) {
      await user.click(scenes.getByRole("button", { name: `Show scene ${index + 1}: ${s.name}` }));
      expect(screen.getByText(s.heading)).toBeVisible();
      expect(screen.getByText(s.description)).toBeVisible();
    }
    await user.click(screen.getByRole("button", { name: "Replay demo" }));
    expect(scenes.getByRole("button", { name: /Show scene 1:/ })).toHaveAttribute("aria-current", "step");
    expect(screen.getByText("Interactive concept · Synthetic data")).toBeVisible();
    expect(screen.getByText(/No LLM\/RAG is connected/)).toBeInTheDocument();
    expect(JSON.stringify(demoGraph.states)).toBe(before);
  });
});
