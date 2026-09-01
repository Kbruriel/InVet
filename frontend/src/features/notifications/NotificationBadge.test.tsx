import { describe, it, expect, beforeEach } from "@jest/globals";
import { render, screen, waitFor } from "@testing-library/react";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type MockFn = jest.MockedFunction<(...args: never[]) => any>;

// Must come before ALL other imports — this is a Jest requirement
jest.mock("@/shared/api/notification", () => ({
  getUnreadCount: jest.fn(),
}));

import { NotificationBadge } from "./NotificationBadge";
import * as notificationApi from "@/shared/api/notification";

describe("NotificationBadge", () => {
  const mockedGetUnread = (notificationApi.getUnreadCount) as MockFn;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders nothing when no unread ", async () => {
    mockedGetUnread.mockResolvedValueOnce({ unread: 0 });

    const { container } = render(<NotificationBadge />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(container.children.length).toBe(0);
    });
  });

  it("renders badge with unread count", async () => {
    mockedGetUnread.mockResolvedValueOnce({ unread: 3 });

    render(<NotificationBadge />);

    await waitFor(() => {
      expect(screen.getByText("3")).toBeTruthy();
      expect(
        screen.getByLabelText("3 notificaciones sin leer"),
      ).toBeTruthy();
    });
  });

  it("renders nothing on error", async () => {
    mockedGetUnread.mockRejectedValueOnce(new Error("API Error"));

    const { container } = render(<NotificationBadge />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(container.children.length).toBe(0);
    });
  });
});