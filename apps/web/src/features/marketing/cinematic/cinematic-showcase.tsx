"use client";

import { useEffect, useRef } from "react";
import { createMovie } from "./renderer";
import { duration } from "./timeline";
import "./cinematic.css";

type Review = { seek(ms: number): void; resume(): void; time(): number };
declare global { interface Window { kryptroomMovieReview?: Review } }

/** Synthetic presentation only. No data/backend connection or operational click targets. */
export function CinematicShowcase() {
  const section = useRef<HTMLElement>(null);
  const svg = useRef<SVGSVGElement>(null);
  useEffect(() => {
    const host = section.current, surface = svg.current;
    if (!host || !surface || !window.matchMedia || !window.IntersectionObserver) return;
    const movie = createMovie(surface);
    const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const narrow = window.matchMedia("(max-width: 700px)");
    let visible = false, time = 0, last: number | null = null, request = 0, reviewing = false;
    const permitted = () => visible && !document.hidden && document.visibilityState === "visible" && !motion.matches && !narrow.matches && !reviewing && time < duration;
    const frame = (now: number) => {
      request = 0;
      if (!permitted()) { last = null; return; }
      if (last !== null) time = Math.min(duration, time + Math.min(80, now - last));
      last = now;
      movie.renderAt(time);
      host.dataset.running = String(permitted());
      if (permitted()) request = requestAnimationFrame(frame);
    };
    const update = () => {
      cancelAnimationFrame(request); request = 0; last = null;
      host.dataset.ready = "true";
      host.dataset.static = String(motion.matches || narrow.matches);
      host.dataset.running = String(permitted());
      if (permitted()) request = requestAnimationFrame(frame);
    };
    const observer = new IntersectionObserver(entries => {
      visible = entries.some(entry => entry.isIntersecting && entry.intersectionRatio >= .25); update();
    }, { threshold: [0, .25, .5] });
    observer.observe(surface);
    document.addEventListener("visibilitychange", update);
    motion.addEventListener("change", update); narrow.addEventListener("change", update);
    // Compile-time development guard: no public timeline, query-string seek or visitor controls.
    if (process.env.NODE_ENV === "development") window.kryptroomMovieReview = {
      seek(ms) { reviewing = true; time = Math.max(0, Math.min(duration, ms)); update(); movie.renderAt(time); },
      resume() { reviewing = false; update(); }, time: () => time,
    };
    update();
    return () => {
      cancelAnimationFrame(request); observer.disconnect(); movie.destroy();
      document.removeEventListener("visibilitychange", update);
      motion.removeEventListener("change", update); narrow.removeEventListener("change", update);
      if (process.env.NODE_ENV === "development") delete window.kryptroomMovieReview;
    };
  }, []);
  return <section ref={section} id="product-walkthrough" className="cinematic-showcase" aria-labelledby="walkthrough-title">
    <h2 id="walkthrough-title" className="eyebrow">KryptRoom · Product Walkthrough</h2>
    <div className="cinematic-frame">
      <div className="cinematic-context"><span>Supply Chain Collaboration</span><span>Concept preview · Synthetic data</span></div>
      <svg ref={svg} viewBox="0 0 1120 620" role="img" aria-labelledby="cinematic-title cinematic-description">
        <title id="cinematic-title">KryptRoom: from independent organizations to proposed actions</title>
        <desc id="cinematic-description">A silent, synthetic product demonstration. Two organizations create a Room, protect four local inputs and simulate a private analysis. Twelve sample risk signals: six production, four transit, two other. Conceptual Ask AI interprets authorized aggregates and proposes actions requiring human review. No real computation, AI, approval or transaction occurs.</desc>
      </svg>
      <div className="cinematic-static">
        <p className="eyebrow">Independent organizations. A shared question.</p>
        <h3>From protected inputs to informed decisions.</h3>
        <ol><li><strong>Manufacturer + Logistics Partner</strong><span>A shared Room; two local inputs per organization.</span></li>
          <li><strong>Private analysis, illustrated</strong><span>Protected inputs remain separate. Only authorized aggregate outputs appear.</span></li>
          <li><strong>12 sample risk signals</strong><span>6 production · 4 transit · 2 other.</span></li>
          <li><strong>Insights for human review</strong><span>Conceptual AI recommendations. No action assigned, approved or executed.</span></li></ol>
        <p>Static overview for smaller screens, reduced motion or unavailable animation.</p>
      </div>
    </div>
  </section>;
}
