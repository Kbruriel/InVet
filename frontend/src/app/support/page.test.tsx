import { render, screen, waitFor } from '@testing-library/react';

import { supportApi } from '@/shared/api/support';

import SupportPage from './page';

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

jest.mock('@/features/support/ui/ticket-form', () => ({
  TicketForm: () => <div data-testid="ticket-form" />,
}));

jest.mock('@/features/support/ui/ticket-list-filtered', () => ({
  TicketListFiltered: () => <div data-testid="ticket-list" />,
}));

const mockedSupportApi = supportApi as jest.Mocked<typeof supportApi>;

describe('SupportPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('carga categorías y compone formulario y listado', async () => {
    mockedSupportApi.getCategories.mockResolvedValue([
      { id: 1, name: 'Técnico' },
      { id: 2, name: 'Facturación' },
    ]);
    render(<SupportPage />);

    expect(screen.getByRole('heading', { name: 'Soporte' })).toBeInTheDocument();
    expect(screen.getByTestId('ticket-form')).toBeInTheDocument();
    expect(screen.getByTestId('ticket-list')).toBeInTheDocument();
    await waitFor(() => expect(mockedSupportApi.getCategories).toHaveBeenCalledTimes(1));
  });

  it('muestra un error si no puede cargar categorías', async () => {
    mockedSupportApi.getCategories.mockRejectedValue(new Error('network'));
    render(<SupportPage />);

    expect(await screen.findByRole('alert')).toHaveTextContent(
      /no fue posible cargar las categorías/i,
    );
  });
});
