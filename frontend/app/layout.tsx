import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DocuSense AI",
  description: "AI document risk analyzer for contracts, leases, HR policies, and compliance documents."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
