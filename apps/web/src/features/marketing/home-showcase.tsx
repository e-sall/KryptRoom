"use client";
import { useEffect, useLayoutEffect, useRef, useState, useSyncExternalStore } from "react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui";
import { demoGraph, demoScenes } from "./demo-model";

export const showcaseDurations = [2600, 2800, 3200, 3600, 3800, 4000, 3600] as const;
export const showcaseDuration = 3600;
const media = "(prefers-reduced-motion: reduce)";
const subscribeHydration = () => () => {};
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
export function ShowcaseLineage({ scene = 6, concealed = false }: { scene?: number; concealed?: boolean }) {
  const paths: Record<string, string> = {
    "S1-S2": "M200 150 C260 150 260 54 340 54", "S1-S3": "M200 150 C260 150 260 246 340 246",
    "S2-S4": "M600 54 C690 54 670 150 760 150", "S3-S4": "M600 246 C690 246 670 150 760 150",
  };
  const mobile: Record<string, string> = {
    "S1-S2": "M500 65 V95 H230 V123", "S1-S3": "M500 65 V95 H770 V123",
    "S2-S4": "M230 210 V235 H500 V267", "S3-S4": "M770 210 V235 H500 V267",
  };
  return <figure className="showcase-lineage" aria-label="Synthetic RoomState lineage" data-concealed={concealed} aria-hidden={concealed || undefined}>
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
  // Server/no-JS output stays a complete static diagram. Only the hydrated
  // slideshow conceals future stages; visibility preserves their layout space.
  const storyReady = useSyncExternalStore(subscribeHydration, () => true, () => false);
  const reduced = useSyncExternalStore(subscribeMotion, () => window.matchMedia?.(media).matches ?? true, () => true);
  const pageVisible = useSyncExternalStore(subscribeVisibility, () => document.visibilityState === "visible", () => false);
  const running = playing && visible && pageVisible && !reduced;
  useEffect(() => {
    if (!ref.current || !window.IntersectionObserver) return;
    const observer = new IntersectionObserver(entries => setVisible(entries.some(e => e.isIntersecting)), { threshold: 0.15 });
    observer.observe(ref.current); return () => observer.disconnect();
  }, []);
  // Stop the timer in the same commit that exposes data-running=false. Passive
  // cleanup can leave one queued clock tick between the DOM update and teardown.
  useLayoutEffect(() => {
    if (!running) return;
    const timer = window.setTimeout(() => setScene(index => (index + 1) % demoScenes.length), showcaseDurations[scene]);
    return () => window.clearTimeout(timer);
  }, [running, scene]);
  const current = demoScenes[scene];
  return <section ref={ref} className="home-showcase" aria-labelledby="showcase-title" id="product-demo" data-running={running} data-scene={scene + 1}>
    <div className="showcase-heading"><h2 id="showcase-title" className="eyebrow">THE PRODUCT, IN MOTION</h2></div>
    <div className="showcase-window">
      <div className="showcase-topbar"><Brand /><span>Supply Chain Collaboration</span><span className="badge badge-preview">SYNTHETIC PREVIEW</span></div>
      <div className="showcase-body">
        <nav className="showcase-scenes" aria-label="Homepage demo scenes">{demoScenes.map((s, i) => <button key={s.name}
          aria-current={scene === i ? "step" : undefined} onClick={() => { setPlaying(false); setScene(i); }}
          aria-label={`Show scene ${i + 1}: ${s.name}`}><span>{String(i + 1).padStart(2, "0")}</span><span>{s.name}</span></button>)}</nav>
        <div className="showcase-stage" data-running={running} aria-label="Homepage demo visualization" data-story-ready={storyReady} data-focus={scene}>
          <div className="showcase-organizations" data-active={scene === 0}><span>Organization A<small>Own environment</small></span><span>Organization B<small>Own environment</small></span></div>
          <div className="showcase-protected-inputs" data-active={scene === 1} data-concealed={storyReady && scene < 1} aria-hidden={storyReady && scene < 1 || undefined}>Protected inputs <span aria-hidden="true">↓</span></div>
          <div className="showcase-operation" data-active={scene === 2} data-concealed={storyReady && scene < 2} aria-hidden={storyReady && scene < 2 || undefined}>Private computation <span>Illustration only</span></div>
          <div className="showcase-film" aria-hidden="true" data-act={scene}><div className="film-orbit film-orbit-a" /><div className="film-orbit film-orbit-b" /><div className="film-packets"><i /><i /><i /></div></div>
          <div className="showcase-lineage-slot"><ShowcaseLineage scene={scene} concealed={storyReady && scene < 3} />
            {storyReady && scene < 3 && <p className="showcase-next-stage">{["Two independent environments. One shared question.", "Protected inputs stay with their owners.", "A private operation can evolve a reusable state."][scene]}<small>Illustration · lineage appears at State Creation</small></p>}
          </div>

          <p className="showcase-story-note" data-highlight={scene >= 4}>{current.note}</p>
        </div>
        <aside className="showcase-context" aria-label="Homepage demo context">
          <p className="eyebrow">SCENE {String(scene + 1).padStart(2, "0")} / 07</p>
          <div className="showcase-current" aria-live={running ? "off" : "polite"} aria-atomic="true"><h3>{current.name}</h3><p>{current.description}</p></div>
          <div className="showcase-moments" role="group" aria-label="Illustrative state details"><section data-moment="4" hidden={scene !== 4}><span>PROTECTED S4</span><strong>Policy gate → permitted output</strong><small>Illustration only · no value disclosed</small></section><section data-moment="5" hidden={scene !== 5}><span>PROVENANCE</span><strong>Commitment ≠ proof ≠ anchor</strong><small>Proof: Not assessed · Anchor: Not anchored</small></section><section data-moment="6" hidden={scene !== 6}><span>INSPECT S4 · SYNTHETIC</span><strong>Parents [S2, S3]</strong><small>Persistent state · ordered lineage · protected artifacts</small></section></div>
          <dl data-focus={scene}><dt>State</dt><dd>S4 · synthetic</dd><dt>Ordered parents</dt><dd>S2 · S3</dd><dt>Proof</dt><dd>Not assessed</dd><dt>Anchor</dt><dd>Not anchored</dd></dl>
          <p className="caption">No dataset, proof, transaction or disclosed result is loaded.</p>
        </aside>
      </div>
      <div className="showcase-controls"><div><Button disabled={reduced} onClick={() => setPlaying(p => !p)} aria-pressed={!playing}>{playing ? "Pause demo" : "Resume demo"}</Button>
        <Button variant="ghost" onClick={() => { setScene(0); setPlaying(true); }}>Replay demo</Button></div>
        <span className="caption">{reduced ? "Reduced motion · choose any scene" : !playing ? "Paused · explore at your pace" : running ? "Automatic visual walkthrough" : "Autoplay waits while out of view"}</span>
        </div>
    </div>
    <noscript><p>This is a static synthetic collaboration diagram. JavaScript is required for the optional slideshow. The explanations and footer demo link remain available.</p></noscript>
  </section>;
}
