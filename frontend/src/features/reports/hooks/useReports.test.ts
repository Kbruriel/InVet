import { renderHook, act, waitFor } from '@testing-library/react';
import * as api from '../api';
import { useReports } from './useReports';

jest.mock('../api', () => ({
  listAppointmentsReport: jest.fn(),
  listServicesReport: jest.fn(),
  getPetsCountReport: jest.fn(),
  listConsultationsReport: jest.fn(),
  listRatingsReport: jest.fn(),
  listPaymentsReport: jest.fn(),
}));

const mockedApi = api as jest.Mocked<typeof api>;

describe('useReports hook (FE-015-T02)', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedApi.listAppointmentsReport.mockResolvedValue({
      items: [{ id: 1 }],
      total: 1,
      page: 1,
      size: 20,
    } as never);
  });

  it('does not fetch on mount (fetch only after Apply)', () => {
    const { result } = renderHook(() => useReports());

    expect(result.current.reportType).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(mockedApi.listAppointmentsReport).not.toHaveBeenCalled();
  });

  it('fetches on apply and exposes data/total/page/loading/error/isEmpty', async () => {
    const { result } = renderHook(() => useReports());

    act(() => {
      result.current.apply('appointments', { period_start: '2026-01-01' });
    });
    expect(result.current.loading).toBe(true);

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(mockedApi.listAppointmentsReport).toHaveBeenCalledWith({
      period_start: '2026-01-01',
      period_end: undefined,
      page: 1,
      size: 20,
    });
    expect(result.current.reportType).toBe('appointments');
    expect(result.current.total).toBe(1);
    expect(result.current.page).toBe(1);
    expect(result.current.size).toBe(20);
    expect(result.current.pages).toBe(1);
    expect(result.current.error).toBeNull();
    expect(result.current.isEmpty).toBe(false);
    expect(result.current.data).toMatchObject({ total: 1 });
  });

  it('computes hasMore from total/size', async () => {
    mockedApi.listAppointmentsReport.mockResolvedValueOnce({
      items: [],
      total: 50,
      page: 1,
      size: 20,
    } as never);

    const { result } = renderHook(() => useReports());
    act(() => result.current.apply('appointments'));
    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.pages).toBe(3);
    expect(result.current.hasMore).toBe(true);
    expect(result.current.isEmpty).toBe(false);
  });

  it('navigates to another page keeping filters', async () => {
    mockedApi.listAppointmentsReport
      .mockResolvedValueOnce({ items: [], total: 50, page: 1, size: 20 } as never);
    mockedApi.listAppointmentsReport
      .mockResolvedValueOnce({ items: [], total: 50, page: 2, size: 20 } as never);

    const { result } = renderHook(() => useReports());
    act(() => result.current.apply('appointments', { period_end: '2026-12-31' }));
    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => result.current.goToPage(2));
    await waitFor(() => {
      expect(mockedApi.listAppointmentsReport).toHaveBeenLastCalledWith({
        period_start: undefined,
        period_end: '2026-12-31',
        page: 2,
        size: 20,
      });
    });
    expect(result.current.page).toBe(2);
  });

  it('maps HTTP errors to a readable error state and supports retry', async () => {
    mockedApi.listAppointmentsReport.mockRejectedValueOnce({
      status: 422,
      detail: 'period_start invalid',
    });

    const { result } = renderHook(() => useReports());
    act(() => result.current.apply('appointments'));
    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.error).toBe('period_start invalid');
    expect(result.current.data).toBeNull();

    // Retry should re-run the same request.
    mockedApi.listAppointmentsReport
      .mockResolvedValueOnce({ items: [], total: 0, page: 1, size: 20 } as never);
    act(() => result.current.retry());
    await waitFor(() => expect(result.current.error).toBeNull());
    expect(result.current.isEmpty).toBe(true);
  });
});
