import { apiClient } from './client';
import {
  supportApi,
  type SupportCategory,
  type SupportTicket,
  type TicketListResponse,
  type TicketStatusChangeResponse,
} from './support';

jest.mock('./client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    patch: jest.fn(),
    delete: jest.fn(),
  },
}));

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

const ticket: SupportTicket = {
  id: 21,
  clinic_id: 4,
  owner_id: 8,
  title: 'No puedo emitir una factura',
  description: 'La pantalla muestra un error.',
  category_id: 2,
  category: { id: 2, name: 'Facturación' },
  status: 'iniciado',
  created_at: '2026-08-30T12:00:00Z',
  updated_at: '2026-08-30T12:00:00Z',
};

describe('supportApi', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('crea un ticket con el cuerpo esperado', async () => {
    mockedApiClient.post.mockResolvedValue(ticket);

    await expect(
      supportApi.createTicket({
        title: ticket.title,
        description: ticket.description ?? undefined,
        category_id: 2,
      }),
    ).resolves.toEqual(ticket);

    expect(mockedApiClient.post).toHaveBeenCalledWith('/tickets', {
      title: ticket.title,
      description: ticket.description,
      category_id: 2,
    });
  });

  it('serializa paginación y estado al listar tickets', async () => {
    const response: TicketListResponse = {
      items: [
        {
          id: ticket.id,
          title: ticket.title,
          status: ticket.status,
          category_name: ticket.category?.name ?? null,
          owner_name: 'Ada Lovelace',
          created_at: ticket.created_at,
        },
      ],
      meta: { total: 1, page: 2, page_size: 10, pages: 1 },
    };
    mockedApiClient.get.mockResolvedValue(response);

    await expect(
      supportApi.listTickets({ page: 2, page_size: 10, status: 'pendiente' }),
    ).resolves.toEqual(response);

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/tickets?page=2&page_size=10&status=pendiente',
    );
  });

  it('obtiene el detalle por ID numérico', async () => {
    mockedApiClient.get.mockResolvedValue(ticket);

    await expect(supportApi.getTicket(21)).resolves.toEqual(ticket);
    expect(mockedApiClient.get).toHaveBeenCalledWith('/tickets/21');
  });

  it('actualiza el estado mediante PATCH y new_status', async () => {
    const response: TicketStatusChangeResponse = {
      ticket_id: 21,
      old_status: 'iniciado',
      new_status: 'pendiente',
    };
    mockedApiClient.patch.mockResolvedValue(response);

    await expect(
      supportApi.updateTicketStatus(21, { new_status: 'pendiente' }),
    ).resolves.toEqual(response);

    expect(mockedApiClient.patch).toHaveBeenCalledWith('/tickets/21/status', {
      new_status: 'pendiente',
    });
  });

  it('extrae las categorías de la envoltura items', async () => {
    const categories: SupportCategory[] = [
      { id: 1, name: 'Técnico' },
      { id: 2, name: 'Facturación' },
    ];
    mockedApiClient.get.mockResolvedValue({ items: categories });

    await expect(supportApi.getCategories()).resolves.toEqual(categories);
    expect(mockedApiClient.get).toHaveBeenCalledWith('/tickets/categories');
  });
});
