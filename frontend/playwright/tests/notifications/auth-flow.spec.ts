import { test, expect } from '@playwright/test';

test.describe('Notification Center Auth Flow', () => {
  test('should redirect to login when accessing without authentication', async ({ page }) => {
    // Visit the notifications page without authentication
    await page.goto('/portal/notifications');
    
    // Should be redirected to login with return URL
    await expect(page).toHaveURL(/login\?returnUrl=\/portal\/notifications/);
  });

  test('should redirect to login when session expires', async ({ page }) => {
    // Visit the notifications page with expired token
    const ctx = page.context();  
    await ctx.addCookies([
      { name: 'session_token', value: 'expired-token', domain: 'localhost', path: '/', httpOnly: true },
      { name: 'user_id', value: 'user-123', domain: 'localhost', path: '/', httpOnly: true }
    ]);
    
    await page.goto('/portal/notifications');
    
    // Should be redirected to login page
    await expect(page).toHaveURL(/login\?returnUrl=\/portal\/notifications/);
  });

  test('should show error banner when API returns 401', async ({ page }) => {
    // Mock authentication but make API return 401
    const ctx = page.context();  
    await ctx.addCookies([
      { name: 'session_token', value: 'mock-token', domain: 'localhost', path: '/', httpOnly: true },
      { name: 'user_id', value: 'user-123', domain: 'localhost', path: '/', httpOnly: true }
    ]);
    
    await page.route('**/api/v1/notifications/**', (route) => {
      if (route.request().method() === 'GET') {
        return route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Unauthorized' })
        });
      }
      route.continue();
    });
    
    await page.goto('/portal/notifications');
    
    // Error banner should be visible
    await expect(page.locator('[data-testid="error-banner"]')).toBeVisible();
  });
});