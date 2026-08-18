/** Cliente API protegido para perfil de sucursal (FE-004) */

import { resolveApiBase } from './api-base';

const API_BASE = resolveApiBase();

export interface BranchProfileProtected {
  id: number;
  name: string;
  address: string | null;
  city: string | null;
  phone: string | null;
  description: string | null;
  logoUrl: string | null;
  services: Array<{
    id: number;
    name: string;
    price: number | null;
    active: boolean;
  }>;
  schedules: Array<{
    id: number;
    dayOfWeek: string;
    openTime: string;
    closeTime: string;
  }>;
  rating: {
    average: number;
    count: number;
  } | null;
  availability: {
    status: 'available' | 'unavailable' | 'full';
    availableSlots: number;
    totalSlots: number;
  } | null;
  additionalData?: Record<string, unknown>;
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function fetchBranchProtected(
  clinicId: number,
  branchId: number
): Promise<BranchProfileProtected> {
  const response = await fetch(
    `${API_BASE}/clinics/${clinicId}/branches/${branchId}`,
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    if (response.status === 401) {
      throw { status: 401, detail: 'No autorizado. Inicia sesión para acceder.' };
    }
    if (response.status === 403) {
      throw { status: 403, detail: 'No tienes permiso para acceder a esta sucursal.' };
    }
    if (response.status === 404) {
      throw { status: 404, detail: 'Sucursal no encontrada.' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al obtener perfil protegido' };
  }

  return response.json();
}
