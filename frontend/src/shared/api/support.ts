import { apiClient } from './client';

// Tipos de datos para soporte

export interface SupportCategory {
  id: string;
  clinic_id: string;
  name: string;
  active: boolean;
}

export interface SupportTicketStatus {
  initiated: 'initiated';
  pending: 'pending';
  process: 'process';
  completed: 'completed';
  closed: 'closed';
}

export type TicketStatus = keyof SupportTicketStatus;

export interface SupportTicket {
  id: string;
  clinic_id: string;
  owner_id: string;
  title: string;
  description?: string;
  category_id?: string;
  status: TicketStatus;
  created_at: string;
}

export interface CreateSupportTicketRequest {
  title: string;
  description?: string;
  category_id?: string;
}

export interface UpdateTicketStatusRequest {
  status: TicketStatus;
}

export interface ListTicketsFilters {
  page?: number;
  page_size?: number;
  status?: TicketStatus; 
}

// Client
export const supportApi = {
  // Crear un ticket de soporte
  createTicket: async (data: CreateSupportTicketRequest): Promise<SupportTicket> => {
    const response = await apiClient.post<SupportTicket>('/tickets', {
      body: JSON.stringify(data),
    });
    return response.json();
  },

  // Listar tickets
  listTickets: async (filters?: ListTicketsFilters): Promise<{
    items: SupportTicket[];
    page: number;
    page_size: number;
    total: number;
  }> => {
    const params = new URLSearchParams();
    
    if (filters?.page !== undefined) params.append('page', filters.page.toString());
    if (filters?.page_size !== undefined) params.append('page_size', filters.page_size.toString());
    if (filters?.status !== undefined) params.append('status', filters.status);
    
    const response = await apiClient.get<{
      items: SupportTicket[];
      page: number;
      page_size: number;
      total: number;
    }>(`/tickets?${params.toString()}`);
    
    return response.json();
  },

  // Obtener detalle de un ticket
  getTicket: async (ticketId: string): Promise<SupportTicket> => {
    const response = await apiClient.get<SupportTicket>(`/tickets/${ticketId}`);
    return response.json();
  },

  // Actualizar el estado de un ticket
  updateTicketStatus: async (
    ticketId: string, 
    data: UpdateTicketStatusRequest
  ): Promise<SupportTicket> => {
    const response = await apiClient.patch<SupportTicket>(
      `/tickets/${ticketId}/status`,
      {
        body: JSON.stringify(data),
      }
    );
    return response.json();
  },

  // Obtener categorías activas
  getCategories: async (): Promise<SupportCategory[]> => {
    const response = await apiClient.get<SupportCategory[]>('/tickets/categories');
    return response.json();
  },
};