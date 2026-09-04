import { apiClient } from '@/shared/api/client';
import {
  listAppointmentsReport,
  listServicesReport,
  getPetsCountReport,
  listConsultationsReport,
  listRatingsReport,
  listPaymentsReport,
} from './api';

jest.mock('@/shared/api/client', () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('reports api client (FE-015-T01)', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('lists appointments report with no filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 1,
      size: 20,
    });

    await listAppointmentsReport();

    expect(mockedApiClient.get).toHaveBeenCalledWith('/reports/appointments');
  });

  it('lists appointments report with filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 2,
      size: 10,
    });

    await listAppointmentsReport({
      period_start: '2026-01-01',
      period_end: '2026-01-31',
      page: 2,
      size: 10,
    });

    const expected = new URLSearchParams();
    expected.set('period_start', '2026-01-01');
    expected.set('period_end', '2026-01-31');
    expected.set('page', '2');
    expected.set('size', '10');
    expect(mockedApiClient.get).toHaveBeenCalledWith(
      `/reports/appointments?${expected.toString()}`,
    );
  });

  it('lists services report with filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 1,
      size: 20,
    });

    await listServicesReport({ period_start: '2026-02-01' });

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/reports/services?period_start=2026-02-01',
    );
  });

  it('gets pets count report with no filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      clinic_id: 1,
      active_count: 3,
    });

    await getPetsCountReport();

    expect(mockedApiClient.get).toHaveBeenCalledWith('/reports/pets');
  });

  it('lists consultations report with filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 1,
      size: 20,
    });

    await listConsultationsReport({ period_end: '2026-03-31' });

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/reports/consultations?period_end=2026-03-31',
    );
  });

  it('lists ratings report with no filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      by_veterinarian: [],
      clinic_avg: 0,
    });

    await listRatingsReport();

    expect(mockedApiClient.get).toHaveBeenCalledWith('/reports/ratings');
  });

  it('lists payments report with filters', async () => {
    mockedApiClient.get.mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 1,
      size: 20,
      total_amount: 0,
    });

    await listPaymentsReport({
      period_start: '2026-04-01',
      period_end: '2026-04-30',
      page: 1,
      size: 50,
    });

    const expected = new URLSearchParams();
    expected.set('period_start', '2026-04-01');
    expected.set('period_end', '2026-04-30');
    expected.set('page', '1');
    expected.set('size', '50');
    expect(mockedApiClient.get).toHaveBeenCalledWith(
      `/reports/payments?${expected.toString()}`,
    );
  });
});
