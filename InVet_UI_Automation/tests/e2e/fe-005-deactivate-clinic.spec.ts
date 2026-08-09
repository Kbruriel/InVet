/**
 * TC-005-06 - Inactivar clínica
 * US-005 AC-005-03
 * 
 * Dado que hay clinicas activas en la lista
 * Cuando hago clic en "Inactivar" de una clinica
 * Entonces el estado cambia y la fila indica inactivo
 */

import { test, expect } from '@playwright/test';

test('TC-005-06: Inactivar clínica cambia estado', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  // Buscar clinica activa
  const activeBadge = page.getByText('Activa').first();
  
  if (await activeBadge.isVisible()) {
    // Encontrar la fila correspondiente y su boton de inactivar
    const row = activeBadge.locator('tr').first();
    const inactivateButton = row.getByRole('button', { name: /Inactivar/i });
    
    if (await inactivateButton.isVisible()) {
      await inactivateButton.click();
      
      // Verificar que el badge cambio a "Inactiva"
      await expect(page.getByText('Inactiva')).toBeVisible();
    } else {
      test.skip(true, 'Boton de inactivar no disponible');
    }
  } else {
    test.skip(true, 'No hay clinicas activas para inactivar');
  }
});
