"use client";
import { useEffect, useRef, useState } from "react";

export const collaborationSteps = Object.freeze([
  { title: "Create Room", concept: "Protected collaboration", text: "Define a shared purpose. Each organization keeps control of its own environment.", detail: "A Room coordinates a collaboration; it is not a central warehouse of raw datasets." },
  { title: "Invite Participants", concept: "Distinct organizations", text: "Agree who participates and what the collaboration may produce.", detail: "Participant identity, approvals and production coordination remain future integration work." },
  { title: "Connect Data", concept: "Cryptographic layers", text: "Reference protected inputs where they belong. Do not expose raw records to other parties.", detail: "The appropriate cryptographic mechanism protects an operation. Encryption at rest alone is not encrypted computation." },
  { title: "Run Computation", concept: "Persistent state", text: "Evolve a protected RoomState. Reveal only explicitly authorized outputs.", detail: "Protected artifacts stay protected and can support subsequent authorized computations. A result does not imply permission to reveal it." },
].map((step) => Object.freeze(step)));

export function HowItWorks() {
  const [step, setStep] = useState(0);
  const section = useRef<HTMLElement>(null);
  const manualSelection = useRef(false);
  useEffect(() => {
    // Scrolling a clicked control into view must not overwrite that choice.
    // Resume scroll-following only on a new deliberate scrolling gesture.
    const resumeScroll = () => { manualSelection.current = false; };
    const resumeScrollKeys = (event: KeyboardEvent) => {
      if (["PageDown", "PageUp", "ArrowDown", "ArrowUp", "Home", "End", " "].includes(event.key)) resumeScroll();
    };
    function onScroll() {
      if (manualSelection.current || window.matchMedia("(prefers-reduced-motion: reduce)").matches || window.innerWidth < 768) return;
      const items = [...(section.current?.querySelectorAll<HTMLElement>("[data-story-step]") ?? [])];
      const nearest = items.map((element, index) => ({ index, distance: Math.abs(element.getBoundingClientRect().top - innerHeight * 0.42) })).sort((a, b) => a.distance - b.distance)[0];
      const bounds = section.current?.getBoundingClientRect();
      if (nearest && bounds && bounds.top < innerHeight * 0.65 && bounds.bottom > innerHeight * 0.4) setStep(nearest.index);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("wheel", resumeScroll, { passive: true });
    window.addEventListener("touchmove", resumeScroll, { passive: true });
    window.addEventListener("keydown", resumeScrollKeys);
    return () => {
      window.removeEventListener("scroll", onScroll); window.removeEventListener("wheel", resumeScroll);
      window.removeEventListener("touchmove", resumeScroll); window.removeEventListener("keydown", resumeScrollKeys);
    };
  }, []);
  return <section ref={section} className="marketing-cadran how-it-works" aria-labelledby="how-title" id="how-it-works">
    <p className="eyebrow">HOW KRYPTROOM WORKS</p><h2 id="how-title">A shared goal.<br />Independent control.</h2>
    <p className="caption">Conceptual journey · not a connected setup or execution service.</p>
    <div className="how-layout"><ol aria-label="Four collaboration steps">{collaborationSteps.map((item, i) =>
      <li key={item.title} data-story-step={i}><button aria-current={step === i ? "step" : undefined} onClick={() => { manualSelection.current = true; setStep(i); }}>
        <span className="story-number">{String(i + 1).padStart(2, "0")}</span><span><strong>{item.title}</strong><small>{item.concept}</small></span></button>
        <p>{item.text}</p><p className="caption">{item.detail}</p></li>)}</ol>
      <div className="how-visual-sticky"><figure className="how-visual" data-step={step} onPointerMove={(event) => {
        if (event.pointerType !== "mouse" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
        const bounds = event.currentTarget.getBoundingClientRect();
        event.currentTarget.style.setProperty("--story-dx", ((event.clientX - bounds.left) / bounds.width - 0.5) * 4 + "px");
      }} onPointerLeave={(event) => event.currentTarget.style.setProperty("--story-dx", "0px")}>
        <svg viewBox="0 0 440 260" role="img" aria-labelledby="how-visual-title" aria-describedby="how-visual-desc"><title id="how-visual-title">{`${collaborationSteps[step].title}: protected collaboration`}</title><desc id="how-visual-desc">Conceptual Room and two independent organizations, protected inputs and a reusable state. Contains no private data and performs no computation.</desc><rect x="12" y="12" width="416" height="236" rx="16" fill="#202421" stroke="#5e6c64"/><text x="220" y="40">Shared Room · illustrative</text><g opacity={step>=1?1:.35}><rect x="36" y="64" width="160" height="58" rx="8" fill="#30332e" stroke="#6c776e"/><rect x="244" y="64" width="160" height="58" rx="8" fill="#30332e" stroke="#6c776e"/><text x="116" y="98">Organization A</text><text x="324" y="98">Organization B</text></g><g opacity={step>=2?1:.25}><path d="M116 123v33h208v-33" fill="none" stroke="#7caad5"/><text x="220" y="147">Protected inputs</text></g><g opacity={step===3?1:.25}><path d="M220 157v22" stroke="#7caad5"/><rect x="95" y="180" width="250" height="46" rx="8" fill="#2c414c" stroke="#7caad5"/><text x="220" y="208">Private operation → RoomState</text></g></svg>
        <figcaption aria-live="polite"><span>{String(step + 1).padStart(2, "0")} / 04</span><strong>{collaborationSteps[step].title}</strong><p>{collaborationSteps[step].text}</p></figcaption>
      </figure><p className="caption">Scroll or choose a step. All explanations remain available without motion.</p></div>
    </div>
  </section>;
}
