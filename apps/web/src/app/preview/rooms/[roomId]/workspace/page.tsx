import { notFound } from "next/navigation";
import { exampleRooms } from "@/features/rooms/preview-model";
import { GraphWorkspace } from "@/features/graph/graph-workspace";
export const dynamicParams = false;
export function generateStaticParams() {
  return exampleRooms.map((room) => ({ roomId: room.id }));
}
export default async function Page({
  params,
}: {
  params: Promise<{ roomId: string }>;
}) {
  const { roomId } = await params;
  const room = exampleRooms.find((room) => room.id === roomId);
  if (!room) notFound();
  return <GraphWorkspace key={room.id} room={room} />;
}
