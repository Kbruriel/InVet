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
  listPrescriptions,
  type Prescription,
  type PrescriptionPageMeta,
} from '@/shared/api/prescription';

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
  if (error instanceof Error) return error.message;
  return fallback;
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) return 'Sin fecha';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(parsed);
}

function clampText(value: string, fallback: string): string {
  const trimmed = value.trim();
  if (!trimmed) return fallback;
  return trimmed.length > 220 ? `${trimmed.slice(0, 220)}…` : trimmed;
}

export default function OwnerPetPrescriptionsPage() {
  const params = useParams();
  const router = useRouter();
  const petParam = params.petId;
  const petId = Number(Array.isArray(petParam) ? petParam[0] : petParam);

  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [meta, setMeta] = useState<PrescriptionPageMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<boolean>(false);
  const [errorText, setErrorText] = useState<string | null>(null);
  const [emptyMessage, setEmptyMessage] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadPrescriptions() {
      setLoading(true);
      setError(false);
      setErrorText(null);
      setEmptyMessage(null);
      setPrescriptions([]);
      setMeta(null);

      if (!Number.isFinite(petId) || petId <= 0) {
        setError(true);
        setErrorText('No pudimos identificar la mascota.');
        setLoading(false);
        return;
      }

      try {
        const response = await listPrescriptions({
          pet_id: petId,
          page,
          page_size: PAGE_SIZE,
        });
        if (!active) return;
        setPrescriptions(response.items);
        setMeta(response.meta);
        if (response.items.length === 0) {
          setEmptyMessage('Aún no hay recetas registradas para esta mascota.');
        }
      } catch (err) {
        if (!active) return;
        const status =
          typeof err === 'object' && err !== null && 'status' in err
            ? Number((err as { status?: unknown }).status)
            : null;
        if (status === 403 || status === 404) {
          setPrescriptions([]);
          setMeta(null);
          setEmptyMessage('No encontramos recetas para esta mascota o no tienes permiso para verla.');
          return;
        }
        setError(true);
        setErrorText(getErrorMessage(err, 'No fue posible cargar las recetas.'));
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadPrescriptions();

    return () => {
      active = false;
    };
  }, [petId, page, reloadToken]);

  if (loading && prescriptions.length === 0) {
    return <LoadingSpinner label="Cargando recetas" />;
  }

  if (error && prescriptions.length === 0) {
    return (
      <ErrorBanner
        message={errorText ?? 'Error de carga'}
        onRetry={() => setReloadToken((c) => c + 1)}
        actionLabel="Reintentar"
      />
    );
  }

  if (prescriptions.length === 0) {
    return (
      <EmptyState
        title="Sin recetas registradas"
        description={emptyMessage ?? 'Todavía no hay recetas para esta mascota.'}
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
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Recetas</p>
            <h1 className="text-3xl font-semibold text-slate-900">
              Recetas de la mascota #{petId}
            </h1>
            <p className="max-w-2xl text-sm text-slate-600">
              Vista de solo lectura de las recetas y tratamientos registrados para esta mascota.
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
              onClick={() => setReloadToken((c) => c + 1)}
            >
              Actualizar
            </Button>
          </div>
        </div>
      </section>

      {error ? <ErrorBanner message={errorText ?? 'Error'} /> : null}

      <Card className="p-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Recetas</p>
            <h2 className="text-xl font-semibold text-slate-900">
              {prescriptions.length} receta{prescriptions.length === 1 ? '' : 's'}
            </h2>
          </div>
          {meta ? (
            <p className="text-sm text-slate-500">
              Página {meta.page} de {meta.pages || 1}
            </p>
          ) : null}
        </div>

        <div className="mt-6 space-y-4">
          {prescriptions.map((p) => (
            <Card key={p.id} className="p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="space-y-2">
                  <p className="text-xs uppercase tracking-[0.18em] text-teal">
                    Receta #{p.id} · Consulta #{p.consultation_id}
                  </p>
                  <h3 className="text-lg font-semibold text-slate-900">
                    {formatDateTime(p.updated_at ?? p.created_at)}
                  </h3>
                  <p className="text-sm text-slate-600">
                    {clampText(p.diagnosis, 'Sin diagnóstico registrado.')}
                  </p>
                  {p.items.length > 0 ? (
                    <p className="text-sm text-slate-500">
                      {p.items.length} medicamento{p.items.length === 1 ? '' : 's'}
                    </p>
                  ) : null}
                  {p.treatments.length > 0 ? (
                    <p className="text-sm text-slate-500">
                      {p.treatments.length} tratamiento{p.treatments.length === 1 ? '' : 'es'}
                    </p>
                  ) : null}
                  {p.reminders.length > 0 ? (
                    <p className="text-sm text-slate-500">
                      {p.reminders.length} recordatorio{p.reminders.length === 1 ? '' : 's'}
                    </p>
                  ) : null}
                </div>

                <div className="flex flex-col items-start gap-3 lg:items-end">
                  <div className="rounded-2xl bg-sandy-50 px-4 py-3 text-right text-sm text-slate-600">
                    <p>Sucursal #{p.branch_id ?? '—'}</p>
                    <p>Veterinario {p.veterinarian_id ? `#${p.veterinarian_id}` : 'por confirmar'}</p>
                  </div>
                  <Link
                    href={`/portal/owner/prescriptions/${p.id}`}
                    className="rounded-full bg-teal px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-teal-dark focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
                  >
                    Ver receta
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {meta && meta.pages > 1 ? (
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {Array.from({ length: meta.pages }, (_, i) => i + 1).map((nextPage) => (
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
