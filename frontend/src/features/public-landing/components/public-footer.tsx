import Link from "next/link";
import { routes } from "@/shared/config/routes";

export function PublicFooter() {
  return (
    <footer className="border-t border-white/60">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-6 py-8 text-sm text-ink-soft lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div>
          <p className="font-semibold text-ink-strong">InVet</p>
          <p>Base tecnica y design system inicial para el flujo de producto.</p>
        </div>

        <nav className="flex flex-wrap gap-4">
          <Link href={routes.home}>Inicio</Link>
          <Link href={routes.clinics}>Clinicas</Link>
          <Link href={routes.signIn}>Iniciar sesion</Link>
          <Link href={routes.registerClinic}>Registrar clinica</Link>
        </nav>
      </div>
    </footer>
  );
}
