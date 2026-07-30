import { ClinicCard } from "@/features/public-landing/components/clinic-card";
import { mockClinics } from "@/features/public-landing/data/mock-clinics";
import { PublicShell } from "@/shared/layout/public-shell";
import { Card } from "@/shared/ui/card";
import { StatePanel } from "@/shared/ui/state-panel";

type ClinicsPageProps = {
  searchParams: Promise<{
    query?: string;
    category?: string;
  }>;
};

function normalize(value: string) {
  return value.trim().toLowerCase();
}

export default async function ClinicsPage({ searchParams }: ClinicsPageProps) {
  const params = await searchParams;
  const query = params.query ?? "";
  const category = params.category ?? "";

  const normalizedQuery = normalize(query);
  const normalizedCategory = normalize(category);

  const filteredClinics = mockClinics.filter((clinic) => {
    const matchesQuery =
      normalizedQuery.length === 0 ||
      normalize(clinic.name).includes(normalizedQuery) ||
      normalize(clinic.city).includes(normalizedQuery) ||
      normalize(clinic.services.join(" ")).includes(normalizedQuery);

    const matchesCategory =
      normalizedCategory.length === 0 ||
      normalize(clinic.category) === normalizedCategory;

    return matchesQuery && matchesCategory;
  });

  return (
    <PublicShell>
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-16 lg:px-8">
        <header className="space-y-3">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-brand-teal">
            Explorador inicial
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-ink-strong">
            Clinicas y servicios de referencia
          </h1>
          <p className="max-w-3xl text-base leading-7 text-ink-soft">
            Este slice deja lista la navegacion, el filtrado base y los estados UX
            mientras los contratos de busqueda reales evolucionan en slices
            posteriores.
          </p>
        </header>

        <Card className="flex flex-wrap gap-3 bg-white/80">
          <span className="rounded-full bg-surface-muted px-4 py-2 text-sm text-ink-soft">
            Consulta: {query || "Sin termino"}
          </span>
          <span className="rounded-full bg-surface-muted px-4 py-2 text-sm text-ink-soft">
            Categoria: {category || "Todas"}
          </span>
          <span className="rounded-full bg-brand-mint/70 px-4 py-2 text-sm font-medium text-ink-strong">
            Resultados: {filteredClinics.length}
          </span>
        </Card>

        {filteredClinics.length === 0 ? (
          <StatePanel
            tone="empty"
            title="No encontramos coincidencias todavia"
            description="La base tecnica ya soporta rutas reales y estados vacios. Los resultados de produccion llegaran cuando el backend exponga la busqueda del dominio."
          />
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filteredClinics.map((clinic) => (
              <ClinicCard key={clinic.slug} clinic={clinic} />
            ))}
          </div>
        )}
      </section>
    </PublicShell>
  );
}
