import { test, expect } from '@playwright/test';

test.describe('Notification Badge', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication 
  const context = page.context();  
  await context.addCookies([
    { name: 'session_id', value: 'test-session-token-value', domain: 'localhost', path: '/' }
  ]);
  });

  test('should hide badge when count is zero', async ({ page }) => {
    await page.goto('/portal/notifications');
    
    // Badge should be hidden when count is 0
    const badge = page.locator('[data-testid="notification-badge"]');
    await expect(badge).not.toBeVisible();
  });

  test('should show badge with count when notifications exist', async ({ page }) => {
    await page.goto('/portal/notifications');
    
    // Mock having unread notifications by intercepting the API
    await page.route('**/api/v1/notifications/unread-count', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ count: 5 })
      });
    });
    
    // Refresh page to fetch new data
    await page.reload();
    
    // Badge should be visible with count
    const badge = page.locator('[data-testid="notification-badge"]');
    await expect(badge).toBeVisible();
    await expect(badge).toContainText('5');
  });
});