/** Cliente API para endpoints publicos (FE-003) */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// --- Clinics ---

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
}): Promise<PaginatedResponse<PublicClinic>> {
  const query = new URLSearchParams();
  if (params?.page) query.set('page', String(params.page));
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.search) query.set('search', params.search);

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

  return response.json();
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

  return response.json();
}

// --- Branches ---

export interface PublicBranch {
  id: number;
  name: string;
  address: string | null;
  city: string | null;
  phone: string | null;
}

export async function fetchPublicBranches(params?: {
  clinicaId?: number;
  search?: string;
}): Promise<PaginatedResponse<PublicBranch>> {
  const query = new URLSearchParams();
  if (params?.clinicaId) query.set('clinica_id', String(params.clinicaId));
  if (params?.search) query.set('search', params.search);

  const response = await fetch(`${API_BASE}/sucursales?${query.toString()}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 422) {
      throw { status: 422, detail: 'Parametros de filtro invalidos' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al listar sucursales' };
  }

  return response.json();
}

// --- Services ---

export interface PublicService {
  id: number;
  name: string;
  description: string | null;
  price: number | null;
  durationMinutes: number | null;
}

export async function fetchPublicServices(params?: {
  sucursalId?: number;
  clinicaId?: number;
}): Promise<PaginatedResponse<PublicService>> {
  const query = new URLSearchParams();
  if (params?.sucursalId) query.set('sucursal_id', String(params.sucursalId));
  if (params?.clinicaId) query.set('clinica_id', String(params.clinicaId));

  const response = await fetch(`${API_BASE}/servicios?${query.toString()}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 422) {
      throw { status: 422, detail: 'Parametros de filtro invalidos' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al listar servicios' };
  }

  return response.json();
}
