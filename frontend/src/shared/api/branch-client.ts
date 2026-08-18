/** Cliente API público para perfil de sucursal (FE-004) */

import { resolveApiBase } from './api-base';

const API_BASE = resolveApiBase();

type BackendBranchService = {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
};

type BackendBranchSchedule = {
  id: number;
  day_of_week: number;
  open_time: string;
  close_time: string;
  is_active: boolean;
};

type BackendRatingSummary = {
  average_rating: number;
  total_reviews: number;
  review_distribution: string | null;
};

type BackendAvailabilitySummary = {
  is_available: boolean;
  next_available_time: string | null;
  availability_type: string | null;
};

type BackendBranchProfile = {
  id: number;
  clinic_id: number;
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
  services: BackendBranchService[];
  schedules: BackendBranchSchedule[];
  rating_summary: BackendRatingSummary | null;
  availability_summary: BackendAvailabilitySummary | null;
  logo_url?: string | null;
  logoUrl?: string | null;
};

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

function mapDayOfWeek(value: number): string {
  const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  return days[value] || String(value);
}

function mapBranchService(service: BackendBranchService): BranchService {
  return {
    id: service.id,
    name: service.name,
    description: service.description,
    price: null,
    durationMinutes: null,
    active: service.is_active,
  };
}

function parseReviewDistribution(raw: string | Record<string, number> | null): Record<string, number> {
  if (!raw) return {};
  if (typeof raw === 'object') return raw;
  try {
    return JSON.parse(raw) as Record<string, number>;
  } catch {
    return {};
  }
}

function mapRatingSummary(
  summary: BackendRatingSummary | null,
  branchId: number,
): RatingSummary | null {
  if (!summary) return null;

  return {
    branchId,
    average: summary.average_rating,
    count: summary.total_reviews,
    distribution: parseReviewDistribution(summary.review_distribution),
  };
}

function mapAvailabilitySummary(
  summary: BackendAvailabilitySummary | null,
  branchId: number,
): AvailabilitySummary | null {
  if (!summary) return null;

  const status = summary.availability_type === 'full'
    ? 'full'
    : summary.is_available
      ? 'available'
      : 'unavailable';

  return {
    branchId,
    status,
    availableSlots: summary.is_available ? 1 : 0,
    totalSlots: 1,
  };
}

function mapBranchSchedule(schedule: BackendBranchSchedule, branchId: number): BranchSchedule {
  return {
    id: schedule.id,
    branchId,
    dayOfWeek: mapDayOfWeek(schedule.day_of_week),
    openTime: schedule.open_time,
    closeTime: schedule.close_time,
    isHoliday: !schedule.is_active,
  };
}

function mapBranchProfile(payload: BackendBranchProfile): BranchProfilePublic {
  return {
    id: payload.id,
    name: payload.name,
    description: payload.description,
    address: payload.address,
    city: payload.city,
    phone: payload.phone,
    logoUrl: payload.logoUrl ?? payload.logo_url ?? null,
    services: (payload.services ?? []).map(mapBranchService),
    schedules: (payload.schedules ?? []).map((schedule) => mapBranchSchedule(schedule, payload.id)),
    rating: mapRatingSummary(payload.rating_summary, payload.id),
    availability: mapAvailabilitySummary(payload.availability_summary, payload.id),
  };
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

  const payload = (await response.json()) as BackendBranchProfile;
  return mapBranchProfile(payload);
}

export async function fetchBranchServices(branchId: number): Promise<BranchService[]> {
  const profile = await fetchBranchPublic(branchId);
  return profile.services;
}

export async function fetchBranchSchedules(branchId: number, date?: string): Promise<BranchSchedule[]> {
  void date;
  const profile = await fetchBranchPublic(branchId);
  return profile.schedules;
}

export async function fetchBranchRatingSummary(branchId: number): Promise<RatingSummary | null> {
  const profile = await fetchBranchPublic(branchId);
  return profile.rating;
}

export async function fetchBranchAvailability(branchId: number): Promise<AvailabilitySummary | null> {
  const profile = await fetchBranchPublic(branchId);
  return profile.availability;
}
