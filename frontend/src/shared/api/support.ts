import { apiClient } from './client';

export const TICKET_STATUSES = [
  'iniciado',
  'pendiente',
  'proceso',
  'completado',
  'cerrado',
] as const;

export type TicketStatus = (typeof TICKET_STATUSES)[number];

export interface SupportCategory {
  id: number;
  name: string;
}

export interface SupportTicket {
  id: number;
  clinic_id: number;
  owner_id: number;
  title: string;
  description: string | null;
  category_id: number | null;
  category?: SupportCategory | null;
  status: TicketStatus;
  created_at: string;
  updated_at: string;
}

export interface SupportTicketListItem {
  id: number;
  title: string;
  status: TicketStatus;
  category_name: string | null;
  owner_name: string;
  created_at: string;
}

export interface CreateSupportTicketRequest {
  title: string;
  description?: string;
  category_id?: number;
}

export interface UpdateTicketStatusRequest {
  new_status: TicketStatus;
}

export interface TicketStatusChangeResponse {
  ticket_id: number;
  old_status: TicketStatus;
  new_status: TicketStatus;
}

export interface ListTicketsFilters {
  page?: number;
  page_size?: number;
  status?: TicketStatus;
}

export interface TicketListResponse {
  items: SupportTicketListItem[];
  meta: {
    total: number;
    page: number;
    page_size: number;
    pages?: number;
  };
}

export const supportApi = {
  createTicket(data: CreateSupportTicketRequest): Promise<SupportTicket> {
    return apiClient.post<SupportTicket>('/tickets', data);
  },

  listTickets(filters?: ListTicketsFilters): Promise<TicketListResponse> {
    const params = new URLSearchParams();

    if (filters?.page !== undefined) params.set('page', filters.page.toString());
    if (filters?.page_size !== undefined) params.set('page_size', filters.page_size.toString());
    if (filters?.status !== undefined) params.set('status', filters.status);

    const query = params.toString();
    return apiClient.get<TicketListResponse>(query ? `/tickets?${query}` : '/tickets');
  },

  getTicket(ticketId: number | string): Promise<SupportTicket> {
    return apiClient.get<SupportTicket>(`/tickets/${ticketId}`);
  },

  updateTicketStatus(
    ticketId: number | string,
    data: UpdateTicketStatusRequest,
  ): Promise<TicketStatusChangeResponse> {
    return apiClient.patch<TicketStatusChangeResponse>(`/tickets/${ticketId}/status`, data);
  },

  async getCategories(): Promise<SupportCategory[]> {
    const response = await apiClient.get<{ items: SupportCategory[] }>('/tickets/categories');
    return response.items;
  },
};
