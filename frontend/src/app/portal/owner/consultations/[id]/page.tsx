'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getConsultation, type Consultation } from '@/shared/api/consultation';
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

function renderText(value: string | null | undefined, fallback: string): string {
  const trimmed = value?.trim();
  if (!trimmed) {
    return fallback;
  }

  return trimmed;
}

export default function OwnerConsultationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const consultationParam = params.id;
  const consultationId = Number(
    Array.isArray(consultationParam) ? consultationParam[0] : consultationParam,
  );

  const [consultation, setConsultation] = useState<Consultation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [emptyMessage, setEmptyMessage] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadConsultation() {
      setLoading(true);
      setError(null);
      setEmptyMessage(null);
      setConsultation(null);

      if (!Number.isFinite(consultationId) || consultationId <= 0) {
        setError('No pudimos identificar la consulta.');
        setLoading(false);
        return;
      }

      try {
        const response = await getConsultation(consultationId);
        if (!active) {
          return;
        }

        setConsultation(response);
      } catch (err) {
        if (!active) {
          return;
        }

        const status =
          typeof err === 'object' && err !== null && 'status' in err
            ? Number((err as { status?: unknown }).status)
            : null;

        if (status === 403 || status === 404) {
          setConsultation(null);
          setEmptyMessage('No encontramos esta consulta o no tienes permiso para verla.');
          return;
        }

        setError(getErrorMessage(err, 'No fue posible cargar el detalle de la consulta.'));
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadConsultation();

    return () => {
      active = false;
    };
  }, [consultationId, reloadToken]);

  if (loading && !consultation) {
    return <LoadingSpinner label="Cargando detalle de la consulta" />;
  }

  if (error && !consultation) {
    return (
      <ErrorBanner
        message={error}
        onRetry={() => setReloadToken((current) => current + 1)}
        actionLabel="Reintentar"
      />
    );
  }

  if (!consultation) {
    return (
      <EmptyState
        title="Consulta no encontrada"
        description={emptyMessage ?? 'La consulta no está disponible para tu cuenta.'}
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
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Detalle clínico</p>
            <h1 className="text-3xl font-semibold text-slate-900">
              Consulta #{consultation.id}
            </h1>
            <p className="max-w-2xl text-sm text-slate-600">
              Vista de solo lectura con los datos clínicos principales de la consulta.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push(`/portal/owner/pets/${consultation.pet_id}/consultations`)}
            >
              Volver al historial
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

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="p-5">
          <p className="text-sm text-slate-500">Consulta</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">#{consultation.id}</p>
        </Card>
        <Card className="p-5">
          <p className="text-sm text-slate-500">Mascota</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">#{consultation.pet_id}</p>
        </Card>
        <Card className="p-5">
          <p className="text-sm text-slate-500">Sucursal</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">#{consultation.branch_id}</p>
        </Card>
        <Card className="p-5">
          <p className="text-sm text-slate-500">Actualizada</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">
            {formatDateTime(consultation.updated_at)}
          </p>
        </Card>
      </div>

      <Card className="p-6">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-[24px] bg-sandy-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Diagnóstico principal</p>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {renderText(consultation.diagnosis, 'Sin diagnóstico registrado.')}
            </p>
          </div>
          <div className="rounded-[24px] bg-sandy-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Historial clínico</p>
            <p className="mt-2 text-sm leading-6 text-slate-700 whitespace-pre-wrap">
              {renderText(consultation.history, 'Sin historia clínica adicional.')}
            </p>
          </div>
          <div className="rounded-[24px] bg-sandy-50 p-4 md:col-span-2">
            <p className="text-sm font-semibold text-slate-900">Recomendaciones</p>
            <p className="mt-2 text-sm leading-6 text-slate-700 whitespace-pre-wrap">
              {renderText(consultation.recommendations, 'Sin recomendaciones registradas.')}
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Cita</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">#{consultation.appointment_id}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Clínica</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">#{consultation.clinic_id}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Veterinario</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">
              {consultation.veterinarian_id ? `#${consultation.veterinarian_id}` : 'Por confirmar'}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Registrada por</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">
              {consultation.created_by ? `#${consultation.created_by}` : 'Sin dato'}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
