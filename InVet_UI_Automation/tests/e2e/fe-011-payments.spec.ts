/**
 * UIA-011 — Automatizacion de la UI de pagos operativos (C1..C9)
 *
 * C1  Formulario de registro visible para el staff con todos los campos.
 * C2  Validacion inline al enviar un formulario incompleto.
 * C3  Crear pago OK -> vista de recibo (no fiscal).
 * C4  Un propietario NO puede registrar un pago (403 superficieado, sin estado de exito).
 * C5  Listado por periodo: estado success (filas) y empty (CTA "Registrar pago").
 * C6  Detalle + boton Cancelar con confirmacion -> estado CANCELLED final.
 * C7  Pago ajeno (otra clinica) responde 404 y la UI superficiea el estado legible sin filtrar internos.
 * C8  Responsive: formulario + listado + detalle usables en mobile.
 * C9  Acentos y e-/ñ sin mojibake en todas las vistas.
 *
 * Nota: el control de permiso lo aplica el backend (sin gate frontend por rol);
 * las aserciones de acceso validan la respuesta 403/404 superficieada en la UI.
 */

import { test, expect, type Page } from "@playwright/test";
import { readAutomationEnv } from "../fixtures/env";
import { authenticateAs } from "../helpers/auth";
import { annotateTraceability, attachGherkinScenario } from "../helpers/traceability";

const env = readAutomationEnv();

// Fixtures estables del slice 011 (sembrados en bootstrap del backend):
// - cita 1000 de la clinica del vet (clicable en el formulario de pagos)
// - servicio 17 activo (prellena el importe)
const APPOINTMENT_ID = 1000;
const SERVICE_ID = 17;
const AMOUNT = "250";
const AMOUNT_RECEIVED = "300";

type Actor = "vet" | "owner" | "owner-clinic2";

function actorCreds(actor: Actor): { email: string; password: string } {
  switch (actor) {
    case "vet":
      return { email: env.vetEmail, password: env.vetPassword };
    case "owner":
      return { email: env.ownerEmail, password: env.ownerPassword };
    case "owner-clinic2":
      return { email: "owner-clinic2@invet.com", password: env.foreignOwnerPassword };
  }
}

const CONSOLE_NOISE =
  /Failed to load resource|favicon|40[0-9]0|403|404|422|409/i;

function hasRuntimeError(errors: string[]): boolean {
  return errors.some(
    (t) =>
      /ReferenceError|TypeError|SyntaxError|is not defined|is not a function/i.test(t) &&
      !CONSOLE_NOISE.test(t),
  );
}

/**
 * Crea un pago real como el actor (vet) para tener un id que abrir en el detalle.
 * Usa el contrato POST /payments. Devuelve el id del pago.
 */
async function seedPayment(page: Page): Promise<number> {
  const { email, password } = actorCreds("vet");
  const login = await page.request.post(`${env.apiBaseUrl}${env.loginApiPath}`, {
    data: { email, password },
  });
  if (login.status() !== 200) {
    throw new Error(`No se pudo autenticar al vet para sembrar un pago (HTTP ${login.status()})`);
  }
  const token = (await login.json()) as { access_token: string };
  const headers = { Authorization: `Bearer ${token.access_token}` };

  const response = await page.request.post(`${env.apiBaseUrl}/api/v1/payments`, {
    data: {
      appointment_id: APPOINTMENT_ID,
      service_id: SERVICE_ID,
      amount: Number(AMOUNT) * 100,
      method: "cash",
      amount_received: Number(AMOUNT_RECEIVED) * 100,
    },
    headers,
  });

  if (response.status() !== 201) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(`Error al sembrar el pago (HTTP ${response.status()} ${body.detail ?? ""})`);
  }

  return (await response.json()).id as number;
}

/** Rellena y envia el formulario de registro de pago. Devuelve la respuesta del POST. */
async function submitPaymentForm(page: Page): Promise<number | null> {
  await page.locator("#appointment_id").selectOption(String(APPOINTMENT_ID));
  await page.locator("#service_id").selectOption(String(SERVICE_ID));
  await page.locator("#amount").fill(AMOUNT);
  await page.locator("#method").selectOption("cash");
  await page.locator("#amount_received").fill(AMOUNT_RECEIVED);

  const postPromise = page
    .waitForResponse(
      (res) => res.url().includes("/api/v1/payments") && res.request().method() === "POST",
      { timeout: 30_000 },
    )
    .catch(() => null);

  await page.getByRole("button", { name: /Registrar pago/i }).click();

  const post = await postPromise;
  if (!post) return null;
  return post.status();
}

test.describe("pagos operativos UI - UIA-011 (C1..C9)", () => {
  // ===========================================================================
  // C1: Forma de pago visible para el staff con todos los campos
  // ===========================================================================
  test(
    "@regression US-011-01 TC-UIA-011-C1 formulario de pago completo",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "011",
        userStory: "US-011-01",
        criteria: ["AC-011-01"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Registro de pago operativo",
        scenario: "El staff abre la vista de registro de pago",
        given: ["un staff/veterinario autenticado (vet) con clinica asociada"],
        when: ["navego a /clinic/payments"],
        then: [
          "aparecen los campos cita, servicio, importe, metodo y (en cash) importe recibido",
          "los selectores de cita y servicio cargan opciones de la clinica",
          "el boton Registrar pago esta disponible",
        ],
      });

      await authenticateAs(page, env.vetEmail, env.vetPassword);
      await page.goto("/clinic/payments");

      await expect(page.getByRole("heading", { name: /Registrar pago/i })).toBeVisible();
      await expect(page.locator("#appointment_id")).toBeEnabled();
      await expect(page.locator("#service_id")).toBeEnabled();
      await expect(page.locator("#amount")).toBeVisible();
      await expect(page.locator("#method")).toBeVisible();
      await expect(page.getByRole("button", { name: /Registrar pago/i })).toBeEnabled();

      // Los selectores cargan opciones reales (cita 1000 / servicio 17 presentes).
      // El id vive en value del option (el texto muestra nombre/precio).
      await expect(page.locator('#appointment_id option[value="1000"]')).toHaveCount(1, { timeout: 30_000 });
      await expect(page.locator('#service_id option[value="17"]')).toHaveCount(1);

      // Al elegir "Efectivo" aparece el campo de importe recibido (condicion CASH).
      await page.locator("#method").selectOption("cash");
      await expect(page.locator("#amount_received")).toBeVisible();
    },
  );

  // ===========================================================================
  // C2: Validacion inline al enviar un formulario incompleto
  // ===========================================================================
  test(
    "@regression US-011-01 TC-UIA-011-C2 validacion inline",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "011",
        userStory: "US-011-01",
        criteria: ["AC-011-02"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Registro de pago operativo",
        scenario: "El staff envia el formulario sin completar los campos",
        given: ["el formulario de pago cargado sin ningun valor"],
        when: ["hace click en Registrar pago sin rellenar nada"],
        then: [
          "aparecen mensajes de error inline por campo (cita, servicio, importe, metodo)",
          "NO se dispara ningun POST al backend",
        ],
      });

      await authenticateAs(page, env.vetEmail, env.vetPassword);
      await page.goto("/clinic/payments");

      // Espera a que los selectores se habiliten (listas cargadas) y el form este listo.
      await expect(page.locator("#appointment_id")).toBeEnabled({ timeout: 30_000 });
      await expect(page.locator("#service_id")).toBeEnabled();

      const postPromise = page
        .waitForResponse(
          (res) => res.url().includes("/api/v1/payments") && res.request().method() === "POST",
          { timeout: 5_000 },
        )
        .catch(() => null);

      await page.getByRole("button", { name: /Registrar pago/i }).click();

      // Errores inline por los campos obligatorios vacios (ids estables de alerta).
      // method tiene valor por defecto (cash), asi que no emite error propio.
      await expect(page.locator("#appointment_id-error").locator("visible=true")).toBeVisible();
      await expect(page.locator("#service_id-error").locator("visible=true")).toBeVisible();
      await expect(page.locator("#amount-error").locator("visible=true")).toBeVisible();

      // Sin submit al backend (la validacion inline corta el envio).
      expect(await postPromise).toBeNull();
    },
  );

  // ===========================================================================
  // C3: Crear pago OK -> vista de recibo (no fiscal)
  // ===========================================================================
  test(
    "@regression US-011-01 TC-UIA-011-C3 crear pago y recibo",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "011",
        userStory: "US-011-01",
        criteria: ["AC-011-01"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Registro de pago operativo",
        scenario: "El staff registra un pago con efectivo y recibe el recibo",
        given: ["el formulario de pago cargado para el staff"],
        when: ["rellena cita, servicio, importe, metodo cash e importe recibido y envia"],
        then: [
          "el backend responde 201",
          "la UI muestra la vista de recibo no fiscal (Pagado registrado, Recibo #, metodo, importe, cambio)",
        ],
      });

      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      await authenticateAs(page, env.vetEmail, env.vetPassword);
      await page.goto("/clinic/payments");
      await expect(page.locator("#appointment_id")).toBeEnabled({ timeout: 30_000 });
      await expect(page.locator("#service_id")).toBeEnabled();

      const status = await submitPaymentForm(page);
      expect(status).toBe(201);

      // Vista de recibo no fiscal.
      await expect(page.getByText(/Pago registrado/i)).toBeVisible({ timeout: 30_000 });
      await expect(page.getByText(/Recibo #/i)).toBeVisible();
      await expect(page.getByText(/Método de pago/i)).toBeVisible();
      await expect(page.getByText(/Importe cobrado/i)).toBeVisible();
      // Cambio en efectivo (300 - 250 = 50 MXN).
      await expect(page.getByText(/Cambio/i)).toBeVisible();
      await expect(page.getByText(/no constituye factura/i)).toBeVisible();

      expect(hasRuntimeError(consoleErrors)).toBe(false);
    },
  );

  // ===========================================================================
  // C4: Propietario no puede registrar un pago (403 superficieado, sin exito)
  // ===========================================================================
  test(
    "@regression US-011-02 TC-UIA-011-C4 propietario sin permiso de creacion",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "011",
        userStory: "US-011-02",
        criteria: ["AC-011-06"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Registro de pago operativo",
        scenario: "El propietario intenta registrar un pago desde la vista clinica",
        given: [
          "un propietario autenticado (owner1) con la vista de pago cargada",
          "el control de rol lo aplica el backend (sin gate frontend)",
        ],
        when: ["hace click en Registrar pago con valores validos"],
        then: [
          "el backend responde 403 al POST de creacion",
          "la UI superficiea un mensaje legible de falta de permiso",
          "NO aparece la vista de exito (Pago registrado / Recibo #)",
        ],
      });

      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      await authenticateAs(page, env.ownerEmail, env.ownerPassword);
      await page.goto("/clinic/payments");
      await expect(page.locator("#appointment_id")).toBeEnabled({ timeout: 30_000 });
      await expect(page.locator("#service_id")).toBeEnabled();

      const status = await submitPaymentForm(page);

      // El backend debe responder 403 (rol propietario sin permiso de escritura).
      expect(status).toBe(403);

      // La UI superficiea un error legible y NO muestra estado de exito.
      const errorBanner = page
        .getByText(/permiso|veterinario|staff|No fue posible|prohibido|403|No se pudo registrar/i)
        .first();
      await expect(errorBanner).toBeVisible({ timeout: 30_000 });

      await expect(page.getByText(/Pago registrado/i)).toHaveCount(0);

      expect(hasRuntimeError(consoleErrors)).toBe(false);
    },
  );

  // ===========================================================================
  // C5: Listado por periodo - estado success (filas) y empty (CTA)
  // ===========================================================================
  test(
    "@regression US-011-01 TC-UIA-011-C5 listado por periodo success/empty",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "011",
        userStory: "US-011-01",
        criteria: ["AC-011-04"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Listado de pagos por periodo",
        scenario: "El staff consulta el historial de pagos con y sin resultados",
        given: ["un pago ya registrado por el staff"
, "el staff autenticado (vet)"],
        when: ["navega a /clinic/payments/history y luego filtra por un rango sin pagos"],
        then: [
          "con pagos: se muestra la lista de recibos paginada y los estados legibles",
          "sin pagos: aparece el estado empty con CTA Registrar pago",
        ],
      });

      const paymentId = await seedPayment(page);
      await authenticateAs(page, env.vetEmail, env.vetPassword);

      // --- Estado success: hay al menos un pago registrado. ---
      await page.goto("/clinic/payments/history");
      await expect(page.getByRole("heading", { name: /Pagos por periodo/i })).toBeVisible();
      // Desktop: celda #N dentro de la tabla; mobile: tarjeta "Recibo #N".
      // filter visible = solo el breakpoint activo (el otro markup esta ocultado).
      await expect(
        page
          .locator(`text=Recibo #${paymentId}`)
          .or(page.locator(`td:text-is("#${paymentId}")`))
          .filter({ visible: true })
          .first(),
      ).toBeVisible({ timeout: 30_000 });
      await expect(page.getByText(/pagos en el periodo|Página/i).first()).toBeVisible();

      // --- Estado empty: rango de fechas futuro sin pagos. ---
      await page.locator("#from_date").fill("2099-01-01");
      await page.locator("#to_date").fill("2099-12-31");
      await page.getByRole("button", { name: /Filtrar/i }).click();
      // El estado empty vive en un contenedor role=status con CTA "Registrar pago"
      // (el CTA de cabecera es un <button> suelto y no un role=status).
      const emptyState = page.locator('[role="status"]', { has: page.getByText(/No hay pagos en este periodo/i) });
      await expect(emptyState).toBeVisible({ timeout: 30_000 });
      await expect(emptyState.getByRole("button", { name: /Registrar pago/i })).toBeVisible();
    },
  );

  // ===========================================================================
  // C6: Detalle + Cancelar con confirmacion -> estado CANCELLED final
  // ===========================================================================
  test(
    "@regression US-011-01 TC-UIA-011-C6 detalle y cancelacion",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "011",
        userStory: "US-011-01",
        criteria: ["AC-011-03", "AC-011-05"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Detalle y cancelacion de pago",
        scenario: "El staff abre el detalle de un pago pagado y lo cancela",
        given: ["un pago en estado pagado del staff", "el staff autenticado (vet)"],
        when: ["abre el detalle, pulsa Cancelar pago y confirma"],
        then: [
          "se muestra el estado cancelado (Cancelado) y el aviso de pago cancelado",
          "el boton Cancelar desaparece por ser estado final",
        ],
      });

      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      const paymentId = await seedPayment(page);
      await authenticateAs(page, env.vetEmail, env.vetPassword);
      await page.goto(`/clinic/payments/${paymentId}`);

      // Detalle del recibo (estado pagado).
      await expect(page.getByRole("heading", { name: `#${paymentId}` })).toBeVisible({ timeout: 30_000 });
      await expect(page.getByText(/Pagado/i).first()).toBeVisible();
      await expect(page.getByText(/Método de pago/i)).toBeVisible();
      await expect(page.getByText(/Importe cobrado/i)).toBeVisible();

      // Aceptar el confirm() nativo y pulsar Cancelar pago.
      page.once("dialog", (dialog) => dialog.accept());
      await page.getByRole("button", { name: /Cancelar pago/i }).click();

      // Estado CANCELLED final + aviso de exito.
      await expect(page.getByText(/Pago cancelado correctamente/i)).toBeVisible({ timeout: 30_000 });
      await expect(page.getByText(/Cancelado/i).first()).toBeVisible();
      // Al estar cancelado no debe existir el boton de cancelar.
      await expect(page.getByRole("button", { name: /Cancelar pago/i })).toHaveCount(0);

      expect(hasRuntimeError(consoleErrors)).toBe(false);
    },
  );

  // ===========================================================================
  // C7: Pago ajeno (otra clinica) -> 404 legible sin filtrar internos
  // ===========================================================================
  test(
    "@regression US-011-02 TC-UIA-011-C7 pago ajeno no visible",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "011",
        userStory: "US-011-02",
        criteria: ["AC-011-07"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Detalle de pago - aislamiento por clinica",
        scenario: "Un clinico de otra clinica intenta abrir el detalle de un pago ajeno",
        given: [
          "un pago existente de la clinica del vet",
          "un staff de otra clinica autenticado (owner-clinic2, clinica 2)",
        ],
        when: ["navega a /clinic/payments/{id_ajeno}"],
        then: [
          "la pagina muestra el estado legible de pago inexistente/sin permiso",
          "NO se muestran los datos del recibo ajeno (Recibo #{id})",
          "no se filtran datos internos del backend",
        ],
      });

      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      const foreignId = await seedPayment(page);
      await authenticateAs(page, "owner-clinic2@invet.com", env.foreignOwnerPassword);
      await page.goto(`/clinic/payments/${foreignId}`);

      // La respuesta 404 superficieada como estado legible.
      const notFound = page.getByText(/El pago no existe o no pertenece a tu clínica|No tienes permiso|No fue posible/i).first();
      await expect(notFound).toBeVisible({ timeout: 30_000 });

      // Sin detalle del recibo ajeno.
      await expect(page.getByRole("heading", { name: `#${foreignId}` })).toHaveCount(0);
      await expect(page.getByText(/Recibo #/i)).toHaveCount(0);

      expect(hasRuntimeError(consoleErrors)).toBe(false);
    },
  );

  // ===========================================================================
  // C8: Responsive - formulario + listado + detalle en mobile
  // ===========================================================================
  test(
    "@regression US-011-01 TC-UIA-011-C8 responsive mobile",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "011",
        userStory: "US-011-01",
        criteria: ["AC-011-08"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Responsive del flujo de pagos",
        scenario: "El staff usa el flujo de pagos en un viewport mobile",
        given: ["viewport mobile (375px) y una cuenta de staff (vet)"],
        when: ["navega entre formulario, listado y detalle en mobile"],
        then: [
          "las vistas se muestran de forma usables (scroll vertical, sin desbordes que rompan el flujo)",
          "los controles primarios siguen siendo alcanzables",
        ],
      });

      const paymentId = await seedPayment(page);
      await page.setViewportSize({ width: 375, height: 720 });
      await authenticateAs(page, env.vetEmail, env.vetPassword);

      // Formulario usable.
      await page.goto("/clinic/payments");
      await expect(page.locator("#appointment_id")).toBeEnabled({ timeout: 30_000 });
      await expect(page.getByRole("button", { name: /Registrar pago/i })).toBeVisible();

      // Listado usable.
      await page.goto("/clinic/payments/history");
      await expect(page.getByRole("heading", { name: /Pagos por periodo/i })).toBeVisible();
      await expect(page.locator("text=Recibo #").first()).toBeVisible({ timeout: 30_000 });

      // Detalle usable.
      await page.goto(`/clinic/payments/${paymentId}`);
      await expect(page.getByRole("heading", { name: `#${paymentId}` })).toBeVisible({ timeout: 30_000 });
      await expect(page.getByText(/Método de pago/i)).toBeVisible();
    },
  );

  // ===========================================================================
  // C9: Acentos y e-/ñ sin mojibake en las vistas
  // ===========================================================================
  test(
    "@regression US-011-01 TC-UIA-011-C9 acentos sin mojibake",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "011",
        userStory: "US-011-01",
        criteria: ["AC-011-08"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Tipografia del flujo de pagos",
        scenario: "Las etiquetas muestran acentos y e-/ñ correctos",
        given: ["las vistas de pagos cargadas"],
        when: ["se inspeccionan las etiquetas visibles"],
        then: [
          "los acentos (Metodo, Pagos, clínica, método) se muestran correctos",
          "no aparece el caracter de reemplazo (mojibake) en el contenido",
        ],
      });

      await authenticateAs(page, env.vetEmail, env.vetPassword);

      // Historial de pagos: encabezados y etiquetas acentuadas en la tabla.
      await page.goto("/clinic/payments/history");
      // Espera a que termine la carga (el loader oculta la tabla con columnas acentuadas).
      await expect(page.getByText(/Cargando pagos/i)).toBeHidden({ timeout: 30_000 });
      const historyBody = await page.locator("body").innerText({ timeout: 30_000 });

      // Formulario: campo de método con etiqueta correcta.
      await page.goto("/clinic/payments");
      const formBody = await page.locator("body").innerText({ timeout: 30_000 });

      const body = `${historyBody}\n${formBody}`;

      // Etiquetas acentuadas presentes y correctas (palabras comunes a ambos
      // breakpoints: la columna "Método" solo existe en la tabla desktop).
      expect(historyBody).toContain("clínica");
      expect(formBody).toContain("Método de pago");
      // Sin mojibake tipico (bytes ISO-8859-1/UTF-8 mal decodificados).
      expect(body).not.toMatch(/Ã.|Â.|â€|ï»¿/);
    },
  );
});
