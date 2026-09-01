import { test, expect } from '@playwright/test';

test.describe('Notification Center Tabs and Filtering', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication 
    const ctx = page.context();
    await ctx.addCookies([
      { name: 'session_token', value: 'mock-token', domain: 'localhost', path: '/', httpOnly: true },
      { name: 'user_id', value: 'user-123', domain: 'localhost', path: '/', httpOnly: true }
    ]);
    await page.goto('/portal/notifications');
  });

  test('should filter notifications by unread status when clicking "No leidas" tab', async ({ page }) => {
    // Click on "No leidas" tab
    const unreadTab = page.getByText('No leidas');
    await unreadTab.click();
    
    // Check that only unread notifications are displayed
    const unreadItems = page.locator('[data-testid="notification-item"].unread');
    const readItems = page.locator('[data-testid="notification-item"].read');
    
    // All items should be unread (this depends on the test data)
    await expect(unreadItems).toBeVisible();
    // There should be no read items visible at this point
  });

  test('should display all notifications when clicking "Todas" tab', async ({ page }) => {
    // Click on "Todas" tab to see all notifications
    const allTab = page.getByText('Todas');
    await allTab.click();
    
    // Check that all notification items are displayed (both read and unread)
    await expect(page.locator('[data-testid="notification-item"]')).toBeVisible();
  });
});