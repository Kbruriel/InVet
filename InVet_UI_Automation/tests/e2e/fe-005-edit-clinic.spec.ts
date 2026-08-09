/**
 * TC-005-05 - Editar clínica
 * US-005 AC-005-02
 * 
 * Dado que hay clinicas en la lista
 * Cuando hago clic en "Editar" de una clinica
 * Entonces el formulario se llena con los datos existentes
 */

import { test, expect } from '@playwright/test';

test('TC-005-05: Editar clínica carga datos existentes', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  // Buscar boton de editar en la tabla
  const editButtons = page.getByRole('button', { name: /Editar/i });
  
  if (await editButtons.count() > 0) {
    await editButtons.first().click();
    
    // Verificar que el formulario se abre con datos precargados
    await expect(page.getByRole('heading', { name: /Editar Clinica/i })).toBeVisible();
    
    // Verificar que los campos tienen valores (no vacios)
    const nameInput = page.locator('input[name="name"]');
    const nameValue = await nameInput.inputValue();
    expect(nameValue.length).toBeGreaterThan(0);
  } else {
    test.skip(true, 'No hay clinicas para editar');
  }
});
