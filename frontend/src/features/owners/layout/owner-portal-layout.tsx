/**
 * Layout del portal de propietario
 */

'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { clearSession, isAuthenticated } from '@/shared/auth/session';
import { Button } from '@/shared/ui/components';

interface OwnerPortalLayoutProps {
  children: React.ReactNode;
}

export function OwnerPortalLayout({ children }: OwnerPortalLayoutProps) {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,_#fff8f0_0%,_#faf3e8_48%,_#f4ede2_100%)]">
      <header className="border-b border-sandy-200 bg-white/90 backdrop-blur">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 py-5 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-teal">InVet</p>
              <h1 className="text-2xl font-semibold text-slate-900">Portal de propietario</h1>
              <p className="text-sm text-slate-600">Gestiona tu perfil, tus mascotas y su historial básico.</p>
            </div>
            <nav className="flex flex-wrap items-center gap-3" aria-label="Navegación del portal propietario">
              <Link href="/portal/owner" className="rounded-full px-4 py-2 text-sm font-semibold text-teal transition-colors hover:bg-teal/10 hover:text-teal-dark focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2">
                Inicio
              </Link>
              <Link href="/portal/owner/edit" className="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition-colors hover:bg-sandy-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2">
                Editar Perfil
              </Link>
              <Link href="/portal/owner/pets/new" className="rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition-colors hover:bg-sandy-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2">
                Registrar mascota
              </Link>
              <Button
                onClick={() => {
                  clearSession();
                  router.push('/login');
                }}
                variant="outline"
                size="sm"
              >
                Cerrar sesión
              </Button>
            </nav>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
