import { MarketingShell } from "@/components/marketing-shell";
import { ButtonLink } from "@/components/ui";
import { HowItWorks } from "@/features/marketing/how-it-works";
import { ProductBoundary } from "@/features/marketing/product-boundary";

export default function Home() {
  return (
    <MarketingShell>
      <section className="hero">
        <p className="eyebrow">PRIVATE DATA COLLABORATION</p>
        <h1>Compute together. Reveal nothing.</h1>
        <p className="hero-description">
          Collaborate on sensitive data without sharing raw datasets.
          <br />
          Reveal only authorized results.
        </p>
        <div className="button-row">
          <ButtonLink href="/book-demo" variant="primary">
            Book a Demo
          </ButtonLink>
          <ButtonLink href="/demo">Explore Product</ButtonLink>
        </div>
      </section>
      <section className="marketing-cadran marketing-intro"><p className="eyebrow">THE COLLABORATION PROBLEM</p><h2>Shared insight.<br />Without a shared raw dataset.</h2>
        <p>Two organizations can have a common question without permission to exchange their records. KryptRoom is built around protected computation and reusable states, with disclosure kept separate.</p></section>
      <HowItWorks />
      <ProductBoundary />
      <section className="marketing-cadran marketing-outro"><h2>See a state become a starting point.</h2><p>Seven scenes. Two fictional organizations. One protected collaboration, explained.</p>
        <div className="button-row"><ButtonLink href="/demo" variant="primary">Explore the interactive demo</ButtonLink><ButtonLink href="/book-demo">Book a Demo</ButtonLink></div></section>
    </MarketingShell>
  );
}
