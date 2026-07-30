import Link from "next/link";
import { PublicShell } from "@/shared/layout/public-shell";
import { routes } from "@/shared/config/routes";
import { buttonClassName } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { StatePanel } from "@/shared/ui/state-panel";

export default function RegisterClinicPage() {
  return (
    <PublicShell>
      <section className="mx-auto flex min-h-[60vh] w-full max-w-4xl flex-col justify-center gap-6 px-6 py-16 lg:px-8">
        <Card className="space-y-6 bg-white/85">
          <StatePanel
            tone="info"
            title="Onboarding de clinicas en preparacion"
            description="La ruta publica ya esta disponible como parte del design system base. Los formularios y permisos completos se habilitaran cuando el slice funcional correspondiente quede planificado."
          />
          <div className="flex flex-wrap gap-3">
            <Link
              href={routes.home}
              className={buttonClassName({ variant: "primary" })}
            >
              Ver landing
            </Link>
            <Link
              href={routes.clinics}
              className={buttonClassName({ variant: "secondary" })}
            >
              Explorar clinicas
            </Link>
          </div>
        </Card>
      </section>
    </PublicShell>
  );
}
