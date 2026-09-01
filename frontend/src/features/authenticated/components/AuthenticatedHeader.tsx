'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getUnreadCount } from '@/shared/api/notification';
import { NotificationBadge } from '@/shared/ui/notification-badge';

export function AuthenticatedHeader() {
  const [unreadCount, setUnreadCount] = useState<number>(0);

  useEffect(() => {
    const fetchUnreadCount = async () => {
      try {
        const response = await getUnreadCount();
        setUnreadCount(response.unread);
      } catch (err) {
        console.error('Error al cargar notificaciones', err);
      }
    };

    fetchUnreadCount();
  }, []);

  return (
    <header lang="es" className="py-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <a href="/" aria-label="InVet, ir al inicio">
          <h1 className="bg-gradient-to-r from-teal to-mint bg-clip-text text-[24px] font-extrabold leading-tight text-transparent">
            InVet
          </h1>
        </a>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-6">
          <nav aria-label="Principal" className="hidden gap-8 sm:flex">
            <Link
              href="/portal/owner"
              className="py-2 text-sm font-medium text-gray-600 transition-colors hover:text-teal dark:text-gray-300 dark:hover:text-teal-light"
            >
              Inicio
            </Link>
            <Link
              href="/portal/owner/pets"
              className="py-2 text-sm font-medium text-gray-600 transition-colors hover:text-teal dark:text-gray-300 dark:hover:text-teal-light"
            >
              Mascotas
            </Link>
            <Link
              href="/portal/owner/appointments"
              className="py-2 text-sm font-medium text-gray-600 transition-colors hover:text-teal dark:text-gray-300 dark:hover:text-teal-light"
            >
              Citas
            </Link>
            <Link
              href="/notifications"
              className="py-2 text-sm font-medium text-gray-600 transition-colors hover:text-teal dark:text-gray-300 dark:hover:text-teal-light relative"
            >
              Notificaciones
              <NotificationBadge count={unreadCount} />
            </Link>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/logout"
              className="px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:text-teal focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
            >
              Cerrar sesión
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}