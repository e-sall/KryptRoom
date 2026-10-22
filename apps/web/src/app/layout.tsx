import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "KryptRoom", template: "%s · KryptRoom" },
  description:
    "Compute together. Reveal nothing. Application foundation preview; no workspace service connected.",
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
