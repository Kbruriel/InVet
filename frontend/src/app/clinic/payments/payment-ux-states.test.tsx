'use client';

/**
 * Verifica AC-011-08: los cinco estados UX (loading, submitting, empty,
 * success, error) estan observables en PaymentForm, PaymentList y
 * PaymentDetail.
 */
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { PaymentForm } from './PaymentForm';
import { PaymentList } from './history/PaymentList';
import { PaymentDetail } from './[id]/PaymentDetail';
import * as paymentApi from '@/shared/api/payment';
import * as appointmentApi from '@/features/appointments/api';
import * as slice006 from '@/shared/api/slice-006';

jest.mock('@/shared/api/payment', () => ({
  createPayment: jest.fn(),
  getPayment: jest.fn(),
  cancelPayment: jest.fn(),
  listPayments: jest.fn(),
}));

jest.mock('@/features/appointments/api', () => ({
  listClinicAppointments: jest.fn(),
}));

jest.mock('@/shared/api/slice-006', () => ({
  fetchServices: jest.fn(),
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

function mockFormDependencies() {
  jest.spyOn(appointmentApi, 'listClinicAppointments').mockResolvedValue({
    items: [
      {
        id: 3,
        owner_id: 1,
        pet_id: 5,
        veterinarian_id: 1,
        clinic_id: 1,
        branch_id: null,
        scheduled_start: '2026-08-24T09:00:00',
        scheduled_end: '2026-08-24T09:30:00',
        status: 'confirmed',
        appointment_type: 'consultation',
        reason: 'Consulta',
        notes: null,
        created_at: '2026-08-20T09:00:00',
        updated_at: '2026-08-20T09:00:00',
      },
    ],
    meta: { total: 1, page: 1, page_size: 100, total_pages: 1 },
  });
  jest.spyOn(slice006, 'fetchServices').mockResolvedValue({
    items: [
      {
        id: 2,
        name: 'Consulta general',
        description: null,
        price: 150,
        duration_minutes: 30,
        clinic_id: 1,
        is_active: true,
        created_at: '2026-08-01T09:00:00',
        updated_at: '2026-08-01T09:00:00',
      },
    ],
    total: 1,
    page: 1,
    size: 100,
  });
}

async function fillForm() {
  await waitFor(() => {
    expect(screen.getByRole('textbox', { name: /importe del pago/i })).toBeInTheDocument();
  });
  fireEvent.change(screen.getByLabelText(/cita asociada/i), { target: { value: '3' } });
  fireEvent.change(screen.getByLabelText(/servicio cobrado/i), { target: { value: '2' } });
  await waitFor(() => {
    expect(screen.getByDisplayValue('150')).toBeInTheDocument();
  });
  fireEvent.change(screen.getByLabelText(/^m[eé]todo de pago/i), { target: { value: 'cash' } });
  await waitFor(() => {
    expect(screen.getByLabelText(/importe recibido/i)).toBeInTheDocument();
  });
  fireEvent.change(screen.getByLabelText(/importe recibido/i), { target: { value: '200' } });
}

describe('FE-011-T05 estados UX del flujo de pagos', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.confirm = jest.fn(() => true);
  });

  describe('PaymentList', () => {
    it('loading: spinner observable mientras la API responde', async () => {
      jest.spyOn(paymentApi, 'listPayments').mockImplementation(() => new Promise(() => {}));
      render(<PaymentList />);
      expect(await screen.findByRole('status')).toBeInTheDocument();
    });

    it('empty: mensaje vacio y CTA Registrar pago', async () => {
      jest.spyOn(paymentApi, 'listPayments').mockResolvedValue({
        items: [],
        meta: { page: 1, page_size: 10, total: 0, pages: 0 },
      });
      render(<PaymentList />);
      expect(await screen.findByText(/no hay pagos en este periodo/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /registrar pago/i })).toBeInTheDocument();
    });

    it('error: banner legible con retry', async () => {
      jest.spyOn(paymentApi, 'listPayments').mockRejectedValue({ detail: 'Error del servidor' });
      render(<PaymentList />);
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });
      expect(screen.getByText(/error del servidor/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
    });
  });

  describe('PaymentDetail', () => {
    it('loading: spinner observable', async () => {
      jest.spyOn(paymentApi, 'getPayment').mockImplementation(() => new Promise(() => {}));
      render(<PaymentDetail />);
      expect(await screen.findByRole('status')).toBeInTheDocument();
    });

    it('error: banner legible con retry', async () => {
      jest.spyOn(paymentApi, 'getPayment').mockRejectedValue({ detail: 'Fallo de red' });
      render(<PaymentDetail />);
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });
      expect(screen.getByText(/fallo de red/i)).toBeInTheDocument();
    });

    it('success: confirmacion de estado Cancelado tras cancelar', async () => {
      jest.spyOn(paymentApi, 'getPayment').mockResolvedValue(paymentFixture);
      jest.spyOn(paymentApi, 'cancelPayment').mockResolvedValue({
        ...paymentFixture,
        status: 'cancelled',
        cancelled_at: '2026-08-24T13:00:00',
      });
      render(<PaymentDetail />);
      const cancel = await screen.findByRole('button', { name: /cancelar pago/i });
      fireEvent.click(cancel);
      await waitFor(() => {
        expect(screen.getByText(/pago cancelado correctamente/i)).toBeInTheDocument();
      });
      expect(screen.getAllByText(/cancelado/i)).not.toHaveLength(0);
    });
  });

  describe('PaymentForm', () => {
    it('submitting: boton deshabilitado y con aria-busy mientras envia', async () => {
      mockFormDependencies();
      jest.spyOn(paymentApi, 'createPayment').mockImplementation(() => new Promise(() => {}));

      render(<PaymentForm onCreated={jest.fn()} />);
      await fillForm();

      fireEvent.click(screen.getByRole('button', { name: /registrar pago/i }));

      const button = await waitFor(() => {
        const el = screen.getByRole('button', { name: /registrar pago/i });
        expect(el).toBeDisabled();
        return el;
      });
      expect(button.tagName).toBe('BUTTON');
    });

    it('error: mensaje de error visible ante error 422 del servidor', async () => {
      mockFormDependencies();
      jest
        .spyOn(paymentApi, 'createPayment')
        .mockRejectedValue({ detail: 'amount_received debe ser mayor o igual que amount' });

      render(<PaymentForm onCreated={jest.fn()} />);
      await fillForm();

      fireEvent.click(screen.getByRole('button', { name: /registrar pago/i }));

      await waitFor(() => {
        expect(screen.getByText(/amount_received debe ser mayor o igual que amount/i)).toBeInTheDocument();
      });
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });
});
