'use client';

import { Button } from '@/shared/ui/components';
import Link from 'next/link';

export function ProfessionalCtaSection() {
  return (
    <section
      aria-label="Registra tu clinica"
      className="rounded-3xl bg-gradient-to-r from-teal to-teal-dark py-12 text-center text-white sm:py-16"
    >
      <div className="mx-auto max-w-2xl px-4">
        <h2 className="text-2xl font-extrabold sm:text-3xl">
          Tienes una clinica veterinaria?
        </h2>
        <p className="mt-3 text-base text-white/80">
          Registra tu clinica en InVet y llega a mas propietarios de mascotas.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link href="/register">
            <Button variant="secondary" size="lg">
              Registrar clinica
            </Button>
          </Link>
          <Link href="/clinicas">
            <Button
              variant="outline"
              size="lg"
              className="border-white text-white hover:bg-white/10"
            >
              Ver clínicas
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
