import { apiClient, ApiError } from './client';

export interface ReviewResponseRead {
  id: number;
  review_id: number;
  branch_id: number;
  user_id: number | null;
  body: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface ReviewRead {
  id: number;
  appointment_id: number;
  branch_id: number;
  clinic_id: number;
  user_id: number | null;
  rating: number;
  comment: string | null;
  response: ReviewResponseRead | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface ReviewCreateData {
  appointment_id: number;
  rating: number;
  comment?: string | null;
}

export interface ReviewRespondData {
  body: string;
}

export interface ReviewListMeta {
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface ReviewListResponse {
  items: ReviewRead[];
  meta: ReviewListMeta;
}

export interface ReviewListParams {
  page?: number;
  page_size?: number;
  branch_id?: number;
}

const BASE_PATH = '/reviews';

export function extractApiError(err: unknown): string {
  if (err && typeof err === 'object' && 'detail' in err) {
    const detail = (err as { detail?: unknown }).detail;
    if (typeof detail === 'string' && detail.length > 0) {
      return detail;
    }
  }
  return err instanceof Error && err.message ? err.message : 'Error desconocido';
}

export function getApiStatus(err: unknown): number | null {
  if (
    err &&
    typeof err === 'object' &&
    'status' in err &&
    typeof (err as { status?: unknown }).status === 'number'
  ) {
    return (err as { status: number }).status;
  }
  return null;
}

export function isApiError(err: unknown): err is ApiError {
  return (
    err !== null &&
    typeof err === 'object' &&
    'status' in err &&
    typeof (err as { status?: unknown }).status === 'number'
  );
}

export async function createReview(data: ReviewCreateData): Promise<ReviewRead> {
  return apiClient.post<ReviewRead>(BASE_PATH, data);
}

export async function getReview(reviewId: number): Promise<ReviewRead> {
  return apiClient.get<ReviewRead>(`${BASE_PATH}/${reviewId}`);
}

export async function listPublicReviews(
  branchId: number,
  params: Omit<ReviewListParams, 'branch_id'> = {},
): Promise<ReviewListResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set('page', String(params.page ?? 1));
  queryParams.set('page_size', String(params.page_size ?? 20));
  return apiClient.get<ReviewListResponse>(
    `${BASE_PATH}/public/${branchId}?${queryParams.toString()}`,
  );
}

export async function listClinicReviews(
  params: ReviewListParams = {},
): Promise<ReviewListResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set('page', String(params.page ?? 1));
  queryParams.set('page_size', String(params.page_size ?? 20));
  if (params.branch_id) {
    queryParams.set('branch_id', String(params.branch_id));
  }
  return apiClient.get<ReviewListResponse>(`${BASE_PATH}?${queryParams.toString()}`);
}

export async function respondReview(
  reviewId: number,
  data: ReviewRespondData,
): Promise<ReviewResponseRead> {
  return apiClient.post<ReviewResponseRead>(`${BASE_PATH}/${reviewId}/respond`, data);
}
