import { notFound } from "next/navigation";
import { exampleRooms } from "@/features/rooms/preview-model";
import { ComputationsWorkspace } from "@/features/operations/computations-workspace";
export const dynamicParams = false;
export const metadata = { title: "Computations · Synthetic preview · KryptRoom" };
export function generateStaticParams() { return exampleRooms.map((room) => ({ roomId: room.id })); }
export default async function Page({ params }: { params: Promise<{ roomId: string }> }) {
  const { roomId } = await params;
  const room = exampleRooms.find((r) => r.id === roomId);
  if (!room) notFound();
  return <ComputationsWorkspace key={room.id} room={room} />;
}
