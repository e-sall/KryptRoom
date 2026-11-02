"use client";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { collaborationSteps } from "./collaboration-steps";
export { collaborationSteps } from "./collaboration-steps";

const subscribeHydration = () => () => {};
export function HowItWorks() {
  const [step, setStep] = useState(0);
  const section = useRef<HTMLElement>(null);
  const hydrated = useSyncExternalStore(subscribeHydration, () => true, () => false);
  useEffect(() => {
    const host = section.current;
    if (!host) return;
    let frame = 0;
    const measure = () => {
      frame = 0;
      const desktop = window.innerWidth >= 1200;
      const nav = document.querySelector('.marketing-navbar')?.getBoundingClientRect();
      const top = Math.ceil(nav?.bottom ?? 72) + 16;
      const travel = Math.round(Math.min(560, Math.max(320, innerHeight * .55)));
      host.style.setProperty('--how-top', `${top}px`);
      host.style.setProperty('--how-height', `${Math.min(600, innerHeight - top - 20)}px`);
      host.style.setProperty('--how-travel', `${travel}px`);
      const distance = top - host.getBoundingClientRect().top;
      host.dataset.scrollStep = String(travel / 4);
      // The outer runway scrolls natively; the compact card never grows.
      if (desktop) setStep(Math.max(0, Math.min(3, Math.floor((distance + 1) / (travel / 4)))));
    };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(measure); };
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(schedule);
    observer?.observe(host);
    const nav = document.querySelector('.marketing-navbar');
    if (nav) observer?.observe(nav);
    schedule();
    return () => {
      cancelAnimationFrame(frame); observer?.disconnect();
      window.removeEventListener('scroll', schedule); window.removeEventListener('resize', schedule);
    };
  }, []);
  const select = (i: number) => {
    setStep(i);
    const host = section.current;
    if (host && innerWidth >= 1200 && host.getBoundingClientRect().height > 0) {
      const top = parseFloat(host.style.getPropertyValue('--how-top')) || 88;
      const interval = Number(host.dataset.scrollStep) || 120;
      window.scrollBy({ top: host.getBoundingClientRect().top - top + (i + .2) * interval, behavior: 'instant' });
    }
  };
  return <section ref={section} className="how-it-works" data-enhanced={hydrated} aria-labelledby="how-title" id="how-it-works">
    <div className="how-panel"><p className="eyebrow section-label">HOW KRYPTROOM WORKS</p><h2 id="how-title">A shared goal.<br />Independent control.</h2>
    <p className="caption">Conceptual journey · not a connected setup or execution service.</p>
    <div className="how-layout"><ol aria-label="Four collaboration steps">{collaborationSteps.map((item, i) =>
      <li key={item.title} data-story-step={i}><button aria-current={step === i ? "step" : undefined} onClick={() => select(i)}>
        <span className="story-number">{String(i + 1).padStart(2, "0")}</span><span><strong>{item.title}</strong><small>{item.concept}</small></span></button>
        </li>)}</ol>
      <div className="how-visual-sticky"><figure className="how-visual" data-step={step} onPointerMove={(event) => {
        if (event.pointerType !== "mouse" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
        const bounds = event.currentTarget.getBoundingClientRect();
        event.currentTarget.style.setProperty("--story-dx", ((event.clientX - bounds.left) / bounds.width - 0.5) * 4 + "px");
      }} onPointerLeave={(event) => event.currentTarget.style.setProperty("--story-dx", "0px")}>
        <svg viewBox="0 0 440 260" role="img" aria-labelledby="how-visual-title" aria-describedby="how-visual-desc"><title id="how-visual-title">{`${collaborationSteps[step].title}: protected collaboration`}</title><desc id="how-visual-desc">Conceptual Room and two independent organizations, protected inputs and a reusable state. Contains no private data and performs no computation.</desc><rect x="12" y="12" width="416" height="236" rx="16" fill="var(--kr-surface)" stroke="var(--kr-border)"/><text x="220" y="40">Shared Room · illustrative</text><g className="how-organizations" opacity={step>=1?1:.12}><rect x="36" y="64" width="160" height="58" rx="8" fill="var(--kr-elevated)" stroke="var(--kr-text-secondary)"/><rect x="244" y="64" width="160" height="58" rx="8" fill="var(--kr-elevated)" stroke="var(--kr-text-secondary)"/><text x="116" y="98">Organization A</text><text x="324" y="98">Organization B</text></g><g className="how-inputs" opacity={step>=2?1:0}><path d="M116 123v33h208v-33" fill="none" stroke="#7caad5"/><text x="220" y="147">Protected inputs</text></g><g className="how-output" opacity={step===3?1:0}><path d="M220 157v22" stroke="#7caad5"/><rect x="95" y="180" width="250" height="46" rx="8" fill="var(--kr-blue-muted)" stroke="#7caad5"/><text x="220" y="208">Private operation → RoomState</text></g></svg>
        <figcaption aria-live="polite"><span>{String(step + 1).padStart(2, "0")} / 04</span><strong>{collaborationSteps[step].title}</strong><p>{collaborationSteps[step].text}</p><p className="caption">{collaborationSteps[step].detail}</p></figcaption>
      </figure><p className="caption">Choose a step. All explanations remain available without motion.</p></div>
    </div><a className="how-exit" href="#persistent-title">Continue to Technology →</a></div>
  </section>;
}
