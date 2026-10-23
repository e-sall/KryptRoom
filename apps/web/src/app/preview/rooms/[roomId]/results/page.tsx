import { notFound } from "next/navigation";
import { exampleRooms } from "@/features/rooms/preview-model";
import { ResultsWorkspace } from "@/features/operations/results-workspace";
export const dynamicParams = false;
export const metadata = { title: "Results · Synthetic preview · KryptRoom" };
export function generateStaticParams() { return exampleRooms.map((room) => ({ roomId: room.id })); }
export default async function Page({ params }: { params: Promise<{ roomId: string }> }) {
  const { roomId } = await params;
  const room = exampleRooms.find((r) => r.id === roomId);
  if (!room) notFound();
  return <ResultsWorkspace key={room.id} room={room} />;
}
