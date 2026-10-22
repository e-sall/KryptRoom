import { RoomsPreviewProvider } from "@/features/rooms/preview-context";
import "@/features/rooms/rooms.css";
export const metadata = {
  title: "Rooms · Synthetic preview",
  robots: { index: false, follow: false },
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return <RoomsPreviewProvider>{children}</RoomsPreviewProvider>;
}
