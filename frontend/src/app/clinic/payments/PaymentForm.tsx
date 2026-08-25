'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { listClinicAppointments } from '@/features/appointments/api';
import type { Appointment } from '@/features/appointments/types';
import { fetchServices } from '@/shared/api/slice-006';
import type { ServiceDTO } from '@/shared/api/slice-006';
import { createPayment } from '@/shared/api/payment';
import type { Payment, PaymentMethod } from '@/shared/api/payment';
import { Button } from '@/shared/ui/components';

interface PaymentFormState {
  appointmentId: string;
  serviceId: string;
  amount: string;
  method: string;
  amountReceived: string;
}

export interface PaymentFormProps {
  onCreated: (payment: Payment) => void;
}

const METHOD_OPTIONS: { value: PaymentMethod | ''; label: string }[] = [
  { value: '', label: 'Selecciona el método de pago' },
  { value: 'cash', label: 'Efectivo' },
  { value: 'transfer', label: 'Transferencia' },
  { value: 'card', label: 'Tarjeta' },
  { value: 'other', label: 'Otro' },
];

const APPOINTMENT_TYPE_LABELS: Record<string, string> = {
  consultation: 'Consulta',
  vaccination: 'Vacunación',
  surgery: 'Cirugía',
  follow_up: 'Seguimiento',
  emergency: 'Emergencia',
  other: 'Otro',
};

const INITIAL_FORM: PaymentFormState = {
  appointmentId: '',
  serviceId: '',
  amount: '',
  method: '',
  amountReceived: '',
};

function formatMoney(cents: number): string {
  return (cents / 100).toLocaleString('es-MX', {
    style: 'currency',
    currency: 'MXN',
  });
}

function formatAppointmentDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function isWholeNumber(value: string): boolean {
  return /^\d+$/.test(value.trim());
}

function buildAppointmentOption(appointment: Appointment): string {
  const typeLabel = APPOINTMENT_TYPE_LABELS[appointment.appointment_type] ?? appointment.appointment_type;
  const pet = appointment.pet_id ? ` · Mascota #${appointment.pet_id}` : '';
  return `#${appointment.id} · ${formatAppointmentDate(appointment.scheduled_start)} · ${typeLabel}${pet}`;
}

function buildServiceOption(service: ServiceDTO): string {
  if (typeof service.price === 'number' && Number.isFinite(service.price)) {
    return `${service.name} · $${service.price.toLocaleString('es-MX')} MXN`;
  }
  return service.name;
}

function validateForm(form: PaymentFormState): Record<string, string> {
  const errors: Record<string, string> = {};

  const appointmentId = Number(form.appointmentId);
  if (!form.appointmentId.trim() || !Number.isInteger(appointmentId) || appointmentId <= 0) {
    errors.appointment_id = 'Selecciona la cita asociada al pago.';
  }

  const serviceId = Number(form.serviceId);
  if (!form.serviceId.trim() || !Number.isInteger(serviceId) || serviceId <= 0) {
    errors.service_id = 'Selecciona el servicio cobrado.';
  }

  if (!form.amount.trim() || !isWholeNumber(form.amount)) {
    errors.amount = 'El importe debe ser un número de pesos (por ejemplo 100).';
  } else if (Number(form.amount) < 0) {
    errors.amount = 'El importe no puede ser negativo.';
  }

  const method = form.method as PaymentMethod;
  if (!METHOD_OPTIONS.some((option) => option.value === method)) {
    errors.method = 'Selecciona el método de pago.';
  }

  if (method === 'cash') {
    if (!form.amountReceived.trim() || !isWholeNumber(form.amountReceived)) {
      errors.amount_received = 'Con efectivo es obligatorio el importe recibido.';
    } else if (Number(form.amountReceived) < 0) {
      errors.amount_received = 'El importe recibido no puede ser negativo.';
    } else if (
      !errors.amount &&
      isWholeNumber(form.amount) &&
      Number(form.amountReceived) < Number(form.amount)
    ) {
      errors.amount_received = 'El importe recibido debe ser mayor o igual al importe del pago.';
    }
  }

  return errors;
}

export function PaymentForm({ onCreated }: PaymentFormProps) {
  const router = useRouter();

  const [form, setForm] = useState<PaymentFormState>(INITIAL_FORM);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [services, setServices] = useState<ServiceDTO[]>([]);
  const [appointmentsLoading, setAppointmentsLoading] = useState(true);
  const [servicesLoading, setServicesLoading] = useState(true);
  const [appointmentsError, setAppointmentsError] = useState<string | null>(null);
  const [servicesError, setServicesError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const loadOptions = () => {
    setAppointmentsLoading(true);
    setServicesLoading(true);
    setAppointmentsError(null);
    setServicesError(null);

    listClinicAppointments({ page: 1, page_size: 100 })
      .then((response) => {
        setAppointments(Array.isArray(response.items) ? response.items : []);
      })
      .catch((err: unknown) => {
        if (err && typeof err === 'object' && 'detail' in err && typeof (err as { detail?: unknown }).detail === 'string') {
          setAppointmentsError((err as { detail: string }).detail);
        } else {
          setAppointmentsError('No fue posible cargar las citas.');
        }
      })
      .finally(() => setAppointmentsLoading(false));

    fetchServices({ page: 1, size: 100, is_active: true })
      .then((response) => {
        setServices(Array.isArray(response.items) ? response.items : []);
      })
      .catch((err: unknown) => {
        if (err && typeof err === 'object' && 'detail' in err && typeof (err as { detail?: unknown }).detail === 'string') {
          setServicesError((err as { detail: string }).detail);
        } else {
          setServicesError('No fue posible cargar los servicios.');
        }
      })
      .finally(() => setServicesLoading(false));
  };

  useEffect(() => {
    loadOptions();
  }, []);

  const selectedService = services.find((service) => service.id === Number(form.serviceId));

  useEffect(() => {
    if (!selectedService) return;
    if (form.amount.trim() !== '') return;
    if (typeof selectedService.price !== 'number' || !Number.isFinite(selectedService.price)) return;
    if (selectedService.price < 0 || !Number.isInteger(selectedService.price)) return;
    setForm((prev) =>
      prev.amount.trim() === '' ? { ...prev, amount: String(selectedService.price) } : prev,
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.serviceId]);

  const isCash = form.method === 'cash';
  const amountCents = isWholeNumber(form.amount) ? Number(form.amount) * 100 : null;
  const receivedCents =
    isWholeNumber(form.amountReceived) ? Number(form.amountReceived) * 100 : null;
  const changeCents =
    isCash && amountCents !== null && receivedCents !== null && receivedCents >= amountCents
      ? receivedCents - amountCents
      : null;

  const updateField = (field: keyof PaymentFormState, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (fieldErrors[field]) {
      const next = { ...fieldErrors };
      delete next[field];
      setFieldErrors(next);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitError(null);

    const errors = validateForm(form);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSubmitting(true);
    try {
      const payment = await createPayment({
        appointment_id: Number(form.appointmentId),
        service_id: Number(form.serviceId),
        amount: Number(form.amount) * 100,
        method: form.method as PaymentMethod,
        amount_received: isCash ? Number(form.amountReceived) * 100 : null,
      });
      onCreated(payment);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'detail' in err && typeof (err as { detail?: unknown }).detail === 'string') {
        setSubmitError((err as { detail: string }).detail);
      } else {
        setSubmitError('No fue posible registrar el pago. Inténtalo nuevamente.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const selectFieldClasses = (hasError: boolean) =>
    `w-full rounded-2xl border px-4 py-3 text-sm outline-none transition-colors focus:ring-2 focus:ring-teal disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400 ${
      hasError ? 'border-red-400 bg-red-50' : 'border-sandy-300 bg-white'
    }`;

  const inputFieldClasses = (hasError: boolean) =>
    `w-full rounded-2xl border px-4 py-3 text-sm outline-none transition-colors focus:ring-2 focus:ring-teal ${
      hasError ? 'border-red-400 bg-red-50' : 'border-sandy-300 bg-white'
    }`;

  return (
    <CardWrapper>
      <form noValidate onSubmit={handleSubmit} className="space-y-8">
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <label htmlFor="appointment_id" className="mb-1 block text-sm font-medium text-slate-700">
              Cita asociada *
            </label>
            {appointmentsError ? (
              <p role="alert" className="mb-2 rounded-2xl border border-red-200 bg-red-50 px-4 py-2 text-xs text-red-700">
                {appointmentsError} Ingresa el ID de la cita manualmente.
              </p>
            ) : null}
            <select
              id="appointment_id"
              name="appointment_id"
               value={form.appointmentId}
               onChange={(event) => updateField('appointmentId', event.target.value)}
              disabled={appointmentsLoading || submitting}
              aria-invalid={Boolean(fieldErrors.appointment_id)}
              aria-describedby={fieldErrors.appointment_id ? 'appointment_id-error' : 'appointment_id-help'}
              className={selectFieldClasses(Boolean(fieldErrors.appointment_id))}
            >
              <option value="">
                {appointmentsLoading
                  ? 'Cargando citas...'
                  : appointments.length === 0
                    ? 'No hay citas disponibles'
                    : 'Selecciona la cita'}
              </option>
              {appointments.map((appointment) => (
                <option key={appointment.id} value={String(appointment.id)}>
                  {buildAppointmentOption(appointment)}
                </option>
              ))}
            </select>
            <div id="appointment_id-help" className="mt-1 text-xs text-slate-500">
              Si la lista no carga, escribe el ID numérico de la cita.
            </div>
            {fieldErrors.appointment_id ? (
              <p id="appointment_id-error" role="alert" className="mt-1 text-xs text-red-600">
                {fieldErrors.appointment_id}
              </p>
            ) : null}
          </div>

          <div>
            <label htmlFor="service_id" className="mb-1 block text-sm font-medium text-slate-700">
              Servicio cobrado *
            </label>
            {servicesError ? (
              <p role="alert" className="mb-2 rounded-2xl border border-red-200 bg-red-50 px-4 py-2 text-xs text-red-700">
                {servicesError} Ingresa el ID del servicio manualmente.
              </p>
            ) : null}
            <select
              id="service_id"
              name="service_id"
               value={form.serviceId}
               onChange={(event) => updateField('serviceId', event.target.value)}
              disabled={servicesLoading || submitting}
              aria-invalid={Boolean(fieldErrors.service_id)}
              aria-describedby={fieldErrors.service_id ? 'service_id-error' : 'service_id-help'}
              className={selectFieldClasses(Boolean(fieldErrors.service_id))}
            >
              <option value="">
                {servicesLoading
                  ? 'Cargando servicios...'
                  : services.length === 0
                    ? 'No hay servicios disponibles'
                    : 'Selecciona el servicio'}
              </option>
              {services.map((service) => (
                <option key={service.id} value={String(service.id)}>
                  {buildServiceOption(service)}
                </option>
              ))}
            </select>
            <div id="service_id-help" className="mt-1 text-xs text-slate-500">
              Selecciona el servicio para prellenar el importe.
            </div>
            {fieldErrors.service_id ? (
              <p id="service_id-error" role="alert" className="mt-1 text-xs text-red-600">
                {fieldErrors.service_id}
              </p>
            ) : null}
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <label htmlFor="amount" className="mb-1 block text-sm font-medium text-slate-700">
              Importe del pago (MXN) *
            </label>
            <input
              id="amount"
              name="amount"
              type="text"
              inputMode="decimal"
              value={form.amount}
              onChange={(event) => updateField('amount', event.target.value)}
              disabled={submitting}
              placeholder="Ej. 100"
              aria-invalid={Boolean(fieldErrors.amount)}
              aria-describedby={fieldErrors.amount ? 'amount-error' : 'amount-help'}
              className={inputFieldClasses(Boolean(fieldErrors.amount))}
            />
            <div id="amount-help" className="mt-1 text-xs text-slate-500">
              Importe en pesos (monto total a cobrar).
            </div>
            {fieldErrors.amount ? (
              <p id="amount-error" role="alert" className="mt-1 text-xs text-red-600">
                {fieldErrors.amount}
              </p>
            ) : null}
          </div>

          <div>
            <label htmlFor="method" className="mb-1 block text-sm font-medium text-slate-700">
              Método de pago *
            </label>
            <select
              id="method"
              name="method"
              value={form.method}
              onChange={(event) => updateField('method', event.target.value)}
              disabled={submitting}
              aria-invalid={Boolean(fieldErrors.method)}
              aria-describedby={fieldErrors.method ? 'method-error' : undefined}
              className={selectFieldClasses(Boolean(fieldErrors.method))}
            >
              {METHOD_OPTIONS.map((option) => (
                <option key={option.value || 'placeholder'} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {fieldErrors.method ? (
              <p id="method-error" role="alert" className="mt-1 text-xs text-red-600">
                {fieldErrors.method}
              </p>
            ) : null}
          </div>
        </div>

        {isCash ? (
          <div className="space-y-3 rounded-2xl border border-sandy-300 bg-sandy-100 p-5">
            <div>
              <label htmlFor="amount_received" className="mb-1 block text-sm font-medium text-slate-700">
                Importe recibido (MXN) *
              </label>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <input
                  id="amount_received"
                  name="amount_received"
                  type="text"
                  inputMode="decimal"
                  value={form.amountReceived}
                  onChange={(event) => updateField('amountReceived', event.target.value)}
                  disabled={submitting}
                  placeholder="Ej. 150"
                  aria-invalid={Boolean(fieldErrors.amount_received)}
                  aria-describedby={
                    fieldErrors.amount_received ? 'amount_received-error' : 'amount_received-help'
                  }
                  className={inputFieldClasses(Boolean(fieldErrors.amount_received))}
                />
                {changeCents !== null ? (
                  <p className="rounded-xl bg-white px-4 py-3 text-sm font-medium text-teal-dark">
                    Cambio: {formatMoney(changeCents)}
                  </p>
                ) : null}
                {changeCents === null && (receivedCents !== null && amountCents !== null && receivedCents < amountCents) ? (
                  <p className="rounded-xl bg-white px-4 py-3 text-sm font-medium text-red-600">
                    El importe recibido es menor que el pago.
                  </p>
                ) : null}
              </div>
              <div id="amount_received-help" className="mt-1 text-xs text-slate-500">
                Cantidad que entrega el cliente, en pesos. El cambio se calcula en vivo.
              </div>
              {fieldErrors.amount_received ? (
                <p id="amount_received-error" role="alert" className="mt-1 text-xs text-red-600">
                  {fieldErrors.amount_received}
                </p>
              ) : null}
            </div>
          </div>
        ) : null}

        {submitError ? (
          <p role="alert" className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {submitError}
          </p>
        ) : null}

        <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <Button type="button" variant="outline" onClick={() => router.push('/clinic/appointments')} disabled={submitting}>
            Volver a citas
          </Button>
          <Button type="submit" size="lg" isLoading={submitting}>
            Registrar pago
          </Button>
        </div>
      </form>
    </CardWrapper>
  );
}

function CardWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-[32px] border border-sandy-300 bg-white p-6 shadow-sm">
      {children}
    </div>
  );
}
