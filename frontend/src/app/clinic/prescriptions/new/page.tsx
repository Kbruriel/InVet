'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { getConsultation, type Consultation } from '@/shared/api/consultation';
import { createPrescription } from '@/shared/api/prescription';
import {
  Button,
  Card,
  ErrorBanner,
  LoadingSpinner,
} from '@/shared/ui/components';

const MAX_DIAGNOSIS = 2000;
const MAX_TREATMENT_NOTES = 3000;

interface ItemRow {
  name: string;
  dosage: string;
  frequency: string;
  duration: string;
}

interface TreatmentRow {
  name: string;
  instructions: string;
}

interface ReminderRow {
  title: string;
  due_at: string;
  note: string;
}

interface FormState {
  diagnosis: string;
  treatment_notes: string;
  items: ItemRow[];
  treatments: TreatmentRow[];
  reminders: ReminderRow[];
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
  if (error instanceof Error) return error.message;
  return fallback;
}

function CreatePrescriptionForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const consultationParam = searchParams.get('consultation_id');
  const consultationId = Number(consultationParam);

  const [consultation, setConsultation] = useState<Consultation | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdId, setCreatedId] = useState<number | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const [form, setForm] = useState<FormState>({
    diagnosis: '',
    treatment_notes: '',
    items: [],
    treatments: [],
    reminders: [],
  });

  const consultationInvalid = !Number.isFinite(consultationId) || consultationId <= 0;

  useEffect(() => {
    if (consultationInvalid) {
      setError('No indicaste una consulta. Incluye `?consultation_id=<id>` en la URL.');
      setLoading(false);
      return;
    }

    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getConsultation(consultationId);
        if (active) {
          setConsultation(data);
          setForm((prev) => ({ ...prev, diagnosis: data.diagnosis || prev.diagnosis }));
        }
      } catch (err) {
        if (active) {
          setError(getErrorMessage(err, 'No fue posible cargar la consulta.'));
        }
      } finally {
        if (active) setLoading(false);
      }
    })();

    return () => {
      active = false;
    };
  }, [consultationId, consultationInvalid]);


  const setItem = (index: number, patch: Partial<ItemRow>) =>
    setForm((prev) => ({
      ...prev,
      items: prev.items.map((it, i) => (i === index ? { ...it, ...patch } : it)),
    }));
  const removeItem = (index: number) =>
    setForm((prev) => ({ ...prev, items: prev.items.filter((_, i) => i !== index) }));
  const addItem = () =>
    setForm((prev) => ({ ...prev, items: [...prev.items, { name: '', dosage: '', frequency: '', duration: '' }] }));

  const setTreatment = (index: number, patch: Partial<TreatmentRow>) =>
    setForm((prev) => ({
      ...prev,
      treatments: prev.treatments.map((t, i) => (i === index ? { ...t, ...patch } : t)),
    }));
  const removeTreatment = (index: number) =>
    setForm((prev) => ({ ...prev, treatments: prev.treatments.filter((_, i) => i !== index) }));
  const addTreatment = () =>
    setForm((prev) => ({ ...prev, treatments: [...prev.treatments, { name: '', instructions: '' }] }));

  const setReminder = (index: number, patch: Partial<ReminderRow>) =>
    setForm((prev) => ({
      ...prev,
      reminders: prev.reminders.map((r, i) => (i === index ? { ...r, ...patch } : r)),
    }));
  const removeReminder = (index: number) =>
    setForm((prev) => ({ ...prev, reminders: prev.reminders.filter((_, i) => i !== index) }));
  const addReminder = () =>
    setForm((prev) => ({ ...prev, reminders: [...prev.reminders, { title: '', due_at: '', note: '' }] }));

  if (loading && !consultation) {
    return <LoadingSpinner label="Cargando la consulta asociada" />;
  }

  if (error && !consultation) {
    return <ErrorBanner message={error} />;
  }

  if (createdId !== null) {
    return (
      <div className="space-y-6 py-8">
        <section className="rounded-[32px] border border-emerald-200 bg-emerald-50 p-6">
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-700">Receta creada</p>
          <h1 className="mt-2 text-3xl font-semibold text-emerald-900">Receta #{createdId}</h1>
          <p className="mt-2 max-w-2xl text-sm text-emerald-800">
            La receta fue registrada correctamente. El propietario podrá verla en su portal.
          </p>
        </section>
        <div className="flex flex-wrap gap-3">
          <Button
            type="button"
            onClick={() =>
              router.push(`/clinic/appointments/${consultation?.appointment_id}/consultation`)
            }
          >
            Volver a la consulta
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Regresar
          </Button>
        </div>
      </div>
    );
  }

  if (!consultation || consultationInvalid) {
    return (
      <ErrorBanner
        message={error ?? 'No pudimos resolver la consulta indicada.'}
        actionLabel="Volver"
        onRetry={() => router.back()}
      />
    );
  }

  const validate = () => {
    const next: Record<string, string> = {};
    if (!form.diagnosis.trim()) next.diagnosis = 'El diagnóstico es obligatorio.';
    else if (form.diagnosis.trim().length > MAX_DIAGNOSIS) {
      next.diagnosis = 'Máximo 2000 caracteres.';
    }
    if (form.treatment_notes.trim().length > MAX_TREATMENT_NOTES) {
      next.treatment_notes = 'Máximo 3000 caracteres.';
    }
    form.items.forEach((it, i) => {
      if (!it.name.trim()) next[`item_${i}`] = 'El nombre del medicamento es obligatorio.';
    });
    form.treatments.forEach((t, i) => {
      if (!t.name.trim()) next[`treatment_${i}`] = 'El nombre del tratamiento es obligatorio.';
    });
    form.reminders.forEach((r, i) => {
      if (!r.title.trim()) next[`reminder_${i}`] = 'El título del recordatorio es obligatorio.';
    });
    setFieldErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    setError(null);

    try {
      const created = await createPrescription({
        consultation_id: consultation.id,
        pet_id: consultation.pet_id,
        veterinarian_id: consultation.veterinarian_id ?? undefined,
        diagnosis: form.diagnosis.trim(),
        treatment_notes: form.treatment_notes.trim() || undefined,
        items: form.items
          .map((it) => ({ name: it.name.trim(), dosage: it.dosage.trim() || undefined, frequency: it.frequency.trim() || undefined, duration: it.duration.trim() || undefined }))
          .filter((it) => it.name),
        treatments: form.treatments
          .map((t) => ({ name: t.name.trim(), instructions: t.instructions.trim() || undefined }))
          .filter((t) => t.name),
        reminders: form.reminders
          .map((r) => ({ title: r.title.trim(), due_at: r.due_at || undefined, note: r.note.trim() || undefined }))
          .filter((r) => r.title),
      });
      setCreatedId(created.id);
    } catch (err) {
      setError(getErrorMessage(err, 'No fue posible registrar la receta.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 py-8">
      <section className="rounded-[32px] border border-sandy-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.2em] text-teal">Receta clínica</p>
            <h1 className="text-3xl font-semibold text-slate-900">Registrar receta</h1>
            <p className="max-w-2xl text-sm text-slate-600">
              Consulta #{consultation.id} · Mascota #{consultation.pet_id} · Sucursal #{consultation.branch_id}
            </p>
          </div>
          <Button type="button" variant="outline" onClick={() => router.push('/portal/owner')}>
            Volver al portal
          </Button>
        </div>
      </section>

      {error ? <ErrorBanner message={error} /> : null}

      <Card className="p-6">
        <form noValidate onSubmit={handleSubmit} className="space-y-8">
          <div>
            <label htmlFor="diagnosis" className="mb-1 block text-sm font-medium text-slate-700">
              Diagnóstico *
            </label>
            <textarea
              id="diagnosis"
              rows={4}
              maxLength={MAX_DIAGNOSIS}
              value={form.diagnosis}
              onChange={(e) => {
                setForm((prev) => ({ ...prev, diagnosis: e.target.value }));
                if (fieldErrors.diagnosis) {
                  const next = { ...fieldErrors };
                  delete next.diagnosis;
                  setFieldErrors(next);
                }
              }}
              className={`w-full rounded-2xl border px-4 py-3 text-sm outline-none transition-colors focus:ring-2 focus:ring-teal ${
                fieldErrors.diagnosis ? 'border-red-400 bg-red-50' : 'border-sandy-300 bg-white'
              }`}
              aria-invalid={Boolean(fieldErrors.diagnosis)}
              aria-describedby={fieldErrors.diagnosis ? 'diagnosis-error' : undefined}
              disabled={submitting}
              placeholder="Diagnóstico principal de la consulta..."
            />
            <div className="mt-1 flex items-center justify-between text-xs text-slate-500">
              <span>{form.diagnosis.length}/{MAX_DIAGNOSIS}</span>
              {fieldErrors.diagnosis ? (
                <span id="diagnosis-error" role="alert" className="text-red-600">
                  {fieldErrors.diagnosis}
                </span>
              ) : null}
            </div>
          </div>

          <div>
            <label htmlFor="treatment_notes" className="mb-1 block text-sm font-medium text-slate-700">
              Notas de tratamiento
            </label>
            <textarea
              id="treatment_notes"
              rows={4}
              maxLength={MAX_TREATMENT_NOTES}
              value={form.treatment_notes}
              onChange={(e) => setForm((prev) => ({ ...prev, treatment_notes: e.target.value }))}
              className="w-full rounded-2xl border border-sandy-300 bg-white px-4 py-3 text-sm outline-none transition-colors focus:ring-2 focus:ring-teal"
              disabled={submitting}
              placeholder="Indicaciones generales de tratamiento (opcional)..."
            />
            <div className="mt-1 flex justify-between text-xs text-slate-500">
              <span>{form.treatment_notes.length}/{MAX_TREATMENT_NOTES}</span>
              {fieldErrors.treatment_notes ? (
                <span role="alert" className="text-red-600">
                  {fieldErrors.treatment_notes}
                </span>
              ) : null}
            </div>
          </div>

          <div>
            <div className="mb-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">Medicamentos</p>
                <p className="text-xs text-slate-500">Listado de medicamentos a recetar (opcional).</p>
              </div>
              <Button type="button" variant="outline" size="sm" onClick={addItem} disabled={submitting}>
                Agregar medicamento
              </Button>
            </div>

            {form.items.length === 0 ? (
              <p className="rounded-2xl border border-dashed border-sandy-300 bg-sandy-50 px-4 py-3 text-sm text-slate-500">
                Aún no hay medicamentos agregados.
              </p>
            ) : null}

            <div className="space-y-3">
              {form.items.map((item, index) => (
                <div key={index} className="grid gap-2 rounded-2xl border border-sandy-300 bg-sandy-50 p-4 md:grid-cols-5">
                  <div className="md:col-span-2">
                    <label className="mb-1 block text-xs text-slate-500">Nombre *</label>
                    <input
                      value={item.name}
                      onChange={(e) => setItem(index, { name: e.target.value })}
                      disabled={submitting}
                      className="w-full rounded-xl border border-sandy-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-teal"
                      placeholder="Amoxicilina 500 mg"
                    />
                    {fieldErrors[`item_${index}`] ? (
                      <p role="alert" className="mt-1 text-xs text-red-600">
                        {fieldErrors[`item_${index}`]}
                      </p>
                    ) : null}
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-slate-500">Dosis</label>
                    <input
                      value={item.dosage}
                      onChange={(e) => setItem(index, { dosage: e.target.value })}
                      disabled={submitting}
                      className="w-full rounded-xl border border-sandy-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-teal"
                      placeholder="1 tableta"
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-slate-500">Frecuencia</label>
                    <input
                      value={item.frequency}
                      onChange={(e) => setItem(index, { frequency: e.target.value })}
                      disabled={submitting}
                      className="w-full rounded-xl border border-sandy-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-teal"
                      placeholder="1 vez / 12h"
                    />
                  </div>
                  <div className="flex items-end gap-2">
                    <div className="flex-1">
                      <label className="mb-1 block text-xs text-slate-500">Duración</label>
                      <input
                        value={item.duration}
                        onChange={(e) => setItem(index, { duration: e.target.value })}
                        disabled={submitting}
                        className="w-full rounded-xl border border-sandy-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-teal"
                        placeholder="7 días"
                      />
                    </div>
                    <Button type="button" variant="outline" size="sm" onClick={() => removeItem(index)} disabled={submitting} aria-label="Quitar medicamento">
                      Quitar
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="mb-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">Tratamientos</p>
                <p className="text-xs text-slate-500">Procedimientos y cuidados adicionales (opcional).</p>
              </div>
              <Button type="button" variant="outline" size="sm" onClick={addTreatment} disabled={submitting}>
                Agregar tratamiento
              </Button>
            </div>
            {form.treatments.length === 0 ? (
              <p className="rounded-2xl border border-dashed border-sandy-300 bg-sandy-50 px-4 py-3 text-sm text-slate-500">
                Aún no hay tratamientos agregados.
              </p>
            ) : null}
            <div className="space-y-3">
              {form.treatments.map((t, index) => (
                <div key={index} className="grid gap-2 rounded-2xl border border-sandy-300 bg-sandy-50 p-4 md:grid-cols-3">
                  <div>
                    <label className="mb-1 block text-xs text-slate-500">Nombre *</label>
                    <input
                      value={t.name}
                      onChange={(e) => setTreatment(index, { name: e.target.value })}
                      disabled={submitting}
                      className="w-full rounded-xl border border-sandy-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-teal"
                      placeholder="Fisioterapia"
                    />
                    {fieldErrors[`treatment_${index}`] ? (
                      <p role="alert" className="mt-1 text-xs text-red-600">
                        {fieldErrors[`treatment_${index}`]}
                      </p>
                    ) : null}
                  </div>
                  <div className="md:col-span-1">
                    <label className="mb-1 block text-xs text-slate-500">Instrucciones</label>
                    <input
                      value={t.instructions}
                      onChange={(e) => setTreatment(index, { instructions: e.target.value })}
                      disabled={submitting}
                      className="w-full rounded-xl border border-sandy-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-teal"
                      placeholder="3 sesiones por semana"
                    />
                  </div>
                  <div className="flex items-end justify-end">
                    <Button type="button" variant="outline" size="sm" onClick={() => removeTreatment(index)} disabled={submitting} aria-label="Quitar tratamiento">
                      Quitar
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="mb-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">Recordatorios</p>
                <p className="text-xs text-slate-500">Seguimiento y controles a programar (opcional).</p>
              </div>
              <Button type="button" variant="outline" size="sm" onClick={addReminder} disabled={submitting}>
                Agregar recordatorio
              </Button>
            </div>
            {form.reminders.length === 0 ? (
              <p className="rounded-2xl border border-dashed border-sandy-300 bg-sandy-50 px-4 py-3 text-sm text-slate-500">
                Aún no hay recordatorios agregados.
              </p>
            ) : null}
            <div className="space-y-3">
              {form.reminders.map((r, index) => (
                <div key={index} className="grid gap-2 rounded-2xl border border-sandy-300 bg-sandy-50 p-4 md:grid-cols-4">
                  <div className="md:col-span-2">
                    <label className="mb-1 block text-xs text-slate-500">Título *</label>
                    <input
                      value={r.title}
                      onChange={(e) => setReminder(index, { title: e.target.value })}
                      disabled={submitting}
                      className="w-full rounded-xl border border-sandy-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-teal"
                      placeholder="Control a 7 días"
                    />
                    {fieldErrors[`reminder_${index}`] ? (
                      <p role="alert" className="mt-1 text-xs text-red-600">
                        {fieldErrors[`reminder_${index}`]}
                      </p>
                    ) : null}
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-slate-500">Vence</label>
                    <input
                      type="date"
                      value={r.due_at ? r.due_at.slice(0, 10) : ''}
                      onChange={(e) => setReminder(index, { due_at: e.target.value })}
                      disabled={submitting}
                      className="w-full rounded-xl border border-sandy-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-teal"
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <input
                      value={r.note}
                      onChange={(e) => setReminder(index, { note: e.target.value })}
                      disabled={submitting}
                      className="w-full rounded-xl border border-sandy-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-teal"
                      placeholder="Nota (opcional)"
                    />
                    <div className="flex justify-end">
                      <Button type="button" variant="outline" size="sm" onClick={() => removeReminder(index)} disabled={submitting} aria-label="Quitar recordatorio">
                        Quitar
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="outline" onClick={() => router.back()} disabled={submitting}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={submitting} disabled={submitting}>
              Registrar receta
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export default function CreatePrescriptionPage() {
  return (
    <Suspense fallback={<LoadingSpinner label="Cargando formulario de receta" />}>
      <CreatePrescriptionForm />
    </Suspense>
  );
}
