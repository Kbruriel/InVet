'use client';

import Link from 'next/link';
import { PublicSearchBar } from './PublicSearchBar';
import { CategoryChipsWrapper } from './CategoryChipsWrapper';
import { HeroBentoVisual } from './HeroBentoVisual';

export function HeroSection() {
  return (
    <section
      aria-label="Busqueda de clinicas"
      className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-sandy-100 via-white to-mint/30 py-16 sm:py-24"
    >
      <div className="mx-auto max-w-3xl px-4 text-center">
        <h2 className="text-3xl font-extrabold text-slate-900 sm:text-5xl">
          Encuentra la clinica ideal para tu mascota
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-base text-slate-600 sm:text-lg">
          Busca, compara y solicita tu cita con las mejores clínicas veterinarias cerca de ti.
        </p>

        <div className="mt-10">
          <PublicSearchBar />
        </div>

        <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            href="/login"
            className="inline-flex min-w-44 items-center justify-center rounded-full border border-sandy-300 bg-white/80 px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm backdrop-blur transition-colors hover:border-teal hover:text-teal focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
          >
            Iniciar sesion
          </Link>
          <Link
            href="/register"
            className="inline-flex min-w-44 items-center justify-center rounded-full bg-teal px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-teal-dark focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
          >
            Registrarse
          </Link>
        </div>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <CategoryChipsWrapper />
        </div>
      </div>

      <HeroBentoVisual />
    </section>
  );
}
