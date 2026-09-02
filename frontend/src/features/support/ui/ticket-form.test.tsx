import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { supportApi, type SupportCategory } from '@/shared/api/support';

import { TicketForm } from './ticket-form';

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
const categories: SupportCategory[] = [
  { id: 1, name: 'Técnico' },
  { id: 2, name: 'Facturación' },
];

describe('TicketForm', () => {
  const onSubmitSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('muestra los campos y las categorías', () => {
    render(<TicketForm categories={categories} onSubmitSuccess={onSubmitSuccess} />);

    expect(screen.getByLabelText(/título/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/descripción/i)).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Facturación' })).toHaveValue('2');
  });

  it('crea el ticket con valores limpios y categoría numérica', async () => {
    mockedSupportApi.createTicket.mockResolvedValue({
      id: 21,
      clinic_id: 4,
      owner_id: 8,
      title: 'Problema de factura',
      description: 'Detalle del problema',
      category_id: 2,
      status: 'iniciado',
      created_at: '2026-08-30T12:00:00Z',
      updated_at: '2026-08-30T12:00:00Z',
    });
    render(<TicketForm categories={categories} onSubmitSuccess={onSubmitSuccess} />);

    fireEvent.change(screen.getByLabelText(/título/i), {
      target: { value: '  Problema de factura  ' },
    });
    fireEvent.change(screen.getByLabelText(/descripción/i), {
      target: { value: '  Detalle del problema  ' },
    });
    fireEvent.change(screen.getByLabelText(/categoría/i), { target: { value: '2' } });
    fireEvent.click(screen.getByRole('button', { name: /crear ticket/i }));

    await waitFor(() => {
      expect(mockedSupportApi.createTicket).toHaveBeenCalledWith({
        title: 'Problema de factura',
        description: 'Detalle del problema',
        category_id: 2,
      });
    });
    expect(onSubmitSuccess).toHaveBeenCalledTimes(1);
  });

  it('informa el fallo sin invocar la confirmación', async () => {
    mockedSupportApi.createTicket.mockRejectedValue(new Error('network'));
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => undefined);
    render(<TicketForm categories={categories} onSubmitSuccess={onSubmitSuccess} />);

    fireEvent.change(screen.getByLabelText(/título/i), {
      target: { value: 'Problema técnico' },
    });
    fireEvent.click(screen.getByRole('button', { name: /crear ticket/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/error al crear el ticket/i);
    expect(onSubmitSuccess).not.toHaveBeenCalled();
    consoleError.mockRestore();
  });
});
