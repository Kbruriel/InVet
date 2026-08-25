'use client';

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { PaymentDetail } from './PaymentDetail';
import { cancelPayment, getPayment } from '@/shared/api/payment';

jest.mock('@/shared/api/payment', () => ({
  getPayment: jest.fn(),
  cancelPayment: jest.fn(),
}));

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
  useParams: () => ({ id: '7' }),
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

describe('PaymentDetail', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.confirm = jest.fn(() => true);
  });

  it('muestra el estado de carga', async () => {
    (getPayment as jest.Mock).mockImplementation(() => new Promise(() => {}));
    render(<PaymentDetail />);
    expect(await screen.findByRole('status')).toBeInTheDocument();
  });

  it('muestra detalles del pago pagado', async () => {
    (getPayment as jest.Mock).mockResolvedValue(paymentFixture);
    render(<PaymentDetail />);
    expect(await screen.findByText('#7')).toBeInTheDocument();
    expect(screen.getAllByText(/pagado/i)).not.toHaveLength(0);
    expect(screen.getAllByText(/efectivo/i)).not.toHaveLength(0);
  });

  it('muestra el banner de error ante fallo de carga', async () => {
    (getPayment as jest.Mock).mockRejectedValue({ detail: 'Error del servidor' });
    render(<PaymentDetail />);
    await waitFor(() => {
      expect(screen.getByText(/error del servidor/i)).toBeInTheDocument();
    });
  });

  it('muestra estado cancelado y fecha de cancelacion', async () => {
    (getPayment as jest.Mock).mockResolvedValue({
      ...paymentFixture,
      status: 'cancelled',
      cancelled_at: '2026-08-24T13:00:00',
    });
    render(<PaymentDetail />);
    expect(await screen.findAllByText(/cancelado/i)).not.toHaveLength(0);
    expect(screen.getByText(/fecha de cancelaci[oó]n/i)).toBeInTheDocument();
  });

  it('cancela el pago si el usuario confirma', async () => {
    (getPayment as jest.Mock).mockResolvedValue(paymentFixture);
    (cancelPayment as jest.Mock).mockResolvedValue({
      ...paymentFixture,
      status: 'cancelled',
      cancelled_at: '2026-08-24T13:00:00',
    });
    render(<PaymentDetail />);
    const cancelButton = await screen.findByRole('button', { name: /cancelar pago/i });

    fireEvent.click(cancelButton);

    await waitFor(() => {
      expect(cancelPayment).toHaveBeenCalledWith(7);
    });
    await waitFor(() => {
      expect(screen.getByText(/pago cancelado correctamente/i)).toBeInTheDocument();
    });
    expect(screen.getAllByText(/cancelado/i)).not.toHaveLength(0);
  });

  it('no cancela si el usuario no confirma el dialogo', async () => {
    (getPayment as jest.Mock).mockResolvedValue(paymentFixture);
    (window.confirm as jest.Mock).mockReturnValue(false);
    render(<PaymentDetail />);
    const cancelButton = await screen.findByRole('button', { name: /cancelar pago/i });

    fireEvent.click(cancelButton);

    expect(cancelPayment).not.toHaveBeenCalled();
  });
});
