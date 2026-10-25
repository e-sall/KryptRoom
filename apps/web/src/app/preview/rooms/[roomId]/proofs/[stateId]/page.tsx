import { notFound } from "next/navigation";
import { exampleRooms } from "@/features/rooms/preview-model";
import { graphFixture } from "@/features/graph/fixtures";
import { ProofsWorkspace } from "@/features/provenance/proofs-workspace";
export const dynamicParams = false;
export const metadata = { title: "Proofs & Provenance · Synthetic preview · KryptRoom" };
export function generateStaticParams() { return exampleRooms.flatMap((r) => graphFixture(r.id).map((s) => ({ roomId: r.id, stateId: s.id }))); }
export default async function Page({ params }: { params: Promise<{ roomId: string; stateId: string }> }) {
  const { roomId, stateId } = await params;
  const room = exampleRooms.find((r) => r.id === roomId);
  if (!room || !graphFixture(roomId).some((s) => s.id === stateId)) notFound();
  return <ProofsWorkspace key={`${roomId}-${stateId}`} room={room} initialSelected={stateId} />;
}
