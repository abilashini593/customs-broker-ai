import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClearBorder AI • Customs Broker Document Extraction & Cross-Check",
  description: "Enterprise SaaS tool for AI document extraction, line item reconciliation, and deterministic cross-checks for customs brokerage.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#09090b] text-zinc-100 antialiased selection:bg-blue-500/30 selection:text-blue-200">
        {children}
      </body>
    </html>
  );
}
