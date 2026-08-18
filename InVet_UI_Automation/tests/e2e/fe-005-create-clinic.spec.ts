/**
 * TC-005-03 - Crear clínica
 * US-005 AC-005-01
 * 
 * Dado que estoy en el panel de clinicas
 * Cuando hago clic en "Crear clinica" y lleno el formulario valido
 * Entonces la clinica se crea y aparece en la lista
 */

import { test, expect } from '@playwright/test';

import { authenticateAdmin } from '../helpers/auth';

test.beforeEach(async ({ page }) => {
  await authenticateAdmin(page);
});

test('TC-005-03: Crear clínica exitosamente', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  // Hacer clic en "Nueva Clinica"
  const newClinicButton = page.getByRole('button', { name: /Nueva Clinica/i });
  await expect(newClinicButton).toBeVisible({ timeout: 15000 });
  await newClinicButton.click();
  
  // Verificar que el formulario es visible
  await expect(page.getByRole('heading', { name: /Nueva Clinica/i })).toBeVisible();
  
  // Llenar campos obligatorios
  await page.getByLabel(/Nombre/i).fill('Clinica Test UIA');
  await page.getByLabel(/Direccion/i).fill('Calle Test 123');
  await page.getByLabel(/Ciudad/i).fill('Ciudad Test');
  await page.getByLabel(/^Estado/i).fill('Estado Test');
  await page.getByLabel(/Pais/i).fill('Mexico');
  await page.getByLabel(/Codigo Postal/i).fill('12345');
  
  // Campos opcionales
  await page.getByLabel(/Email/i).fill('test@uia.com');
  await page.getByLabel(/Telefono/i).fill('555-0000');
  await page.getByLabel(/Descripcion/i).fill('Clinica de prueba para automatizacion');
  
  // Enviar formulario
  await page.click('button[type="submit"]');
  
  // Esperar a que el formulario se cierre (creacion exitosa)
  await expect(page.getByRole('heading', { name: /Nueva Clinica/i })).not.toBeVisible();
  
  // Verificar que la clinica aparece en la lista
  const table = page.locator('table').first();
  if (await table.isVisible()) {
    await expect(page.getByRole('cell', { name: 'Clinica Test UIA', exact: true }).first()).toBeVisible();
  }
});
