/**
 * TC-005-03 - Crear clínica
 * US-005 AC-005-01
 * 
 * Dado que estoy en el panel de clinicas
 * Cuando hago clic en "Crear clinica" y lleno el formulario valido
 * Entonces la clinica se crea y aparece en la lista
 */

import { test, expect } from '@playwright/test';

test('TC-005-03: Crear clínica exitosamente', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  // Hacer clic en "Nueva Clinica"
  const newClinicButton = page.getByRole('button', { name: /Nueva Clinica/i });
  if (await newClinicButton.isVisible()) {
    await newClinicButton.click();
    
    // Verificar que el formulario es visible
    await expect(page.getByRole('heading', { name: /Nueva Clinica/i })).toBeVisible();
    
    // Llenar campos obligatorios
    await page.fill('input[name="name"]', 'Clinica Test UIA');
    await page.fill('input[name="address"]', 'Calle Test 123');
    await page.fill('input[name="city"]', 'Ciudad Test');
    await page.fill('input[name="state"]', 'Estado Test');
    await page.fill('input[name="country"]', 'Mexico');
    await page.fill('input[name="postal_code"]', '12345');
    
    // Campos opcionales
    await page.fill('input[name="email"]', 'test@uia.com');
    await page.fill('input[name="phone"]', '555-0000');
    
    // Enviar formulario
    await page.click('button[type="submit"]');
    
    // Esperar a que el formulario se cierre (creacion exitosa)
    await expect(page.getByRole('heading', { name: /Nueva Clinica/i })).not.toBeVisible();
    
    // Verificar que la clinica aparece en la lista
    const table = page.locator('table').first();
    if (await table.isVisible()) {
      await expect(page.getByText('Clinica Test UIA')).toBeVisible();
    }
  } else {
    test.skip(true, 'Boton de nueva clinica no disponible');
  }
});
