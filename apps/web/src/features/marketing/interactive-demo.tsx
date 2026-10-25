"use client";
import { useState, type KeyboardEvent } from "react";
import { Brand } from "@/components/brand";
import { Button, ButtonLink } from "@/components/ui";
import { demoGraph, demoScenes, demoRoomId, initialDemoScene, boundedScene } from "./demo-model";
import { DemoDiagram } from "./demo-diagram";

export function InteractiveDemo() {
  const [scene, setScene] = useState(initialDemoScene);
  const [presentation, setPresentation] = useState(false);
  const [selected, setSelected] = useState("S4");
  const current = demoScenes[scene];
  const state = demoGraph.states.find((s) => s.id === selected)!;
  function go(index: number) { setScene(boundedScene(index)); setSelected("S4"); }
  function sceneKeys(event: KeyboardEvent<HTMLElement>) {
    const delta = ["ArrowRight", "ArrowDown"].includes(event.key) ? 1 : ["ArrowLeft", "ArrowUp"].includes(event.key) ? -1 : 0;
    if (!delta && !["Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? 6 : boundedScene(scene + delta);
    go(next);
    event.currentTarget.querySelectorAll<HTMLButtonElement>("button")[next]?.focus();
  }
  return <section className="interactive-demo" aria-label="Preloaded interactive demonstration" data-mode={presentation ? "presentation" : "explore"}>
    <div className="demo-toolbar"><div><strong>Demo Preview</strong><span className="demo-scenario-label">Preloaded Scenario · Synthetic</span></div>
      <div className="segmented-control" role="group" aria-label="Demo mode">
        <button aria-pressed={!presentation} onClick={() => setPresentation(false)}>Explore</button>
        <button aria-pressed={presentation} onClick={() => setPresentation(true)}>Presentation</button>
      </div>
    </div>
    <div className="demo-frame">
      <div className="demo-brandbar"><Brand /><span>Interactive Demo</span><span className="demo-scenario-label">No live execution</span></div>
      <div className="demo-columns">
        <aside className="demo-sequence" aria-label="Demo sequence">
          <p className="eyebrow">{presentation ? "PRESENTATION MODE" : "DEMO SEQUENCE"}</p>
          <h2>How privacy<br />becomes useful.</h2>
          <nav aria-label="Demo scenes" onKeyDown={sceneKeys}>{demoScenes.map((step, i) =>
            <button key={step.name} aria-current={scene === i ? "step" : undefined} onClick={() => go(i)}><span>{String(i + 1).padStart(2, "0")}</span>{step.name}</button>)}</nav>
          <div className="demo-sequence-footer"><strong>{presentation ? "Presentation Mode" : "Explore Mode"}</strong><p>{presentation ? "Guided scene navigation" : "Choose scenes freely"}</p></div>
        </aside>
        <div className="demo-center" aria-label="Demo visualization">
          <div className="demo-center-heading"><span>PROTECTED COMPUTATION → PERSISTENT STATE</span><span>SCENE {String(scene + 1).padStart(2, "0")} / 07</span></div>
          <DemoDiagram scene={scene} selected={selected} onSelect={setSelected} />
        </div>
        <aside className="demo-inspector" aria-label="Demo context">
          <p className="eyebrow">{presentation ? "PRESENTATION NOTES" : "SCENE INSPECTOR"}</p>
          <div className="demo-current" aria-live="polite" aria-atomic="true"><span className="demo-scene-number">SCENE {String(scene + 1).padStart(2, "0")} / 07</span><h2>{current.name}</h2></div>
          <div className="demo-context-block"><p className="eyebrow">SCENARIO TYPE</p><p>Deterministic visual replay</p></div>
          <div className="demo-context-block"><p className="eyebrow">CURRENT MOMENT</p><h3>{current.heading}</h3><p>{current.description}</p></div>
          <details className="demo-explanation" key={scene}><summary>What this scene means</summary><p>{current.note}</p>
            {scene === 5 && <p>Layer A: actual chain inclusion and canonical finality. Layer B: document/commitment consistency. Layer C: explicit cryptographic proof verification. None is performed here; B does not establish C or MPC correctness.</p>}
          </details>
          {scene === 6 && <div className="demo-selected-state" aria-live="polite"><h3>{state.id} · {state.title}</h3><dl><dt>Ordered parents</dt><dd>{state.parent_state_ids.join(" · ") || "None"}</dd><dt>Operation label</dt><dd>{state.operation}</dd><dt>Context</dt><dd>{state.contextLabel}</dd></dl>
            <ButtonLink href={`/preview/rooms/${demoRoomId}/workspace/${state.id}`}>Inspect {state.id} in workspace</ButtonLink>
            <ButtonLink href={`/preview/rooms/${demoRoomId}/proofs/${state.id}`}>Explore {state.id} provenance</ButtonLink>
          </div>}
          <dl className="demo-status"><dt>Proof status</dt><dd>Not assessed</dd><dt>Anchor</dt><dd>Not anchored</dd></dl>
          <p className="caption">No live computation or transaction</p>
        </aside>
      </div>
    </div>
    <div className="demo-controls">
      <Button disabled={scene === 0} onClick={() => go(scene - 1)}>Previous</Button>
      <nav aria-label="Demo scene shortcuts" onKeyDown={sceneKeys}>{demoScenes.map((step, i) =>
        <button key={step.name} aria-label={`Scene ${i + 1}: ${step.name}`} aria-current={scene === i ? "step" : undefined} onClick={() => go(i)}>{String(i + 1).padStart(2, "0")}</button>)}</nav>
      <Button disabled={scene === 6} onClick={() => go(scene + 1)}>Next</Button>
    </div>
    <div className="demo-reset"><Button variant="ghost" onClick={() => { go(0); setPresentation(false); }}>Restart demo</Button><p className="caption">Replay changes the view only. No authorization, persistence or disclosure occurs.</p></div>
  </section>;
}
