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
  const response = await apiClient.get(`${BASE_PATH}/${appointmentId}`);
  return response.json();
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

  const response = await apiClient.get(`${BASE_PATH}?my_appointments=true&${queryParams}`);
  return response.json();
}

/**
 * Listar citas de la clínica (para staff/clinica).
 */
export async function listClinicAppointments(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  branch_id?: number;
  vet_id?: number;
}): Promise<AppointmentListResponse> {
  const queryParams = new URLSearchParams();
  if (params?.page) queryParams.set('page', String(params.page));
  if (params?.page_size) queryParams.set('page_size', String(params.page_size));
  if (params?.status) queryParams.set('status', params.status);
  if (params?.branch_id) queryParams.set('branch_id', String(params.branch_id));
  if (params?.vet_id) queryParams.set('vet_id', String(params.vet_id));

  const response = await apiClient.get(`${BASE_PATH}?${queryParams}`);
  return response.json();
}

/**
 * Crear una nueva cita.
 */
export async function createAppointment(data: AppointmentCreate): Promise<Appointment> {
  const response = await apiClient.post(BASE_PATH, data);
  return response.json();
}

/**
 * Actualizar campos parciales de una cita.
 */
export async function updateAppointment(
  appointmentId: number,
  data: Partial<AppointmentCreate>
): Promise<Appointment> {
  const response = await apiClient.put(`${BASE_PATH}/${appointmentId}`, data);
  return response.json();
}

/**
 * Transicionar el estado de una cita.
 */
export async function transitionStatus(
  appointmentId: number,
  data: StatusTransition
): Promise<Appointment> {
  const response = await apiClient.post(`${BASE_PATH}/${appointmentId}/status`, data);
  return response.json();
}

/**
 * Cancelar una cita (DELETE o PUT con action=cancel).
 */
export async function cancelAppointment(appointmentId: number): Promise<Appointment> {
  const response = await apiClient.delete(`${BASE_PATH}/${appointmentId}`);
  return response.json();
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

  const response = await apiClient.get(`${BASE_PATH}/availability?${queryParams}`);
  return response.json();
}
