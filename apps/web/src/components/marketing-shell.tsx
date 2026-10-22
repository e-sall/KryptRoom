import { Brand } from "./brand";
import { ButtonLink } from "./ui";
import { Icon } from "./icon";
import Link from "next/link";
import type { ReactNode } from "react";

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
            <Link key={name} href={`/${name.toLowerCase()}`}>
              {name}
            </Link>
          ))}
        </nav>
        <ButtonLink href="/book-demo" variant="primary">
          Book a Demo <Icon name="arrow" />
        </ButtonLink>
      </header>
      <main id="main-content" tabIndex={-1}>
        {children}
      </main>
      <footer className="marketing-footer">
        <span>KryptRoom · Interface foundation</span>
        <Link href="/design-system">Design system</Link>
        <Link href="/app/rooms">Open workspace</Link>
      </footer>
    </div>
  );
}
