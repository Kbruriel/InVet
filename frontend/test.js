import { describe, it, expect, jest, beforeEach } from '@jest/globals';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock API module with explicit jest.fn() factories
const listNotificationsMock = jest.fn().mockResolvedValue({ items: [], meta: {} });
const getUnreadCountMock = jest.fn().mockResolvedValue({ unread: 0 });
const markNotificationReadMock = jest.fn().mockResolvedValue(undefined);
@<#MARKER#>@;

jest.mock('@/shared/api/notification', () => ({
  listNotifications: (...args) => listNotificationsMock(...args),
  getUnreadCount: (...args) => getUnreadCountMock(...args),
  markNotificationRead: (id) => markNotificationReadMock(id),
  markAllNotificationsRead: () => markAllNotificationsReadMock(),
}));

describe('NotificationCenter', () => {
  @<#MARKER@>;
