import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { supportApi, type TicketListResponse } from '@/shared/api/support';

import { TicketList } from './ticket-list';

jest.mock('@/shared/api/support', () => ({
  ...jest.requireActual('@/shared/api/support'),
  supportApi: {
    createTicket: jest.fn(),
    listTickets: jest.fn(),
    getTicket: jest.fn(),
    updateTicketStatus: jest.fn(),
    getCategories: jest.fn(),
  },
}));

const mockedSupportApi = supportApi as jest.Mocked<typeof supportApi>;
const response: TicketListResponse = {
  items: [
    {
      id: 21,
      title: 'Error al facturar',
      status: 'iniciado',
      category_name: 'Facturación',
      owner_name: 'Ada Lovelace',
      created_at: '2026-08-30T12:00:00Z',
    },
  ],
  meta: { total: 1, page: 1, page_size: 10, pages: 1 },
};

describe('TicketList', () => {
  const onTicketClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('carga y muestra los tickets', async () => {
    mockedSupportApi.listTickets.mockResolvedValue(response);
    render(<TicketList onTicketClick={onTicketClick} />);

    expect(await screen.findByText('Error al facturar')).toBeInTheDocument();
    expect(mockedSupportApi.listTickets).toHaveBeenCalledWith({ page: 1, page_size: 10 });
  });

  it('notifica el ID al seleccionar una fila', async () => {
    mockedSupportApi.listTickets.mockResolvedValue(response);
    render(<TicketList onTicketClick={onTicketClick} />);

    const title = await screen.findByText('Error al facturar');
    fireEvent.click(title.closest('tr') as HTMLTableRowElement);
    expect(onTicketClick).toHaveBeenCalledWith(21);
  });

  it('muestra el estado vacío', async () => {
    mockedSupportApi.listTickets.mockResolvedValue({
      items: [],
      meta: { total: 0, page: 1, page_size: 10, pages: 0 },
    });
    render(<TicketList onTicketClick={onTicketClick} />);

    expect(await screen.findByText(/no hay tickets para mostrar/i)).toBeInTheDocument();
  });

  it('permite reintentar después de un error', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => undefined);
    mockedSupportApi.listTickets
      .mockRejectedValueOnce(new Error('network'))
      .mockResolvedValueOnce(response);
    render(<TicketList onTicketClick={onTicketClick} />);

    fireEvent.click(await screen.findByRole('button', { name: /reintentar/i }));
    await waitFor(() => expect(screen.getByText('Error al facturar')).toBeInTheDocument());
    consoleError.mockRestore();
  });
});
