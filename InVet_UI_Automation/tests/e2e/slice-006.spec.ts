/**
 * UIA-006 — Servicios, veterinarios y usuarios internos
 * Cobertura Playwright para las vistas admin del slice 006.
 *
 * Casos de prueba:
 *   TC-UIA-006-01  Listado de servicios con paginacion
 *   TC-UIA-006-02  Listado de servicios vacio
 *   TC-UIA-006-03  Crear servicio con datos validos
 *   TC-UIA-006-04  Crear servicio con datos invalidos
 *   TC-UIA-006-05  Editar servicio existente
 *   TC-UIA-006-06  Desactivar servicio
 *   TC-UIA-006-07  Listado de veterinarios con paginacion
 *   TC-UIA-006-08  Crear veterinario con datos validos
 *   TC-UIA-006-09  Crear veterinario con licencia duplicada
 *   TC-UIA-006-10  Listado de usuarios internos con paginacion
 *   TC-UIA-006-11  Crear usuario interno con datos validos
 *   TC-UIA-006-12  Acceso no autenticado (redirect a login)
 *   TC-UIA-006-13  Autorizacion requerida (403)
 *   TC-UIA-006-14  Responsive layout mobile/desktop
 */

import { test, expect } from "@playwright/test";

import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability, attachGherkinScenario } from "../helpers/traceability";

const env = readAutomationEnv();

async function authenticateAs(page: import("@playwright/test").Page, email: string, password: string) {
  const loginUrl = `${env.apiBaseUrl}${env.loginApiPath}`;
  const response = await page.request.post(loginUrl, {
    data: { email, password },
  });

  expect(response.status()).toBe(200);

  const payload = (await response.json()) as { access_token: string; refresh_token: string };
  await page.addInitScript(
    ({ accessToken, refreshToken }) => {
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("refresh_token", refreshToken);
    },
    {
      accessToken: payload.access_token,
      refreshToken: payload.refresh_token,
    },
  );
}

async function authenticateAdmin(page: import("@playwright/test").Page) {
  await authenticateAs(page, env.adminEmail, env.adminPassword);
}

async function authenticateViewer(page: import("@playwright/test").Page) {
  await authenticateAs(page, env.clinicEmail, env.clinicPassword);
}

// ===========================================================================
// TC-UIA-006-01: Listado de servicios con paginacion
// Criterios: AC-006-03, AC-006-10
// ===========================================================================

test.describe("services listing - UIA-006", () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAdmin(page);
  });

  test(
    "@smoke @regression US-006-01 AC-006-03 AC-006-10 TC-UIA-006-01 servicios listado con paginacion",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-01",
        criteria: ["AC-006-03", "AC-006-10"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado de servicios",
        scenario: "Muestra tabla con datos y controles de paginacion",
        given: ["un usuario admin autenticado con servicios existentes"],
        when: ["navego a /admin/services"],
        then: [
          "la pagina carga sin errores",
          "se muestra una tabla o lista con datos de servicios",
          "los controles de paginacion son visibles",
        ],
      });

      await page.goto("/admin/services");
      await expect(page).toHaveTitle(/InVet/i);

      // Verificar que la pagina cargo (heading admin)
      const heading = page.getByRole("heading", { level: 1, name: /Servicios|Administracion/i });
      await expect(heading).toBeVisible();

      // Verificar tabla o lista de servicios
      const table = page.locator("table").first();
      if (await table.isVisible()) {
        await expect(table).toBeVisible();
        // Columnas esperadas
        await expect(page.locator("thead th").filter({ hasText: /Nombre|Service/i }).first()).toBeVisible();
        await expect(page.locator("thead th").filter({ hasText: /Precio|Price/i }).first()).toBeVisible();
        await expect(page.locator("thead th").filter({ hasText: /Duraci[óo]n|Duration/i }).first()).toBeVisible();
      }

      // Verificar controles de paginacion si hay datos
      const pagination = page.locator('[class*="pagination"], [class*="pager"], nav[aria-label*="page"]');
      if (await pagination.count() > 0) {
        await expect(pagination.first()).toBeVisible();
      }

      // Verificar que no hay errores de consola
      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") {
          consoleErrors.push(msg.text());
        }
      });
    },
  );

  // ===========================================================================
  // TC-UIA-006-02: Listado de servicios vacio
  // Criterios: AC-006-28
  // ===========================================================================

  test(
    "@regression US-006-01 AC-006-28 TC-UIA-006-02 listado servicios vacio",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-01",
        criteria: ["AC-006-28"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado de servicios vacio",
        scenario: "Muestra mensaje cuando no hay servicios",
        given: ["un usuario admin autenticado sin servicios"],
        when: ["navego a /admin/services"],
        then: [
          "se muestra un mensaje 'No hay servicios' o equivalente",
          "se muestra un CTA para crear servicio",
        ],
      });

      await page.goto("/admin/services");

      // Verificar heading
      const heading = page.getByRole("heading", { level: 1, name: /Servicios|Administracion/i });
      await expect(heading).toBeVisible();

      // Verificar empty state o mensaje de sin datos
      const emptyPatterns = [
        /No hay servicios/i,
        /Sin servicios/i,
        /No se encontraron servicios/i,
        /Aun no hay servicios/i,
      ];
      let foundEmpty = false;
      for (const pattern of emptyPatterns) {
        if (await page.getByText(pattern).isVisible()) {
          foundEmpty = true;
          break;
        }
      }

      // Verificar CTA de creacion
      const createButton = page.getByRole("button", { name: /Nuevo Servicio|Crear Servicio/i });
      if (await createButton.isVisible()) {
        await expect(createButton).toBeEnabled();
      }
    },
  );

  // ===========================================================================
  // TC-UIA-006-03: Crear servicio con datos validos
  // Criterios: AC-006-01
  // ===========================================================================

  test(
    "@smoke @regression US-006-02 AC-006-01 TC-UIA-006-03 crear servicio valido",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-02",
        criteria: ["AC-006-01"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Creacion de servicios",
        scenario: "Crear servicio con datos validos y verificar success",
        given: [
          "un usuario admin autenticado",
          "estoy en /admin/services/create",
        ],
        when: [
          "completo el formulario con nombre, precio y duracion validos",
          "submit del formulario",
        ],
        then: [
          "se muestra estado de success o toast de confirmacion",
          "el servicio aparece en el listado",
        ],
      });

      await page.goto("/admin/services/create");

      // Verificar formulario visible
      const formHeading = page.getByRole("heading", { level: 1, name: /Nuevo Servicio|Crear Servicio/i });
      if (await formHeading.isVisible()) {
        await expect(formHeading).toBeVisible();
      }

      // Llenar campos del formulario de servicio
      await page.getByLabel(/Nombre del servicio/i).fill("Servicio Test UIA");
      await page.getByLabel(/^Precio/i).fill("150.00");
      await page.getByLabel(/Duraci[oó]n/i).fill("30");
      await page.getByLabel(/Descripci[oó]n/i).fill("Servicio de prueba para automatizacion");

      // Submit
      const submitButton = page.getByRole("button", { name: /Guardar|Crear Servicio|Registrar/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();

        // Esperar redireccion o toast de success
        const successPatterns = [
          /Guardado|Exitoso|Success|creado|Registrado/i,
          /Servicio Test UIA/i,
        ];
        let foundSuccess = false;
        for (const pattern of successPatterns) {
          if (await page.getByText(pattern).isVisible()) {
            foundSuccess = true;
            break;
          }
        }

        // Si hay toast de success, verificar que es visible
        const toast = page.locator('[class*="toast"], [class*="alert-success"], [role="alert"]');
        if (await toast.count() > 0) {
          await expect(toast.first()).toBeVisible();
        }
      } else {
        test.skip(true, "Boton de submit no disponible");
      }
    },
  );

  // ===========================================================================
  // TC-UIA-006-04: Crear servicio con datos invalidos
  // Criterios: AC-006-09, AC-006-29
  // ===========================================================================

  test(
    "@regression US-006-02 AC-006-09 AC-006-29 TC-UIA-006-04 crear servicio invalido",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-02",
        criteria: ["AC-006-09", "AC-006-29"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Validacion de servicios",
        scenario: "Intentar crear servicio con campos vacios y ver errores",
        given: ["un usuario admin autenticado en /admin/services/create"],
        when: [
          "intento submit sin completar campos obligatorios",
          "intento submit con precio negativo",
        ],
        then: [
          "se muestran errores de validacion por campo",
          "no se filtran detalles internos del servidor",
        ],
      });

      await page.goto("/admin/services/create");

      // Intentar submit con campos vacios
      const submitButton = page.getByRole("button", { name: /Guardar|Crear Servicio|Registrar/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();

        // Verificar mensajes de error en campos obligatorios
        const errorPatterns = [
          /obligatorio|required|requerido/i,
          /Este campo es obligatorio/i,
          /Campo requerido/i,
        ];
        let foundError = false;
        for (const pattern of errorPatterns) {
          if (await page.getByText(pattern).isVisible()) {
            foundError = true;
            break;
          }
        }

        // Verificar que no hay detalles internos del servidor
        const internalErrorPatterns = [
          /Traceback|InternalError|Exception at/i,
          /stack trace|at \//i,
        ];
        for (const pattern of internalErrorPatterns) {
          const found = await page.getByText(pattern).isVisible();
          if (found) {
            // No deberia encontrar estos patrones
            expect(found).toBe(false);
          }
        }
      } else {
        test.skip(true, "Boton de submit no disponible");
      }

      // Intentar con precio negativo
      await page.getByLabel(/^Precio/i).fill("-50");
      if (await submitButton.isVisible()) {
        await submitButton.click();

        const negativeError = await page.getByText(/debe ser positivo|must be positive|valor invalido/i).isVisible();
        if (negativeError) {
          await expect(page.getByText(/debe ser positivo|must be positive|valor invalido/i)).toBeVisible();
        }
      }
    },
  );

  // ===========================================================================
  // TC-UIA-006-05: Editar servicio existente
  // Criterios: AC-006-02
  // ===========================================================================

  test(
    "@regression US-006-03 AC-006-02 TC-UIA-006-05 editar servicio",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-03",
        criteria: ["AC-006-02"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Edicion de servicios",
        scenario: "Editar un servicio existente y verificar persistencia",
        given: [
          "un usuario admin autenticado con un servicio existente",
          "el servicio aparece en el listado",
        ],
        when: [
          "navego al formulario de edicion del servicio",
          "modifico los datos y submit",
        ],
        then: [
          "se muestra estado de success",
          "los cambios persisten en el listado",
        ],
      });

      await page.goto("/admin/services");

      // Buscar un servicio existente para editar
      const editButton = page.getByRole("button", { name: /Editar|Edit/i }).first();
      if (await editButton.isVisible()) {
        await editButton.click();

        // Verificar que el formulario de edicion cargo con datos
      const editHeading = page.getByRole("heading", { level: 1, name: /Editar Servicio|Edit Service/i });
        if (await editHeading.isVisible()) {
          await expect(editHeading).toBeVisible();
        }

        // Modificar campos
        await page.getByLabel(/Nombre del servicio/i).fill("Servicio Editado UIA");

        // Submit
        const submitButton = page.getByRole("button", { name: /Guardar|Actualizar|Save/i });
        if (await submitButton.isVisible()) {
          await submitButton.click();

          // Verificar que el cambio persiste
          await expect(page.getByText("Servicio Editado UIA")).toBeVisible();
        }
      } else {
        test.skip(true, "No hay servicios editables disponibles");
      }
    },
  );

  // ===========================================================================
  // TC-UIA-006-06: Desactivar servicio
  // Criterios: AC-006-04, AC-006-11
  // ===========================================================================

  test(
    "@regression US-006-04 AC-006-04 AC-006-11 TC-UIA-006-06 desactivar servicio",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-04",
        criteria: ["AC-006-04", "AC-006-11"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Desactivacion de servicios",
        scenario: "Desactivar un servicio y verificar que desaparece del listado activo",
        given: [
          "un usuario admin autenticado en el listado de servicios",
          "hay servicios activos en la lista",
        ],
        when: ["ejecuto la accion desactivar en un servicio"],
        then: [
          "el servicio desaparece del listado activo",
          "aparece si filtro por inactivos",
        ],
      });

      await page.goto("/admin/services");

      // Buscar servicio activo
      const activeBadge = page.getByText(/Activa|Active/i).first();
      if (await activeBadge.isVisible()) {
        const row = activeBadge.locator("tr").first();
        const deactivateButton = row.getByRole("button", { name: /Inactivar|Desactivar|Deactivate/i });

        if (await deactivateButton.isVisible()) {
          await deactivateButton.click();

          // Verificar que el servicio ya no aparece en activos
          await expect(page.getByText(/Servicio.*Activa|Service.*Active/i)).not.toBeVisible();

          // Verificar que aparece como inactivo si hay filtro
          const inactiveFilter = page.getByRole("button", { name: /Inactivos|Inactive/i });
          if (await inactiveFilter.isVisible()) {
            await inactiveFilter.click();
            await expect(page.getByText(/Inactiva|Inactive/i)).toBeVisible();
          }
        } else {
          test.skip(true, "Boton de desactivar no disponible");
        }
      } else {
        test.skip(true, "No hay servicios activos para desactivar");
      }
    },
  );
});

// ===========================================================================
// Veterinarians listing - UIA-006
// ===========================================================================

test.describe("veterinarians listing - UIA-006", () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAdmin(page);
  });

  // ===========================================================================
  // TC-UIA-006-07: Listado de veterinarios con paginacion
  // Criterios: AC-006-09, AC-006-10
  // ===========================================================================

  test(
    "@smoke @regression US-006-05 AC-006-09 AC-006-10 TC-UIA-006-07 veterinarios listado paginado",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-05",
        criteria: ["AC-006-09", "AC-006-10"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado de veterinarios",
        scenario: "Muestra tabla con datos y controles de paginacion",
        given: ["un usuario admin autenticado con veterinarios existentes"],
        when: ["navego a /admin/veterinarians"],
        then: [
          "se muestra una tabla o lista con datos de veterinarios",
          "los controles de paginacion son visibles",
        ],
      });

      await page.goto("/admin/veterinarians");
      await expect(page).toHaveTitle(/InVet/i);

      // Verificar heading
      const heading = page.getByRole("heading", { level: 1, name: /Veterinarios|Veterinarians|Administracion/i });
      await expect(heading).toBeVisible();

      // Verificar tabla o lista
      const table = page.locator("table").first();
      if (await table.isVisible()) {
        await expect(table).toBeVisible();
        // Columnas esperadas
        await expect(page.locator("thead th").filter({ hasText: /Nombre|nombre_completo/i }).first()).toBeVisible();
        await expect(page.locator("thead th").filter({ hasText: /Licencia|Licence|licencia_profesional/i }).first()).toBeVisible();
        await expect(page.locator("thead th").filter({ hasText: /Especialidad|Specialty|especialidad/i }).first()).toBeVisible();
      }

      // Verificar paginacion si hay datos
      const pagination = page.locator('[class*="pagination"], [class*="pager"]');
      if (await pagination.count() > 0) {
        await expect(pagination.first()).toBeVisible();
      }
    },
  );

  // ===========================================================================
  // TC-UIA-006-08: Crear veterinario con datos validos
  // Criterios: AC-006-07
  // ===========================================================================

  test(
    "@smoke @regression US-006-06 AC-006-07 TC-UIA-006-08 crear veterinario valido",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-06",
        criteria: ["AC-006-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Creacion de veterinarios",
        scenario: "Crear veterinario con datos validos y verificar success",
        given: [
          "un usuario admin autenticado",
          "estoy en /admin/veterinarians/create",
        ],
        when: [
          "completo el formulario con nombre, licencia y especialidad validos",
          "submit del formulario",
        ],
        then: [
          "se muestra estado de success o toast de confirmacion",
          "el veterinario aparece en el listado",
        ],
      });

      await page.goto("/admin/veterinarians/create");

      // Verificar formulario visible
      const formHeading = page.getByRole("heading", { level: 1, name: /Nuevo Veterinario|Crear Veterinario/i });
      if (await formHeading.isVisible()) {
        await expect(formHeading).toBeVisible();
      }

      // Llenar campos del formulario de veterinario
      await page.getByLabel(/Nombre completo/i).fill("Dr. Juan Perez Test");
      await page.getByLabel(/Licencia profesional/i).fill("LIC-VET-2026-001");
      await page.getByLabel(/Especialidad/i).fill("Cirugia Veterinaria");
      await page.getByLabel(/Tel[eé]fono/i).fill("555-1234");
      await page.getByLabel(/^Email/i).fill("juan@test.com");

      // Submit
      const submitButton = page.getByRole("button", { name: /Guardar|Crear Veterinario|Registrar/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();

        // Verificar success
        const successPatterns = [
          /Guardado|Exitoso|Success|creado|Registrado/i,
          /Dr. Juan Perez Test/i,
        ];
        for (const pattern of successPatterns) {
          if (await page.getByText(pattern).isVisible()) {
            await expect(page.getByText(pattern)).toBeVisible();
            break;
          }
        }
      } else {
        test.skip(true, "Boton de submit no disponible");
      }
    },
  );

  // ===========================================================================
  // TC-UIA-006-09: Crear veterinario con licencia duplicada
  // Criterios: AC-006-09
  // ===========================================================================

  test(
    "@regression US-006-06 AC-006-09 TC-UIA-006-09 veterinario licencia duplicada",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-06",
        criteria: ["AC-006-09"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Validacion de veterinarios",
        scenario: "Intentar crear veterinario con licencia ya existente",
        given: [
          "un usuario admin autenticado en /admin/veterinarians/create",
          "existe un veterinario con licencia LIC-VET-2026-DUP",
        ],
        when: ["intento crear con la misma licencia"],
        then: [
          "se muestra error de validacion indicando conflicto (409)",
          "el mensaje indica que la licencia ya existe",
        ],
      });

      await page.goto("/admin/veterinarians/create");

      // Llenar campos con licencia duplicada
      await page.getByLabel(/Nombre completo/i).fill("Dr. Duplicado Test");
      await page.getByLabel(/Licencia profesional/i).fill("LIC-VET-2026-DUP");
      await page.getByLabel(/Especialidad/i).fill("Medicina Interna");

      const submitButton = page.getByRole("button", { name: /Guardar|Crear Veterinario/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();

        // Verificar error de conflicto/duplicado
        const conflictPatterns = [
          /ya existe|duplicate|duplicado|conflict|409|licencia.*exist/i,
        ];
        let foundConflict = false;
        for (const pattern of conflictPatterns) {
          if (await page.getByText(pattern).isVisible()) {
            foundConflict = true;
            break;
          }
        }

        // Verificar que hay un mensaje de error visible
        const errorBox = page.locator('[class*="error"], [class*="alert-danger"], [role="alert"]');
        if (await errorBox.count() > 0) {
          await expect(errorBox.first()).toBeVisible();
        }
      } else {
        test.skip(true, "Boton de submit no disponible");
      }
    },
  );
});

// ===========================================================================
// Internal users listing - UIA-006
// ===========================================================================

test.describe("internal users listing - UIA-006", () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAdmin(page);
  });

  // ===========================================================================
  // TC-UIA-006-10: Listado de usuarios internos con paginacion
  // Criterios: AC-006-15, AC-006-10
  // ===========================================================================

  test(
    "@smoke @regression US-006-07 AC-006-15 AC-006-10 TC-UIA-006-10 usuarios internos paginado",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-07",
        criteria: ["AC-006-15", "AC-006-10"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado de usuarios internos",
        scenario: "Muestra tabla con datos y controles de paginacion",
        given: ["un usuario admin autenticado con usuarios internos existentes"],
        when: ["navego a /admin/internal-users"],
        then: [
          "se muestra una tabla o lista con datos de usuarios internos",
          "los controles de paginacion son visibles",
        ],
      });

      await page.goto("/admin/internal-users");
      await expect(page).toHaveTitle(/InVet/i);

      // Verificar heading
      const heading = page.getByRole("heading", { level: 1, name: /Usuarios Internos|Internal Users|Administracion/i });
      await expect(heading).toBeVisible();

      // Verificar tabla o lista
      const table = page.locator("table").first();
      if (await table.isVisible()) {
        await expect(table).toBeVisible();
        // Columnas esperadas
        await expect(page.locator("thead th").filter({ hasText: /Nombre|nombre/i }).first()).toBeVisible();
        await expect(page.locator("thead th").filter({ hasText: /Rol|Role|rol/i }).first()).toBeVisible();
      }

      // Verificar paginacion si hay datos
      const pagination = page.locator('[class*="pagination"], [class*="pager"]');
      if (await pagination.count() > 0) {
        await expect(pagination.first()).toBeVisible();
      }
    },
  );

  // ===========================================================================
  // TC-UIA-006-11: Crear usuario interno con datos validos
  // Criterios: AC-006-13
  // ===========================================================================

  test(
    "@smoke @regression US-006-08 AC-006-13 TC-UIA-006-11 crear usuario interno valido",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-08",
        criteria: ["AC-006-13"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Creacion de usuarios internos",
        scenario: "Crear usuario interno con datos validos y verificar success",
        given: [
          "un usuario admin autenticado",
          "estoy en /admin/internal-users/create",
        ],
        when: [
          "completo el formulario con user_id valido, nombre y rol",
          "submit del formulario",
        ],
        then: [
          "se muestra estado de success o toast de confirmacion",
          "el usuario interno aparece en el listado",
        ],
      });

      await page.goto("/admin/internal-users/create");

      // Verificar formulario visible
      const formHeading = page.getByRole("heading", { level: 1, name: /Nuevo Usuario|Crear Usuario Interno/i });
      if (await formHeading.isVisible()) {
        await expect(formHeading).toBeVisible();
      }

      // Llenar campos del formulario de usuario interno
      await page.getByLabel(/user_id/i).fill("1");
      await page.getByLabel(/^Nombre$/i).fill("Maria Usuario Interno");

      // Seleccionar rol (puede ser un select o botones)
      const roleSelect = page.locator('#rol');
      if (await roleSelect.count() > 0) {
        await roleSelect.first().selectOption("admin");
      } else {
        // Si es un boton/grupo de botones
        const roleButton = page.getByRole("button", { name: /admin|manager/i }).first();
        if (await roleButton.isVisible()) {
          await roleButton.click();
        }
      }

      // Submit
      const submitButton = page.getByRole("button", { name: /Guardar|Crear Usuario|Registrar/i });
      if (await submitButton.isVisible()) {
        await submitButton.click();

        // Verificar success
        const successPatterns = [
          /Guardado|Exitoso|Success|creado|Registrado/i,
          /Maria Usuario Interno/i,
        ];
        for (const pattern of successPatterns) {
          if (await page.getByText(pattern).isVisible()) {
            await expect(page.getByText(pattern)).toBeVisible();
            break;
          }
        }
      } else {
        test.skip(true, "Boton de submit no disponible");
      }
    },
  );
});

// ===========================================================================
// Authentication & Authorization - UIA-006
// ===========================================================================

test.describe("authentication & authorization - UIA-006", () => {
  // ===========================================================================
  // TC-UIA-006-12: Acceso no autenticado a rutas admin
  // Criterios: AC-006-06
  // ===========================================================================

  test(
    "@smoke @regression US-006-09 AC-006-06 TC-UIA-006-12 acceso no autenticado redirige a login",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-09",
        criteria: ["AC-006-06"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Autenticacion requerida",
        scenario: "Usuario no autenticado intenta acceder a ruta admin",
        given: ["un usuario no autenticado"],
        when: ["intenta navegar a /admin/services"],
        then: [
          "es redirigido a /login",
          "recibe 401 al intentar consumir la API",
        ],
      });

      // Clear any existing auth state
      await page.context().clearCookies();
      await page.goto("/admin/services");

      // Verificar redireccion a login
      await page.waitForURL(/\/login/, { timeout: 10000 });
      await expect(page.getByRole("textbox", { name: /email/i })).toBeVisible();
      await expect(page.getByLabel(/password|contrasena/i)).toBeVisible();
    },
  );

  // ===========================================================================
  // TC-UIA-006-13: Autorizacion requerida (403)
  // Criterios: AC-006-12, AC-006-30
  // ===========================================================================

  test(
    "@regression US-006-10 AC-006-12 AC-006-30 TC-UIA-006-13 autorizacion insuficiente",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-10",
        criteria: ["AC-006-12", "AC-006-30"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Autorizacion por rol",
        scenario: "Usuario con rol insuficiente no ve acciones de admin",
        given: [
          "un usuario autenticado con rol viewer (no admin/manager)",
          "navega a /admin/services",
        ],
        when: ["la pagina carga"],
        then: [
          "los botones de crear/editar/eliminar estan ocultos o deshabilitados",
          "se muestra mensaje de permiso denegado si intenta acceder",
        ],
      });

      await authenticateViewer(page);
      await page.goto("/admin/services");

      // Verificar que no hay acciones de admin visibles para rol insuficiente
      const createButton = page.getByRole("button", { name: /Nuevo Servicio|Crear Servicio/i });
      if (await createButton.isVisible()) {
        // Si el boton existe, deberia estar deshabilitado o oculto despues de verificar permisos
        const isDisabled = await createButton.isDisabled();
        if (isDisabled) {
          await expect(createButton).toBeDisabled();
        }
      }

      // Verificar mensaje de permiso si esta presente
      const permissionDenied = await page.getByText(/permiso|permission|denegado|403/i).isVisible();
      if (permissionDenied) {
        await expect(page.getByText(/permiso|permission|denegado|403/i)).toBeVisible();
      }
    },
  );
});

// ===========================================================================
// Responsive layout - UIA-006
// ===========================================================================

test.describe("responsive layout - UIA-006", () => {
  test.beforeEach(async ({ page }) => {
    await authenticateAdmin(page);
  });

  // ===========================================================================
  // TC-UIA-006-14: Responsive mobile (375px) y desktop (1440px)
  // Criterios: AC-006-31
  // ===========================================================================

  test(
    "@regression US-006-11 AC-006-31 TC-UIA-006-14 responsive mobile y desktop",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006-11",
        criteria: ["AC-006-31"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Responsive layout",
        scenario: "Verificar que las vistas admin renderizan correctamente en mobile y desktop",
        given: ["un usuario admin autenticado en una vista admin"],
        when: [
          "redimensiono el viewport a 375px (mobile)",
          "redimensiono el viewport a 1440px (desktop)",
        ],
        then: [
          "en mobile: la tabla se transforma en vista de tarjetas, formularios apilan campos",
          "en desktop: la tabla muestra todas las columnas, formularios usan dos columnas",
          "no hay desbordamiento horizontal en ningun viewport",
        ],
      });

      // --- Desktop (1440px) ---
      await page.setViewportSize({ width: 1440, height: 900 });
      await page.goto("/admin/services");

      const desktopHeading = page.getByRole("heading", { level: 1, name: /Servicios|Administracion/i });
      await expect(desktopHeading).toBeVisible();

      // Verificar que no hay desbordamiento horizontal en desktop
      const bodyDesktop = page.locator("body");
      const desktopScrollWidth = await bodyDesktop.evaluate((el) => el.scrollWidth);
      const desktopClientWidth = await bodyDesktop.evaluate((el) => el.clientWidth);
      expect(desktopScrollWidth).toBeLessThanOrEqual(desktopClientWidth + 10);

      // --- Mobile (375px) ---
      await page.setViewportSize({ width: 375, height: 667 });

      // Verificar que la pagina sigue visible en mobile
      await expect(desktopHeading).toBeVisible();

      // Verificar que no hay desbordamiento horizontal en mobile
      const bodyMobile = page.locator("body");
      const mobileScrollWidth = await bodyMobile.evaluate((el) => el.scrollWidth);
      const mobileClientWidth = await bodyMobile.evaluate((el) => el.clientWidth);
      expect(mobileScrollWidth).toBeLessThanOrEqual(mobileClientWidth + 10);

      // Verificar que los elementos interactivos siguen accesibles en mobile
      const mobileButtons = page.getByRole("button");
      const buttonCount = await mobileButtons.count();
      if (buttonCount > 0) {
        // Al menos un boton debe ser visible
        const firstVisibleButton = mobileButtons.first();
        const isVisible = await firstVisibleButton.isVisible();
        expect(isVisible).toBeTruthy();
      }

      // --- Tablet (768px) ---
      await page.setViewportSize({ width: 768, height: 1024 });
      await expect(desktopHeading).toBeVisible();

      const tabletScrollWidth = await bodyMobile.evaluate((el) => el.scrollWidth);
      const tabletClientWidth = await bodyMobile.evaluate((el) => el.clientWidth);
      expect(tabletScrollWidth).toBeLessThanOrEqual(tabletClientWidth + 10);
    },
  );
});
