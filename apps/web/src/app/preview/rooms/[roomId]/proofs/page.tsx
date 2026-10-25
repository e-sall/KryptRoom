import { notFound } from "next/navigation";
import { exampleRooms } from "@/features/rooms/preview-model";
import { ProofsWorkspace } from "@/features/provenance/proofs-workspace";
export const dynamicParams = false;
export const metadata = { title: "Proofs & Provenance · Synthetic preview · KryptRoom" };
export function generateStaticParams() { return exampleRooms.map((r) => ({ roomId: r.id })); }
export default async function Page({ params }: { params: Promise<{ roomId: string }> }) {
  const { roomId } = await params;
  const room = exampleRooms.find((r) => r.id === roomId);
  if (!room) notFound();
  return <ProofsWorkspace key={room.id} room={room} />;
}
