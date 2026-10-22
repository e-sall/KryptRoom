import Link from "next/link";

/** P01/P04 SVG geometry, adapted to one scalable mark. Both branches are gray. */
export function KLogo({ size = 26 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 20 30"
      fill="none"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M0 7 L9 1 L9 27 L0 22 Z" fill="var(--kr-text-primary)" />
      <path d="M11 4 L19 0 L19 17 L11 21 Z" fill="var(--kr-logo-upper)" />
      <path d="M11 23 L19 19 L19 29 L11 26 Z" fill="var(--kr-logo-lower)" />
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
    <Link
      href={href}
      className={`brand${compact ? " brand-compact" : ""}`}
      aria-label="KryptRoom home"
    >
      <KLogo />
      <span>KryptRoom</span>
    </Link>
  );
}
