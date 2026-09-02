import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { supportApi, type SupportTicket } from '@/shared/api/support';

import { TicketStatusUpdater } from './ticket-status-updater';

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
const ticket: SupportTicket = {
  id: 21,
  clinic_id: 4,
  owner_id: 8,
  title: 'Error al facturar',
  description: 'Detalle',
  category_id: 2,
  status: 'iniciado',
  created_at: '2026-08-30T12:00:00Z',
  updated_at: '2026-08-30T12:00:00Z',
};

describe('TicketStatusUpdater', () => {
  const onStatusUpdated = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('muestra sólo las transiciones permitidas', () => {
    render(<TicketStatusUpdater ticket={ticket} onStatusUpdated={onStatusUpdated} />);

    expect(screen.getByRole('button', { name: 'Pendiente' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'En proceso' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Cerrado' })).not.toBeInTheDocument();
  });

  it('envía new_status y actualiza el detalle', async () => {
    mockedSupportApi.updateTicketStatus.mockResolvedValue({
      ticket_id: 21,
      old_status: 'iniciado',
      new_status: 'pendiente',
    });
    render(<TicketStatusUpdater ticket={ticket} onStatusUpdated={onStatusUpdated} />);

    fireEvent.click(screen.getByRole('button', { name: 'Pendiente' }));

    await waitFor(() => {
      expect(mockedSupportApi.updateTicketStatus).toHaveBeenCalledWith(21, {
        new_status: 'pendiente',
      });
    });
    expect(onStatusUpdated).toHaveBeenCalledTimes(1);
  });

  it('no renderiza acciones para un ticket cerrado', () => {
    const { container } = render(
      <TicketStatusUpdater
        ticket={{ ...ticket, status: 'cerrado' }}
        onStatusUpdated={onStatusUpdated}
      />,
    );

    expect(container).toBeEmptyDOMElement();
  });
});
