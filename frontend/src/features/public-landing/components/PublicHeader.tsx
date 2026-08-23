'use client';

import Link from 'next/link';

export function PublicHeader() {
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
            <a
              href="/clinicas"
              className="py-2 text-sm font-medium text-gray-600 transition-colors hover:text-teal dark:text-gray-300 dark:hover:text-teal-light"
            >
              Clínicas
            </a>
            <a
              href="/servicios"
              className="py-2 text-sm font-medium text-gray-600 transition-colors hover:text-teal dark:text-gray-300 dark:hover:text-teal-light"
            >
              Servicios
            </a>
            <a
              href="/como-funciona"
              className="py-2 text-sm font-medium text-gray-600 transition-colors hover:text-teal dark:text-gray-300 dark:hover:text-teal-light"
            >
              Cómo funciona
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="rounded-full border border-sandy-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:border-teal hover:text-teal focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
            >
              Iniciar sesion
            </Link>
            <Link
              href="/register"
              className="rounded-full bg-teal px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-teal-dark focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
            >
              Registrarse
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
