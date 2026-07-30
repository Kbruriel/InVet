import Link from "next/link";
import { PublicShell } from "@/shared/layout/public-shell";
import { routes } from "@/shared/config/routes";
import { buttonClassName } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { StatePanel } from "@/shared/ui/state-panel";

export default function RegisterPage() {
  return (
    <PublicShell>
      <section className="mx-auto flex min-h-[60vh] w-full max-w-4xl flex-col justify-center gap-6 px-6 py-16 lg:px-8">
        <Card className="space-y-6 bg-white/85">
          <StatePanel
            tone="success"
            title="Registro base listo para crecer"
            description="FE-001 deja las rutas reales, el layout y los componentes compartidos para que el formulario completo de registro llegue sobre una base tecnica consistente."
          />
          <div className="flex flex-wrap gap-3">
            <Link
              href={routes.registerClinic}
              className={buttonClassName({ variant: "primary" })}
            >
              Registrar clinica
            </Link>
            <Link
              href={routes.home}
              className={buttonClassName({ variant: "secondary" })}
            >
              Volver al inicio
            </Link>
          </div>
        </Card>
      </section>
    </PublicShell>
  );
}
