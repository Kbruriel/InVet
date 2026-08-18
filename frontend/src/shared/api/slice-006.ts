/** Cliente API para slice 006 — Servicios, veterinarios y usuarios internos */

import { resolveApiBase } from './api-base';

const API_BASE = resolveApiBase();

/* ── Helpers ─────────────────────────────────────────────────────────────── */

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const token = getToken();
  const base: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) base['Authorization'] = `Bearer ${token}`;
  return { ...base, ...extra };
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const err = error as { detail?: string };
    throw { status: response.status, detail: err.detail || `HTTP ${response.status}` } as ApiError;
  }
  if (response.status === 204) return null as unknown as T;
  return response.json() as Promise<T>;
}

/* ── Types ───────────────────────────────────────────────────────────────── */

export interface ApiError {
  status: number;
  detail: string;
}

// Service
export interface ServiceCreateDTO {
  name: string;
  description?: string;
  price: number;
  duration_minutes: number;
  clinic_id: number;
}

export interface ServiceUpdateDTO {
  name?: string;
  description?: string;
  price?: number;
  duration_minutes?: number;
  is_active?: boolean;
}

export interface ServiceDTO {
  id: number;
  name: string;
  description: string | null;
  price: number;
  duration_minutes: number;
  clinic_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedServiceList {
  items: ServiceDTO[];
  total: number;
  page: number;
  size: number;
}

// Veterinarian
export interface VeterinarianCreateDTO {
  nombre_completo: string;
  licencia_profesional: string;
  especialidad: string;
  telefono?: string;
  email?: string;
  clinic_id: number;
}

export interface VeterinarianUpdateDTO {
  nombre_completo?: string;
  licencia_profesional?: string;
  especialidad?: string;
  telefono?: string;
  email?: string;
  is_active?: boolean;
}

export interface VeterinarianDTO {
  id: number;
  nombre_completo: string;
  licencia_profesional: string;
  especialidad: string;
  telefono: string | null;
  email: string | null;
  clinic_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedVeterinarianList {
  items: VeterinarianDTO[];
  total: number;
  page: number;
  size: number;
}

// Internal User
export interface InternalUserCreateDTO {
  user_id: number;
  nombre: string;
  rol: string;
  branch_ids?: number[];
  clinic_id: number;
}

export interface InternalUserUpdateDTO {
  nombre?: string;
  rol?: string;
  is_active?: boolean;
  branch_ids?: number[];
}

export interface InternalUserDTO {
  id: number;
  user_id: number;
  nombre: string;
  rol: string;
  clinic_id: number;
  is_active: boolean;
  branch_ids: number[];
  created_at: string;
  updated_at: string;
}

export interface PaginatedInternalUserList {
  items: InternalUserDTO[];
  total: number;
  page: number;
  size: number;
}

// Assignment
export interface AssignmentDTO {
  id: number;
  veterinarian_id: number;
  service_id: number;
  created_at: string;
}

/* ── Services CRUD ───────────────────────────────────────────────────────── */

export async function fetchServices(params?: {
  page?: number;
  size?: number;
  clinic_id?: number;
  is_active?: boolean;
}): Promise<PaginatedServiceList> {
  const query = new URLSearchParams();
  if (params?.page) query.set('page', String(params.page));
  if (params?.size) query.set('page_size', String(params.size));
  if (params?.clinic_id) query.set('clinic_id', String(params.clinic_id));
  if (params?.is_active !== undefined) query.set('is_active', String(params.is_active));

  const response = await fetch(`${API_BASE}/services?${query.toString()}`, {
    method: 'GET',
    headers: authHeaders(),
  });
  return parseResponse<PaginatedServiceList>(response);
}

export async function createService(payload: ServiceCreateDTO): Promise<ServiceDTO> {
  const response = await fetch(`${API_BASE}/services`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return parseResponse<ServiceDTO>(response);
}

export async function fetchService(id: number): Promise<ServiceDTO> {
  const response = await fetch(`${API_BASE}/services/${id}`, {
    method: 'GET',
    headers: authHeaders(),
  });
  return parseResponse<ServiceDTO>(response);
}

export async function updateService(id: number, payload: ServiceUpdateDTO): Promise<ServiceDTO> {
  const response = await fetch(`${API_BASE}/services/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return parseResponse<ServiceDTO>(response);
}

export async function deactivateService(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/services/${id}/deactivate`, {
    method: 'PATCH',
    headers: authHeaders(),
  });
  return parseResponse<void>(response);
}

/* ── Veterinarians CRUD ──────────────────────────────────────────────────── */

export async function fetchVeterinarians(params?: {
  page?: number;
  size?: number;
  clinic_id?: number;
  is_active?: boolean;
}): Promise<PaginatedVeterinarianList> {
  const query = new URLSearchParams();
  if (params?.page) query.set('page', String(params.page));
  if (params?.size) query.set('page_size', String(params.size));
  if (params?.clinic_id) query.set('clinic_id', String(params.clinic_id));
  if (params?.is_active !== undefined) query.set('is_active', String(params.is_active));

  const response = await fetch(`${API_BASE}/veterinarians?${query.toString()}`, {
    method: 'GET',
    headers: authHeaders(),
  });
  return parseResponse<PaginatedVeterinarianList>(response);
}

export async function createVeterinarian(payload: VeterinarianCreateDTO): Promise<VeterinarianDTO> {
  const response = await fetch(`${API_BASE}/veterinarians`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return parseResponse<VeterinarianDTO>(response);
}

export async function fetchVeterinarian(id: number): Promise<VeterinarianDTO> {
  const response = await fetch(`${API_BASE}/veterinarians/${id}`, {
    method: 'GET',
    headers: authHeaders(),
  });
  return parseResponse<VeterinarianDTO>(response);
}

export async function updateVeterinarian(id: number, payload: VeterinarianUpdateDTO): Promise<VeterinarianDTO> {
  const response = await fetch(`${API_BASE}/veterinarians/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return parseResponse<VeterinarianDTO>(response);
}

export async function deactivateVeterinarian(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/veterinarians/${id}/deactivate`, {
    method: 'PATCH',
    headers: authHeaders(),
  });
  return parseResponse<void>(response);
}

/* ── Internal Users CRUD ─────────────────────────────────────────────────── */

export async function fetchInternalUsers(params?: {
  page?: number;
  size?: number;
  clinic_id?: number;
  is_active?: boolean;
}): Promise<PaginatedInternalUserList> {
  const query = new URLSearchParams();
  if (params?.page) query.set('page', String(params.page));
  if (params?.size) query.set('page_size', String(params.size));
  if (params?.clinic_id) query.set('clinic_id', String(params.clinic_id));
  if (params?.is_active !== undefined) query.set('is_active', String(params.is_active));

  const response = await fetch(`${API_BASE}/internal-users?${query.toString()}`, {
    method: 'GET',
    headers: authHeaders(),
  });
  return parseResponse<PaginatedInternalUserList>(response);
}

export async function createInternalUser(payload: InternalUserCreateDTO): Promise<InternalUserDTO> {
  const response = await fetch(`${API_BASE}/internal-users`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return parseResponse<InternalUserDTO>(response);
}

export async function fetchInternalUser(id: number): Promise<InternalUserDTO> {
  const response = await fetch(`${API_BASE}/internal-users/${id}`, {
    method: 'GET',
    headers: authHeaders(),
  });
  return parseResponse<InternalUserDTO>(response);
}

export async function updateInternalUser(id: number, payload: InternalUserUpdateDTO): Promise<InternalUserDTO> {
  const response = await fetch(`${API_BASE}/internal-users/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return parseResponse<InternalUserDTO>(response);
}

export async function deactivateInternalUser(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/internal-users/${id}/deactivate`, {
    method: 'PATCH',
    headers: authHeaders(),
  });
  return parseResponse<void>(response);
}

/* ── Associations ────────────────────────────────────────────────────────── */

export async function assignServiceToVeterinarian(
  veterinarianId: number,
  serviceId: number
): Promise<AssignmentDTO> {
  const response = await fetch(`${API_BASE}/veterinarians/${veterinarianId}/assign-service`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ service_id: serviceId }),
  });
  return parseResponse<AssignmentDTO>(response);
}

export async function unassignServiceFromVeterinarian(
  veterinarianId: number,
  serviceId: number
): Promise<void> {
  const response = await fetch(
    `${API_BASE}/veterinarians/${veterinarianId}/assign-service/${serviceId}`,
    { method: 'DELETE', headers: authHeaders() }
  );
  return parseResponse<void>(response);
}

export async function assignBranchToInternalUser(
  internalUserId: number,
  branchId: number
): Promise<AssignmentDTO> {
  const response = await fetch(`${API_BASE}/internal-users/${internalUserId}/assign-branch`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ branch_id: branchId }),
  });
  return parseResponse<AssignmentDTO>(response);
}

export async function unassignBranchFromInternalUser(
  internalUserId: number,
  branchId: number
): Promise<void> {
  const response = await fetch(
    `${API_BASE}/internal-users/${internalUserId}/assign-branch/${branchId}`,
    { method: 'DELETE', headers: authHeaders() }
  );
  return parseResponse<void>(response);
}
