export default function LoginPage() {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-180px)] max-w-md flex-col justify-center py-12">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase text-teal-dark">Acceso seguro</p>
        <h2 className="text-3xl font-bold text-slate-950">Inicia sesion en InVet</h2>
        <p className="text-sm text-slate-600">
          Entra con tus credenciales para continuar con la gestion de tu cuenta.
        </p>
      </div>

      <form className="mt-8 space-y-5" aria-label="Formulario de inicio de sesion">
        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium text-slate-800">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-teal focus:outline-none focus:ring-2 focus:ring-teal/20"
            placeholder="qa@example.com"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium text-slate-800">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-teal focus:outline-none focus:ring-2 focus:ring-teal/20"
            placeholder="secret123"
          />
        </div>

        <button
          type="submit"
          className="w-full rounded-md bg-teal px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-teal-dark"
        >
          Iniciar sesion
        </button>
      </form>
    </section>
  );
}
