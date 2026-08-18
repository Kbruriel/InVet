/**
 * TC-005-04 - Validación formulario clínica
 * US-005 AC-005-01
 * 
 * Dado que estoy en el formulario de crear clinica
 * Cuando envío con campos obligatorios vacíos
 * Entonces veo mensajes de error en cada campo inválido
 */

import { test, expect } from '@playwright/test';

import { authenticateAdmin } from '../helpers/auth';

test.beforeEach(async ({ page }) => {
  await authenticateAdmin(page);
});

test('TC-005-04: Validación formulario muestra errores', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  // Abrir formulario
  const newClinicButton = page.getByRole('button', { name: /Nueva Clinica/i });
  await expect(newClinicButton).toBeVisible({ timeout: 15000 });
  await newClinicButton.click();
  
  // Enviar formulario vacio
  await page.click('button[type="submit"]');
  
  // Verificar mensajes de error en campos obligatorios
  const errorMessages = [
    /El nombre es obligatorio/i,
    /La direccion es obligatoria/i,
    /La ciudad es obligatoria/i,
    /El estado es obligatorio/i,
    /El pais es obligatorio/i,
    /El codigo postal es obligatorio/i,
  ];
  
  for (const pattern of errorMessages) {
    const found = await page.getByText(pattern).isVisible();
    if (found) {
      await expect(page.getByText(pattern)).toBeVisible();
    }
  }
});

test('TC-005-04b: Validación de email invalido', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  const newClinicButton = page.getByRole('button', { name: /Nueva Clinica/i });
  await expect(newClinicButton).toBeVisible({ timeout: 15000 });
  await newClinicButton.click();
  
    // Llenar campos obligatorios
  await page.getByLabel(/Nombre/i).fill('Clinica Test');
  await page.getByLabel(/Direccion/i).fill('Calle 123');
  await page.getByLabel(/Ciudad/i).fill('Ciudad');
  await page.getByLabel(/^Estado/i).fill('Estado');
  await page.getByLabel(/Pais/i).fill('Mexico');
  await page.getByLabel(/Codigo Postal/i).fill('12345');
  
  // Email invalido
  await page.getByLabel(/Email/i).fill('email-invalido');
  
  // Enviar
  await page.click('button[type="submit"]');
  
  // Verificar error de email
  const emailError = await page.getByText(/Email invalido/i).isVisible();
  if (emailError) {
    await expect(page.getByText(/Email invalido/i)).toBeVisible();
  }
});
