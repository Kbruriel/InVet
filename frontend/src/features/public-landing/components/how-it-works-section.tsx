import { SectionHeading } from "@/shared/ui/section-heading";
import { Card } from "@/shared/ui/card";

const steps = [
  {
    title: "Explora servicios",
    description: "La base publica ya permite navegar por categorias y rutas reales sin placeholders rotos.",
  },
  {
    title: "Valida el contrato",
    description: "El cliente API centralizado deja preparado el consumo de `/api/v1` sin duplicar fetches por todo el proyecto.",
  },
  {
    title: "Escala con confianza",
    description: "Los checks automatizados cuidan lint, tipado, pruebas y build desde el arranque del frontend.",
  },
];

export function HowItWorksSection() {
  return (
    <section className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-6 py-8 lg:px-8 lg:py-12">
      <SectionHeading
        eyebrow="Como funciona"
        title="La base visual ya responde como un producto en construccion, no como un boceto aislado."
        description="FE-001 aterriza arquitectura, estados UX y navegacion inicial para que cada slice nuevo tenga una plataforma estable sobre la cual iterar."
      />

      <div className="grid gap-4 md:grid-cols-3">
        {steps.map((step, index) => (
          <Card key={step.title} className="bg-white/85">
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-brand-teal">
              Paso {index + 1}
            </p>
            <h3 className="mt-4 text-xl font-semibold text-ink-strong">
              {step.title}
            </h3>
            <p className="mt-3 text-sm leading-6 text-ink-soft">
              {step.description}
            </p>
          </Card>
        ))}
      </div>
    </section>
  );
}
