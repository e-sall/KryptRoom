import { useId } from "react";
import { sampleAggregates, sampleCardinality } from "./presentation";

export function PsiResult() {
  return <><h2 className="result-editorial-title">Only the overlap.</h2>
    <p className="caption">One illustrative count. No matching identities displayed.</p>
    <div className="psi-editorial"><div><p className="eyebrow">ILLUSTRATIVE CARDINALITY</p>
      <p className="result-number">{sampleCardinality.toLocaleString("en-US")}</p><p className="caption">Intersection size · fixed sample value</p></div>
      <svg viewBox="0 0 240 180" aria-hidden="true"><circle cx="90" cy="80" r="58" /><circle cx="146" cy="80" r="58" />
        <circle className="intersection-dot" cx="118" cy="80" r="4" /><text x="51" y="85">A</text><text x="174" y="85">B</text>
        <text className="intersection-caption" x="118" y="166" textAnchor="middle">Size only</text></svg>
    </div><div className="result-conclusion"><h3>A count is not a list of matches.</h3>
      <p>No individual records or matching identifiers are included in this fixture.</p></div></>;
}
export function JoinResult({ stateLabel }: { stateLabel: string }) {
  return <><h2 className="result-editorial-title">A state, not a spreadsheet.</h2>
    <p className="caption">A conceptual protected handoff. No joined dataset exists in this preview.</p>
    <div className="join-handoff" aria-label="Illustrative two-organization protected handoff">
      <div className="join-organizations">{["A", "B"].map((org) => <div key={org}><span className="organization-token">{org}</span>
        <strong>Example Organization {org}</strong><p className="caption">Protected reference only</p></div>)}</div>
      <div className="join-branches" aria-hidden="true"><span>↘</span><span>↙</span></div>
      <div className="join-state"><span className="eyebrow">PROTECTED STATE · ILLUSTRATION</span><strong>{stateLabel}</strong>
        <span className="caption">Private Join · Sample</span></div>
    </div><div className="result-conclusion"><h3>No plaintext joined rows.</h3>
      <p>Only reference labels and relationships are shown. No secret shares are loaded or reconstructed.</p></div></>;
}
export function AnalyticsChart() {
  const id = useId();
  return <figure className="analytics-chart"><svg viewBox="0 0 520 240" role="img" aria-labelledby={`${id}-title ${id}-desc`}>
    <title id={`${id}-title`}>Illustrative aggregate units by cohort</title>
    <desc id={`${id}-desc`}>Fixed samples: Cohort A 42, B 68, C 55, D 81. Not computed from private data. The table view contains exactly these values.</desc>
    {[0, 50, 100].map((v) => <g key={v}><path className="chart-grid" d={`M40 ${200 - v * 1.7} H510`} /><text className="chart-axis" x="38" y={204 - v * 1.7} textAnchor="end">{v}</text></g>)}
    {sampleAggregates.map((bar, i) => <g key={bar.cohort}><rect className={i === 3 ? "chart-bar emphasized" : "chart-bar"}
      x={65 + i * 114} y={200 - bar.value * 1.7} width="62" height={bar.value * 1.7} rx="5" />
      <text x={96 + i * 114} y={190 - bar.value * 1.7} textAnchor="middle">{bar.value}</text>
      <text x={96 + i * 114} y="225" textAnchor="middle">Cohort {bar.cohort}</text></g>)}
  </svg><figcaption>Fixed synthetic units · no underlying records. Chart and table use the same four values.</figcaption></figure>;
}
export function AnalyticsTable() {
  return <table className="analytics-table"><caption>Illustrative aggregates · fixed synthetic units, not MPC/FHE outputs</caption>
    <thead><tr><th scope="col">Cohort</th><th scope="col">Sample units</th></tr></thead>
    <tbody>{sampleAggregates.map((bar) => <tr key={bar.cohort}><th scope="row">Cohort {bar.cohort}</th><td>{bar.value}</td></tr>)}</tbody>
  </table>;
}
