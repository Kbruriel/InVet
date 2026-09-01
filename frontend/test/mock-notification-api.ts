/* eslint-disable */
// Mock for '@/shared/api/notification' — no fetch, no resolveApiBase, deterministic outputs
import type { NotificationList as ApiNotificationList } from '../src/shared/api/notification';

const defaultListResponse: ApiNotificationList = {
  items: [],
  meta: { page: 1, page_size: 20, total: 0, pages: 1, unread_only: false },
};

let _listResponse: ApiNotificationList | undefined = defaultListResponse;
let _unreadCount: { unread: number } | undefined = { unread: 0 };
let _errorOnList: Error | undefined = undefined;
let _marksReadIds: number[] = [];
let _countMarkAllRead = 0;

export function overrideListResponse(data: ApiNotificationList): void {
  _listResponse = data;
}

export function overrideUnreadCount(data: { unread: number }): void {
  _unreadCount = data;
}

export function enableApiError(): void {
  _errorOnList = new Error('API connection failed');
}

export function resetMockState(): void {
  _listResponse = defaultListResponse;
  _unreadCount = { unread: 0 };
  _errorOnList = undefined;
  _marksReadIds = [];
  _countMarkAllRead = 0;
}

// ── Exported API surface (must match real export names) ─────────────

export async function listNotifications(): Promise<ApiNotificationList> {
  if (_errorOnList) throw _errorOnList;
  return _listResponse!;
}

export async function getUnreadCount() {
  if (_errorOnList) throw _errorOnList;
  return _unreadCount ?? { unread: 0 };
}

export async function markNotificationRead(id: number): Promise<void> {
  _marksReadIds.push(id);
}

export async function markAllNotificationsRead() {
  _countMarkAllRead++;
  return { read: _countMarkAllRead };
}

export function getMarkedReadIds(): number[] {
  return [..._marksReadIds];
}

// ── Re-export types so consumers don't break ────────────────────────
export type NotificationList = ApiNotificationList;
