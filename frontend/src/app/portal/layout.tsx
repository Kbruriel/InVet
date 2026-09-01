import type { Metadata } from "next";
import "./globals.css";
import { AuthenticatedHeader } from "@/features/authenticated/components/AuthenticatedHeader";

export const metadata: Metadata = {
  title: "InVet - Plataforma de Clinicas Veterinarias",
  description: "Busca, compara y agenda tu cita con las mejores clinicas veterinarias.",
};

export default function PortalLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className="antialiased">
        <div className="mx-auto max-w-[1280px] px-4 sm:px-6 lg:px-8">
          <AuthenticatedHeader />
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}