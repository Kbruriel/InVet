import { getAccessToken } from '@/shared/auth/session';

import { resolveApiBase } from './api-base';

const API_BASE = resolveApiBase();

export interface ApiError {
  status: number;
  detail: string;
}

export interface OwnerResponse {
  id: number;
  user_id: number;
  nombre: string;
  email: string;
  telefono: string | null;
  direccion: string | null;
  fecha_creacion: string;
}

export interface OwnerUpdateData {
  nombre?: string;
  email?: string;
  telefono?: string;
  direccion?: string;
}

export interface PetCreateData {
  nombre: string;
  especie: string;
  raza: string;
  edad: number;
  peso?: number;
  fecha_nacimiento?: string;
}

export interface PetUpdateData {
  nombre?: string;
  especie?: string;
  raza?: string;
  edad?: number;
  peso?: number;
  fecha_nacimiento?: string;
}

export interface PetResponse {
  id: number;
  owner_id: number;
  nombre: string;
  especie: string;
  raza: string;
  edad: number;
  peso: number | null;
  fecha_nacimiento: string | null;
}

export interface PetHistoryEntry {
  id: number;
  fecha?: string | null;
  motivo?: string | null;
  diagnostico?: string | null;
  veterinario?: string | null;
}

export interface PetHistoryResponse {
  items: PetHistoryEntry[];
  meta?: {
    page?: number;
    page_size?: number;
    total?: number;
  };
}

export interface PetListResponse {
  items: PetResponse[];
  meta: {
    page: number;
    page_size: number;
    size?: number;
    total: number;
    pages?: number;
  };
}

function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const token = getAccessToken();
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return { ...headers, ...extra };
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    const detail =
      typeof error === 'object' && error && 'detail' in error && typeof error.detail === 'string'
        ? error.detail
        : `HTTP ${response.status}`;

    throw { status: response.status, detail } as ApiError;
  }

  if (response.status === 204) {
    return null as unknown as T;
  }

  return response.json() as Promise<T>;
}

export async function getMyOwner(): Promise<OwnerResponse> {
  const response = await fetch(`${API_BASE}/owners/me`, {
    method: 'GET',
    headers: authHeaders(),
  });

  return parseResponse<OwnerResponse>(response);
}

export async function updateMyOwner(data: OwnerUpdateData): Promise<OwnerResponse> {
  const response = await fetch(`${API_BASE}/owners/me`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  return parseResponse<OwnerResponse>(response);
}

export async function getMyPets(page = 1, pageSize = 20): Promise<PetListResponse> {
  const query = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

  const response = await fetch(`${API_BASE}/owners/me/pets?${query.toString()}`, {
    method: 'GET',
    headers: authHeaders(),
  });

  const data = await parseResponse<PetListResponse>(response);
  return {
    ...data,
    meta: {
      ...data.meta,
      page_size: data.meta.page_size ?? data.meta.size ?? pageSize,
      pages:
        data.meta.pages ??
        Math.max(1, Math.ceil((data.meta.total || 0) / Math.max(data.meta.page_size || pageSize, 1))),
    },
  };
}

export async function createPet(data: PetCreateData): Promise<PetResponse> {
  const response = await fetch(`${API_BASE}/owners/me/pets`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  return parseResponse<PetResponse>(response);
}

export async function getPet(petId: number): Promise<PetResponse> {
  const response = await fetch(`${API_BASE}/pets/${petId}`, {
    method: 'GET',
    headers: authHeaders(),
  });

  return parseResponse<PetResponse>(response);
}

export async function updatePet(petId: number, data: PetUpdateData): Promise<PetResponse> {
  const response = await fetch(`${API_BASE}/pets/${petId}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  return parseResponse<PetResponse>(response);
}

export async function deletePet(petId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/pets/${petId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });

  await parseResponse<void>(response);
}

export async function getPetHistory(petId: number): Promise<PetHistoryResponse> {
  const response = await fetch(`${API_BASE}/pets/${petId}/history`, {
    method: 'GET',
    headers: authHeaders(),
  });

  return parseResponse<PetHistoryResponse>(response);
}
