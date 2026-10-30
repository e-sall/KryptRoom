"use client";
import { useRef } from "react";
import { solutions } from "@/features/marketing/solutions";
import { Brand } from "./brand";
import { ButtonLink } from "./ui";
import { Icon } from "./icon";
import Link from "next/link";
import type { ReactNode } from "react";
import "@/features/marketing/marketing.css";
import "@/features/marketing/editorial.css";

export function MarketingShell({ children }: { children: ReactNode }) {
  const dropdown = useRef<HTMLDetailsElement>(null);
  return (
    <div className="marketing-shell">
      <link rel="preload" href="/fonts/newsreader.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
      <link rel="preload" href="/fonts/dm-sans.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="marketing-navbar">
        <Brand />
        <nav aria-label="Product navigation">
          <Link prefetch={false} href="/product">Product</Link>
          <Link prefetch={false} href="/technology">Technology</Link>
          <details className="solutions-dropdown" ref={dropdown} onKeyDown={e => { if (e.key === "Escape") { e.preventDefault(); dropdown.current?.removeAttribute("open"); dropdown.current?.querySelector("summary")?.focus(); } }} onBlur={e => { if (!e.currentTarget.contains(e.relatedTarget as Node)) e.currentTarget.removeAttribute("open"); }}>
            <summary>Solutions <span aria-hidden="true">⌄</span></summary>
            <div className="solutions-menu"><p className="eyebrow">POSSIBLE APPLICATIONS</p>{solutions.map(s => <Link prefetch={false} key={s.slug} href={`/${s.slug}`} onClick={() => dropdown.current?.removeAttribute("open")}><Icon name={s.icon} /><span><strong>{s.name}</strong><small>{s.description}</small></span><span aria-hidden="true">→</span></Link>)}</div>
          </details>
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
        <Link prefetch={false} href="/security">Security &amp; limitations</Link>
        <Link prefetch={false} href="/developers">Implementation evidence</Link>
        <Link prefetch={false} href="/demo">Interactive demo</Link>
        <Link prefetch={false} href="/preview/rooms">Explore synthetic workspace</Link>
      </footer>
    </div>
  );
}
