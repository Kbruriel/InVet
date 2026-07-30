import Link from "next/link";
import { routes } from "@/shared/config/routes";
import { buttonClassName } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

export function ProfessionalCtaSection() {
  return (
    <section className="mx-auto w-full max-w-6xl px-6 py-12 lg:px-8 lg:py-16">
      <Card className="overflow-hidden bg-gradient-to-r from-brand-teal to-[#0a7d82] text-white">
        <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
          <div className="space-y-3">
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-brand-mint">
              CTA inicial
            </p>
            <h2 className="text-3xl font-semibold tracking-tight">
              La ruta para registrar una clinica ya existe y puede evolucionar sin rehacer la navegacion.
            </h2>
            <p className="max-w-2xl text-sm leading-7 text-white/80">
              FE-001 deja la experiencia publica alineada con el tono visual de InVet y preparada para que los proximos slices agreguen autenticacion, onboarding y flujos de negocio.
            </p>
          </div>

          <Link
            href={routes.registerClinic}
            className={buttonClassName({
              variant: "secondary",
              size: "lg",
              className: "bg-white text-brand-teal hover:bg-white/90",
            })}
          >
            Solicitar alta de clinica
          </Link>
        </div>
      </Card>
    </section>
  );
}
