import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import Home from "../src/app/page";
import { InteractiveDemo } from "../src/features/marketing/interactive-demo";
import { HowItWorks, collaborationSteps } from "../src/features/marketing/how-it-works";
import { MarketingContent } from "../src/features/marketing/marketing-pages";
import { demoGraph, demoScenes } from "../src/features/marketing/demo-model";
import { graphFixture } from "../src/features/graph/fixtures";

const scenes = () => within(screen.getByRole("navigation", { name: "Demo scenes" }));
const context = () => within(screen.getByLabelText("Demo context"));
describe("P01 P02 P05 presentation contracts", () => {
  it("preserves the tagline and accessible demo/booking destinations", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Compute together. Reveal nothing.");
    const link = screen.getByRole("link", { name: "See how it works" });
    expect(link).toHaveAttribute("href", "/#how-it-works");
    expect(screen.queryByRole("link", { name: "Explore Product" })).not.toBeInTheDocument();
    screen.getAllByRole("link", { name: "Book a Demo" }).forEach((link) => expect(link).toHaveAttribute("href", "/book-demo"));
  });
  it("offers exactly the four approved steps and keeps every explanation available", async () => {
    const user = userEvent.setup(); render(<HowItWorks />);
    expect(collaborationSteps.map((step) => step.title)).toEqual(["Create Room", "Invite Participants", "Connect Data", "Run Computation"]);
    for (const step of collaborationSteps) {
      const button = screen.getByRole("button", { name: new RegExp(step.title) });
      await user.click(button); expect(button).toHaveAttribute("aria-current", "step");
      expect(screen.getByRole("figure")).toHaveTextContent(step.title);
      expect(screen.getByText(step.detail)).toBeVisible();
    }
    expect(screen.getByRole("img")).toHaveAccessibleDescription(/no private data/);
  });
  it("starts on restored V1 scene four with seven scenes and no assertion of verification", () => {
    render(<InteractiveDemo />);
    expect(scenes().getAllByRole("button")).toHaveLength(7);
    expect(scenes().getByRole("button", { name: /State Creation/ })).toHaveAttribute("aria-current", "step");
    expect(context().getByRole("heading", { name: "State Creation" })).toBeVisible();
    expect(context().getByText("Not assessed")).toBeVisible();
    expect(context().getByText("Not anchored")).toBeVisible();
    expect(screen.queryByText(/^(Verified|Finalized)$/)).not.toBeInTheDocument();
  });
  it("restarts at Organizations and enforces both navigation bounds", async () => {
    const user = userEvent.setup(); render(<InteractiveDemo />);
    await user.click(screen.getByRole("button", { name: "Presentation" }));
    await user.click(screen.getByRole("button", { name: "Restart demo" }));
    expect(screen.getByRole("button", { name: "Explore" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    for (const step of demoScenes.slice(1)) {
      await user.click(screen.getByRole("button", { name: "Next" }));
      expect(context().getByRole("heading", { name: step.name })).toBeVisible();
    }
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Previous" }));
    expect(context().getByRole("heading", { name: "Proof & Provenance" })).toBeVisible();
  });
  it.each(demoScenes.map((step, i) => [step.name, i] as const))("direct selection synchronizes %s and its explanation", async (name, i) => {
    const user = userEvent.setup(); render(<InteractiveDemo />);
    await user.click(screen.getByRole("button", { name: `Scene ${i + 1}: ${name}` }));
    expect(context().getByRole("heading", { name })).toBeVisible();
    await user.click(screen.getByText("What this scene means"));
    expect(context().getByText(demoScenes[i].note)).toBeVisible();
  });
  it("preserves selected state across mode changes and reuses the existing branched catalog", async () => {
    const user = userEvent.setup(); const before = JSON.stringify(graphFixture("supply-chain")); render(<InteractiveDemo />);
    await user.click(scenes().getByRole("button", { name: /Explore the State/ }));
    expect(demoGraph.edges.map((edge) => `${edge.parent}-${edge.child}`)).toEqual(["S1-S2", "S1-S3", "S2-S4", "S3-S4"]);
    expect(context().getByText("S2 · S3")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Inspect S2: Private Join" }));
    for (const mode of ["Presentation", "Explore"]) {
      await user.click(screen.getByRole("button", { name: mode }));
      expect(context().getByRole("link", { name: "Inspect S2 in workspace" })).toHaveAttribute("href", "/preview/rooms/supply-chain/workspace/S2");
      expect(context().getByRole("link", { name: "Explore S2 provenance" })).toHaveAttribute("href", "/preview/rooms/supply-chain/proofs/S2");
    }
    expect(JSON.stringify(graphFixture("supply-chain"))).toBe(before);
  });
  it("supports scene keyboard navigation and focus", async () => {
    const user = userEvent.setup(); render(<InteractiveDemo />);
    scenes().getByRole("button", { name: /State Creation/ }).focus();
    await user.keyboard("{End}"); expect(scenes().getByRole("button", { name: /Explore the State/ })).toHaveFocus();
    await user.keyboard("{Home}"); expect(scenes().getByRole("button", { name: /Organizations/ })).toHaveFocus();
    await user.keyboard("{ArrowRight}"); expect(scenes().getByRole("button", { name: /Protected Inputs/ })).toHaveFocus();
  });
  it("does not invent a booking provider, form or appointment", () => {
    const { container } = render(<MarketingContent section="book-demo" />);
    expect(screen.getByText("Unavailable", { exact: true })).toBeVisible();
    expect(container.querySelectorAll("form,input,iframe")).toHaveLength(0);
    expect(screen.getByRole("link", { name: "Contact the Founder" })).toHaveAttribute("href", "mailto:elimanesall.eng@gmail.com?subject=KryptRoom%20-%20Demo%20Inquiry");
  });
});
