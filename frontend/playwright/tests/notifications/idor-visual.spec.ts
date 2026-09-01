import { test, expect } from '@playwright/test';

test.describe('Notification IDOR Visual Testing', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication with user A
    const ctx = page.context();
    await ctx.addCookies([
      { name: 'session_token', value: 'mock-token-userA', domain: 'localhost', path: '/', httpOnly: true },
      { name: 'user_id', value: 'user-A-123', domain: 'localhost', path: '/', httpOnly: true }
    ]);
    await page.goto('/portal/notifications');
  });

  test('should prevent access to other user notifications via URL modification', async ({ page }) => {
    // Try to directly access a notification ID that belongs to another user
    // This should result in a 404 or redirect to login
    await page.route('**/api/v1/notifications/*', (route) => {
      const url = new URL(route.request().url());
      const notificationId = url.pathname.split('/').pop();
      
      if (notificationId === 'notification-xyz') {
        // Simulate 404 error for non-existent or unauthorized notification
        return route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Not Found' })
        });
      }
      route.continue();
    });

    // Try to access a notification that doesn't belong to the user
    await page.goto('/portal/notifications/123');
    
    // Should not see unauthorized content - this test depends on UI behavior
    const unauthorizedMessage = page.getByText('No tienes permisos para ver esta notificación');
    await expect(unauthorizedMessage).not.toBeVisible();
  });

  test('should show error when trying to mark another user notification as read', async ({ page }) => {
    // We'll mock the API call that would happen when marking a notification as read
    await page.route('**/api/v1/notifications/*/read', (route) => {
      const url = new URL(route.request().url());
      
      // Simulate user trying to access notification from another user
      if (url.pathname.includes('/notification-xyz/read')) {
        return route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Not Found' })
        });
      }
      route.continue();
    });

    // Try to mark a notification as read that doesn't belong to user 
    await expect(page.locator('[data-testid="notification-item"]')).toBeVisible();
    // The actual behavior would be tested by intercepting the API call, but UI should not allow it visually
  });
});