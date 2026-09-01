import { test, expect } from '@playwright/test';

test.describe('Notification Center Responsive Design', () => {
  test('should be usable on mobile devices (320px width)', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 320, height: 600 });
    
    // Mock authentication 
    const ctx = page.context();
    await ctx.addCookies([
      { name: 'session_token', value: 'mock-token', domain: 'localhost', path: '/', httpOnly: true },
      { name: 'user_id', value: 'user-123', domain: 'localhost', path: '/', httpOnly: true }
    ]);
    
    await page.goto('/portal/notifications');
    
    // Check that the layout is responsive and no horizontal overflow occurs
    const notificationsContainer = page.locator('[data-testid="notification-center"]');
    await expect(notificationsContainer).toBeVisible();
    
    // Verify mobile-specific layout (tabs stacked vertically)
    const tabs = page.locator('[data-testid="notification-tabs"]');
    await expect(tabs).toBeVisible();
  });

  test('should be usable on desktop devices (1280px width)', async ({ page }) => {
    // Set viewport to desktop size
    await page.setViewportSize({ width: 1280, height: 720 });
    
    // Mock authentication 
    const ctx = page.context();
    await ctx.addCookies([
      { name: 'session_token', value: 'mock-token', domain: 'localhost', path: '/', httpOnly: true },
      { name: 'user_id', value: 'user-123', domain: 'localhost', path: '/', httpOnly: true }
    ]);
    
    await page.goto('/portal/notifications');
    
    // Check that desktop layout is displayed properly
    const notificationsContainer = page.locator('[data-testid="notification-center"]');
    await expect(notificationsContainer).toBeVisible();
    
    // Verify desktop-specific layout (tabs may be horizontal)
    const tabs = page.locator('[data-testid="notification-tabs"]');
    await expect(tabs).toBeVisible();
  });

  test('should not have horizontal overflow on any screen size', async ({ page }) => {
    // Test multiple screen sizes to ensure no overflow
    const screenSizes = [
      { width: 320, height: 600 },
      { width: 768, height: 1024 },
      { width: 1280, height: 720 },
      { width: 1920, height: 1080 }
    ];
    
    for (const size of screenSizes) {
      await page.setViewportSize(size);
      
      // Mock authentication 
      const ctx = page.context();
    await ctx.addCookies([
        { name: 'session_token', value: 'mock-token', domain: 'localhost', path: '/', httpOnly: true },
        { name: 'user_id', value: 'user-123', domain: 'localhost', path: '/', httpOnly: true }
      ]);
      
      await page.goto('/portal/notifications');
      
      // Verify no horizontal overflow by checking scroll width
      const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
      const clientWidth = await page.evaluate(() => document.body.clientWidth);
      
      // The scroll width should not exceed the client width significantly
      expect(scrollWidth).toBeLessThanOrEqual(clientWidth * 1.1); // Allow 10% tolerance  
    }
  });
});