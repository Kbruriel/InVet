/** Cliente API para la pagina publica de clinicas (FE-003). */

import { resolveApiBase } from './api-base';

const API_BASE = resolveApiBase();

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

type BackendPaginatedResponse<T> = {
  data?: T[];
  items?: T[];
  pagination?: {
    page?: number;
    size?: number;
    limit?: number;
    total?: number;
    total_pages?: number;
    totalPages?: number;
  };
  page?: number;
  limit?: number;
  total?: number;
  totalPages?: number;
};

function normalizeClinicResponse<T>(payload: BackendPaginatedResponse<T>): PaginatedResponse<T> {
  if (Array.isArray(payload.items)) {
    const limit = payload.limit ?? payload.items.length;
    const total = payload.total ?? payload.items.length;
    return {
      items: payload.items,
      total,
      page: payload.page ?? 1,
      limit,
      totalPages: payload.totalPages ?? (limit > 0 ? Math.ceil(total / limit) : 0),
    };
  }

  if (Array.isArray(payload.data)) {
    const pagination = payload.pagination ?? {};
    const limit = pagination.size ?? pagination.limit ?? payload.limit ?? payload.data.length;
    const total = pagination.total ?? payload.total ?? payload.data.length;
    return {
      items: payload.data,
      total,
      page: pagination.page ?? payload.page ?? 1,
      limit,
      totalPages:
        pagination.total_pages ??
        pagination.totalPages ??
        payload.totalPages ??
        (limit > 0 ? Math.ceil(total / limit) : 0),
    };
  }

  return {
    items: [],
    total: 0,
    page: 1,
    limit: 0,
    totalPages: 0,
  };
}

function normalizePublicClinic<T extends Partial<PublicClinic>>(clinic: T): PublicClinic {
  return {
    logoUrl: null,
    rating: null,
    description: null,
    address: null,
    city: null,
    ...clinic,
  } as PublicClinic;
}

export interface PublicClinic {
  id: number;
  name: string;
  description: string | null;
  address: string | null;
  city: string | null;
  logoUrl: string | null;
  rating: number | null;
}

export async function fetchPublicClinics(params?: {
  page?: number;
  limit?: number;
  search?: string;
  category?: string;
  serviceType?: string;
}): Promise<PaginatedResponse<PublicClinic>> {
  const query = new URLSearchParams();
  if (params?.page) query.set('page', String(params.page));
  if (params?.limit) {
    query.set('limit', String(params.limit));
    query.set('size', String(params.limit));
  }
  if (params?.search) query.set('search', params.search);
  const serviceType = params?.serviceType || params?.category;
  if (serviceType) query.set('service_type', serviceType);

  const response = await fetch(`${API_BASE}/clinicas?${query.toString()}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 422) {
      throw { status: 422, detail: 'Parametros de consulta invalidos' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al listar clinicas' };
  }

  const payload = (await response.json()) as BackendPaginatedResponse<PublicClinic>;
  const normalized = normalizeClinicResponse(payload);
  return {
    ...normalized,
    items: normalized.items.map(normalizePublicClinic),
  };
}

export async function fetchPublicClinicDetail(id: number): Promise<PublicClinic> {
  const response = await fetch(`${API_BASE}/clinicas/${id}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw { status: 404, detail: 'Clinica no encontrada' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al obtener detalle de clinica' };
  }

  const payload = (await response.json()) as Partial<PublicClinic>;
  return normalizePublicClinic(payload);
}
