import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { supportApi, type TicketListResponse } from '@/shared/api/support';

import { TicketListFiltered } from './ticket-list-filtered';

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
      status: 'pendiente',
      category_name: 'Facturación',
      owner_name: 'Ada Lovelace',
      created_at: '2026-08-30T12:00:00Z',
    },
  ],
  meta: { total: 1, page: 1, page_size: 10, pages: 1 },
};

describe('TicketListFiltered', () => {
  const onTicketClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockedSupportApi.listTickets.mockResolvedValue(response);
  });

  it('muestra el listado y el filtro de estados canónicos', async () => {
    render(<TicketListFiltered onTicketClick={onTicketClick} />);

    expect(await screen.findByText('Error al facturar')).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'pendiente' })).toHaveValue('pendiente');
  });

  it('vuelve a consultar desde la primera página al filtrar', async () => {
    render(<TicketListFiltered onTicketClick={onTicketClick} />);
    await screen.findByText('Error al facturar');

    fireEvent.change(screen.getByLabelText(/filtrar por estado/i), {
      target: { value: 'pendiente' },
    });

    await waitFor(() => {
      expect(mockedSupportApi.listTickets).toHaveBeenLastCalledWith({
        page: 1,
        page_size: 10,
        status: 'pendiente',
      });
    });
  });

  it('notifica el ID numérico al seleccionar el ticket', async () => {
    render(<TicketListFiltered onTicketClick={onTicketClick} />);

    const title = await screen.findByText('Error al facturar');
    fireEvent.click(title.closest('tr') as HTMLTableRowElement);
    expect(onTicketClick).toHaveBeenCalledWith(21);
  });
});
