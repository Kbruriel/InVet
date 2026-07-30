import { ApiStatusCard } from "@/features/public-landing/components/api-status-card";
import { Card } from "@/shared/ui/card";

const highlights = [
  {
    title: "Rutas reales",
    description: "La landing, clinicas, inicio de sesion y registro ya navegan sin enlaces vacios.",
  },
  {
    title: "Shared UI",
    description: "Botones, cards y paneles de estado listos para reutilizar en siguientes slices.",
  },
  {
    title: "Checks automatizados",
    description: "Lint, typecheck, test y build se ejecutan desde el mismo wrapper del repositorio.",
  },
];

export function HeroBentoVisual() {
  return (
    <div className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
      <Card className="grid gap-4 bg-brand-teal text-white">
        <div className="space-y-3">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-brand-mint">
            Base tecnica lista
          </p>
          <h3 className="text-3xl font-semibold tracking-tight">
            Un frontend que ya puede crecer sin rehacer la cimentacion.
          </h3>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          {highlights.map((item) => (
            <div
              key={item.title}
              className="rounded-[24px] bg-white/10 p-4 backdrop-blur"
            >
              <p className="font-semibold">{item.title}</p>
              <p className="mt-2 text-sm leading-6 text-white/80">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </Card>

      <ApiStatusCard />
    </div>
  );
}
