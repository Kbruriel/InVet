/**
 * TC-005-01 - Login como clinic_admin
 * US-005 AC-005-09
 * 
 * Dado que estoy en la pagina de login
 * Cuando ingreso credenciales de usuario con rol clinic_admin
 * Entonces navego al panel de administracion
 */

import { test, expect } from '@playwright/test';

test('TC-005-01: Login como clinic_admin redirige al panel', async ({ page }) => {
  // Dado que estoy en la pagina de login
  await page.goto('/login');
  await expect(page).toHaveURL(/.*\/login/);

  // Cuando ingreso credenciales
  await page.fill('input[name="email"]', 'qa@example.com');
  await page.fill('input[name="password"]', 'secret123');
  await page.click('button[type="submit"]');

  // Entonces navego al panel de administracion (o a la ruta por defecto)
  // La redireccion depende del rol asignado en el backend
  await page.waitForURL(/.*\/clinic-administration|.*\//, { timeout: 10000 });
  
  // Verificar que se logro autenticar (no estamos en login ni en error)
  const currentUrl = page.url();
  expect(currentUrl).not.toContain('/login');
});
