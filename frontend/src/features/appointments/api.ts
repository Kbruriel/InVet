/**
 * Cliente API tipado para citas (FE-008).
 * Centraliza el consumo de endpoints /api/v1/appointments
 */

import { apiClient } from '@/shared/api/client';
import type {
  Appointment,
  AppointmentCreate,
  AppointmentListResponse,
  AvailabilityResponse,
  StatusTransition,
} from './types';

const BASE_PATH = '/api/v1/appointments';

/**
 * Obtener una cita por ID con tenant isolation.
 */
export async function getAppointment(appointmentId: number): Promise<Appointment> {
  return apiClient.get<Appointment>(`${BASE_PATH}/${appointmentId}`);
}

/**
 * Listar citas propias del propietario autenticado.
 */
export async function listMyAppointments(params?: {
  page?: number;
  page_size?: number;
  status?: string;
}): Promise<AppointmentListResponse> {
  const queryParams = new URLSearchParams();
  if (params?.page) queryParams.set('page', String(params.page));
  if (params?.page_size) queryParams.set('page_size', String(params.page_size));
  if (params?.status) queryParams.set('status', params.status);

  return apiClient.get<AppointmentListResponse>(`${BASE_PATH}?my_appointments=true&${queryParams}`);
}

/**
 * Listar citas de la clínica (para staff/clinica).
 */
export async function listClinicAppointments(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  clinic_id?: number;
  branch_id?: number;
  veterinarian_id?: number;
  vet_id?: number;
  date_from?: string;
  date_to?: string;
}): Promise<AppointmentListResponse> {
  const queryParams = new URLSearchParams();
  if (params?.page) queryParams.set('page', String(params.page));
  if (params?.page_size) queryParams.set('page_size', String(params.page_size));
  if (params?.status) queryParams.set('status', params.status);
  if (params?.clinic_id) queryParams.set('clinic_id', String(params.clinic_id));
  if (params?.branch_id) queryParams.set('branch_id', String(params.branch_id));
  if (params?.veterinarian_id) queryParams.set('veterinarian_id', String(params.veterinarian_id));
  if (params?.vet_id) queryParams.set('vet_id', String(params.vet_id));
  if (params?.date_from) queryParams.set('date_from', params.date_from);
  if (params?.date_to) queryParams.set('date_to', params.date_to);

  return apiClient.get<AppointmentListResponse>(`${BASE_PATH}?${queryParams}`);
}

/**
 * Crear una nueva cita.
 */
export async function createAppointment(data: AppointmentCreate): Promise<Appointment> {
  return apiClient.post<Appointment>(BASE_PATH, data);
}

/**
 * Actualizar campos parciales de una cita.
 */
export async function updateAppointment(
  appointmentId: number,
  data: Partial<AppointmentCreate>
): Promise<Appointment> {
  return apiClient.put<Appointment>(`${BASE_PATH}/${appointmentId}`, data);
}

/**
 * Transicionar el estado de una cita.
 */
export async function transitionStatus(
  appointmentId: number,
  data: StatusTransition
): Promise<Appointment> {
  return apiClient.post<Appointment>(`${BASE_PATH}/${appointmentId}/status`, data);
}

/**
 * Cancelar una cita (DELETE o PUT con action=cancel).
 */
export async function cancelAppointment(appointmentId: number): Promise<Appointment> {
  return apiClient.delete<Appointment>(`${BASE_PATH}/${appointmentId}`);
}

/**
 * Obtener slots disponibles por fecha.
 */
export async function getAvailability(params: {
  date: string;
  vet_id?: number | null;
  clinic_id?: number;
  branch_id?: number | null;
}): Promise<AvailabilityResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set('date', params.date);
  if (params.vet_id) queryParams.set('vet_id', String(params.vet_id));
  if (params.clinic_id) queryParams.set('clinic_id', String(params.clinic_id));
  if (params.branch_id) queryParams.set('branch_id', String(params.branch_id));

  return apiClient.get<AvailabilityResponse>(`${BASE_PATH}/availability?${queryParams}`);
}
