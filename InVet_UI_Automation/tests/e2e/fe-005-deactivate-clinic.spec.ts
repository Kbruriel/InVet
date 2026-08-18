/**
 * TC-005-06 - Inactivar clínica
 * US-005 AC-005-03
 * 
 * Dado que hay clinicas activas en la lista
 * Cuando hago clic en "Inactivar" de una clinica
 * Entonces el estado cambia y la fila indica inactivo
 */

import { test, expect } from '@playwright/test';

import { authenticateAdmin } from '../helpers/auth';

test.beforeEach(async ({ page }) => {
  await authenticateAdmin(page);
});

test('TC-005-06: Inactivar clínica cambia estado', async ({ page }) => {
  await page.goto('/clinic-administration');

  const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
  expect(accessToken).toBeTruthy();

  const clinicName = `Clinica UIA Inactiva ${Date.now()}`;
  const createResponse = await page.request.post('http://localhost:8000/api/v1/clinics', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    data: {
      name: clinicName,
      description: 'Clinica de prueba para inactivacion automatizada',
      address: 'Calle Prueba 123',
      city: 'Ciudad Prueba',
      state: 'Estado Prueba',
      country: 'Mexico',
      postal_code: '12345',
      phone: '555-0101',
      email: `uia-${Date.now()}@example.com`,
    },
  });

  expect(createResponse.status()).toBe(201);

  await page.reload({ waitUntil: 'networkidle' });

  // Buscar la fila creada por esta prueba
  const row = page.locator('tr').filter({ has: page.getByText(clinicName) }).first();
  await expect(row).toBeVisible({ timeout: 15000 });

  const inactivateButton = row.getByRole('button', { name: /Inactivar/i });
  await expect(inactivateButton).toBeVisible();
  await inactivateButton.click();

  // Al desactivarla, la clinica deja de aparecer en el listado activo
  await expect(page.getByText(clinicName)).toHaveCount(0, { timeout: 15000 });
});
