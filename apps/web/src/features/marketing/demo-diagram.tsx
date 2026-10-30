import { demoGraph } from "./demo-model";

/** P05's branched silhouette with HTML labels; all edges come from the PR3 catalog. */
export function DemoDiagram({ scene, selected, onSelect }: { scene: number; selected: string; onSelect: (id: string) => void }) {
  const paths: Record<string, string> = {
    "S1-S2": "M180 120 C230 120 230 50.85 290 50.85",
    "S1-S3": "M180 120 C230 120 230 189.15 290 189.15",
    "S2-S4": "M510 50.85 C580 50.85 560 120 640 120",
    "S3-S4": "M510 189.15 C580 189.15 560 120 640 120",
  };
  const mobilePaths: Record<string, string> = {
    "S1-S2": "M500 74 V100 H230 V125", "S1-S3": "M500 74 V100 H770 V125",
    "S2-S4": "M230 210 V230 H500 V256", "S3-S4": "M770 210 V230 H500 V256",
  };
  return <div className="demo-visual" data-scene={scene + 1}>
    <div className="demo-organizations" data-emphasis={scene === 0}>
      {["A", "B"].map((letter) => <div key={letter}><strong>Organization {letter}</strong><span>Private environment</span></div>)}
    </div>
    <div className="demo-input-lines" data-visible={scene >= 1} aria-hidden="true"><i /><i /></div>
    <div className="demo-operation" data-visible={scene >= 2} data-emphasis={scene === 2}>
      <strong>Private computation</strong><span>Protected operation · illustration</span><div className="demo-operation-track" aria-hidden="true">• ─ • ─ • ─ • ─ •</div>
    </div>
    <section className="demo-lineage" aria-label="Illustrative RoomState lineage" data-visible={scene >= 3}>
      <h3 className="eyebrow">ROOMSTATE LINEAGE</h3>
      <div className="demo-dag">
        <svg className="demo-desktop-edges" viewBox="0 0 1000 240" preserveAspectRatio="none" aria-hidden="true">{demoGraph.edges.map((edge) =>
          <path key={edge.parent + edge.child} data-edge={edge.parent + "-" + edge.child} data-parent-index={edge.parentIndex}
            data-selected={edge.parent === selected || edge.child === selected} d={paths[edge.parent + "-" + edge.child]} />)}</svg>
        <svg className="demo-mobile-edges" viewBox="0 0 1000 330" preserveAspectRatio="none" aria-hidden="true">{demoGraph.edges.map((edge) =>
          <path key={edge.parent + edge.child} data-edge={edge.parent + "-" + edge.child} data-parent-index={edge.parentIndex}
            data-selected={edge.parent === selected || edge.child === selected} d={mobilePaths[edge.parent + "-" + edge.child]} />)}</svg>
        {demoGraph.states.map((state) => <button className={"demo-state demo-" + state.id.toLowerCase()} key={state.id}
          disabled={scene !== 6} aria-pressed={scene === 6 ? selected === state.id : undefined}
          aria-label={`Inspect ${state.id}: ${state.title}`} onClick={() => onSelect(state.id)}>
          {state.id === "S4" && <span className="demo-new-state">NEW ROOMSTATE · EXAMPLE</span>}
          <strong>{state.id}</strong><span>{state.title}</span>
          <small>Parents: {state.parent_state_ids.join(" · ") || "None"}</small>
        </button>)}
      </div>
      <p className="demo-lineage-caption">S1 branches to S2 and S3. Both lead to S4. Ordered parents of S4: S2, S3.</p>
    </section>
    <div className="demo-outcomes">
      <section data-visible={scene >= 4} data-emphasis={scene === 4}><h3>AUTHORIZED RESULT</h3><p>Approved output only</p><small>Concept only · no value disclosed</small></section>
      <section data-visible={scene >= 5} data-emphasis={scene === 5}><h3>PROOF &amp; PROVENANCE</h3><p>Proof · Not assessed</p><small>Chain anchor · Not anchored</small></section>
    </div>
    <p className="caption">Preloaded demonstration · No live execution</p>
  </div>;
}
