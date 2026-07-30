import Link from "next/link";
import { routes } from "@/shared/config/routes";
import { buttonClassName } from "@/shared/ui/button";

const navItems = [
  { label: "Clinicas", href: routes.clinics },
  { label: "Urgencias", href: `${routes.clinics}?category=Urgencias` },
  { label: "Estetica", href: `${routes.clinics}?category=Estetica` },
];

export function PublicHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-white/60 bg-white/75 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-6 py-4 lg:px-8">
        <Link href={routes.home} className="flex items-center gap-3">
          <span className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-brand-teal text-lg font-semibold text-white">
            I
          </span>
          <div>
            <p className="text-lg font-semibold text-ink-strong">InVet</p>
            <p className="text-sm text-ink-soft">Veterinaria digital confiable</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-medium text-ink-soft md:flex">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="transition hover:text-ink-strong">
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <Link
            href={routes.signIn}
            className={buttonClassName({ variant: "ghost", className: "hidden md:inline-flex" })}
          >
            Iniciar sesion
          </Link>
          <Link
            href={routes.register}
            className={buttonClassName({ variant: "primary" })}
          >
            Registrarse
          </Link>
        </div>
      </div>
    </header>
  );
}
