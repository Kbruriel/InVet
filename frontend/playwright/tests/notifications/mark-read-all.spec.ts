import { test, expect } from '@playwright/test';

test.describe('Mark All Notifications as Read', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication 
    const ctx = page.context();
    await ctx.addCookies([
      { name: 'session_token', value: 'mock-token', domain: 'localhost', path: '/', httpOnly: true },
      { name: 'user_id', value: 'user-123', domain: 'localhost', path: '/', httpOnly: true }
    ]);
    await page.goto('/portal/notifications');
  });

  test('should mark all notifications as read and show success toast', async ({ page }) => {
    // Click on "Leer todas" button
    const readAllButton = page.getByRole('button', { name: 'Leer todas' });
    await readAllButton.click();
    
    // Check that a toast message appears confirming the action
    await expect(page.getByText('Notificaciones marcadas como leídas')).toBeVisible();
    
    // Verify that the list is now empty (since all are marked as read)
    await expect(page.locator('[data-testid="notification-item"]')).not.toBeVisible();
  });
});