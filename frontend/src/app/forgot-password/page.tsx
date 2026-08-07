'use client';

import { useState } from 'react';
import { authRequestPasswordReset } from '@/shared/api/auth';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setSubmitting(true);

    try {
      await authRequestPasswordReset(email);
      setSuccess(true);
    } catch (err) {
      const authErr = err as { detail?: string };
      setError(authErr.detail || 'Error en la solicitud');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-180px)] max-w-md flex-col justify-center py-12">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase text-[#006065]">Recuperar cuenta</p>
        <h2 className="text-3xl font-bold text-slate-950">Recuperar password</h2>
        <p className="text-sm text-slate-600">
          Ingresa tu correo y te enviaremos instrucciones para restablecer tu contrasena.
        </p>
      </div>

      {error && (
        <div role="alert" className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div role="status" className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
          Si el correo existe en el sistema, se ha enviado un enlace de recuperacion.
        </div>
      )}

      <form className="mt-8 space-y-4" aria-label="Formulario de recuperacion" onSubmit={handleSubmit}>
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

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-[#006065] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#004d50] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'Enviando...' : 'Enviar enlace de recuperacion'}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-600">
        Recordaste tu contrasena?{' '}
        <a href="/login" className="text-[#006065] font-semibold hover:underline">
          Volver a iniciar sesion
        </a>
      </p>
    </section>
  );
}
