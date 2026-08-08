/** Cliente API público para perfil de sucursal (FE-004) */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// --- DTOs del perfil público ---

export interface BranchService {
  id: number;
  name: string;
  description: string | null;
  price: number | null;
  durationMinutes: number | null;
  active: boolean;
}

export interface BranchSchedule {
  id: number;
  branchId: number;
  dayOfWeek: string;
  openTime: string;
  closeTime: string;
  isHoliday: boolean;
}

export interface RatingSummary {
  branchId: number;
  average: number;
  count: number;
  distribution: Record<string, number>;
}

export interface AvailabilitySummary {
  branchId: number;
  status: 'available' | 'unavailable' | 'full';
  availableSlots: number;
  totalSlots: number;
}

export interface BranchProfilePublic {
  id: number;
  name: string;
  address: string | null;
  city: string | null;
  phone: string | null;
  description: string | null;
  logoUrl: string | null;
  services: BranchService[];
  schedules: BranchSchedule[];
  rating: RatingSummary | null;
  availability: AvailabilitySummary | null;
}

// --- Fetchers públicos ---

export async function fetchBranchPublic(branchId: number): Promise<BranchProfilePublic> {
  const response = await fetch(`${API_BASE}/clinics/branches/${branchId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw { status: 404, detail: 'Sucursal no encontrada' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al obtener perfil de sucursal' };
  }

  return response.json();
}

export async function fetchBranchServices(branchId: number): Promise<BranchService[]> {
  const response = await fetch(`${API_BASE}/clinics/branches/${branchId}/services`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw { status: 404, detail: 'Servicios no encontrados para esta sucursal' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al listar servicios' };
  }

  return response.json();
}

export async function fetchBranchSchedules(branchId: number, date?: string): Promise<BranchSchedule[]> {
  const query = new URLSearchParams();
  if (date) query.set('date', date);

  const response = await fetch(`${API_BASE}/clinics/branches/${branchId}/schedules?${query.toString()}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 400) {
      throw { status: 400, detail: 'Fecha inválida' };
    }
    if (response.status === 404) {
      throw { status: 404, detail: 'Horarios no encontrados para esta sucursal' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al listar horarios' };
  }

  return response.json();
}

export async function fetchBranchRatingSummary(branchId: number): Promise<RatingSummary> {
  const response = await fetch(`${API_BASE}/clinics/branches/${branchId}/rating-summary`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw { status: 404, detail: 'Resumen de calificaciones no encontrado' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al obtener calificaciones' };
  }

  return response.json();
}

export async function fetchBranchAvailability(branchId: number): Promise<AvailabilitySummary> {
  const response = await fetch(`${API_BASE}/clinics/branches/${branchId}/availability`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw { status: 404, detail: 'Disponibilidad no encontrada para esta sucursal' };
    }
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw { status: response.status, detail: (error as { detail?: string }).detail || 'Error al obtener disponibilidad' };
  }

  return response.json();
}
