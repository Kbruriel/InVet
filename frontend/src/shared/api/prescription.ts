import { apiClient } from './client';

export interface PrescriptionItemInput {
  name: string;
  dosage?: string | null;
  frequency?: string | null;
  duration?: string | null;
}

export interface PrescriptionTreatmentInput {
  name: string;
  instructions?: string | null;
}

export interface PrescriptionReminderInput {
  title: string;
  due_at?: string | null;
  note?: string | null;
}

export interface PrescriptionItem {
  id?: number;
  name: string;
  dosage: string | null;
  frequency: string | null;
  duration: string | null;
}

export interface PrescriptionTreatment {
  id?: number;
  name: string;
  instructions: string;
}

export interface PrescriptionReminder {
  id?: number;
  title: string;
  due_at: string | null;
  note: string | null;
}

export interface Prescription {
  id: number;
  consultation_id: number;
  pet_id: number;
  clinic_id: number;
  branch_id: number | null;
  veterinarian_id: number | null;
  diagnosis: string;
  treatment_notes: string;
  created_by: number | null;
  items: PrescriptionItem[];
  treatments: PrescriptionTreatment[];
  reminders: PrescriptionReminder[];
  created_at: string | null;
  updated_at: string | null;
}

export interface PrescriptionCreateData {
  consultation_id: number;
  pet_id: number;
  clinic_id?: number | null;
  veterinarian_id?: number | null;
  diagnosis: string;
  treatment_notes?: string | null;
  items?: PrescriptionItemInput[];
  treatments?: PrescriptionTreatmentInput[];
  reminders?: PrescriptionReminderInput[];
}

export interface PrescriptionPageMeta {
  page: number;
  page_size: number;
  size?: number;
  total: number;
  pages: number;
}

export interface PrescriptionListResponse {
  items: Prescription[];
  meta: PrescriptionPageMeta;
}

export interface PrescriptionListParams {
  page?: number;
  page_size?: number;
  pet_id?: number;
}

const BASE_PATH = '/prescriptions';

export async function createPrescription(
  data: PrescriptionCreateData,
): Promise<Prescription> {
  return apiClient.post<Prescription>(BASE_PATH, data);
}

export async function getPrescription(
  prescriptionId: number,
): Promise<Prescription> {
  return apiClient.get<Prescription>(`${BASE_PATH}/${prescriptionId}`);
}

export async function listPrescriptions(
  params: PrescriptionListParams = {},
): Promise<PrescriptionListResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set('page', String(params.page ?? 1));
  queryParams.set('page_size', String(params.page_size ?? 20));

  if (params.pet_id) {
    queryParams.set('pet_id', String(params.pet_id));
  }

  const query = queryParams.toString();
  return apiClient.get<PrescriptionListResponse>(
    query ? `${BASE_PATH}?${query}` : BASE_PATH,
  );
}
