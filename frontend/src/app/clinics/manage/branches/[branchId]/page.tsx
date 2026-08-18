'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Card, Button, ErrorBanner, LoadingSpinner } from '@/shared/ui/components';
import { fetchBranchProtected, BranchProfileProtected } from '@/shared/api/branch-client-protected';
import { RequireAuth } from '@/shared/auth/RequireAuth';

type UiState = 'loading' | 'success' | 'error';

function ProtectedBranchPageContent() {
  const params = useParams();
  const clinicParam = params.clinicId;
  const branchParam = params.branchId;
  const clinicId = Number(Array.isArray(clinicParam) ? clinicParam[0] : clinicParam ?? 1);
  const branchId = Number(Array.isArray(branchParam) ? branchParam[0] : branchParam);

  const [branch, setBranch] = useState<BranchProfileProtected | null>(null);
  const [state, setState] = useState<UiState>('loading');
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState('loading');
    setError(null);
    try {
      const data = await fetchBranchProtected(clinicId, branchId);
      setBranch(data);
      setState('success');
    } catch (err) {
      const e = err as { status?: number; detail?: string };
      if (e.status === 401) {
        window.location.href = '/login';
        return;
      }
      setError(e.detail || 'No se pudo cargar el perfil de la sucursal.');
      setState('error');
    }
  }, [clinicId, branchId]);

  useEffect(() => {
    if (clinicId && branchId) load();
  }, [clinicId, branchId, load]);

  if (state === 'loading') {
    return <LoadingSpinner label="Cargando perfil de sucursal..." />;
  }

  if (state === 'error') {
    return <ErrorBanner message={error ?? 'Error desconocido'} onRetry={load} actionLabel="Reintentar" />;
  }

  if (!branch) return null;

  return (
    <main>
      <section aria-label={`Perfil protegido de ${branch.name}`} className="py-10">
        <div className="mb-6">
          <Link href="/clinicas" className="text-sm text-teal hover:underline">
            &larr; Volver a clínicas
          </Link>
        </div>

        <Card className="p-8">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
            {branch.logoUrl && (
              <img
                src={branch.logoUrl}
                alt={`Logo de ${branch.name}`}
                className="h-24 w-24 flex-shrink-0 rounded-full object-cover"
                width={96}
                height={96}
              />
            )}
            <div className="flex-1">
              <h1 className="text-2xl font-extrabold text-slate-900 sm:text-3xl">{branch.name}</h1>
              {branch.city && (
                <p className="mt-1 text-sm text-slate-500">📍 {branch.city}</p>
              )}
              {branch.address && (
                <p className="mt-1 text-sm text-slate-600">{branch.address}</p>
              )}
              {branch.phone && (
                <p className="mt-1 text-sm text-slate-600">📞 {branch.phone ?? ''}</p>
              )}
              {branch.rating && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-lg text-teal">{'★'.repeat(Math.round(branch.rating.average))}</span>
                  <span className="text-sm font-medium text-slate-700">{branch.rating.average.toFixed(1)}</span>
                  <span className="text-xs text-slate-500">({branch.rating.count})</span>
                </div>
              )}
              {branch.availability && (
                <div className="mt-2">
                  <span
                    className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${
                      branch.availability.status === 'available'
                        ? 'bg-green-100 text-green-800'
                        : branch.availability.status === 'unavailable'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {branch.availability.status === 'available'
                      ? 'Disponible'
                      : branch.availability.status === 'unavailable'
                      ? 'No disponible'
                      : 'Sin cupos'}
                  </span>
                </div>
              )}
            </div>
          </div>

          {branch.description && (
            <div className="mt-6 border-t border-sandy-300 pt-6">
              <h2 className="mb-3 text-lg font-semibold text-slate-900">Acerca de</h2>
              <p className="text-sm leading-relaxed text-slate-700">{branch.description}</p>
            </div>
          )}

          {branch.services.length > 0 && (
            <div className="mt-6 border-t border-sandy-300 pt-6">
              <h2 className="mb-3 text-lg font-semibold text-slate-900">Servicios</h2>
              <ul className="space-y-2">
                {branch.services.map((service) => (
                  <li key={service.id} className="flex items-center justify-between rounded-lg bg-slate-50 p-3">
                    <span className="text-sm text-slate-700">{service.name}</span>
                    <div className="flex items-center gap-3">
                      {service.price != null && (
                        <span className="text-sm font-semibold text-teal">${service.price.toFixed(2)}</span>
                      )}
                      {!service.active && (
                        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                          Inactivo
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {branch.schedules.length > 0 && (
            <div className="mt-6 border-t border-sandy-300 pt-6">
              <h2 className="mb-3 text-lg font-semibold text-slate-900">Horarios</h2>
              <ul className="space-y-2">
                {branch.schedules.map((schedule) => (
                  <li key={schedule.id} className="flex items-center justify-between rounded-lg bg-slate-50 p-3">
                    <span className="text-sm text-slate-700">{schedule.dayOfWeek}</span>
                    <span className="text-sm text-slate-600">
                      {schedule.openTime} - {schedule.closeTime}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-6 flex flex-wrap gap-4 border-t border-sandy-300 pt-6">
            <Link href={`/register?branch=${branchId}`}>
              <Button size="lg">Solicitar cita</Button>
            </Link>
            <Link href="/clinicas">
              <Button variant="outline" size="lg">
                Otras clínicas
              </Button>
            </Link>
          </div>
        </Card>
      </section>
    </main>
  );
}

export default function ProtectedBranchPage() {
  return (
    <RequireAuth>
      <ProtectedBranchPageContent />
    </RequireAuth>
  );
}
