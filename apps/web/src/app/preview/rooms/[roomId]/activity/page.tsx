import { notFound } from "next/navigation";
import { exampleRooms } from "@/features/rooms/preview-model";
import { ActivityWorkspace } from "@/features/provenance/activity-workspace";
export const dynamicParams = false;
export const metadata = { title: "Activity & History · Synthetic preview · KryptRoom" };
export function generateStaticParams() { return exampleRooms.map((r) => ({ roomId: r.id })); }
export default async function Page({ params }: { params: Promise<{ roomId: string }> }) {
  const { roomId } = await params;
  const room = exampleRooms.find((r) => r.id === roomId);
  if (!room) notFound();
  return <ActivityWorkspace key={room.id} room={room} />;
}
