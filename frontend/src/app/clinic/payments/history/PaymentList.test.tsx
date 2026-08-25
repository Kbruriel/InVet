'use client';

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { PaymentList } from './PaymentList';
import { listPayments } from '@/shared/api/payment';

const mockPush = jest.fn();

jest.mock('@/shared/api/payment', () => ({
  listPayments: jest.fn(),
}));

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}));

const paymentFixture = {
  id: 7,
  appointment_id: 3,
  service_id: 2,
  clinic_id: 1,
  amount: 15000,
  method: 'cash' as const,
  amount_received: 20000,
  change_amount: 5000,
  status: 'paid' as const,
  paid_at: '2026-08-24T12:00:00',
  cancelled_at: null,
  created_by: null,
};

describe('PaymentList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('muestra el estado de carga', async () => {
    (listPayments as jest.Mock).mockImplementation(() => new Promise(() => {}));
    render(<PaymentList />);
    expect(await screen.findByRole('status')).toBeInTheDocument();
  });

  it('muestra el estado vacio con CTA', async () => {
    (listPayments as jest.Mock).mockResolvedValue({
      items: [],
      meta: { page: 1, page_size: 10, total: 0, pages: 0 },
    });
    render(<PaymentList />);
    expect(
      await screen.findByRole('button', { name: /registrar pago/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/no hay pagos en este periodo/i)).toBeInTheDocument();
  });

  it('muestra el estado de error con retry', async () => {
    (listPayments as jest.Mock).mockRejectedValue({ detail: 'Error del servidor' });
    render(<PaymentList />);
    await waitFor(() => {
      expect(screen.getByText(/error del servidor/i)).toBeInTheDocument();
    });
    expect(
      screen.getByRole('button', { name: /reintentar/i }),
    ).toBeInTheDocument();
  });

  it('muestra las filas de pago', async () => {
    (listPayments as jest.Mock).mockResolvedValue({
      items: [paymentFixture],
      meta: { page: 1, page_size: 10, total: 1, pages: 1 },
    });
    render(<PaymentList />);
    expect(await screen.findAllByText('#7')).not.toHaveLength(0);
    expect(screen.getAllByText(/pagado/i)).not.toHaveLength(0);
  });

  it('filtra al enviar el formulario de fechas', async () => {
    (listPayments as jest.Mock).mockResolvedValue({
      items: [],
      meta: { page: 1, page_size: 10, total: 0, pages: 0 },
    });
    render(<PaymentList />);
    await screen.findByRole('button', { name: /registrar pago/i });

    fireEvent.change(screen.getByLabelText(/desde/i), { target: { value: '2026-08-01' } });
    fireEvent.click(screen.getByRole('button', { name: /^filtrar$/i }));

    await waitFor(() => {
      expect(listPayments).toHaveBeenLastCalledWith(
        expect.objectContaining({ from_date: '2026-08-01', page: 1 }),
      );
    });
  });
});
