import { Badge, ButtonLink } from "@/components/ui";
import { ProductBoundary } from "./product-boundary";

export function MarketingContent({ section }: { section: string }) {
  if (section === "book-demo") return <section className="marketing-cadran booking-boundary">
    <Badge status="unavailable" /><h2>A conversation, not a pretend reservation.</h2>
    <p>Booking is not connected yet. No availability or reservation is offered in this preview.</p>
    <p className="caption">No calendar provider is configured. No contact details are collected, no slot is invented and no meeting is booked.</p>
    <div className="button-row"><ButtonLink href="/demo" variant="primary">Explore the interactive demo</ButtonLink><ButtonLink href="/product">Understand the product</ButtonLink></div>
  </section>;
  if (section === "product") return <><section className="marketing-cadran"><p className="eyebrow">PERSISTENT PRIVATE COLLABORATION</p><h2>More than an isolated job.</h2>
    <p>Organizations collaborate through a Room. Private computations evolve immutable, protected RoomStates that retain their parent relationships and can be reused by subsequent authorized operations.</p>
    <p>Raw datasets are not a shared workspace asset. Computation and disclosure are separate decisions.</p>
    <div className="button-row"><ButtonLink href="/demo" variant="primary">Explore the interactive demo</ButtonLink><ButtonLink href="/preview/rooms">Explore synthetic Rooms</ButtonLink><ButtonLink href="/#how-it-works">How it works</ButtonLink></div>
  </section><ProductBoundary /></>;
  if (section === "technology") return <section className="marketing-cadran marketing-reading"><h2>The mechanism follows the operation.</h2>
    <dl><dt>Private matching and computation</dt><dd>Cardinality-only PSI; two-party SecretFlow SPU CHEETAH/FM128 private join, analytics and a fixed neural-network fixture. The model is semi-honest, not malicious security.</dd>
      <dt>Persistent protected state</dt><dd>Node-local secret shares are encrypted at rest with AES-256-GCM and reloaded for subsequent computation. Encryption at rest is distinct from MPC.</dd>
      <dt>Bounded homomorphic transition</dt><dd>OpenFHE BGV adds two fixed four-integer vectors. A single private-key owner controls decryption; this is not threshold FHE.</dd>
      <dt>Proof and audit</dt><dd>M5 proves a bounded committed metadata relation, not MPC arithmetic. M7 records an opaque public commitment; the blockchain is neither the state machine nor proof of private computation correctness.</dd></dl>
    <ButtonLink href="/demo">Explore the synthetic explanation</ButtonLink>
  </section>;
  if (section === "security") return <section className="marketing-cadran marketing-reading"><h2>Privacy needs precise boundaries.</h2>
    <p>KryptRoom is an experimental research prototype, not a production-ready or independently audited security product.</p>
    <ul><li>Two-party honest-but-curious assumptions, non-collusion and trusted participant hosts.</li><li>Default-deny disclosure. Matched identifiers and plaintext joined rows are not authorized outputs.</li><li>No protection claimed against compromised hosts, malicious participants, side channels or repeated-query inference.</li><li>Production identity, authenticated coordination, key custody, rotation, recovery and anti-rollback remain future work.</li><li>No regulatory certification or suitability for real patient data is claimed.</li></ul>
    <h3>Production workspace connection</h3><Badge status="unavailable" /><p className="caption">The preview grants no permissions and supplies no verifier or chain authority.</p>
    <p>Layer A establishes actual chain inclusion/finality; Layer B checks document consistency; Layer C is explicit cryptographic proof verification. A matching commitment is not a general correctness proof.</p>
    <ButtonLink href="/developers">Read the implementation evidence</ButtonLink>
  </section>;
  return <section className="marketing-cadran marketing-reading"><h2>Inspect the implementation. Keep its limits in view.</h2>
    <p>The public repository documents the bounded runtime acceptance chains, threat model and milestone evidence. There is no production Workspace API, SDK integration contract or authentication service to wire into this preview.</p>
    <p>Future adapters must provide authenticated, field-filtered metadata and authoritative decisions. Client state and synthetic fixtures are never permission grants.</p>
    <div className="button-row"><ButtonLink href="https://github.com/e-sall/KryptRoom">Public repository</ButtonLink><ButtonLink href="https://github.com/e-sall/KryptRoom/blob/dev/SECURITY.md">Security policy</ButtonLink><ButtonLink href="/preview/rooms">Explore synthetic workspace</ButtonLink></div>
  </section>;
}
