import Link from 'next/link';
import { SignalArtwork } from './signal-artwork';
import './signal-v4.css';

export function SignalV4() {
  return <><section id="product-demo" className="signal-showcase" aria-label="KryptRoom · The Signal V4">
    <div className="signal-art"><SignalArtwork /></div>
    <div className="signal-mobile-summary">
      <p>Two companies. One answer. No raw data shared.</p>
      <p><strong>12</strong> Shared risk signals</p>
      <p>Production: 6 / 12 · 50%<br />Transit: 4 / 12 · 33%<br />Other: 2 / 12 · 17%</p>
      <p>Synthetic preview · No live computation</p>
    </div>
  </section><div className="signal-followup"><Link className="signal-walkthrough-link" href="/demo#product-walkthrough">Explore the full product walkthrough →</Link></div></>;
}
