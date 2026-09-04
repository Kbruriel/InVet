/**
 * Definición de columnas para cada tipo de reporte (FE-015-T05).
 *
 * La tabla genérica (`ReportTable`) acepta `columns` y `rows` de tipo
 * `ReportColumn<Record<string, unknown>>[]`. Esta carpeta mapea el tipo de
 * reporte a las columnas concretas usadas en UI, y decide cómo normalizar
 * `data` del hook `useReports` a un array de filas homogéneo.
 */

import type { ReportColumn } from './components/ReportTable';
import type { PetCount, RatingsReport, ReportType } from './api';

/** Safely convert an unknown row value to a display string (or '—' for null/undefined). */
function s(value: unknown): string {
  return value == null ? '—' : String(value);
}

function formatEs(value: string | null | undefined): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('es-MX', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatMoney(value: number): string {
  // Los reportes devuelven monto en pesos (no en centavos) según backend.
  return value.toLocaleString('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 2,
  });
}

function formatBool(value: boolean): string {
  return value ? 'Activo' : 'Inactivo';
}

type RowRecord = Record<string, unknown>;

export interface ReportColumnSet {
  title: string;
  isAggregation: boolean;
  columns: ReportColumn<RowRecord>[];
  /** Extrae el array de filas desde `data` del hook useReports. */
  getRows: (data: unknown) => RowRecord[];
}

export function getReportColumns(type: ReportType | null): ReportColumnSet | null {
  switch (type) {
    case 'appointments':
      return {
        title: 'Citas médicas',
        isAggregation: false,
        getRows: (data: unknown) =>
          ((data as { items?: RowRecord[] } | null)?.items ?? []).map((r) => ({ ...r })),
        columns: [
          { key: 'pet_name', header: 'Mascota', render: (r) => s(r.pet_name) },
          { key: 'owner_name', header: 'Dueño', render: (r) => s(r.owner_name) },
          { key: 'veterinarian_name', header: 'Veterinario', render: (r) => s(r.veterinarian_name) },
          { key: 'appointment_type', header: 'Tipo', render: (r) => s(r.appointment_type) },
          { key: 'status', header: 'Estado', render: (r) => s(r.status) },
          { key: 'scheduled_start', header: 'Inicio', align: 'right', render: (r) => formatEs(r.scheduled_start as string | undefined) },
          { key: 'scheduled_end', header: 'Fin', align: 'right', render: (r) => formatEs(r.scheduled_end as string | undefined) },
        ],
      };
    case 'services':
      return {
        title: 'Servicios',
        isAggregation: false,
        getRows: (data: unknown) =>
          ((data as { items?: RowRecord[] } | null)?.items ?? []).map((r) => ({ ...r })),
        columns: [
          { key: 'name', header: 'Nombre', render: (r) => s(r.name) },
          { key: 'description', header: 'Descripción', render: (r) => s(r.description) },
          { key: 'price', header: 'Precio', align: 'right', render: (r) => formatMoney(Number(r.price)) },
          { key: 'duration_minutes', header: 'Duración', align: 'right', render: (r) => `${Number(r.duration_minutes ?? 0)} min` },
          { key: 'is_active', header: 'Activo', align: 'center', render: (r) => formatBool(Boolean(r.is_active)) },
        ],
      };
    case 'pets':
      return {
        title: 'Mascotas activas',
        isAggregation: true,
        getRows: (data: unknown) => {
          const d = (data as PetCount | null) ?? ({ clinic_id: 0, active_count: 0 } as PetCount);
          return [
            {
              clinic_id: d.clinic_id,
              active_count: d.active_count,
            },
          ];
        },
        columns: [
          { key: 'clinic_id', header: 'Clínica', render: (r) => String(r.clinic_id) },
          { key: 'active_count', header: 'Mascotas activas', align: 'center', render: (r) => String(r.active_count ?? 0) },
        ],
      };
    case 'consultations':
      return {
        title: 'Consultas',
        isAggregation: false,
        getRows: (data: unknown) =>
          ((data as { items?: RowRecord[] } | null)?.items ?? []).map((r) => ({ ...r })),
        columns: [
          { key: 'pet_name', header: 'Mascota', render: (r) => s(r.pet_name) },
          { key: 'veterinarian_name', header: 'Veterinario', render: (r) => s(r.veterinarian_name) },
          { key: 'diagnosis', header: 'Diagnóstico', render: (r) => s(r.diagnosis) },
          { key: 'recommendations', header: 'Recomendaciones', render: (r) => s(r.recommendations) },
        ],
      };
    case 'ratings':
      return {
        title: 'Calificaciones',
        isAggregation: true,
        getRows: (data: unknown) => {
          const d = (data as RatingsReport | null) ?? ({ by_veterinarian: [], clinic_avg: 0 } as RatingsReport);
          const vets: RowRecord[] = (d.by_veterinarian ?? []).map((v) => ({
            veterinarian_id: v.veterinarian_id,
            average_rating: v.average_rating,
            total_reviews: v.total_reviews,
          }));
          const totalReviews = vets.reduce((acc, row) => acc + (Number(row.total_reviews) || 0), 0);
          return [
            ...vets,
            { _synthetic: 'clinic_avg', veterinarian_id: null, average_rating: d.clinic_avg, total_reviews: totalReviews },
          ];
        },
        columns: [
          {
            key: '_row',
            header: 'Veterinario / Clínica',
            render: (r) =>
              (r as { _synthetic?: string })._synthetic === 'clinic_avg'
                ? 'Clínica (promedio)'
                : `Veterinario #${r.veterinarian_id != null ? r.veterinarian_id : '—'}`,
          },
          { key: 'average_rating', header: 'Promedio', align: 'center', render: (r) => Number(r.average_rating).toFixed(2) },
          { key: 'total_reviews', header: 'Opiniones', align: 'right', render: (r) => String(r.total_reviews ?? 0) },
        ],
      };
    case 'payments':
      return {
        title: 'Pagos',
        isAggregation: false,
        getRows: (data: unknown) =>
          ((data as { items?: RowRecord[] } | null)?.items ?? []).map((r) => ({ ...r })),
        columns: [
          { key: 'paid_at', header: 'Fecha', align: 'right', render: (r) => formatEs(r.paid_at as string | undefined) },
          { key: 'amount', header: 'Monto', align: 'right', render: (r) => formatMoney(Number(r.amount)) },
          { key: 'payment_method', header: 'Método', render: (r) => s(r.payment_method) },
          { key: 'status', header: 'Estado', render: (r) => s(r.status) },
          { key: 'appointment_id', header: 'Cita', align: 'right', render: (r) => (r.appointment_id != null ? String(r.appointment_id) : '—') },
        ],
      };
    default:
      return null;
  }
}
