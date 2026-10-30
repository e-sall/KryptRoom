import { solutions } from "@/features/marketing/solutions";
import { notFound } from "next/navigation";
import { MarketingShell } from "@/components/marketing-shell";
import { InteractiveDemo } from "@/features/marketing/interactive-demo";
import { MarketingContent } from "@/features/marketing/marketing-pages";

const sections: Record<string, string> = {
  ...Object.fromEntries(solutions.map(s => [s.slug, s.name])),
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
      <section className="marketing-page-heading" hidden={["product","technology","security","developers"].includes(section)}>
        <p className="eyebrow">{section === "demo" ? "INTERACTIVE PRODUCT PREVIEW · SYNTHETIC" : "KRYPTROOM · PRIVATE DATA COLLABORATION"}</p>
        <h1>{title}</h1>
        {section === "demo" && <p className="caption">Explore a preloaded scenario. No computation, proof, authorization or blockchain transaction is executed.</p>}
      </section>
      {section === "demo" ? <InteractiveDemo /> : <MarketingContent section={section} />}
    </MarketingShell>
  );
}
