import { PersistentRooms } from "@/features/rooms/persistent-rooms";
export default async function Page({params}:{params:Promise<{roomId:string}>}){
  const id=(await params).roomId;
  return <PersistentRooms key={id} roomId={id}/>;
}
