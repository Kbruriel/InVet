/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, jest, beforeEach, afterEach } from '@jest/globals';
import { render, screen, waitFor, act } from '@testing-library/react';
import { NotificationCenter } from './NotificationCenter';

/** Helper to build a plain-object mock compatible with JSDOM (no global Response). */
function makeMock<T extends Record<string, unknown>>(data: T, ok = true): {
  ok: boolean;
  status: number;
  json: () => Promise<T>;
} {
  return {
    ok,
    status: ok ? 200 : 500,
    json: async () => data,
  };
}

/** explicit any so TypeScript does not infer `never` for the return value */
let mockFetch: any;

beforeEach(() => {
  mockFetch = jest.fn();
  global.fetch = mockFetch;
});

afterEach(() => {
  // @ts-expect-error — delete does not exist on Global fetch types
  delete global.fetch;
});

/* ================================================================
   Tests
=============================================================== */

describe('NotificationCenter', () => {

  it('shows notifications on success from a mocked API response', async () => {
    const mockItems = [
      {
        id: 1, clinic_id: 100, user_id: 42, event_type: 'appointment_created', subject: 'Cita creada', body: 'appointment/1 - Mascota: gato', ref_type: 'appointment', ref_id: 1, is_read: false, read_at: null, created_at: '2026-08-25T10:00:00Z'
      },
    ];

    const mockItemsAny = mockItems as any;
    mockFetch.mockResolvedValueOnce(
      makeMock({
        items: mockItemsAny,
        meta: { page: 1, page_size: 20, total: 1, pages: 1, unread_only: false }
      })
    );
    
    await act(async () => { render(<NotificationCenter />); });

    // The text 'Cita creada' from the notification should appear
    await waitFor(() => expect(screen.getByText(/Cita creada/)).toBeTruthy(), { timeout: 3000 });
  });

  it('shows empty state when API returns no notifications', async () => {
    mockFetch.mockResolvedValueOnce(
      makeMock({
        items: [], meta: { page: 1, page_size: 20, total: 0, pages: 1, unread_only: false } as any
      })
    );

    await act(async () => { render(<NotificationCenter />); });

    // Should NOT show any error message after successful (but empty) load
    await waitFor(() => expect(screen.queryByText(/error/)).toBeFalsy(), { timeout: 3000 });
  });

  it('shows error when API call fails', async () => {
    mockFetch.mockResolvedValueOnce(
      makeMock({ detail: 'API connection failed' } as any, false) // status=500
    );

    await act(async () => { render(<NotificationCenter />); });

    // Should show error message with content from API response (detail field)
    await waitFor(() => expect(screen.getByText(/connection failed/)).toBeTruthy(), { timeout: 3000 });
  });

  it('renders all tabs by default and uses the default activeTab', async () => {
    const items = [
      {
        id: 1, clinic_id: 100, user_id: 42, event_type: 'appointment_created', subject: 'Appt A', body: 'body-a', ref_type: 'appointment', ref_id: 1, is_read: false, read_at: null, created_at: '2026-08-25T10:00:00Z'},
      {
        id: 2, clinic_id: 100, user_id: 42, event_type: 'payment_completed', subject: 'Pago B', body: 'body-b', ref_type: 'payment', ref_id: 2, is_read: true, read_at: '2026-08-25T11:00:00Z', created_at: '2026-08-25T11:00:00Z'},
    ];

    const itemsAny = items as any;
    mockFetch.mockResolvedValueOnce(
      makeMock({
        items: itemsAny,
        meta: { page: 1, page_size: 20, total: 2, pages: 1, unread_only: false } as any
      })
    );

    await act(async () => { render(<NotificationCenter />); });

    // Should show both tabs by default (Todas / No leidas)
    expect(screen.getByText(/Todas/)).toBeTruthy();
  });

});
