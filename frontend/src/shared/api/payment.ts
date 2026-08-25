import { apiClient } from './client';

export type PaymentMethod = 'cash' | 'transfer' | 'card' | 'other';

export type PaymentStatus = 'paid' | 'cancelled';

export interface Payment {
  id: number;
  appointment_id: number;
  service_id: number;
  clinic_id: number;
  amount: number;
  method: PaymentMethod;
  amount_received: number | null;
  change_amount: number | null;
  status: PaymentStatus;
  paid_at: string;
  cancelled_at: string | null;
  created_by: number | null;
}

export interface PaymentCreateData {
  appointment_id: number;
  service_id: number;
  amount: number;
  method: PaymentMethod;
  /** Obligatorio y >= amount cuando method === 'cash'. */
  amount_received?: number | null;
}

export interface PaymentListParams {
  page?: number;
  page_size?: number;
  appointment_id?: number;
  from_date?: string;
  to_date?: string;
  status?: PaymentStatus;
}

export interface PaymentPageMeta {
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface PaymentListResponse {
  items: Payment[];
  meta: PaymentPageMeta;
}

const BASE_PATH = '/payments';

// El backend espera datetime ISO para from_date/to_date. Los inputs de la UI
// (type="date") emiten solo fecha "YYYY-MM-DD"; se normaliza añadiendo hora.
function toIsoDate(value: string, endOfDay: boolean): string {
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return `${value}T${endOfDay ? '23:59:59' : '00:00:00'}`;
  }
  return value;
}

export async function createPayment(data: PaymentCreateData): Promise<Payment> {
  return apiClient.post<Payment>(BASE_PATH, data);
}

export async function getPayment(paymentId: number): Promise<Payment> {
  return apiClient.get<Payment>(`${BASE_PATH}/${paymentId}`);
}

export async function cancelPayment(paymentId: number): Promise<Payment> {
  return apiClient.post<Payment>(`${BASE_PATH}/${paymentId}/cancel`);
}

export async function listPayments(
  params: PaymentListParams = {},
): Promise<PaymentListResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set('page', String(params.page ?? 1));
  queryParams.set('page_size', String(params.page_size ?? 20));

  if (params.appointment_id) {
    queryParams.set('appointment_id', String(params.appointment_id));
  }
  if (params.from_date) {
    queryParams.set('from_date', toIsoDate(params.from_date, false));
  }
  if (params.to_date) {
    queryParams.set('to_date', toIsoDate(params.to_date, true));
  }
  if (params.status) {
    queryParams.set('status', params.status);
  }

  const query = queryParams.toString();
  return apiClient.get<PaymentListResponse>(
    query ? `${BASE_PATH}?${query}` : BASE_PATH,
  );
}
