import { apiClient } from './client';

export interface Consultation {
  id: number;
  appointment_id: number;
  pet_id: number;
  clinic_id: number;
  branch_id: number;
  veterinarian_id: number | null;
  history: string;
  diagnosis: string;
  recommendations: string;
  created_by: number | null;
  updated_at: string | null;
}

export interface ConsultationCreateData {
  appointment_id: number;
  pet_id: number;
  clinic_id?: number;
  branch_id?: number | null;
  veterinarian_id?: number | null;
  history?: string | null;
  diagnosis: string;
  recommendations?: string | null;
}

export interface ConsultationPageMeta {
  page: number;
  page_size: number;
  size?: number;
  total: number;
  pages: number;
}

export interface ConsultationListResponse {
  items: Consultation[];
  meta: ConsultationPageMeta;
}

export interface ConsultationListParams {
  page?: number;
  page_size?: number;
  pet_id?: number;
  clinic_id?: number;
}

const BASE_PATH = '/api/v1/consultations';

export async function createConsultation(
  data: ConsultationCreateData,
): Promise<Consultation> {
  return apiClient.post<Consultation>(BASE_PATH, data);
}

export async function getConsultation(
  consultationId: number,
): Promise<Consultation> {
  return apiClient.get<Consultation>(`${BASE_PATH}/${consultationId}`);
}

export async function listConsultations(
  params: ConsultationListParams = {},
): Promise<ConsultationListResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set('page', String(params.page ?? 1));
  queryParams.set('page_size', String(params.page_size ?? 20));

  if (params.pet_id) {
    queryParams.set('pet_id', String(params.pet_id));
  }

  if (params.clinic_id) {
    queryParams.set('clinic_id', String(params.clinic_id));
  }

  const query = queryParams.toString();
  return apiClient.get<ConsultationListResponse>(
    query ? `${BASE_PATH}?${query}` : BASE_PATH,
  );
}
