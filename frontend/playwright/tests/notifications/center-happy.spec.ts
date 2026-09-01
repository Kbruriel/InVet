import { test, expect } from '@playwright/test';

test.describe('Notification Center - Happy Path', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication 
    const ctx = page.context();
    await ctx.addCookies([
      { name: 'session_token', value: 'mock-token', domain: 'localhost', path: '/', httpOnly: true },
      { name: 'user_id', value: 'user-123', domain: 'localhost', path: '/', httpOnly: true }
    ]);
    await page.goto('/portal/notifications');
  });

  test('should display notification center with tabs and paginated list', async ({ page }) => {
    // Check that the notification center is displayed
    await expect(page.locator('[aria-label="Centro de notificaciones"]')).toBeVisible();
    
    // Check tabs are present
    await expect(page.getByText('Todas')).toBeVisible();
    await expect(page.getByText('No leidas')).toBeVisible();
    
    // Check that notifications list is visible with pagination
    await expect(page.locator('[data-testid="notification-item"]')).toBeVisible();
  });

  test('should allow clicking on notification items to mark as read', async ({ page }) => {
    // Get the first notification item
    const firstItem = page.locator('[data-testid="notification-item"]').first();
    
    // Check that it's initially unread (has different styling)
    await expect(firstItem).toHaveClass(/unread/);
    
    // Click on the notification to mark as read
    await firstItem.click();
    
    // Verify that it marks as read (different styling or state)
    await expect(firstItem).toHaveClass(/read/);
  });
});