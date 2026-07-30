import Link from "next/link";
import { PublicShell } from "@/shared/layout/public-shell";
import { routes } from "@/shared/config/routes";
import { buttonClassName } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { StatePanel } from "@/shared/ui/state-panel";

export default function SignInPage() {
  return (
    <PublicShell>
      <section className="mx-auto flex min-h-[60vh] w-full max-w-4xl flex-col justify-center gap-6 px-6 py-16 lg:px-8">
        <Card className="space-y-6 bg-white/85">
          <StatePanel
            tone="info"
            title="Inicio de sesion preparado para slices posteriores"
            description="La ruta ya existe para evitar enlaces vacios y conservar la navegacion publica coherente mientras el flujo de autenticacion evoluciona."
          />
          <div className="flex flex-wrap gap-3">
            <Link
              href={routes.home}
              className={buttonClassName({ variant: "primary" })}
            >
              Volver al inicio
            </Link>
            <Link
              href={routes.register}
              className={buttonClassName({ variant: "secondary" })}
            >
              Ir a registro
            </Link>
          </div>
        </Card>
      </section>
    </PublicShell>
  );
}
