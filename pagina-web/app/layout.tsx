import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mercado Laboral en Colombia | MinTIC 2026",
  description:
    "Landing page profesional para visualizar indicadores y tableros del mercado laboral en Colombia con integracion de Power BI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
