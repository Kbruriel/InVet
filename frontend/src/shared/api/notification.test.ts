/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, jest, beforeEach, afterEach } from '@jest/globals';
import * as notificationApi from './notification';

const originalFetch = globalThis?.fetch;

beforeEach(() => {
  (globalThis as any).fetch = jest.fn();
  jest.clearAllMocks();
});

afterEach(() => {
  Object.assign(globalThis, { fetch: originalFetch });
});

/** Shape of the minimal mock Response needed by notification.ts */
interface MockRes {
  ok: boolean;
  status: number;
  json: () => Promise<unknown>;
}

function mockOk<T extends Record<string, unknown>>(data: T): MockRes {
  return {
    ok: true,
    status: 200,
    json: async () => data,
  };
}

function mockFail<T extends Record<string, unknown>>(data: T, status: number): MockRes {
  return {
    ok: false,
    status,
    json: async () => data,
  };
}

describe('Notification API Client', () => {

  // ------------------------------------------------------------------ listNotifications
  it('lists notifications successfully', async () => {
    const mockItems = [
      {
        id: 1,
        clinic_id: 100,
        user_id: 42,
        event_type: 'appointment_created',
        subject: 'Notificacion appointment_created',
        body: 'appointment/1 - Mascota: gato',
        ref_type: 'appointment',
        ref_id: 1,
        is_read: false,
        read_at: null,
        created_at: '2026-08-25T10:00:00Z',
      },
    ];

    const mockFetch = (globalThis as any).fetch;
    mockFetch.mockResolvedValueOnce(
      mockOk({
        items: mockItems,
        meta: { page: 1, page_size: 20, total: 1, pages: 1, unread_only: false },
      })
    );

    const result = await notificationApi.listNotifications(1, 20, false);
    expect((result as any).items.length).toBe(1);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('handles list notifications with error', async () => {
    const mockFetch = (globalThis as any).fetch;
    mockFetch.mockResolvedValueOnce(mockFail({ detail: 'Not found' }, 404) as unknown as Response);

    const p = notificationApi.listNotifications(1, 20, false);
    await expect(p).rejects.toHaveProperty('detail', 'Not found');
    await expect(p).rejects.toHaveProperty('status', 404);
  });

  // ------------------------------------------------------------------ getUnreadCount
  it('gets unread count successfully', async () => {
    const mockFetch = (globalThis as any).fetch;
    mockFetch.mockResolvedValueOnce(mockOk({ unread: 3 }));

    const result = await notificationApi.getUnreadCount();
    expect((result as any).unread).toBe(3);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('handles unread count with error', async () => {
    const mockFetch = (globalThis as any).fetch;
    mockFetch.mockResolvedValueOnce(mockFail({ detail: 'Server error' }, 500) as unknown as Response);

    await expect(notificationApi.getUnreadCount()).rejects.toHaveProperty('status', 500);
  });

  // -------------------------------------------------------------- markNotificationRead
  it('marks notification as read successfully', async () => {
    const mockFetch = (globalThis as any).fetch;
    mockFetch.mockResolvedValueOnce(
      mockOk({
        id: 1,
        clinic_id: 100,
        user_id: 42,
        event_type: 'appointment_created',
        subject: 'Subject X',
        body: 'body-x',
        ref_type: 'appointment',
        ref_id: 1,
        is_read: true,
        read_at: '2026-08-25T10:30:00Z',
        created_at: '2026-08-25T10:00:00Z',
      })
    );

    const result = await notificationApi.markNotificationRead(1);
    expect((result as any).is_read).toBe(true);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('handles mark notification read with error', async () => {
    const mockFetch = (globalThis as any).fetch;
    mockFetch.mockResolvedValueOnce(mockFail({ detail: 'Not found' }, 404) as unknown as Response);

    await expect(notificationApi.markNotificationRead(999)).rejects.toHaveProperty('detail', 'Not found');
  });

  // ---------------------------------------------------------- markAllNotificationsRead
  it('marks all notifications as read successfully', async () => {
    const mockFetch = (globalThis as any).fetch;
    mockFetch.mockResolvedValueOnce(mockOk({ read: 3 }));

    const result = await notificationApi.markAllNotificationsRead();
    expect((result as any).read).toBe(3);
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it('handles mark all notifications read with error', async () => {
    const mockFetch = (globalThis as any).fetch;
    mockFetch.mockResolvedValueOnce(mockFail({ detail: 'Forbidden' }, 403) as unknown as Response);

    await expect(notificationApi.markAllNotificationsRead()).rejects.toHaveProperty('detail', 'Forbidden');
  });
});
