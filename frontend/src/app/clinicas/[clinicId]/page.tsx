'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { fetchPublicClinicDetail, PublicClinic } from '@/shared/api/public';
import { Card, Button } from '@/shared/ui/components';

type UiState = 'loading' | 'success' | 'error';

export default function ClinicDetailPage() {
  const params = useParams();
  const clinicId = Number(params.clinicId);
  const [clinic, setClinic] = useState<PublicClinic | null>(null);
  const [state, setState] = useState<UiState>('loading');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setState('loading');
      setError(null);
      try {
        const data = await fetchPublicClinicDetail(clinicId);
        if (!cancelled) {
          setClinic(data);
          setState('success');
        }
      } catch (err) {
        const e = err as { status?: number; detail?: string };
        if (!cancelled) {
          setError(e.detail || 'No se pudo cargar el detalle de la clinica.');
          setState('error');
        }
      }
    }

    if (clinicId) load();
    return () => { cancelled = true; };
  }, [clinicId]);

  if (state === 'loading') {
    return (
      <section className="py-16" role="status" aria-label="Cargando detalle de clinica">
        <div className="flex items-center justify-center">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-teal/30 border-t-teal" />
          <span className="sr-only">Cargando...</span>
        </div>
      </section>
    );
  }

  if (state === 'error') {
    return (
      <section className="py-16" role="alert">
        <div className="mx-auto max-w-xl rounded-xl bg-red-50 p-8 text-center">
          <p className="text-lg font-semibold text-red-700">{error}</p>
          <Link href="/clinicas">
            <Button variant="outline" size="sm" className="mt-4">
              Volver al listado
            </Button>
          </Link>
        </div>
      </section>
    );
  }

  if (!clinic) return null;

  return (
    <section aria-label={`Detalle de ${clinic.name}`} className="py-10">
      <div className="mb-6">
        <Link href="/clinicas" className="text-sm text-teal hover:underline">
          &larr; Volver a clínicas
        </Link>
      </div>

      <Card className="p-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
          {clinic.logoUrl && (
            <img
              src={clinic.logoUrl}
              alt={`Logo de ${clinic.name}`}
              className="h-24 w-24 flex-shrink-0 rounded-full object-cover"
              width={96}
              height={96}
            />
          )}
          <div className="flex-1">
            <h1 className="text-2xl font-extrabold text-slate-900 sm:text-3xl">{clinic.name}</h1>
            {clinic.city && (
              <p className="mt-1 text-sm text-slate-500">📍 {clinic.city}</p>
            )}
            {clinic.address && (
              <p className="mt-1 text-sm text-slate-600">{clinic.address}</p>
            )}
            {clinic.rating != null && (
              <div className="mt-2 flex items-center gap-1" aria-label={`Calificacion ${clinic.rating} de 5 estrellas`}>
                <span className="text-lg text-teal">{'★'.repeat(Math.round(clinic.rating))}</span>
                <span className="text-sm text-slate-500">{clinic.rating} / 5</span>
              </div>
            )}
          </div>
        </div>

        {clinic.description && (
          <div className="mt-6 border-t border-sandy-300 pt-6">
            <h2 className="mb-3 text-lg font-semibold text-slate-900">Acerca de</h2>
            <p className="text-sm leading-relaxed text-slate-700">{clinic.description}</p>
          </div>
        )}

        <div className="mt-6 flex flex-wrap gap-4 border-t border-sandy-300 pt-6">
          <Link href="/register">
            <Button size="lg">Solicita tu cita</Button>
          </Link>
          <Link href="/clinicas">
            <Button variant="outline" size="lg">
              Otras clinicas
            </Button>
          </Link>
        </div>
      </Card>
    </section>
  );
}
