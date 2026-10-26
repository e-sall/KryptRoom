import Link from "next/link";

/** Canonical thin K: latest P11 original, consistent with corrected P05/P06.
 * Shared by marketing, sidebar, rail, mobile header and component specimens.
 */
export function KLogo({ size = 26 }: { size?: number }) {
  return (
    <svg
      className="k-logo"
      width={size}
      height={size}
      viewBox="0 0 22 30"
      fill="none"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M1 7 L7 4 V27 L1 24 Z" fill="var(--kr-text-primary)" />
      <path d="M9 12 L20 4 L16 12 L9 19 Z" fill="var(--kr-logo-upper)" />
      <path d="M9 19 L16 12 L21 26 L14 23 Z" fill="var(--kr-logo-lower)" />
    </svg>
  );
}

export function Brand({
  href = "/",
  compact = false,
}: {
  href?: string;
  compact?: boolean;
}) {
  return (
    <Link prefetch={false}
      href={href}
      className={`brand${compact ? " brand-compact" : ""}`}
      aria-label="KryptRoom home"
    >
      <KLogo />
      <span>KryptRoom</span>
    </Link>
  );
}
