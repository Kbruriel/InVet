/**
 * TC-005-10 - Responsive
 * US-005 AC-005-10
 * 
 * Dado que estoy en el panel de administracion
 * Cuando redimensiono la ventana a tamaño mobile
 * Entonces la interfaz se adapta correctamente sin desbordamiento
 */

import { test, expect } from '@playwright/test';

test('TC-005-10: Panel responsive en mobile', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  // Verificar en desktop primero
  await page.setViewportSize({ width: 1280, height: 720 });
  const heading = page.getByRole('heading', { name: /Administracion/i });
  await expect(heading).toBeVisible();
  
  // Redimensionar a mobile
  await page.setViewportSize({ width: 375, height: 667 });
  
  // Verificar que el contenido no se desborda horizontalmente
  const body = page.locator('body');
  const scrollWidth = await body.evaluate((el) => el.scrollWidth);
  const clientWidth = await body.evaluate((el) => el.clientWidth);
  
  expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 10); // Margen de 10px
  
  // Verificar que el heading sigue visible
  await expect(heading).toBeVisible();
});

test('TC-005-10b: Panel responsive en tablet', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  // Verificar en tablet
  await page.setViewportSize({ width: 768, height: 1024 });
  
  const heading = page.getByRole('heading', { name: /Administracion/i });
  await expect(heading).toBeVisible();
  
  // Verificar que no hay desbordamiento horizontal
  const body = page.locator('body');
  const scrollWidth = await body.evaluate((el) => el.scrollWidth);
  const clientWidth = await body.evaluate((el) => el.clientWidth);
  
  expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 10);
});
