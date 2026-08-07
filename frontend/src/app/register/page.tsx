'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authRegister } from '@/shared/api/auth';

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Las contrasenas no coinciden');
      return;
    }

    setSubmitting(true);

    try {
      await authRegister({ email, password, firstName, lastName });
      router.push('/login?registered=true');
    } catch (err) {
      const authErr = err as { detail?: string; status?: number };
      if (authErr.status === 409) {
        setError('Ya existe un usuario con ese correo');
      } else {
        setError(authErr.detail || 'Error en el registro');
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-180px)] max-w-md flex-col justify-center py-12">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase text-[#006065]">Crear cuenta</p>
        <h2 className="text-3xl font-bold text-slate-950">Registrarse en InVet</h2>
        <p className="text-sm text-slate-600">
          Completa el formulario para crear tu cuenta.
        </p>
      </div>

      {error && (
        <div role="alert" className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <form className="mt-8 space-y-4" aria-label="Formulario de registro" onSubmit={handleSubmit}>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="firstName" className="block text-sm font-medium text-slate-800">
              Nombre
            </label>
            <input
              id="firstName"
              type="text"
              required
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-[#006065] focus:outline-none focus:ring-2 focus:ring-[#006065]/20"
              placeholder="Juan"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="lastName" className="block text-sm font-medium text-slate-800">
              Apellido
            </label>
            <input
              id="lastName"
              type="text"
              required
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-[#006065] focus:outline-none focus:ring-2 focus:ring-[#006065]/20"
              placeholder="Perez"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium text-slate-800">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-[#006065] focus:outline-none focus:ring-2 focus:ring-[#006065]/20"
            placeholder="tu@correo.com"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium text-slate-800">
            Contrasena
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-[#006065] focus:outline-none focus:ring-2 focus:ring-[#006065]/20"
            placeholder="Minimo 6 caracteres"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-800">
            Confirmar contrasena
          </label>
          <input
            id="confirmPassword"
            type="password"
            required
            minLength={6}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-[#006065] focus:outline-none focus:ring-2 focus:ring-[#006065]/20"
            placeholder="Repite tu contrasena"
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-[#006065] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#004d50] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'Registrando...' : 'Registrarse'}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-600">
        Ya tienes cuenta?{' '}
        <a href="/login" className="text-[#006065] font-semibold hover:underline">
          Iniciar sesion
        </a>
      </p>
    </section>
  );
}
