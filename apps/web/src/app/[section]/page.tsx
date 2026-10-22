import { notFound } from "next/navigation";
import { MarketingShell } from "@/components/marketing-shell";
import { ButtonLink, Badge } from "@/components/ui";

const sections: Record<string, string> = {
  product: "Product",
  technology: "Technology",
  security: "Security",
  developers: "Developers",
  "book-demo": "Book a Demo",
  demo: "Interactive Demo",
};
export const dynamicParams = false;
export function generateStaticParams() {
  return Object.keys(sections).map((section) => ({ section }));
}
export async function generateMetadata({
  params,
}: {
  params: Promise<{ section: string }>;
}) {
  return { title: sections[(await params).section] ?? "Not found" };
}
export default async function MarketingPage({
  params,
}: {
  params: Promise<{ section: string }>;
}) {
  const { section } = await params;
  const title = sections[section];
  if (!title) notFound();
  return (
    <MarketingShell>
      <section className="hero placeholder-marketing">
        <p className="eyebrow">KRYPTROOM · PR 1 FOUNDATION</p>
        <h1>{title}</h1>
        <Badge status="unavailable" />
        <p className="hero-description">
          {section === "book-demo"
            ? "Booking is not connected yet. No availability or reservation is offered in this preview."
            : "This page is reserved for the marketing and demo implementation in PR 6."}
        </p>
        <ButtonLink href="/app/rooms">Explore the app shell</ButtonLink>
      </section>
    </MarketingShell>
  );
}
