/**
 * FilterBar de reportes (FE-015-T03 / BE-015).
 *
 * Expone:
 * - Selector de tipo de reporte (6 opciones).
 * - Dos inputs de fecha (period_start / period_end), ambos opcionales.
 * - Botón "Aplicar" que dispara `onApply(type, filters)` SOLO si la validación
 *   pasa. Rechaza period_start > period_end antes de enviar.
 */

'use client';

import { useState, type FormEvent } from 'react';
import { Button } from '@/shared/ui/components';
import type { ReportType } from '../api';

export interface FilterBarProps {
  /** Callback de aplicación de filtros (el hook/página decide la petición). */
  onApply: (
    type: ReportType,
    filters: { period_start?: string; period_end?: string },
  ) => void;
  disabled?: boolean;
  initialValue?: ReportType;
  loading?: boolean;
}

export interface ReportTypeOption {
  value: ReportType;
  label: string;
}

export const REPORT_TYPE_OPTIONS: ReportTypeOption[] = [
  { value: 'appointments', label: 'Citas médicas' },
  { value: 'services', label: 'Servicios' },
  { value: 'pets', label: 'Mascotas activas' },
  { value: 'consultations', label: 'Consultas' },
  { value: 'ratings', label: 'Calificaciones' },
  { value: 'payments', label: 'Pagos' },
];

export function FilterBar({
  onApply,
  disabled,
  initialValue = 'appointments',
  loading = false,
}: FilterBarProps) {
  const [type, setType] = useState<ReportType>(initialValue);
  const [periodStart, setPeriodStart] = useState<string>('');
  const [periodEnd, setPeriodEnd] = useState<string>('');
  const [validationError, setValidationError] = useState<string | null>(null);

  function clearError() {
    setValidationError(null);
  }

  function validate(): string | null {
    const a = periodStart || null;
    const b = periodEnd || null;
    if (a && b && a > b) {
      return 'period_start no puede ser posterior a period_end.';
    }
    return null;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError();
    const err = validate();
    if (err) {
      setValidationError(err);
      return;
    }
    onApply(type, {
      period_start: periodStart || undefined,
      period_end: periodEnd || undefined,
    });
  }

  function handleReset() {
    setPeriodStart('');
    setPeriodEnd('');
    clearError();
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="grid gap-4 rounded-[32px] border border-sandy-300 bg-white p-6 sm:grid-cols-2 md:grid-cols-4"
      role="search"
      aria-label="Filtros de reportes"
    >
      <div>
        <label
          htmlFor="report-type"
          className="mb-1 block text-sm font-medium text-slate-700"
        >
          Tipo de reporte
        </label>
        <select
          id="report-type"
          name="report-type"
          value={type}
          onChange={(event) => {
            setType(event.target.value as ReportType);
            clearError();
          }}
          disabled={disabled}
          className={`w-full appearance-none rounded-[18px] border bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-teal ${
            validationError ? 'border-red-400' : 'border-sandy-300'
          }`}
        >
          {REPORT_TYPE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label
          htmlFor="period-start"
          className="mb-1 block text-sm font-medium text-slate-700"
        >
          Desde
        </label>
        <input
          id="period-start"
          name="period_start"
          type="date"
          value={periodStart}
          max={periodEnd || undefined}
          onChange={(event) => {
            setPeriodStart(event.target.value);
            clearError();
          }}
          disabled={disabled}
          className="w-full rounded-[18px] border border-sandy-300 bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-teal"
        />
      </div>

      <div>
        <label
          htmlFor="period-end"
          className="mb-1 block text-sm font-medium text-slate-700"
        >
          Hasta
        </label>
        <input
          id="period-end"
          name="period_end"
          type="date"
          value={periodEnd}
          min={periodStart || undefined}
          onChange={(event) => {
            setPeriodEnd(event.target.value);
            clearError();
          }}
          disabled={disabled}
          className={`w-full rounded-[18px] border bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-teal ${
            validationError ? 'border-red-400' : 'border-sandy-300'
          }`}
        />
      </div>

      <div className="flex items-end gap-2 sm:col-span-2 md:col-span-4">
        <Button type="submit" disabled={disabled} isLoading={loading}>
          Aplicar
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={handleReset}
          disabled={disabled || loading}
        >
          Restaurar
        </Button>
      </div>

      {validationError && (
        <div
          role="alert"
          className="sm:col-span-2 md:col-span-4 -mt-2 rounded-[18px] bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
        >
          {validationError}
        </div>
      )}
    </form>
  );
}
