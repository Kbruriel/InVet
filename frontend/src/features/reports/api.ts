/**
 * Cliente API tipado para reportes operativos (FE-015-T01 / BE-015).
 *
 * Centraliza las seis llamadas HTTP del slice y exporta los tipos TypeScript
 * para cada respuesta. El `clinic_id` nunca se envía por query: el backend lo
 * deriva del JWT (get_current_access_user) para garantizar tenant isolation.
 */

import { apiClient } from '@/shared/api/client';

const BASE_PATH = '/reports';

/** Tipos de reporte soportados por la UI. */
export type ReportType =
  | 'appointments'
  | 'services'
  | 'pets'
  | 'consultations'
  | 'ratings'
  | 'payments';

/** Opciones de filtro comunes a todos los reportes. */
export interface ReportFilters {
  /** Fecha inicio del periodo, formato YYYY-MM-DD. Opcional. */
  period_start?: string | null;
  /** Fecha fin del periodo, formato YYYY-MM-DD. Opcional. */
  period_end?: string | null;
  /** Página 1-indexada (solo reportes paginados). */
  page?: number;
  /** Tamaño de página (1..100). Solo reportes paginados. */
  size?: number;
}

// ---------------------------------------------------------------------------
// DTOs alineados con backend/app/api/v1/schemas/report_schemas.py
// ---------------------------------------------------------------------------

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export interface AppointmentSummary {
  id: number;
  clinic_id: number;
  pet_name: string | null;
  owner_name: string | null;
  veterinarian_name: string | null;
  appointment_type: string;
  status: string;
  scheduled_start: string;
  scheduled_end: string;
}

export interface ServiceSummary {
  id: number;
  clinic_id: number;
  name: string;
  description: string | null;
  price: number;
  duration_minutes: number;
  is_active: boolean;
}

export interface PetCount {
  clinic_id: number;
  active_count: number;
}

export interface ConsultationSummary {
  id: number;
  clinic_id: number;
  pet_name: string | null;
  veterinarian_name: string | null;
  diagnosis: string | null;
  history: string | null;
  recommendations: string | null;
}

export interface RatingSummary {
  veterinarian_id: number | null;
  average_rating: number;
  total_reviews: number;
}

export interface RatingsReport {
  by_veterinarian: RatingSummary[];
  clinic_avg: number;
}

export interface PaymentSummary {
  id: number;
  clinic_id: number;
  appointment_id: number | null;
  service_id: number | null;
  amount: number;
  payment_method: string;
  status: string;
  paid_at: string;
}

export interface PaymentsReport {
  items: PaymentSummary[];
  total: number;
  page: number;
  size: number;
  total_amount: number;
}

// ---------------------------------------------------------------------------
// Helpers internos
// ---------------------------------------------------------------------------

function buildQuery(filters: ReportFilters): string {
  const params = new URLSearchParams();
  if (filters.period_start) params.set('period_start', filters.period_start);
  if (filters.period_end) params.set('period_end', filters.period_end);
  if (filters.page) params.set('page', String(filters.page));
  if (filters.size) params.set('size', String(filters.size));
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

// ---------------------------------------------------------------------------
// Funciones tipadas por endpoint
// ---------------------------------------------------------------------------

export async function listAppointmentsReport(
  filters: ReportFilters = {},
): Promise<Paginated<AppointmentSummary>> {
  return apiClient.get<Paginated<AppointmentSummary>>(
    `${BASE_PATH}/appointments${buildQuery(filters)}`,
  );
}

export async function listServicesReport(
  filters: ReportFilters = {},
): Promise<Paginated<ServiceSummary>> {
  return apiClient.get<Paginated<ServiceSummary>>(
    `${BASE_PATH}/services${buildQuery(filters)}`,
  );
}

export async function getPetsCountReport(
  filters: ReportFilters = {},
): Promise<PetCount> {
  return apiClient.get<PetCount>(`${BASE_PATH}/pets${buildQuery(filters)}`);
}

export async function listConsultationsReport(
  filters: ReportFilters = {},
): Promise<Paginated<ConsultationSummary>> {
  return apiClient.get<Paginated<ConsultationSummary>>(
    `${BASE_PATH}/consultations${buildQuery(filters)}`,
  );
}

export async function listRatingsReport(
  filters: ReportFilters = {},
): Promise<RatingsReport> {
  return apiClient.get<RatingsReport>(`${BASE_PATH}/ratings${buildQuery(filters)}`);
}

export async function listPaymentsReport(
  filters: ReportFilters = {},
): Promise<PaymentsReport> {
  return apiClient.get<PaymentsReport>(`${BASE_PATH}/payments${buildQuery(filters)}`);
}
