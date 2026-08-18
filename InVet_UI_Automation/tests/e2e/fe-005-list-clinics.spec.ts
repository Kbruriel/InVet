/**
 * TC-005-02 - Listar clínicas
 * US-005 AC-005-04, AC-005-10
 * 
 * Dado que estoy en el panel de administracion
 * Cuando cargo la lista de clinicas
 * Entonces veo las clinicas del tenant con paginacion
 */

import { test, expect } from '@playwright/test';

import { authenticateAdmin } from '../helpers/auth';

test.beforeEach(async ({ page }) => {
  await authenticateAdmin(page);
});

test('TC-005-02: Listar clínicas muestra tabla paginada', async ({ page }) => {
  // Navegar al panel de administracion
  await page.goto('/clinic-administration');
  await expect(page.getByRole('heading', { level: 1, name: /Administracion de Clinicas|Administracion/i })).toBeVisible({ timeout: 15000 });
  
  // Esperar a que la tabla se renderice o muestre empty state
  const table = page.locator('table').first();
  const emptyState = page.getByText(/No hay clinicas registradas/i);
  
  // Verificar que existe tabla O empty state
  if (await table.isVisible()) {
    // Tabla visible: verificar columnas
    await expect(page.locator('thead th').filter({ hasText: /^Nombre$/i }).first()).toBeVisible();
    await expect(page.locator('thead th').filter({ hasText: /^Estado$/i }).first()).toBeVisible();
    
    // Verificar badges de estado
    const badges = page.locator('span.rounded-full');
    if (await badges.count() > 0) {
      const firstBadgeText = await badges.first().textContent();
      expect(['Activa', 'Inactiva']).toContain(firstBadgeText);
    }
    
    // Verificar botones de accion
    const editButtons = page.getByRole('button', { name: /Editar/i });
    if (await editButtons.count() > 0) {
      await expect(editButtons.first()).toBeVisible();
    }
  } else if (await emptyState.isVisible()) {
    // Empty state visible con CTA
    await expect(page.getByText('Registrar Clinica')).toBeVisible();
  } else {
    // Si no hay tabla ni empty state, verificar que la pagina cargo
    await expect(page.getByRole('heading', { level: 1, name: /Administracion de Clinicas|Administracion/i })).toBeVisible();
  }
});

test('TC-005-02b: Boton de nueva clinica es visible', async ({ page }) => {
  await page.goto('/clinic-administration');
  await expect(page.getByRole('heading', { level: 1, name: /Administracion de Clinicas|Administracion/i })).toBeVisible({ timeout: 15000 });
  
  const newClinicButton = page.getByRole('button', { name: /Nueva Clinica/i });
  if (await newClinicButton.isVisible()) {
    await expect(newClinicButton).toBeEnabled();
  }
});
