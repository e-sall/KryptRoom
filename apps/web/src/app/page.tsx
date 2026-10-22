import { MarketingShell } from "@/components/marketing-shell";
import { ButtonLink } from "@/components/ui";

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
          <ButtonLink href="/app/rooms">Explore Product</ButtonLink>
        </div>
      </section>
    </MarketingShell>
  );
}
