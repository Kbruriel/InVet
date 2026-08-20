'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getAppointment } from '@/features/appointments/api';
import type { Appointment } from '@/features/appointments/types';
import {
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  LoadingSpinner,
} from '@/shared/ui/components';
import { createConsultation } from '@/shared/api/consultation';

const MAX_HISTORY = 3000;
const MAX_DIAGNOSIS = 2000;
const MAX_RECOMMENDATIONS = 3000;

interface ConsultationFormState {
  history: string;
  diagnosis: string;
  recommendations: string;
}

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
    return 'Sin registro';
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

function formatMinutes(start?: string | null, end?: string | null): string {
  if (!start || !end) {
    return 'Sin duración';
  }

  const startDate = new Date(start);
  const endDate = new Date(end);
  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    return 'Sin duración';
  }

  return `${Math.max(0, Math.round((endDate.getTime() - startDate.getTime()) / 60000))} min`;
}

export default function ConsultationEntryPage() {
  const params = useParams();
  const router = useRouter();
  const appointmentParam = params.id;
  const appointmentId = Number(Array.isArray(appointmentParam) ? appointmentParam[0] : appointmentParam);

  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formData, setFormData] = useState<ConsultationFormState>({
    history: '',
    diagnosis: '',
    recommendations: '',
  });

  useEffect(() => {
    let active = true;

    async function loadAppointment() {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);

      if (!Number.isFinite(appointmentId) || appointmentId <= 0) {
        setError('No pudimos identificar la cita.');
        setLoading(false);
        return;
      }

      try {
        const data = await getAppointment(appointmentId);
        if (!active) {
          return;
        }

        setAppointment(data);
      } catch (err) {
        if (!active) {
          return;
        }

        setError(getErrorMessage(err, 'No fue posible cargar la cita.'));
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadAppointment();

    return () => {
      active = false;
    };
  }, [appointmentId]);

  const handleChange = (field: keyof ConsultationFormState, value: string) => {
    setFormData((current) => ({ ...current, [field]: value }));
    if (fieldErrors[field]) {
      setFieldErrors((current) => {
        const next = { ...current };
        delete next[field];
        return next;
      });
    }
  };

  const validate = () => {
    const nextErrors: Record<string, string> = {};

    if (!formData.diagnosis.trim()) {
      nextErrors.diagnosis = 'El diagnóstico es obligatorio.';
    } else if (formData.diagnosis.trim().length > MAX_DIAGNOSIS) {
      nextErrors.diagnosis = 'El diagnóstico no debe superar 2000 caracteres.';
    }

    if (formData.history.trim().length > MAX_HISTORY) {
      nextErrors.history = 'La historia clínica no debe superar 3000 caracteres.';
    }

    if (formData.recommendations.trim().length > MAX_RECOMMENDATIONS) {
      nextErrors.recommendations = 'Las recomendaciones no deben superar 3000 caracteres.';
    }

    setFieldErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!appointment || appointment.pet_id == null) {
      setError('No pudimos resolver la cita o la mascota asociada.');
      return;
    }

    if (!validate()) {
      return;
    }

    setSubmitting(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const created = await createConsultation({
        appointment_id: appointment.id,
        pet_id: appointment.pet_id,
        branch_id: appointment.branch_id ?? undefined,
        veterinarian_id: appointment.veterinarian_id ?? undefined,
        history: formData.history.trim() || undefined,
        diagnosis: formData.diagnosis.trim(),
        recommendations: formData.recommendations.trim() || undefined,
      });

      setSuccessMessage(`Consulta registrada con éxito. ID #${created.id}.`);
      setFormData({ history: '', diagnosis: '', recommendations: '' });
      setFieldErrors({});
    } catch (err) {
      setError(getErrorMessage(err, 'No fue posible registrar la consulta.'));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner label="Cargando cita para registrar la consulta" />;
  }

  if (error && !appointment) {
    return (
      <ErrorBanner
        message={error}
        onRetry={() => {
          void (async () => {
            setLoading(true);
            setError(null);
            try {
              const data = await getAppointment(appointmentId);
              setAppointment(data);
            } catch (retryError) {
              setError(getErrorMessage(retryError, 'No fue posible cargar la cita.'));
            } finally {
              setLoading(false);
            }
          })();
        }}
        actionLabel="Reintentar"
      />
    );
  }

  if (!appointment) {
    return (
      <EmptyState
        title="No encontramos la cita"
        description="Revisa el identificador de la cita o vuelve a la agenda."
        actionLabel="Volver a la agenda"
        onAction={() => router.push('/clinic/appointments')}
      />
    );
  }

  if (appointment.status !== 'completed') {
    return (
      <EmptyState
        title="La cita aún no está completada"
        description="Solo puedes registrar una consulta cuando la cita ya terminó y su estado es completed."
        actionLabel="Volver a la cita"
        onAction={() => router.push(`/clinic/appointments/${appointmentId}`)}
      />
    );
  }

  return (
    <div className="space-y-6 py-8">
      <section className="rounded-[32px] border border-sandy-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Consulta médica</p>
            <h1 className="text-3xl font-semibold text-slate-900">Registrar consulta</h1>
            <p className="max-w-2xl text-sm text-slate-600">
              Completa el diagnóstico clínico de la cita terminada. La historia y las recomendaciones son opcionales.
            </p>
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push(`/clinic/appointments/${appointmentId}`)}
          >
            Volver a la cita
          </Button>
        </div>
      </section>

      {successMessage ? (
        <div
          className="rounded-[24px] border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm font-medium text-emerald-800"
          role="status"
          aria-live="polite"
        >
          {successMessage}
        </div>
      ) : null}

      {error ? <ErrorBanner message={error} /> : null}

      <Card className="p-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Cita</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">#{appointment.id}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Mascota</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">
              {appointment.pet_id ? `#${appointment.pet_id}` : 'Sin mascota'}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Sucursal</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">
              {appointment.branch_id ? `#${appointment.branch_id}` : 'Derivada de la cita'}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Duración</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">
              {formatMinutes(appointment.scheduled_start, appointment.scheduled_end)}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-[24px] bg-sandy-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Inicio de la cita</p>
            <p className="mt-1 text-sm text-slate-600">{formatDateTime(appointment.scheduled_start)}</p>
          </div>
          <div className="rounded-[24px] bg-sandy-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Fin de la cita</p>
            <p className="mt-1 text-sm text-slate-600">{formatDateTime(appointment.scheduled_end)}</p>
          </div>
          <div className="rounded-[24px] bg-sandy-50 p-4 md:col-span-2">
            <p className="text-sm font-semibold text-slate-900">Estado</p>
            <p className="mt-1 text-sm text-slate-600">
              La cita debe estar en <span className="font-semibold text-teal">completed</span> para registrar la consulta.
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6" noValidate>
          <div>
            <label htmlFor="diagnosis" className="mb-1 block text-sm font-medium text-slate-700">
              Diagnóstico *
            </label>
            <textarea
              id="diagnosis"
              rows={5}
              maxLength={MAX_DIAGNOSIS}
              value={formData.diagnosis}
              onChange={(event) => handleChange('diagnosis', event.target.value)}
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition-colors focus:ring-2 focus:ring-teal ${
                fieldErrors.diagnosis ? 'border-red-400 bg-red-50' : 'border-sandy-300 bg-white'
              }`}
              aria-invalid={Boolean(fieldErrors.diagnosis)}
              aria-describedby={fieldErrors.diagnosis ? 'diagnosis-error' : undefined}
              disabled={submitting}
              placeholder="Describe el diagnóstico principal de la consulta..."
            />
            <div className="mt-1 flex items-center justify-between gap-3 text-xs text-slate-500">
              <span>{formData.diagnosis.length}/{MAX_DIAGNOSIS}</span>
              {fieldErrors.diagnosis ? (
                <span id="diagnosis-error" className="text-red-600" role="alert">
                  {fieldErrors.diagnosis}
                </span>
              ) : null}
            </div>
          </div>

          <div>
            <label htmlFor="history" className="mb-1 block text-sm font-medium text-slate-700">
              Historia clínica
            </label>
            <textarea
              id="history"
              rows={4}
              maxLength={MAX_HISTORY}
              value={formData.history}
              onChange={(event) => handleChange('history', event.target.value)}
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition-colors focus:ring-2 focus:ring-teal ${
                fieldErrors.history ? 'border-red-400 bg-red-50' : 'border-sandy-300 bg-white'
              }`}
              aria-invalid={Boolean(fieldErrors.history)}
              aria-describedby={fieldErrors.history ? 'history-error' : undefined}
              disabled={submitting}
              placeholder="Contexto clínico relevante o notas de la exploración..."
            />
            <div className="mt-1 flex items-center justify-between gap-3 text-xs text-slate-500">
              <span>{formData.history.length}/{MAX_HISTORY}</span>
              {fieldErrors.history ? (
                <span id="history-error" className="text-red-600" role="alert">
                  {fieldErrors.history}
                </span>
              ) : null}
            </div>
          </div>

          <div>
            <label htmlFor="recommendations" className="mb-1 block text-sm font-medium text-slate-700">
              Recomendaciones
            </label>
            <textarea
              id="recommendations"
              rows={4}
              maxLength={MAX_RECOMMENDATIONS}
              value={formData.recommendations}
              onChange={(event) => handleChange('recommendations', event.target.value)}
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition-colors focus:ring-2 focus:ring-teal ${
                fieldErrors.recommendations ? 'border-red-400 bg-red-50' : 'border-sandy-300 bg-white'
              }`}
              aria-invalid={Boolean(fieldErrors.recommendations)}
              aria-describedby={fieldErrors.recommendations ? 'recommendations-error' : undefined}
              disabled={submitting}
              placeholder="Tratamiento, cuidados y seguimiento sugerido..."
            />
            <div className="mt-1 flex items-center justify-between gap-3 text-xs text-slate-500">
              <span>{formData.recommendations.length}/{MAX_RECOMMENDATIONS}</span>
              {fieldErrors.recommendations ? (
                <span id="recommendations-error" className="text-red-600" role="alert">
                  {fieldErrors.recommendations}
                </span>
              ) : null}
            </div>
          </div>

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push(`/clinic/appointments/${appointmentId}`)}
              disabled={submitting}
            >
              Cancelar
            </Button>
            <Button type="submit" isLoading={submitting} disabled={submitting}>
              Registrar consulta
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
