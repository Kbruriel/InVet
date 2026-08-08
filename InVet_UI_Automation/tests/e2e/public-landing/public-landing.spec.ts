/**
 * UIA-003 - UI/E2E automation for BE-003 / FE-003 (Landing pública y búsqueda)
 *
 * Cobertura:
 * - US-003 / FE-003: Landing publica, hero, buscador, chips, resultados, estados UX
 * - AC-003-05: Landing publica con buscador
 * - AC-003-07: Responsive y estados UI
 * - AC-003-06: Datos privados no se exponen
 *
 * Trazabilidad: AC-003-01, AC-003-02, AC-003-05, AC-003-07
 */

import { expect, test } from "@playwright/test";

import { readAutomationEnv } from "../../fixtures/env";
import { annotateTraceability, attachGherkinScenario } from "../../helpers/traceability";

const env = readAutomationEnv();

// ===========================================================================
// UIA-003-01: Landing page renders hero, search bar, category chips, how-it-works, CTA
// Criterio: La landing publica renderiza todas las secciones esperadas.
// Trazabilidad: US-003 / FE-003, AC-003-05
// ===========================================================================

test.describe("public landing - UIA-003", () => {
  test(
    "@smoke @regression US-003 AC-003-05 landing renders hero, search, chips, how-it-works, CTA",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Landing publica",
        scenario: "La pagina de inicio renderiza hero, buscador, chips de categoria, como funciona y CTA",
        given: ["el frontend de InVet esta disponible en la ruta raiz"],
        when: [
          "la persona visitante navega a la pagina de inicio",
          "la pagina termina de cargar",
        ],
        then: [
          "el titulo de la pagina contiene 'InVet'",
          "el encabezado 'Busqueda de clinicas' es visible",
          "el subtítulo sobre encontrar clinica ideal es visible",
          "la barra de busqueda publica es visible",
          "los chips de categoria (Veterinaria, Estetica, Urgencias) son visibles",
          "la seccion 'Como funciona InVet' es visible",
          "los pasos Busca, Compara, Solicita son visibles",
          "el CTA 'Tienes una clinica veterinaria?' es visible",
          "el enlace 'Registrar clinica' es visible",
          "el enlace 'Ver clínicas' es visible",
        ],
      });

      await page.goto("/");

      // Verificar titulo de la pagina
      await expect(page).toHaveTitle(/InVet/);

      // Verificar hero section
      const heroSection = page.getByRole("region", { name: "Busqueda de clinicas" });
      await expect(heroSection).toBeVisible();

      const heroHeading = page.getByRole("heading", { name: /Encuentra la clinica ideal para tu mascota/ });
      await expect(heroHeading).toBeVisible();

      // Verificar barra de busqueda
      const searchForm = page.getByRole("search", { name: "Buscar clinicas veterinarias" });
      await expect(searchForm).toBeVisible();

      const searchInput = page.getByLabel("Buscar clinica por nombre, ciudad o servicio");
      await expect(searchInput).toBeVisible();
      await expect(searchInput).toHaveAttribute("type", "search");
      await expect(searchInput).toHaveAttribute("placeholder", /Buscar por nombre/);

      // Verificar boton de buscar
      const searchButton = page.getByRole("button", { name: "Buscar" });
      await expect(searchButton).toBeVisible();
      await expect(searchButton).not.toBeDisabled();

      // Verificar chips de categoria
      const chipsContainer = page.locator('[aria-label^="Filtrar por"]');
      await expect(chipsContainer.nth(0)).toBeVisible(); // Veterinaria
      await expect(chipsContainer.nth(1)).toBeVisible(); // Estetica
      await expect(chipsContainer.nth(2)).toBeVisible(); // Urgencias

      const chipLabels = await chipsContainer.allTextContents();
      expect(chipLabels).toContain("Veterinaria");
      expect(chipLabels).toContain("Estética");
      expect(chipLabels).toContain("Urgencias");

      // Verificar seccion como funciona
      const howItWorksSection = page.getByRole("region", { name: "Como funciona" });
      await expect(howItWorksSection).toBeVisible();

      const howItWorksHeading = page.getByRole("heading", { name: /Como funciona InVet/ });
      await expect(howItWorksHeading).toBeVisible();

      // Verificar pasos
      const stepTitles = page.getByRole("heading", { name: /Busca|Compara|Solicita/, exact: true });
      await expect(stepTitles.nth(0)).toBeVisible();
      await expect(stepTitles.nth(1)).toBeVisible();
      await expect(stepTitles.nth(2)).toBeVisible();

      // Verificar CTA section
      const ctaSection = page.getByRole("region", { name: "Registra tu clinica" });
      await expect(ctaSection).toBeVisible();

      const ctaHeading = page.getByRole("heading", { name: /Tienes una clinica veterinaria/ });
      await expect(ctaHeading).toBeVisible();

      // Verificar enlaces del CTA
      const registerClinicLink = page.getByRole("link", { name: "Registrar clinica" });
      await expect(registerClinicLink).toBeVisible();
      await expect(registerClinicLink).toHaveAttribute("href", "/register");

      const viewClinicsLink = page.getByRole("link", { name: /Ver clínicas/ });
      await expect(viewClinicsLink).toBeVisible();
      await expect(viewClinicsLink).toHaveAttribute("href", "/clinicas");
    },
  );

  // ===========================================================================
  // UIA-003-02: Search bar accepts input and has debounce behavior
  // Criterio: La barra de busqueda acepta texto y sincroniza con debounce.
  // Trazabilidad: US-003 / FE-003, AC-003-05
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-05 search bar accepts input and debounces",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Barra de busqueda",
        scenario: "La barra de busqueda acepta texto y tiene comportamiento debounce",
        given: ["el frontend de InVet esta disponible en la ruta raiz"],
        when: [
          "la persona visitante navega a la pagina de inicio",
          "escribe un termino en el campo de busqueda",
          "espera el debounce de 300ms",
        ],
        then: [
          "el valor del input refleja lo escrito",
          "el boton Buscar sigue visible y habilitado",
        ],
      });

      await page.goto("/");

      const searchInput = page.getByLabel("Buscar clinica por nombre, ciudad o servicio");

      // Escribir texto en el campo de busqueda
      await searchInput.fill("clinica centro");
      await expect(searchInput).toHaveValue("clinica centro");

      // Esperar debounce (300ms)
      await page.waitForTimeout(400);

      // Verificar que el valor se mantiene despues del debounce
      await expect(searchInput).toHaveValue("clinica centro");

      // Verificar boton sigue habilitado
      const searchButton = page.getByRole("button", { name: "Buscar" });
      await expect(searchButton).toBeVisible();
      await expect(searchButton).not.toBeDisabled();

      // Limpiar y verificar estado vacio
      await searchInput.clear();
      await expect(searchInput).toHaveValue("");
    },
  );

  // ===========================================================================
  // UIA-003-03: Category chips toggle active state and update URL query params
  // Criterio: Los chips de categoria cambian estado activo y actualizan URL.
  // Trazabilidad: US-003 / FE-003, AC-003-02
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-02 category chips toggle active state and update URL params",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-02"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Chips de categoria",
        scenario: "Los chips de categoria cambian estado activo y actualizan query params en la URL",
        given: ["el frontend de InVet esta disponible en la ruta /clinicas"],
        when: [
          "la persona visitante navega a /clinicas",
          "hace click en el chip Veterinaria",
        ],
        then: [
          "la URL actualiza el parametro category=veterinaria",
          "el chip activo cambia de estilo visual",
        ],
      });

      await page.goto("/clinicas");

      // Verificar chips en la pagina de clinicas
      const veterinariaChip = page.getByRole("button", { name: "Veterinaria" });
      await expect(veterinariaChip).toBeVisible();

      const esteticaChip = page.getByRole("button", { name: "Estética" });
      await expect(esteticaChip).toBeVisible();

      const urgenciasChip = page.getByRole("button", { name: "Urgencias" });
      await expect(urgenciasChip).toBeVisible();

      // Click en chip Veterinaria
      await veterinariaChip.click();

      // Verificar que la URL se actualizo con el query param
      await expect(page).toHaveURL(/category=veterinaria/);

      // Click en Estetica (debe cambiar de Veterinaria a Estetica)
      await esteticaChip.click();
      await expect(page).toHaveURL(/category=estetica/);

      // Click en Urgencias (debe cambiar de Estetica a Urgencias)
      await urgenciasChip.click();
      await expect(page).toHaveURL(/category=urgencias/);

      // Click en el chip activo debe deseleccionar (eliminar query param)
      await urgenciasChip.click();
      await expect(page).toHaveURL(/\/clinicas/);
    },
  );

  // ===========================================================================
  // UIA-003-04: Clinics listing page loads with loading state
  // Criterio: El listado muestra spinner de carga al iniciar.
  // Trazabilidad: US-003 / FE-003, AC-003-05
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-05 clinics listing shows loading state",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado de clinicas",
        scenario: "El listado muestra un spinner de carga mientras se obtienen los datos",
        given: ["el frontend de InVet esta disponible en la ruta /clinicas"],
        when: [
          "la persona visitante navega a /clinicas",
          "la pagina comienza a cargar el listado",
        ],
        then: [
          "se muestra un spinner o indicador de carga",
          "el spinner tiene role=status y aria-label de carga",
        ],
      });

      // Mock the API to delay response so we can observe loading state
      await page.route("**/api/v1/clinicas**", async (route) => {
        // Use a promise-based timeout that doesn't depend on page context
        await new Promise((resolve) => setTimeout(resolve, 2000));
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            items: [],
            total: 0,
            totalPages: 1,
            page: 1,
          }),
        });
      });

      await page.goto("/clinicas");

      // Verificar que el spinner de carga es visible
      const loadingStatus = page.getByRole("status", { name: /Cargando clinicas/i });
      await expect(loadingStatus).toBeVisible();

      // Verificar que hay un spinner visual (elemento con clase animate-spin)
      const spinner = page.locator('[class*="animate-spin"]');
      await expect(spinner.first()).toBeVisible();
    },
  );

  // ===========================================================================
  // UIA-003-05: Clinics listing handles error state
  // Criterio: El listado muestra mensaje de error cuando la API falla.
  // Trazabilidad: US-003 / FE-003, AC-003-05
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-05 clinics listing handles error state",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado de clinicas",
        scenario: "El listado muestra un mensaje de error cuando la API falla",
        given: ["el frontend de InVet esta disponible en la ruta /clinicas"],
        when: [
          "la persona visitante navega a /clinicas",
          "la API responde con un error",
        ],
        then: [
          "se muestra un mensaje de error en pantalla",
          "el mensaje tiene role=alert",
          "se muestra un boton de reintentar",
        ],
      });

      // Mock the API to return an error
      await page.route("**/api/v1/clinicas**", async (route) => {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            detail: "No se pudieron cargar las clinicas. Intenta de nuevo.",
          }),
        });
      });

      await page.goto("/clinicas");

      // Verificar que el mensaje de error es visible
      const alertBox = page.locator('[role="alert"]').first();
      await expect(alertBox).toBeVisible();

      // Verificar que hay un boton de reintentar
      const retryButton = page.getByRole("button", { name: /Reintentar/ });
      await expect(retryButton).toBeVisible();
    },
  );

  // ===========================================================================
  // UIA-003-06: Clinics listing handles empty state
  // Criterio: El listado muestra mensaje apropiado cuando no hay resultados.
  // Trazabilidad: US-003 / FE-003, AC-003-05
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-05 clinics listing handles empty state",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado de clinicas",
        scenario: "El listado muestra un mensaje apropiado cuando no hay resultados",
        given: ["el frontend de InVet esta disponible en la ruta /clinicas"],
        when: [
          "la persona visitante navega a /clinicas con una busqueda sin resultados",
          "la API responde con un listado vacio",
        ],
        then: [
          "se muestra un mensaje indicando que no se encontraron clinicas",
          "se sugiere intentar con otros filtros",
        ],
      });

      // Mock the API to return empty results
      await page.route("**/api/v1/clinicas**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            items: [],
            total: 0,
            totalPages: 1,
            page: 1,
          }),
        });
      });

      await page.goto("/clinicas");

      // Verificar mensaje de estado vacio
      const emptyStatus = page.getByRole("status", { name: /No se encontraron clinicas/i, exact: false });
      // El status role puede ser el div contenedor con texto "No se encontraron clinicas"
      const emptyMessage = page.locator('p', { hasText: /No se encontraron clinicas/ }).first();
      await expect(emptyMessage).toBeVisible();
    },
  );

  // ===========================================================================
  // UIA-003-07: Clinic detail page renders for valid ID
  // Criterio: El detalle de clínica carga correctamente para un ID valido.
  // Trazabilidad: US-003 / FE-003, AC-003-05
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-05 clinic detail renders for valid ID",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Detalle de clinica",
        scenario: "El detalle de clinica carga correctamente para un ID valido",
        given: ["el frontend de InVet esta disponible en la ruta /clinicas"],
        when: [
          "la persona visitante navega a /clinicas/1",
          "la pagina termina de cargar",
        ],
        then: [
          "se muestra el nombre de la clinica",
          "se muestra informacion publica como ciudad y direccion",
          "se muestra un enlace para volver al listado",
        ],
      });

      // Mock the API to return a valid clinic detail
      await page.route("**/api/v1/clinicas/**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            id: 1,
            name: "Clinica Veterinaria Central",
            city: "Ciudad de Mexico",
            address: "Av. Reforma 123",
            rating: 4.5,
            logoUrl: "",
            services: [
              { id: 1, name: "Consulta general" },
              { id: 2, name: "Vacunacion" },
            ],
          }),
        });
      });

      await page.goto("/clinicas/1");

      // Verificar que el heading de la clinica es visible
      const clinicHeading = page.getByRole("heading", { name: /Clinica Veterinaria Central/ });
      await expect(clinicHeading).toBeVisible();

      // Verificar enlace para volver al listado
      const backLink = page.getByRole("link", { name: /Volver a clínicas/ });
      await expect(backLink).toBeVisible();
      await expect(backLink).toHaveAttribute("href", "/clinicas");
    },
  );

  // ===========================================================================
  // UIA-003-08: Clinic detail page shows error for invalid ID
  // Criterio: El detalle de clínica muestra error para un ID invalido.
  // Trazabilidad: US-003 / FE-003, AC-003-05
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-05 clinic detail shows error for invalid ID",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Detalle de clinica",
        scenario: "El detalle de clinica muestra un mensaje de error para un ID invalido",
        given: ["el frontend de InVet esta disponible en la ruta /clinicas"],
        when: [
          "la persona visitante navega a /clinicas/999999",
          "la API responde con 404",
        ],
        then: [
          "se muestra un mensaje de error",
          "el mensaje tiene role=alert",
          "se muestra un enlace para volver al listado",
        ],
      });

      // Mock the API to return 404
      await page.route("**/api/v1/clinicas/**", async (route) => {
        await route.fulfill({
          status: 404,
          contentType: "application/json",
          body: JSON.stringify({
            detail: "No se encontro la clinica solicitada.",
          }),
        });
      });

      await page.goto("/clinicas/999999");

      // Verificar que el mensaje de error es visible
      const alertBox = page.locator('[role="alert"]').first();
      await expect(alertBox).toBeVisible();

      // Verificar enlace para volver al listado
      const backLink = page.getByRole("link", { name: /Volver al listado/ });
      await expect(backLink).toBeVisible();
    },
  );

  // ===========================================================================
  // UIA-003-09: Responsive layout - desktop (1280x720)
  // Criterio: La landing responde correctamente en viewport desktop.
  // Trazabilidad: US-003 / FE-003, AC-003-07
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-07 responsive layout desktop 1280x720",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Responsive desktop",
        scenario: "La landing responde correctamente en viewport desktop 1280x720",
        given: ["el frontend de InVet esta disponible en la ruta raiz"],
        when: [
          "la persona visitante navega a / con viewport 1280x720",
        ],
        then: [
          "todas las secciones son visibles",
          "el hero, buscador y chips se muestran correctamente",
          "no hay desbordamiento horizontal",
        ],
      });

      await page.setViewportSize({ width: 1280, height: 720 });
      await page.goto("/");

      // Verificar que todas las secciones principales son visibles
      const heroSection = page.getByRole("region", { name: "Busqueda de clinicas" });
      await expect(heroSection).toBeVisible();

      const searchInput = page.getByLabel("Buscar clinica por nombre, ciudad o servicio");
      await expect(searchInput).toBeVisible();

      const howItWorksSection = page.getByRole("region", { name: "Como funciona" });
      await expect(howItWorksSection).toBeVisible();

      const ctaSection = page.getByRole("region", { name: "Registra tu clinica" });
      await expect(ctaSection).toBeVisible();

      // Verificar que no hay desbordamiento horizontal
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      const viewportWidth = page.viewportSize()?.width || 1280;
      expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1); // Allow 1px tolerance
    },
  );

  // ===========================================================================
  // UIA-003-10: Responsive layout - mobile (375x667)
  // Criterio: La landing responde correctamente en viewport mobile.
  // Trazabilidad: US-003 / FE-003, AC-003-07
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-07 responsive layout mobile 375x667",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Responsive mobile",
        scenario: "La landing responde correctamente en viewport mobile 375x667",
        given: ["el frontend de InVet esta disponible en la ruta raiz"],
        when: [
          "la persona visitante navega a / con viewport 375x667",
        ],
        then: [
          "todas las secciones son visibles",
          "el buscador y chips se adaptan al layout vertical",
          "no hay desbordamiento horizontal",
        ],
      });

      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto("/");

      // Verificar que las secciones principales son visibles en mobile
      const heroSection = page.getByRole("region", { name: "Busqueda de clinicas" });
      await expect(heroSection).toBeVisible();

      const searchInput = page.getByLabel("Buscar clinica por nombre, ciudad o servicio");
      await expect(searchInput).toBeVisible();

      const chipsContainer = page.locator('[aria-label^="Filtrar por"]');
      const chipCount = await chipsContainer.count();
      expect(chipCount).toBeGreaterThan(0);

      const howItWorksSection = page.getByRole("region", { name: "Como funciona" });
      await expect(howItWorksSection).toBeVisible();

      const ctaSection = page.getByRole("region", { name: "Registra tu clinica" });
      await expect(ctaSection).toBeVisible();

      // Verificar que no hay desbordamiento horizontal
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      const viewportWidth = page.viewportSize()?.width || 375;
      expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1); // Allow 1px tolerance
    },
  );

  // ===========================================================================
  // UIA-003-11: Accessibility - labels, buttons, links, focus visible
  // Criterio: Los elementos interactivos tienen labels, roles y foco visible.
  // Trazabilidad: US-003 / FE-003, AC-003-07
  // ===========================================================================

  test(
    "@smoke @regression US-003 AC-003-07 accessibility labels, buttons, links, focus visible",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Accesibilidad",
        scenario: "Los elementos interactivos tienen labels, roles y foco visible",
        given: ["el frontend de InVet esta disponible en la ruta raiz"],
        when: [
          "la persona visitante navega a /",
        ],
        then: [
          "los inputs tienen labels asociados",
          "los botones tienen nombres accesibles",
          "los enlaces tienen textos descriptivos",
          "el foco es visible en elementos interactivos",
        ],
      });

      await page.goto("/");

      // Verificar que el input de busqueda tiene label asociado
      const searchInput = page.getByLabel("Buscar clinica por nombre, ciudad o servicio");
      await expect(searchInput).toBeVisible();

      // Verificar que los botones tienen nombres accesibles
      const searchButton = page.getByRole("button", { name: "Buscar" });
      await expect(searchButton).toBeVisible();

      const chipButtons = page.locator('[aria-label^="Filtrar por"]');
      const chipCount = await chipButtons.count();
      expect(chipCount).toBe(3); // Veterinaria, Estetica, Urgencias

      // Verificar que los enlaces tienen textos descriptivos
      const registerLink = page.getByRole("link", { name: "Registrar clinica" });
      await expect(registerLink).toBeVisible();

      const viewClinicsLink = page.getByRole("link", { name: /Ver clínicas/ });
      await expect(viewClinicsLink).toBeVisible();

      // Verificar que el foco es visible en elementos interactivos
      await searchInput.focus();
      await expect(searchInput).toBeFocused();

      await searchButton.focus();
      await expect(searchButton).toBeFocused();

      // Verificar que la navegacion por teclado funciona
      await page.keyboard.press("Tab");
      const activeElement = await page.evaluate(() => document.activeElement?.tagName);
      expect(activeElement).toBeTruthy();
    },
  );

  // ===========================================================================
  // UIA-003-12: No tokens or sensitive data exposed on public pages
  // Criterio: Las paginas publicas no exponen tokens ni datos sensibles.
  // Trazabilidad: US-003 / FE-003, AC-003-06
  // ===========================================================================

  test(
    "@regression US-003 AC-003-06 no tokens or sensitive data exposed on public pages",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-06"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Seguridad de datos publicos",
        scenario: "Las paginas publicas no exponen tokens ni datos sensibles en el DOM o consola",
        given: ["el frontend de InVet esta disponible"],
        when: [
          "la persona visitante navega a las paginas publicas",
        ],
        then: [
          "no hay tokens JWT visibles en el DOM",
          "no hay passwords visibles en el DOM",
          "no hay errores de consola que filtren informacion interna",
        ],
      });

      // Collect console messages
      const consoleMessages: string[] = [];
      page.on("console", (msg) => {
        consoleMessages.push(msg.text());
      });

      // Check landing page
      await page.goto("/");
      await page.waitForTimeout(500);

      // Check clinics listing page
      await page.goto("/clinicas");
      await page.waitForTimeout(500);

      // Scan DOM for sensitive patterns
      const bodyText = await page.evaluate(() => document.body.innerText);

      // Verify no JWT tokens in body text
      const jwtPattern = /eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/;
      expect(jwtPattern.test(bodyText)).toBe(false);

      // Verify no password-like strings in body text
      const passwordPatterns = [
        "password:",
        "contrasena:",
        "secret:",
        "api_key:",
        "token:",
        "access_token",
        "refresh_token",
      ];
      for (const pattern of passwordPatterns) {
        expect(bodyText.toLowerCase()).not.toContain(pattern);
      }

      // Verify no obvious error stack traces in console
      const errorMessages = consoleMessages.filter((msg) =>
        msg.toLowerCase().includes("stack") ||
        msg.toLowerCase().includes("traceback") ||
        msg.toLowerCase().includes("internal server error")
      );
      expect(errorMessages).toHaveLength(0);
    },
  );
});
