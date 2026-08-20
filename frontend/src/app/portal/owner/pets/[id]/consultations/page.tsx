'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import {
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  LoadingSpinner,
} from '@/shared/ui/components';
import {
  listConsultations,
  type Consultation,
  type ConsultationPageMeta,
} from '@/shared/api/consultation';

const PAGE_SIZE = 6;

function getErrorMessage(error: unknown, fallback: string): string {
  if (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    typeof (error as { detail?: unknown }).detail === 'string'
  ) {
    return (error as { detail: string }).detail;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return 'Sin fecha';
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(parsed);
}

function clampText(value: string, fallback: string): string {
  const trimmed = value.trim();
  if (!trimmed) {
    return fallback;
  }

  return trimmed.length > 220 ? `${trimmed.slice(0, 220)}…` : trimmed;
}

export default function OwnerPetConsultationsPage() {
  const params = useParams();
  const router = useRouter();
  const petParam = params.id;
  const petId = Number(Array.isArray(petParam) ? petParam[0] : petParam);

  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [meta, setMeta] = useState<ConsultationPageMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [emptyMessage, setEmptyMessage] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadConsultations() {
      setLoading(true);
      setError(null);
      setEmptyMessage(null);
      setConsultations([]);
      setMeta(null);

      if (!Number.isFinite(petId) || petId <= 0) {
        setError('No pudimos identificar la mascota.');
        setLoading(false);
        return;
      }

      try {
        const response = await listConsultations({
          pet_id: petId,
          page,
          page_size: PAGE_SIZE,
        });

        if (!active) {
          return;
        }

        setConsultations(response.items);
        setMeta(response.meta);
        if (response.items.length === 0) {
          setEmptyMessage('Aún no hay consultas registradas para esta mascota.');
        }
      } catch (err) {
        if (!active) {
          return;
        }

        const status = typeof err === 'object' && err !== null && 'status' in err
          ? Number((err as { status?: unknown }).status)
          : null;

        if (status === 403 || status === 404) {
          setConsultations([]);
          setMeta(null);
          setEmptyMessage('No encontramos consultas para esta mascota o no tienes permiso para verla.');
          return;
        }

        setError(getErrorMessage(err, 'No fue posible cargar las consultas.'));
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadConsultations();

    return () => {
      active = false;
    };
  }, [petId, page, reloadToken]);

  if (loading && consultations.length === 0) {
    return <LoadingSpinner label="Cargando historial de consultas" />;
  }

  if (error && consultations.length === 0) {
    return (
      <ErrorBanner
        message={error}
        onRetry={() => setReloadToken((current) => current + 1)}
        actionLabel="Reintentar"
      />
    );
  }

  if (consultations.length === 0) {
    return (
      <EmptyState
        title="Sin consultas registradas"
        description={emptyMessage ?? 'Todavía no se han registrado consultas para esta mascota.'}
        actionLabel="Volver a la mascota"
        onAction={() => router.push(`/portal/owner/pets/${petId}`)}
      />
    );
  }

  return (
    <div className="space-y-6 py-8">
      <section className="rounded-[32px] border border-sandy-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Historial clínico</p>
            <h1 className="text-3xl font-semibold text-slate-900">
              Consultas de la mascota #{petId}
            </h1>
            <p className="max-w-2xl text-sm text-slate-600">
              Vista de solo lectura para propietarios. Aquí aparecen las consultas registradas y su diagnóstico principal.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push(`/portal/owner/pets/${petId}`)}
            >
              Volver a la mascota
            </Button>
            <Button
              type="button"
              onClick={() => setReloadToken((current) => current + 1)}
            >
              Actualizar
            </Button>
          </div>
        </div>
      </section>

      {error ? <ErrorBanner message={error} /> : null}

      <Card className="p-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Consultas</p>
            <h2 className="text-xl font-semibold text-slate-900">
              {consultations.length} registro{consultations.length === 1 ? '' : 's'} encontrado{consultations.length === 1 ? '' : 's'}
            </h2>
          </div>
          {meta ? (
            <p className="text-sm text-slate-500">
              Página {meta.page} de {meta.pages || 1}
            </p>
          ) : null}
        </div>

        <div className="mt-6 space-y-4">
          {consultations.map((consultation) => (
            <Card key={consultation.id} className="p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="space-y-2">
                  <p className="text-xs uppercase tracking-[0.18em] text-teal">
                    Consulta #{consultation.id}
                  </p>
                  <h3 className="text-lg font-semibold text-slate-900">
                    {formatDateTime(consultation.updated_at)}
                  </h3>
                  <p className="text-sm text-slate-600">
                    {clampText(consultation.diagnosis, 'Sin diagnóstico registrado.')}
                  </p>
                  <p className="text-sm text-slate-500">
                    {clampText(consultation.history, 'Sin historia clínica adicional.')}
                  </p>
                </div>

                <div className="flex flex-col items-start gap-3 lg:items-end">
                  <div className="rounded-2xl bg-sandy-50 px-4 py-3 text-right text-sm text-slate-600">
                    <p>Sucursal #{consultation.branch_id}</p>
                    <p>Veterinario {consultation.veterinarian_id ? `#${consultation.veterinarian_id}` : 'por confirmar'}</p>
                  </div>
                  <Link
                    href={`/portal/owner/consultations/${consultation.id}`}
                    className="rounded-full bg-teal px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-teal-dark focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
                  >
                    Ver detalle
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {meta && meta.pages > 1 ? (
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {Array.from({ length: meta.pages }, (_, index) => index + 1).map((nextPage) => (
              <Button
                key={nextPage}
                type="button"
                variant={nextPage === meta.page ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setPage(nextPage)}
                disabled={nextPage === meta.page}
              >
                {nextPage}
              </Button>
            ))}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
