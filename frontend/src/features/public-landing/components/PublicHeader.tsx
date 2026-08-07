'use client';

export function PublicHeader() {
  return (
    <header lang="es" className="flex items-center justify-between py-5">
      <a href="/" aria-label="InVet, ir al inicio">
        <h1 className="bg-gradient-to-r from-teal to-mint bg-clip-text text-[24px] font-extrabold leading-tight text-transparent">
          InVet
        </h1>
      </a>
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
    </header>
  );
}
