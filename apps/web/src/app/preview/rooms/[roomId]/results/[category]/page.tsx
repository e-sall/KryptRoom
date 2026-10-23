import { notFound } from "next/navigation";
import { exampleRooms } from "@/features/rooms/preview-model";
import { ResultsWorkspace } from "@/features/operations/results-workspace";
import { isOperation, operationIds } from "@/features/operations/presentation";
export const dynamicParams = false;
export const metadata = { title: "Result example · Synthetic preview · KryptRoom" };
export function generateStaticParams() { return exampleRooms.flatMap((room) => operationIds.map((category) => ({ roomId: room.id, category }))); }
export default async function Page({ params }: { params: Promise<{ roomId: string; category: string }> }) {
  const { roomId, category } = await params;
  const room = exampleRooms.find((r) => r.id === roomId);
  if (!room || !isOperation(category)) notFound();
  return <ResultsWorkspace key={`${room.id}-${category}`} room={room} operation={category} />;
}
