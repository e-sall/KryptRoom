import { notFound } from "next/navigation";
import { exampleRooms } from "@/features/rooms/preview-model";
import { RoomsPreview } from "@/features/rooms/rooms-preview";
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
  if (!exampleRooms.some((room) => room.id === roomId)) notFound();
  return <RoomsPreview screen="workspace" roomId={roomId} />;
}
