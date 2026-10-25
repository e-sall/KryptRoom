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
  useEffect(() => {
    function onScroll() {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || window.innerWidth < 768) return;
      const items = [...(section.current?.querySelectorAll<HTMLElement>("[data-story-step]") ?? [])];
      const nearest = items.map((element, index) => ({ index, distance: Math.abs(element.getBoundingClientRect().top - innerHeight * 0.42) })).sort((a, b) => a.distance - b.distance)[0];
      const bounds = section.current?.getBoundingClientRect();
      if (nearest && bounds && bounds.top < innerHeight * 0.65 && bounds.bottom > innerHeight * 0.4) setStep(nearest.index);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return <section ref={section} className="marketing-cadran how-it-works" aria-labelledby="how-title" id="how-it-works">
    <p className="eyebrow">HOW KRYPTROOM WORKS</p><h2 id="how-title">A shared goal.<br />Independent control.</h2>
    <p className="caption">Conceptual journey · not a connected setup or execution service.</p>
    <div className="how-layout"><ol aria-label="Four collaboration steps">{collaborationSteps.map((item, i) =>
      <li key={item.title} data-story-step={i}><button aria-current={step === i ? "step" : undefined} onClick={() => setStep(i)}>
        <span className="story-number">{String(i + 1).padStart(2, "0")}</span><span><strong>{item.title}</strong><small>{item.concept}</small></span></button>
        <p>{item.text}</p><p className="caption">{item.detail}</p></li>)}</ol>
      <div className="how-visual-sticky"><figure className="how-visual" data-step={step} onPointerMove={(event) => {
        if (event.pointerType !== "mouse" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
        const bounds = event.currentTarget.getBoundingClientRect();
        event.currentTarget.style.setProperty("--story-dx", ((event.clientX - bounds.left) / bounds.width - 0.5) * 4 + "px");
      }} onPointerLeave={(event) => event.currentTarget.style.setProperty("--story-dx", "0px")}>
        <svg viewBox="0 0 360 390" role="img" aria-labelledby="how-visual-title" aria-describedby="how-visual-desc">
          <title id="how-visual-title">Protected collaboration to reusable RoomState</title>
          <desc id="how-visual-desc">Two separate organizations connect through abstract cryptographic layers and a network to a protected state. This diagram contains no private data and performs no computation.</desc>
          <g className="how-organizations"><rect x="15" y="20" width="150" height="60" rx="9" /><rect x="195" y="20" width="150" height="60" rx="9" />
            <text x="90" y="45">Organization A</text><text x="270" y="45">Organization B</text><text className="how-subtext" x="90" y="64">Own environment</text><text className="how-subtext" x="270" y="64">Own environment</text></g>
          <g className="how-routes" data-active={step >= 1}><path d="M90 80 V103 Q90 115 102 115 H140 V141" /><path d="M270 80 V103 Q270 115 258 115 H220 V141" /></g>
          <g className="how-layers" data-active={step >= 2}>
            <path d="M20 163 L180 119 L340 163 L180 207 Z" /><path d="M20 200 L180 156 L340 200 L180 244 Z" /><path d="M20 237 L180 193 L340 237 L180 281 Z" />
            <g className="how-network"><path d="M108 198 L141 191 L173 204 L207 190 L243 200 L200 226 L173 204 L130 217 L108 198 M130 217 L168 238 L200 226 L228 243 M141 191 L200 226" />
              {[[108,198],[141,191],[173,204],[207,190],[243,200],[130,217],[200,226],[168,238],[228,243]].map(([x,y]) => <circle key={x + "-" + y} cx={x} cy={y} r="3" />)}</g>
          </g>
          <g className="how-state" data-active={step === 3}><path d="M180 282 V311 M176 306 L180 312 L184 306" /><rect x="60" y="322" width="240" height="52" rx="10" />
            <text x="180" y="345">New protected RoomState</text><text className="how-subtext" x="180" y="363">Explicitly authorized outputs only</text></g>
        </svg>
        <figcaption aria-live="polite"><span>{String(step + 1).padStart(2, "0")} / 04</span><strong>{collaborationSteps[step].title}</strong><p>{collaborationSteps[step].text}</p></figcaption>
      </figure><p className="caption">Scroll or choose a step. All explanations remain available without motion.</p></div>
    </div>
  </section>;
}
