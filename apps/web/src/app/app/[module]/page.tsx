import { notFound } from "next/navigation";
import { findModule, modules } from "@/lib/navigation";
import { ModulePlaceholder } from "@/components/module-placeholder";

export const dynamicParams = false;
export function generateStaticParams() {
  return modules.map(({ id }) => ({ module: id }));
}
export async function generateMetadata({
  params,
}: {
  params: Promise<{ module: string }>;
}) {
  return { title: findModule((await params).module)?.title ?? "Not found" };
}
export default async function ModulePage({
  params,
}: {
  params: Promise<{ module: string }>;
}) {
  const currentModule = findModule((await params).module);
  if (!currentModule) notFound();
  return <ModulePlaceholder module={currentModule} />;
}
