import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InVet",
  description: "Base tecnica y design system inicial para InVet.",
};

type RootLayoutProps = Readonly<{
  children: React.ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
