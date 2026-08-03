import './globals.css';
import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';

const jakarta = Plus_Jakarta_Sans({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'InVet - Encuentra la clínica veterinaria perfecta',
  description: 'Busca y compara clínicas veterinarias cerca de ti',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className={jakarta.className}>{children}</body>
    </html>
  );
}