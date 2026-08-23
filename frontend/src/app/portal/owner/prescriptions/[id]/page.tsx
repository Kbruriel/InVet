'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getPrescription, type Prescription } from '@/shared/api/prescription';
import {
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  LoadingSpinner,
} from '@/shared/ui/components';

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

function formatDue(value: string | null | undefined): string {
  if (!value) return 'Sin vencimiento';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
  }).format(parsed);
}

function renderText(value: string | null | undefined, fallback: string): string {
  const trimmed = value?.trim();
  return trimmed ? trimmed : fallback;
}

export default function OwnerPrescriptionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const idParam = params.id;
  const prescriptionId = Number(Array.isArray(idParam) ? idParam[0] : idParam);

  const [prescription, setPrescription] = useState<Prescription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [emptyMessage, setEmptyMessage] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadPrescription() {
      setLoading(true);
      setError(null);
      setEmptyMessage(null);
      setPrescription(null);

      if (!Number.isFinite(prescriptionId) || prescriptionId <= 0) {
        setError('No pudimos identificar la receta.');
        setLoading(false);
        return;
      }

      try {
        const response = await getPrescription(prescriptionId);
        if (!active) return;
        setPrescription(response);
      } catch (err) {
        if (!active) return;
        const status =
          typeof err === 'object' && err !== null && 'status' in err
            ? Number((err as { status?: unknown }).status)
            : null;
        if (status === 403 || status === 404) {
          setPrescription(null);
          setEmptyMessage('No encontramos esta receta o no tienes permiso para verla.');
          return;
        }
        setError(getErrorMessage(err, 'No fue posible cargar el detalle de la receta.'));
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadPrescription();

    return () => {
      active = false;
    };
  }, [prescriptionId, reloadToken]);

  if (loading && !prescription) {
    return <LoadingSpinner label="Cargando detalle de la receta" />;
  }

  if (error && !prescription) {
    return (
      <ErrorBanner
        message={error}
        onRetry={() => setReloadToken((c) => c + 1)}
        actionLabel="Reintentar"
      />
    );
  }

  if (!prescription) {
    return (
      <EmptyState
        title="Receta no encontrada"
        description={emptyMessage ?? 'La receta no está disponible para tu cuenta.'}
        actionLabel="Volver al portal"
        onAction={() => router.push('/portal/owner')}
      />
    );
  }

  return (
    <div className="space-y-6 py-8">
      <section className="rounded-[32px] border border-sandy-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Receta</p>
            <h1 className="text-3xl font-semibold text-slate-900">
              Receta #{prescription.id}
            </h1>
            <p className="max-w-2xl text-sm text-slate-600">
              Detalle de la receta, sus medicamentos, tratamientos y recordatorios.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push(`/portal/owner/pets/${prescription.pet_id}/prescriptions`)}
            >
              Volver a las recetas
            </Button>
            <Button type="button" onClick={() => setReloadToken((c) => c + 1)}>
              Actualizar
            </Button>
          </div>
        </div>
      </section>

      {error ? <ErrorBanner message={error} /> : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="p-5">
          <p className="text-sm text-slate-500">Consulta</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">#{prescription.consultation_id}</p>
        </Card>
        <Card className="p-5">
          <p className="text-sm text-slate-500">Mascota</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">#{prescription.pet_id}</p>
        </Card>
        <Card className="p-5">
          <p className="text-sm text-slate-500">Sucursal</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">#{prescription.branch_id ?? '—'}</p>
        </Card>
        <Card className="p-5">
          <p className="text-sm text-slate-500">Registrada</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">
            {formatDateTime(prescription.created_at)}
          </p>
        </Card>
      </div>

      <Card className="p-6">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-[24px] bg-sandy-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Diagnóstico</p>
            <p className="mt-2 text-sm leading-6 whitespace-pre-wrap text-slate-700">
              {renderText(prescription.diagnosis, 'Sin diagnóstico registrado.')}
            </p>
          </div>
          <div className="rounded-[24px] bg-sandy-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Notas de tratamiento</p>
            <p className="mt-2 text-sm leading-6 whitespace-pre-wrap text-slate-700">
              {renderText(prescription.treatment_notes, 'Sin notas registradas.')}
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-lg font-semibold text-slate-900">Medicamentos</h2>
        {prescription.items.length === 0 ? (
          <p className="mt-3 text-sm text-slate-500">Sin medicamentos registrados.</p>
        ) : (
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {prescription.items.map((item, index) => (
              <div key={item.id ?? index} className="rounded-2xl border border-sandy-200 bg-white p-4">
                <p className="text-sm font-semibold text-slate-900">{item.name}</p>
                <div className="mt-2 grid gap-1 text-sm text-slate-600">
                  {item.dosage ? <p>Dosis: {item.dosage}</p> : null}
                  {item.frequency ? <p>Frecuencia: {item.frequency}</p> : null}
                  {item.duration ? <p>Duración: {item.duration}</p> : null}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card className="p-6">
        <h2 className="text-lg font-semibold text-slate-900">Tratamientos</h2>
        {prescription.treatments.length === 0 ? (
          <p className="mt-3 text-sm text-slate-500">Sin tratamientos registrados.</p>
        ) : (
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {prescription.treatments.map((t, index) => (
              <div key={t.id ?? index} className="rounded-2xl border border-sandy-200 bg-white p-4">
                <p className="text-sm font-semibold text-slate-900">{t.name}</p>
                <p className="mt-2 text-sm leading-6 whitespace-pre-wrap text-slate-600">
                  {renderText(t.instructions, 'Sin instrucciones.')}
                </p>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card className="p-6">
        <h2 className="text-lg font-semibold text-slate-900">Recordatorios</h2>
        {prescription.reminders.length === 0 ? (
          <p className="mt-3 text-sm text-slate-500">Sin recordatorios registrados.</p>
        ) : (
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {prescription.reminders.map((r, index) => (
              <div key={r.id ?? index} className="rounded-2xl border border-sandy-200 bg-white p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-slate-900">{r.title}</p>
                  <p className="text-xs text-slate-500">{formatDue(r.due_at)}</p>
                </div>
                {r.note ? (
                  <p className="mt-2 text-sm leading-6 whitespace-pre-wrap text-slate-600">{r.note}</p>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card className="p-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Clínica</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">#{prescription.clinic_id}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Veterinario</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">
              {prescription.veterinarian_id ? `#${prescription.veterinarian_id}` : 'Por confirmar'}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Creado por</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">
              {prescription.created_by ? `#${prescription.created_by}` : 'Sin dato'}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Última actualización</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">
              {formatDateTime(prescription.updated_at)}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
