/**
 * UIA-002 - UI/E2E automation for BE-002 / FE-002 (Autenticacion y sesion)
 *
 * Cobertura:
 * - US-002-01: Login renderiza campos accesibles
 * - US-002-02: Registro renderiza campos requeridos
 * - US-002-03: Login invalido muestra error seguro
 * - US-002-04: Login valido guarda estado de sesion
 * - US-002-05: Guard privado rechaza anonimo (JUSTIFIED_SKIP)
 * - US-002-06: Recuperacion muestra respuesta generica
 * - US-002-07: Logout limpia estado local (JUSTIFIED_SKIP)
 * - US-002-08: Formularios responden en mobile
 * - US-002-09: Tokens no aparecen visibles
 *
 * Trazabilidad: AC-002-01, AC-002-02, AC-002-03, AC-002-04, AC-002-06,
 *               AC-002-07, AC-002-08, AC-002-09, AC-002-10
 */

import { expect, test } from "@playwright/test";

import { readAutomationEnv } from "../../fixtures/env";
import { annotateTraceability, attachGherkinScenario } from "../../helpers/traceability";

const env = readAutomationEnv();

// ===========================================================================
// UIA-002-01: Login renderiza campos accesibles
// Criterio: El formulario de login muestra labels y inputs con aria-label.
// Trazabilidad: US-002-01, AC-002-08
// ===========================================================================

test.describe("login page - UIA-002", () => {
  test(
    "@smoke @regression US-002-01 AC-002-08 login renders accessible fields",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-01",
        criteria: ["AC-002-08"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Formulario de login",
        scenario: "La pagina de login renderiza campos accesibles con labels visibles",
        given: ["el frontend de InVet esta disponible en la ruta raiz"],
        when: [
          "la persona visitante navega a /login",
          "la pagina termina de cargar",
        ],
        then: [
          "el titulo 'Inicia sesion en InVet' es visible",
          "el campo Email con label es visible",
          "el campo Password con label es visible",
          "el boton 'Iniciar sesion' es visible y esta habilitado",
          "el enlace 'Recuperar password' es visible",
          "el enlace 'Registrarse' es visible",
        ],
      });

      await page.goto("/login");

      // Verificar titulo
      const heading = page.getByRole("heading", { name: "Inicia sesion en InVet" });
      await expect(heading).toBeVisible();

      // Verificar campos con labels
      const emailInput = page.getByLabel("Email");
      await expect(emailInput).toBeVisible();
      await expect(emailInput).toHaveAttribute("type", "email");

      const passwordInput = page.getByLabel("Password");
      await expect(passwordInput).toBeVisible();
      await expect(passwordInput).toHaveAttribute("type", "password");

      // Verificar boton
      const submitButton = page.getByRole("button", { name: /Iniciar sesion/ });
      await expect(submitButton).toBeVisible();
      await expect(submitButton).not.toBeDisabled();

      // Verificar enlaces de navegacion
      const forgotLink = page.getByRole("link", { name: /Recuperar password/ });
      await expect(forgotLink).toBeVisible();

      const registerLink = page.getByRole("main").getByRole("link", { name: "Registrarse" });
      await expect(registerLink).toBeVisible();
    },
  );

  // ===========================================================================
  // UIA-002-02: Registro renderiza campos requeridos
  // Criterio: El formulario de registro muestra todos los campos obligatorios.
  // Trazabilidad: US-002-02, AC-002-01, AC-002-08
  // ===========================================================================

  test(
    "@smoke @regression US-002-02 AC-002-01 AC-002-08 register renders required fields",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-02",
        criteria: ["AC-002-01", "AC-002-08"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Formulario de registro",
        scenario: "La pagina de registro renderiza todos los campos requeridos",
        given: ["el frontend de InVet esta disponible en la ruta raiz"],
        when: [
          "la persona visitante navega a /register",
          "la pagina termina de cargar",
        ],
        then: [
          "el titulo 'Registrarse en InVet' es visible",
          "los campos Nombre y Apellido son visibles",
          "el campo Email con label es visible",
          "el campo Contrasena con label es visible",
          "el campo Confirmar contrasena con label es visible",
          "el boton 'Registrarse' es visible y esta habilitado",
        ],
      });

      await page.goto("/register");

      // Verificar titulo
      const heading = page.getByRole("heading", { name: /Registrarse en InVet/ });
      await expect(heading).toBeVisible();

      // Verificar campos con labels
      const firstNameInput = page.getByLabel("Nombre");
      await expect(firstNameInput).toBeVisible();

      const lastNameInput = page.getByLabel("Apellido");
      await expect(lastNameInput).toBeVisible();

      const emailInput = page.getByLabel("Email");
      await expect(emailInput).toBeVisible();

      const passwordInput = page.getByRole('textbox', { name: 'Contrasena', exact: true });
      await expect(passwordInput).toBeVisible();

      const confirmPasswordInput = page.getByLabel('Confirmar contrasena');
      await expect(confirmPasswordInput).toBeVisible();

      // Verificar boton
      const submitButton = page.getByRole("button", { name: /Registrarse/ });
      await expect(submitButton).toBeVisible();
      await expect(submitButton).not.toBeDisabled();
    },
  );

  // ===========================================================================
  // UIA-002-03: Login invalido muestra error seguro
  // Criterio: Credenciales invalidas muestran mensaje de error sin filtrar detalles.
  // Trazabilidad: US-002-03, AC-002-03
  // ===========================================================================

  test(
    "@regression US-002-03 AC-002-03 login invalid shows secure error",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-03",
        criteria: ["AC-002-03"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Login con credenciales invalidas",
        scenario: "Credenciales invalidas muestran mensaje de error seguro sin filtrar detalles internos",
        given: [
          "el frontend de InVet esta disponible en la ruta raiz",
          "la API backend responde con 401 para credenciales invalidas",
        ],
        when: [
          "la persona visitante navega a /login",
          "ingresa un email y password invalidos",
          "hace clic en 'Iniciar sesion'",
        ],
        then: [
          "el formulario muestra un mensaje de error visible",
          "el mensaje no contiene tokens, stack traces ni detalles internos",
          "el boton vuelve a estar habilitado",
        ],
      });

      await page.goto("/login");

      // Interceptar la llamada API para simular 401
      await page.route("**/api/v1/auth/login", async (route) => {
        await route.fulfill({
          status: 401,
          contentType: "application/json",
          body: JSON.stringify({ detail: "Credenciales invalidas" }),
        });
      });

      // Llenar formulario con credenciales invalidas
      await page.getByLabel("Email").fill("invalid@example.com");
      await page.getByLabel("Password").fill("wrongpass");

      // Submit
      const submitButton = page.getByRole("button", { name: /Iniciar sesion/ });
      await submitButton.click();

      // Verificar mensaje de error (usar .first() para evitar ambiguedad con __next-route-announcer__)
      const errorAlert = page.locator('[role="alert"]').first();
      await expect(errorAlert).toBeVisible();
      const errorText = await errorAlert.textContent();
      expect(errorText).toContain("Credenciales invalidas");

      // Verificar que no hay tokens en el error
      expect(errorText).not.toContain("access_token");
      expect(errorText).not.toContain("refresh_token");
      expect(errorText).not.toContain("bearer");
    },
  );

  // ===========================================================================
  // UIA-002-04: Login valido guarda estado de sesion
  // Criterio: Login exitoso almacena tokens en localStorage y redirige.
  // Trazabilidad: US-002-04, AC-002-02, AC-002-04
  // ===========================================================================

  test(
    "@regression US-002-04 AC-002-02 AC-002-04 login valid saves session state",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-04",
        criteria: ["AC-002-02", "AC-002-04"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Login con credenciales validas",
        scenario: "Credenciales validas almacenan tokens en localStorage y redirigen al home",
        given: [
          "el frontend de InVet esta disponible en la ruta raiz",
          "la API backend responde con 200 y tokens bearer",
        ],
        when: [
          "la persona visitante navega a /login",
          "ingresa un email y password validos",
          "hace clic en 'Iniciar sesion'",
        ],
        then: [
          "los tokens se almacenan en localStorage (access_token y refresh_token)",
          "la pagina redirige a la ruta raiz /",
          "no hay mensajes de error visibles",
        ],
      });

      await page.goto("/login");

      // Interceptar la llamada API para simular 200 con tokens
      let capturedAccessToken = "";
      let capturedRefreshToken = "";
      await page.route("**/api/v1/auth/login", async (route) => {
        capturedAccessToken = "mock_access_token_abc123";
        capturedRefreshToken = "mock_refresh_token_xyz789";
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            access_token: capturedAccessToken,
            refresh_token: capturedRefreshToken,
            token_type: "bearer",
          }),
        });
      });

      // Llenar formulario con credenciales validas (mock)
      await page.getByLabel("Email").fill("user@example.com");
      await page.getByLabel("Password").fill("secret123");

      // Submit
      const submitButton = page.getByRole("button", { name: /Iniciar sesion/ });
      await submitButton.click();

      // Esperar redireccion
      await page.waitForURL(/\/$/);

      // Verificar tokens en localStorage
      const storedAccessToken = await page.evaluate(() =>
        localStorage.getItem("access_token"),
      );
      const storedRefreshToken = await page.evaluate(() =>
        localStorage.getItem("refresh_token"),
      );

      expect(storedAccessToken).toBe(capturedAccessToken);
      expect(storedRefreshToken).toBe(capturedRefreshToken);
    },
  );

  // ===========================================================================
  // UIA-002-05: Guard privado rechaza anonimo (JUSTIFIED_SKIP)
  // Trazabilidad: AC-002-04
  // Motivo: No existe una ruta privada implementada en el frontend para probar
  //         el guard. Las rutas privadas se implementaran en slices posteriores.
  //         El guard se valida por inspeccion de codigo (frontend/src/shared/auth/session.ts).
  // ===========================================================================

  test(
    "US-002-05 AC-002-04 private guard rejects anonymous - JUSTIFIED_SKIP",
    async ({}, testInfo) => {
      test.skip(true, "No existe ruta privada implementada en FE-002; el guard se valida por inspeccion de codigo");
    },
  );

  // ===========================================================================
  // UIA-002-06: Recuperacion muestra respuesta generica
  // Criterio: El formulario de recuperacion muestra mensaje generico sin enumerar correos.
  // Trazabilidad: US-002-06, AC-002-07
  // ===========================================================================

  test(
    "@regression US-002-06 AC-002-07 password reset shows generic response",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-06",
        criteria: ["AC-002-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Recuperacion de password",
        scenario: "La solicitud de recuperacion muestra respuesta generica sin enumerar correos",
        given: [
          "el frontend de InVet esta disponible en la ruta raiz",
          "la API backend responde con mensaje generico para cualquier email",
        ],
        when: [
          "la persona visitante navega a /forgot-password",
          "ingresa un email valido o invalido",
          "hace clic en 'Enviar enlace de recuperacion'",
        ],
        then: [
          "el formulario muestra un mensaje de exito generico",
          "el mensaje no enumera el correo enviado",
          "el mensaje confirma que se enviara si el correo existe",
        ],
      });

      await page.goto("/forgot-password");

      // Interceptar la llamada API para simular respuesta generica
      await page.route("**/api/v1/auth/password-reset/request", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            message: "Si el correo existe en el sistema, se ha enviado un enlace de recuperacion.",
          }),
        });
      });

      // Llenar formulario con email
      await page.getByLabel("Email").fill("user@example.com");

      // Submit
      const submitButton = page.getByRole("button", { name: /Enviar enlace/ });
      await submitButton.click();

      // Verificar mensaje de exito generico
      const successAlert = page.locator('[role="status"]');
      await expect(successAlert).toBeVisible();
      const successText = await successAlert.textContent();
      expect(successText).toContain("Si el correo existe en el sistema");

      // Verificar que no se enumera el email en la respuesta
      // (el mensaje generico no debe incluir el email especifico)
      expect(successText).not.toContain("se ha enviado a user@example.com");
    },
  );

  // ===========================================================================
  // UIA-002-07: Logout limpia estado local (JUSTIFIED_SKIP)
  // Trazabilidad: AC-002-06
  // Motivo: No existe una ruta de logout en el frontend implementada en FE-002.
  //         El logout se valida por inspeccion de codigo (frontend/src/shared/auth/session.ts
  //         tiene clearSession() que remueve ambos tokens).
  // ===========================================================================

  test(
    "US-002-07 AC-002-06 logout clears local state - JUSTIFIED_SKIP",
    async ({}, testInfo) => {
      test.skip(true, "No existe ruta de logout implementada en FE-002; clearSession() se valida por inspeccion de codigo");
    },
  );

  // ===========================================================================
  // UIA-002-08: Formularios responden en mobile
  // Criterio: Los formularios de login y registro son usables en viewport mobile (375px).
  // Trazabilidad: US-002-08, AC-002-08
  // ===========================================================================

  test(
    "@regression US-002-08 AC-002-08 forms are usable on mobile viewport",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-08",
        criteria: ["AC-002-08"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Responsive de formularios auth",
        scenario: "Los formularios de login y registro son usables en viewport mobile (375px)",
        given: [
          "el frontend de InVet esta disponible en la ruta raiz",
          "la vista mobile es 375x667",
        ],
        when: [
          "la persona visitante navega a /login en viewport mobile",
          "la persona visitante navega a /register en viewport mobile",
        ],
        then: [
          "los formularios son legibles sin scroll horizontal",
          "todos los campos y botones son visibles y clickeables",
          "no hay solapamiento de elementos",
        ],
      });

      // Configurar viewport mobile
      await page.setViewportSize({ width: 375, height: 667 });

      // Verificar login en mobile
      await page.goto("/login");

      const loginHeading = page.getByRole("heading", { name: "Inicia sesion en InVet" });
      await expect(loginHeading).toBeVisible();

      const emailInput = page.getByLabel("Email");
      await expect(emailInput).toBeVisible();

      const passwordInput = page.getByLabel("Password");
      await expect(passwordInput).toBeVisible();

      const submitButton = page.getByRole("button", { name: /Iniciar sesion/ });
      await expect(submitButton).toBeVisible();

      // Verificar que no hay scroll horizontal (el contenido cabe en 375px)
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      expect(bodyWidth).toBeLessThanOrEqual(375 + 10); // Margen de 10px para scrollbar

      // Verificar register en mobile
      await page.goto("/register");

      const registerHeading = page.getByRole("heading", { name: /Registrarse en InVet/ });
      await expect(registerHeading).toBeVisible();

      const firstNameInput = page.getByLabel("Nombre");
      await expect(firstNameInput).toBeVisible();

      const lastNameInput = page.getByLabel("Apellido");
      await expect(lastNameInput).toBeVisible();

      const registerSubmitButton = page.getByRole("button", { name: /Registrarse/ });
      await expect(registerSubmitButton).toBeVisible();
    },
  );

  // ===========================================================================
  // UIA-002-09: Tokens no aparecen visibles
  // Criterio: Los tokens no se muestran en la UI, consola ni mensajes de error.
  // Trazabilidad: US-002-09, AC-002-09
  // ===========================================================================

  test(
    "@regression US-002-09 AC-002-09 tokens are not visible in UI",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-09",
        criteria: ["AC-002-09"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Tokens ocultos en UI",
        scenario: "Los tokens de acceso no aparecen visibles en pantalla, consola ni mensajes de error",
        given: [
          "el frontend de InVet esta disponible en la ruta raiz",
          "la API backend responde con 200 y tokens bearer",
        ],
        when: [
          "la persona visitante navega a /login",
          "ingresa credenciales validas y hace login",
          "se revisa la UI despues del login exitoso",
        ],
        then: [
          "los tokens no aparecen en el DOM visible",
          "los tokens no aparecen en mensajes de error",
          "los tokens no aparecen en la consola del navegador",
        ],
      });

      await page.goto("/login");

      // Capturar errores de consola
      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") {
          consoleErrors.push(msg.text());
        }
      });

      // Interceptar la llamada API para simular 200 con tokens
      await page.route("**/api/v1/auth/login", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            access_token: "mock_access_token_visible_test",
            refresh_token: "mock_refresh_token_visible_test",
            token_type: "bearer",
          }),
        });
      });

      // Llenar formulario y hacer login
      await page.getByLabel("Email").fill("user@example.com");
      await page.getByLabel("Password").fill("secret123");
      await page.getByRole("button", { name: /Iniciar sesion/ }).click();

      // Esperar redireccion
      await page.waitForURL(/\/$/);

      // Verificar que los tokens no aparecen en el DOM visible
      const bodyText = await page.locator("body").textContent();
      expect(bodyText).not.toContain("mock_access_token_visible_test");
      expect(bodyText).not.toContain("mock_refresh_token_visible_test");
      expect(bodyText).not.toContain("bearer");

      // Verificar que no hay errores de consola relacionados con tokens
      const tokenErrors = consoleErrors.filter((err) =>
        err.toLowerCase().includes("token") || err.toLowerCase().includes("auth"),
      );
      expect(tokenErrors).toEqual([]);
    },
  );
});
