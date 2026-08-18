/** Cliente API para administracion de clinicas (FE-005) */

import { resolveApiBase } from './api-base';

const API_BASE = resolveApiBase();

export interface ClinicCreatePayload {
  name: string;
  description?: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  phone?: string;
  email?: string;
}

export interface ClinicUpdatePayload {
  name?: string;
  description?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  phone?: string;
  email?: string;
}

export interface ClinicStatusPayload {
  active: boolean;
}

export interface ClinicRead {
  id: number;
  name: string;
  description: string | null;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  phone: string | null;
  email: string | null;
  is_active: boolean;
}

export interface ClinicListResponse {
  items: ClinicRead[];
  total: number;
  page: number;
  size: number;
}

export interface ApiError {
  status: number;
  detail: string;
}

/** Obtener token de localStorage */
function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/** Construir headers con auth */
function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const token = getToken();
  const base: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) base['Authorization'] = `Bearer ${token}`;
  return { ...base, ...extra };
}

/** Parsear respuesta con manejo de errores */
async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const err = error as { detail?: string };
    throw { status: response.status, detail: err.detail || `HTTP ${response.status}` } as ApiError;
  }
  return response.json() as Promise<T>;
}

// --- Clinicas CRUD ---

export async function fetchClinics(params?: { page?: number; size?: number }): Promise<ClinicListResponse> {
  const query = new URLSearchParams();
  if (params?.page) query.set('page', String(params.page));
  if (params?.size) query.set('size', String(params.size));

  const response = await fetch(`${API_BASE}/clinics?${query.toString()}`, {
    method: 'GET',
    headers: authHeaders(),
  });

  return parseResponse<ClinicListResponse>(response);
}

export async function createClinic(payload: ClinicCreatePayload): Promise<ClinicRead> {
  const response = await fetch(`${API_BASE}/clinics`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  return parseResponse<ClinicRead>(response);
}

export async function updateClinic(clinicId: number, payload: ClinicUpdatePayload): Promise<ClinicRead> {
  const response = await fetch(`${API_BASE}/clinics/${clinicId}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  return parseResponse<ClinicRead>(response);
}

export async function changeClinicStatus(clinicId: number, payload: ClinicStatusPayload): Promise<ClinicRead> {
  const response = await fetch(`${API_BASE}/clinics/${clinicId}/status`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  return parseResponse<ClinicRead>(response);
}

export async function getClinic(clinicId: number): Promise<ClinicRead> {
  const response = await fetch(`${API_BASE}/clinics/${clinicId}`, {
    method: 'GET',
    headers: authHeaders(),
  });

  return parseResponse<ClinicRead>(response);
}
