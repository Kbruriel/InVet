'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { authConfirmPasswordReset } from '@/shared/api/auth';

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const resetToken = searchParams.get('token');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!resetToken) {
      setError('Token de recuperacion no valido');
    }
  }, [resetToken]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (newPassword !== confirmPassword) {
      setError('Las contrasenas no coinciden');
      return;
    }

    if (!resetToken) {
      setError('Token de recuperacion no valido');
      return;
    }

    setSubmitting(true);

    try {
      await authConfirmPasswordReset(resetToken, newPassword);
      setSuccess(true);
      setTimeout(() => router.push('/login?reset=true'), 3000);
    } catch (err) {
      const authErr = err as { detail?: string };
      setError(authErr.detail || 'Error al restablecer la contrasena');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-180px)] max-w-md flex-col justify-center py-12">
      <div className="space-y-2">
        <p className="text-sm font-semibold uppercase text-[#006065]">Nueva contrasena</p>
        <h2 className="text-3xl font-bold text-slate-950">Restablecer password</h2>
        <p className="text-sm text-slate-600">
          Ingresa tu nueva contrasena para completar la recuperacion.
        </p>
      </div>

      {error && (
        <div role="alert" className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div role="status" className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
          Contrasena restablecida correctamente. Redirigiendo...
        </div>
      )}

      <form className="mt-8 space-y-4" aria-label="Formulario de nueva contrasena" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label htmlFor="newPassword" className="block text-sm font-medium text-slate-800">
            Nueva contrasena
          </label>
          <input
            id="newPassword"
            type="password"
            required
            minLength={6}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-[#006065] focus:outline-none focus:ring-2 focus:ring-[#006065]/20"
            placeholder="Minimo 6 caracteres"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-800">
            Confirmar nueva contrasena
          </label>
          <input
            id="confirmPassword"
            type="password"
            required
            minLength={6}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full rounded-md border border-sandy-300 bg-white px-3 py-2 text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus:border-[#006065] focus:outline-none focus:ring-2 focus:ring-[#006065]/20"
            placeholder="Repite tu nueva contrasena"
          />
        </div>

        <button
          type="submit"
          disabled={submitting || !resetToken}
          className="w-full rounded-md bg-[#006065] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#004d50] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'Procesando...' : 'Restablecer contrasena'}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-600">
        <a href="/login" className="text-[#006065] font-semibold hover:underline">
          Volver a iniciar sesion
        </a>
      </p>
    </section>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div>Cargando...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
