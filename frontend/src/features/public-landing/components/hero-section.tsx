import Link from "next/link";
import { CategoryChips } from "@/features/public-landing/components/category-chips";
import { HeroBentoVisual } from "@/features/public-landing/components/hero-bento-visual";
import { PublicSearchBar } from "@/features/public-landing/components/public-search-bar";
import { routes } from "@/shared/config/routes";
import { buttonClassName } from "@/shared/ui/button";

export function HeroSection() {
  return (
    <section className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 py-16 lg:px-8 lg:py-24">
      <div className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="space-y-8">
          <div className="space-y-5">
            <p className="inline-flex rounded-full border border-brand-teal/15 bg-white/70 px-4 py-2 text-sm font-semibold uppercase tracking-[0.25em] text-brand-teal">
              Base tecnica FE-001
            </p>
            <h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-ink-strong md:text-6xl">
              InVet prepara la experiencia publica antes de crecer el producto.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-ink-soft">
              Este primer slice deja el design system, las rutas reales y el cliente
              API centralizado para que las siguientes iteraciones construyan valor
              sin volver a discutir la estructura base.
            </p>
          </div>

          <PublicSearchBar />
          <CategoryChips />

          <div className="flex flex-wrap gap-3">
            <Link
              href={routes.registerClinic}
              className={buttonClassName({ variant: "primary", size: "lg" })}
            >
              Registrar clinica
            </Link>
            <Link
              href={routes.signIn}
              className={buttonClassName({ variant: "secondary", size: "lg" })}
            >
              Iniciar sesion
            </Link>
          </div>
        </div>

        <HeroBentoVisual />
      </div>
    </section>
  );
}
