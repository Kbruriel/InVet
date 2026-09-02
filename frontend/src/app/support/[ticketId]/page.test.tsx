import { render, screen } from '@testing-library/react';

import { supportApi, type SupportTicket } from '@/shared/api/support';

import SupportTicketPage from './page';

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

jest.mock('./ticket-status-updater', () => ({
  TicketStatusUpdater: () => <div data-testid="status-updater" />,
}));

const mockedSupportApi = supportApi as jest.Mocked<typeof supportApi>;
const ticket: SupportTicket = {
  id: 21,
  clinic_id: 4,
  owner_id: 8,
  title: 'Error al facturar',
  description: 'La pantalla muestra un error.',
  category_id: 2,
  category: { id: 2, name: 'Facturación' },
  status: 'iniciado',
  created_at: '2026-08-30T12:00:00Z',
  updated_at: '2026-08-30T12:00:00Z',
};

describe('SupportTicketPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('muestra el detalle obtenido por ID numérico', async () => {
    mockedSupportApi.getTicket.mockResolvedValue(ticket);
    render(<SupportTicketPage params={{ ticketId: '21' }} />);

    expect(await screen.findByRole('heading', { name: 'Error al facturar' })).toBeInTheDocument();
    expect(screen.getByText('Facturación')).toBeInTheDocument();
    expect(screen.getByTestId('status-updater')).toBeInTheDocument();
    expect(mockedSupportApi.getTicket).toHaveBeenCalledWith(21);
  });

  it('distingue una respuesta 404', async () => {
    mockedSupportApi.getTicket.mockRejectedValue({ status: 404, detail: 'not found' });
    render(<SupportTicketPage params={{ ticketId: '21' }} />);

    expect(await screen.findByRole('alert')).toHaveTextContent(/no existe/i);
  });

  it('rechaza un ID inválido sin consultar la API', async () => {
    render(<SupportTicketPage params={{ ticketId: 'abc' }} />);

    expect(await screen.findByRole('alert')).toHaveTextContent(/no es válido/i);
    expect(mockedSupportApi.getTicket).not.toHaveBeenCalled();
  });
});
