"use client";
import { useEffect, useLayoutEffect, useRef, useState, useSyncExternalStore } from "react";
import { BusinessVisual } from "./business-visual";
import { businessScenes, businessDurations } from "./business-story";
import { Button } from "@/components/ui";
import { demoGraph } from "./demo-model";

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
    "S1-S2": "M200 150 C260 150 260 62.5 340 62.5", "S1-S3": "M200 150 C260 150 260 237.5 340 237.5",
    "S2-S4": "M600 62.5 C690 62.5 670 150 760 150", "S3-S4": "M600 237.5 C690 237.5 670 150 760 150",
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
  // Server/no-JS output includes a fixed dashboard and full narrative. Only the hydrated
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
    const timer = window.setTimeout(() => setScene(index => (index + 1) % businessScenes.length), businessDurations[scene]);
    return () => window.clearTimeout(timer);
  }, [running, scene]);
  const displayScene = storyReady ? scene : 4;
  return <section ref={ref} className="home-showcase business-showcase" aria-labelledby="showcase-title" id="product-demo" data-running={running} data-scene={scene+1}>
    <div className="showcase-heading"><h2 id="showcase-title" className="eyebrow">THE PRODUCT, IN MOTION</h2></div>
    <div className="showcase-window business-window"><div className="business-topbar"><span>Manufacturing &amp; Supply Chain Collaboration</span><span className="business-concept">Interactive concept · Synthetic data</span></div>
      <div className="business-story-caption" aria-live={running?"off":"polite"}><span>{String(displayScene+1).padStart(2,"0")} / 07</span><div><h3>{businessScenes[displayScene].heading}</h3><p>{businessScenes[displayScene].description}</p></div></div>
      <BusinessVisual scene={displayScene}/>
      <div className="business-controls"><div><Button disabled={reduced} onClick={()=>setPlaying(p=>!p)} aria-pressed={!playing}>{playing?"Pause demo":"Resume demo"}</Button><Button variant="ghost" onClick={()=>{setScene(0);setPlaying(true);}}>Replay demo</Button></div><nav aria-label="Homepage demo scenes">{businessScenes.map((s,i)=><button key={s.name} aria-label={`Show scene ${i+1}: ${s.name}`} aria-current={scene===i?"step":undefined} onClick={()=>{setPlaying(false);setScene(i);}}>{String(i+1).padStart(2,"0")}</button>)}</nav><span className="caption">{reduced?"Reduced motion · choose a scene":running?"Automatic concept walkthrough":"Paused or outside the viewport"}</span></div>
    </div><noscript><div className="business-static"><p>Static synthetic business concept. No computation, authorization or disclosure occurs.</p><ol>{businessScenes.map(s=><li key={s.name}><strong>{s.name}</strong>: {s.description}</li>)}</ol></div></noscript>
  </section>;
}
