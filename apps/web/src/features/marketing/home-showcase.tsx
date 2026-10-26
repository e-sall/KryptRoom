"use client";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Brand } from "@/components/brand";
import { Button, ButtonLink } from "@/components/ui";
import { demoGraph, demoScenes } from "./demo-model";

export const showcaseDuration = 6000;
const media = "(prefers-reduced-motion: reduce)";
function subscribeMotion(notify: () => void) {
  if (!window.matchMedia) return () => {};
  const query = window.matchMedia(media); query.addEventListener("change", notify);
  return () => query.removeEventListener("change", notify);
}
function subscribeVisibility(notify: () => void) {
  document.addEventListener("visibilitychange", notify);
  return () => document.removeEventListener("visibilitychange", notify);
}

/** One read-only catalog shared with /demo; the timer advances presentation only. */
export function ShowcaseLineage({ scene = 6 }: { scene?: number }) {
  const paths: Record<string, string> = {
    "S1-S2": "M200 150 C260 150 260 54 340 54", "S1-S3": "M200 150 C260 150 260 246 340 246",
    "S2-S4": "M600 54 C690 54 670 150 760 150", "S3-S4": "M600 246 C690 246 670 150 760 150",
  };
  const mobile: Record<string, string> = {
    "S1-S2": "M500 65 V95 H230 V123", "S1-S3": "M500 65 V95 H770 V123",
    "S2-S4": "M230 210 V235 H500 V267", "S3-S4": "M770 210 V235 H500 V267",
  };
  return <figure className="showcase-lineage" aria-label="Synthetic RoomState lineage">
    <div className="showcase-dag" data-stage={scene}>
      {([false, true] as const).map(narrow => <svg key={String(narrow)} className={narrow ? "showcase-edges-mobile" : "showcase-edges-desktop"}
        viewBox={`0 0 1000 ${narrow ? 340 : 300}`} preserveAspectRatio="none" aria-hidden="true">
        {demoGraph.edges.map(e => <path key={e.parent + e.child} data-edge={`${e.parent}-${e.child}`} data-parent-index={e.parentIndex}
          d={(narrow ? mobile : paths)[`${e.parent}-${e.child}`]} />)}
      </svg>)}
      <ol aria-label="RoomStates and ordered parents">{demoGraph.states.map(s => <li key={s.id} className={`showcase-state showcase-${s.id.toLowerCase()}`} data-emphasis={s.id === "S4" && scene >= 3}>
        <span>{s.id === "S4" ? "REUSABLE STATE" : "PROTECTED STATE"}</span><strong>{s.id} <span>{s.title}</span></strong>
        <small>Parents: {s.parent_state_ids.join(" · ") || "None"}</small>
      </li>)}</ol>
    </div>
    <figcaption>S1 → S2 &amp; S3 → S4. Ordered parents of S4: S2, S3.</figcaption>
  </figure>;
}

export function HomeShowcase() {
  const ref = useRef<HTMLElement>(null);
  const [scene, setScene] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [visible, setVisible] = useState(false);
  const reduced = useSyncExternalStore(subscribeMotion, () => window.matchMedia?.(media).matches ?? true, () => true);
  const pageVisible = useSyncExternalStore(subscribeVisibility, () => document.visibilityState === "visible", () => false);
  const running = playing && visible && pageVisible && !reduced;
  useEffect(() => {
    if (!ref.current || !window.IntersectionObserver) return;
    const observer = new IntersectionObserver(entries => setVisible(entries.some(e => e.isIntersecting)), { threshold: 0.15 });
    observer.observe(ref.current); return () => observer.disconnect();
  }, []);
  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(() => setScene(index => (index + 1) % demoScenes.length), showcaseDuration);
    return () => window.clearInterval(timer);
  }, [running]);
  const current = demoScenes[scene];
  return <section ref={ref} className="home-showcase" aria-labelledby="showcase-title" id="product-demo" data-running={running} data-scene={scene + 1}>
    <div className="showcase-heading"><div><p className="eyebrow">THE PRODUCT, IN MOTION</p><h2 id="showcase-title">A shared question.<br />A protected way forward.</h2></div>
      <p>Seven moments in a private collaboration.<br />Synthetic demonstration · no live execution.</p></div>
    <div className="showcase-window">
      <div className="showcase-topbar"><Brand /><span>Supply Chain Collaboration</span><span className="badge badge-preview">SYNTHETIC PREVIEW</span></div>
      <div className="showcase-body">
        <nav className="showcase-scenes" aria-label="Homepage demo scenes">{demoScenes.map((s, i) => <button key={s.name}
          aria-current={scene === i ? "step" : undefined} onClick={() => { setPlaying(false); setScene(i); }}
          aria-label={`Show scene ${i + 1}: ${s.name}`}><span>{String(i + 1).padStart(2, "0")}</span><span>{s.name}</span></button>)}</nav>
        <div className="showcase-stage" aria-label="Homepage demo visualization">
          <div className="showcase-organizations" data-active={scene === 0}><span>Organization A<small>Own environment</small></span><span>Organization B<small>Own environment</small></span></div>
          <div className="showcase-protected-inputs" data-active={scene === 1}>Protected inputs <span aria-hidden="true">↓</span></div>
          <div className="showcase-operation" data-active={scene === 2}>Private computation <span>Illustration only</span></div>
          <ShowcaseLineage scene={scene} />
        </div>
        <aside className="showcase-context" aria-label="Homepage demo context">
          <p className="eyebrow">SCENE {String(scene + 1).padStart(2, "0")} / 07</p>
          <div className="showcase-current" aria-live={running ? "off" : "polite"} aria-atomic="true"><h3>{current.name}</h3><p>{current.description}</p></div>
          <dl><dt>State</dt><dd>S4 · synthetic</dd><dt>Ordered parents</dt><dd>S2 · S3</dd><dt>Proof</dt><dd>Not assessed</dd><dt>Anchor</dt><dd>Not anchored</dd></dl>
          <p className="caption">No dataset, proof, transaction or disclosed result is loaded.</p>
        </aside>
      </div>
      <div className="showcase-controls"><div><Button disabled={reduced} onClick={() => setPlaying(p => !p)} aria-pressed={!playing}>{playing ? "Pause demo" : "Resume demo"}</Button>
        <Button variant="ghost" onClick={() => { setScene(0); setPlaying(true); }}>Replay demo</Button></div>
        <span className="caption">{reduced ? "Reduced motion · choose any scene" : !playing ? "Paused · explore at your pace" : running ? "Automatic visual walkthrough" : "Autoplay waits while out of view"}</span>
        <ButtonLink href="/demo">Open full demo <span aria-hidden="true">↗</span></ButtonLink></div>
    </div>
    <noscript><p>This is a static synthetic collaboration diagram. JavaScript is required for the optional slideshow. The explanations and full demo link remain available.</p></noscript>
  </section>;
}
