"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { routes } from "@/shared/config/routes";
import { Button } from "@/shared/ui/button";

export function buildClinicSearchHref(query: string) {
  const params = new URLSearchParams({ query: query.trim() });
  return `${routes.clinics}?${params.toString()}`;
}

type PublicSearchBarProps = {
  onSearch?: (href: string) => void;
};

export function PublicSearchBar({ onSearch }: PublicSearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmed = query.trim();

    if (trimmed.length === 0) {
      setError("Ingresa una clinica, ciudad o servicio.");
      return;
    }

    setError(null);

    startTransition(() => {
      const href = buildClinicSearchHref(trimmed);

      if (onSearch) {
        onSearch(href);
        return;
      }

      router.push(href);
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-[28px] border border-white/60 bg-white/80 p-3 shadow-[0_24px_80px_-36px_rgba(18,52,59,0.35)] backdrop-blur"
      noValidate
    >
      <div className="flex flex-col gap-3 md:flex-row">
        <label className="flex-1">
          <span className="sr-only">Busca una clinica, ciudad o servicio</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Busca una clinica, ciudad o servicio"
            className="h-14 w-full rounded-full border border-brand-teal/15 bg-white px-5 text-base text-ink-strong shadow-sm outline-none transition placeholder:text-ink-soft/70 focus:border-brand-teal"
            aria-invalid={Boolean(error)}
            aria-describedby={error ? "public-search-error" : undefined}
          />
        </label>

        <Button type="submit" size="lg" disabled={isPending}>
          {isPending ? "Buscando..." : "Buscar"}
        </Button>
      </div>

      {error ? (
        <p
          id="public-search-error"
          className="mt-3 px-3 text-sm font-medium text-rose-700"
          role="alert"
        >
          {error}
        </p>
      ) : (
        <p className="mt-3 px-3 text-sm text-ink-soft">
          Explora la estructura inicial del producto usando rutas reales y validacion cliente.
        </p>
      )}
    </form>
  );
}
