import { apiClient } from './client';
import {
  cancelPayment,
  createPayment,
  getPayment,
  listPayments,
} from './payment';

jest.mock('./client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

function fakePayment(overrides: Record<string, unknown> = {}) {
  return {
    id: 1,
    appointment_id: 1,
    service_id: 1,
    clinic_id: 1,
    amount: 1000,
    method: 'cash',
    amount_received: 1200,
    change_amount: 200,
    status: 'paid',
    paid_at: '2026-08-24T12:00:00',
    cancelled_at: null,
    created_by: null,
    ...overrides,
  };
}

describe('payment api client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('creates a payment', async () => {
    mockedApiClient.post.mockResolvedValueOnce(fakePayment());

    await createPayment({
      appointment_id: 1,
      service_id: 1,
      amount: 1000,
      method: 'cash',
      amount_received: 1200,
    });

    expect(mockedApiClient.post).toHaveBeenCalledWith('/payments', {
      appointment_id: 1,
      service_id: 1,
      amount: 1000,
      method: 'cash',
      amount_received: 1200,
    });
  });

  it('gets a payment by id', async () => {
    mockedApiClient.get.mockResolvedValueOnce(fakePayment());

    await getPayment(4);

    expect(mockedApiClient.get).toHaveBeenCalledWith('/payments/4');
  });

  it('cancels a payment', async () => {
    mockedApiClient.post.mockResolvedValueOnce(
      fakePayment({ status: 'cancelled', cancelled_at: '2026-08-24T13:00:00' }),
    );

    await cancelPayment(4);

    expect(mockedApiClient.post).toHaveBeenCalledWith('/payments/4/cancel');
  });

  it('lists payments with default filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [fakePayment()],
      meta: { page: 1, page_size: 20, total: 1, pages: 1 },
    });

    await listPayments();

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/payments?page=1&page_size=20',
    );
  });

  it('lists payments with all filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      meta: { page: 2, page_size: 10, total: 5, pages: 1 },
    });

    await listPayments({
      page: 2,
      page_size: 10,
      appointment_id: 7,
      from_date: '2026-08-01T00:00:00',
      to_date: '2026-08-31T23:59:59',
      status: 'paid',
    });

    const expected = new URLSearchParams();
    expected.set('page', '2');
    expected.set('page_size', '10');
    expected.set('appointment_id', '7');
    expected.set('from_date', '2026-08-01T00:00:00');
    expected.set('to_date', '2026-08-31T23:59:59');
    expected.set('status', 'paid');
    expect(mockedApiClient.get).toHaveBeenCalledWith(
      `/payments?${expected.toString()}`,
    );
  });
});
