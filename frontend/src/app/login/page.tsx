'use client';

import { Suspense, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { authLogin } from '@/shared/api/auth';

function LoginInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const returnUrl = searchParams.get('returnUrl');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const resolveReturnUrl = () => {
    if (
      returnUrl &&
      returnUrl.startsWith('/') &&
      !returnUrl.startsWith('//') &&
      !returnUrl.startsWith('/login')
    ) {
      return returnUrl;
    }
    return '/';
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      const result = await authLogin({ email, password });
      localStorage.setItem('access_token', result.access_token);
      localStorage.setItem('refresh_token', result.refresh_token);
      router.push(resolveReturnUrl());
      router.refresh();
    } catch (err) {
      const authErr = err as { detail?: string };
      setError(authErr.detail || 'Error al iniciar sesion');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-180px)] max-w-md flex-col justify-center py-12">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase text-[#006065]">Acceso seguro</p>
        <h2 className="text-3xl font-bold text-slate-950">Inicia sesion en InVet</h2>
        <p className="text-sm text-slate-600">
          Entra con tus credenciales para continuar con la gestion de tu cuenta.
        </p>
      </div>

      {error && (
        <div role="alert" className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <form className="mt-8 space-y-5" aria-label="Formulario de inicio de sesion" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium text-slate-800">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-[#006065] focus:outline-none focus:ring-2 focus:ring-[#006065]/20"
            placeholder="tu@correo.com"
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
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-[#006065] focus:outline-none focus:ring-2 focus:ring-[#006065]/20"
            placeholder="Minimo 6 caracteres"
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-[#006065] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#004d50] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'Iniciando...' : 'Iniciar sesion'}
        </button>
      </form>

      <div className="mt-6 space-y-2 text-center">
        <a href="/forgot-password" className="block text-sm text-[#006065] hover:underline">
          Recuperar password
        </a>
        <p className="text-sm text-slate-600">
          No tienes cuenta?{' '}
          <a href="/register" className="text-[#006065] font-semibold hover:underline">
            Registrarse
          </a>
        </p>
      </div>
    </section>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginInner />
    </Suspense>
  );
}
