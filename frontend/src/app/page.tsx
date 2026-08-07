/**
 * US-001 / AC-001-05 - Root public shell for FE-001
 *
 * This page provides the public landing shell that the base slice requires.
 * It renders without authentication and serves as the entry point for InVet.
 */

export default function HomePage() {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-180px)] max-w-3xl flex-col items-center justify-center py-20 text-center">
      <div className="space-y-6">
        <h1 className="text-4xl font-bold text-slate-950 sm:text-5xl">
          Bienvenido a InVet
        </h1>
        <p className="max-w-xl text-lg text-slate-600">
          La plataforma para buscar, comparar y agendar citas con las mejores clínicas veterinarias.
        </p>
        <div className="flex items-center justify-center gap-4 pt-4">
          <a
            href="/login"
            className="rounded-md bg-teal px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-teal-dark"
          >
            Iniciar sesión
          </a>
          <a
            href="/clinicas"
            className="rounded-md border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
          >
            Explorar clínicas
          </a>
        </div>
      </div>
    </section>
  );
}
