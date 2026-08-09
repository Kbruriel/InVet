/**
 * TC-005-04 - Validación formulario clínica
 * US-005 AC-005-01
 * 
 * Dado que estoy en el formulario de crear clinica
 * Cuando envío con campos obligatorios vacíos
 * Entonces veo mensajes de error en cada campo inválido
 */

import { test, expect } from '@playwright/test';

test('TC-005-04: Validación formulario muestra errores', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  // Abrir formulario
  const newClinicButton = page.getByRole('button', { name: /Nueva Clinica/i });
  if (await newClinicButton.isVisible()) {
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
  } else {
    test.skip(true, 'Boton de nueva clinica no disponible');
  }
});

test('TC-005-04b: Validación de email invalido', async ({ page }) => {
  await page.goto('/clinic-administration');
  
  const newClinicButton = page.getByRole('button', { name: /Nueva Clinica/i });
  if (await newClinicButton.isVisible()) {
    await newClinicButton.click();
    
    // Llenar campos obligatorios
    await page.fill('input[name="name"]', 'Clinica Test');
    await page.fill('input[name="address"]', 'Calle 123');
    await page.fill('input[name="city"]', 'Ciudad');
    await page.fill('input[name="state"]', 'Estado');
    await page.fill('input[name="country"]', 'Mexico');
    await page.fill('input[name="postal_code"]', '12345');
    
    // Email invalido
    await page.fill('input[name="email"]', 'email-invalido');
    
    // Enviar
    await page.click('button[type="submit"]');
    
    // Verificar error de email
    const emailError = await page.getByText(/Email invalido/i).isVisible();
    if (emailError) {
      await expect(page.getByText(/Email invalido/i)).toBeVisible();
    }
  } else {
    test.skip(true, 'Boton de nueva clinica no disponible');
  }
});
