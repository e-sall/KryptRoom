import { Brand } from "./brand";
import { ButtonLink } from "./ui";
import { Icon } from "./icon";
import Link from "next/link";
import type { ReactNode } from "react";
import "@/features/marketing/marketing.css";

export function MarketingShell({ children }: { children: ReactNode }) {
  return (
    <div className="marketing-shell">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="marketing-navbar">
        <Brand />
        <nav aria-label="Product navigation">
          {["Product", "Technology", "Security", "Developers"].map((name) => (
            <Link prefetch={false} key={name} href={`/${name.toLowerCase()}`}>
              {name}
            </Link>
          ))}
          <Link prefetch={false} href="/demo">Demo</Link>
        </nav>
        <ButtonLink href="/book-demo" variant="primary">
          Book a Demo <Icon name="arrow" />
        </ButtonLink>
      </header>
      <main id="main-content" tabIndex={-1}>
        {children}
      </main>
      <footer className="marketing-footer">
        <span>KryptRoom · Experimental research prototype</span>
        <Link prefetch={false} href="/design-system">Design system</Link>
        <Link prefetch={false} href="/preview/rooms">Explore synthetic workspace</Link>
      </footer>
    </div>
  );
}
