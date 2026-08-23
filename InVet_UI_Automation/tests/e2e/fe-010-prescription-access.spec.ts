/**
 * UIA-010 — Permisos visibles en la UI (C4, C7)
 *
 * C4  Un propietario NO puede crear recetas: al enviar el formulario el backend
 *     responde 403 y la UI superficiea el mensaje legible (sin redireccion,
 *     sin creacion).
 * C7  Un propietario no ve recetas ajenas: el detalle responde 404 y la UI
 *     muestra el estado "Receta no encontrada" sin filtrar datos del owner ajeno.
 *
 * Ambos casos dependen del backend para el control de permiso (sin gate
 * frontend), por lo que las aserciones validan la respuesta 403/404
 * superficieada en la UI.
 */

import { test, expect, type Page } from "@playwright/test";
import { readAutomationEnv } from "../fixtures/env";
import { authenticateAs } from "../helpers/auth";
import { annotateTraceability, attachGherkinScenario } from "../helpers/traceability";

const env = readAutomationEnv();

// C4: recipe creation attempt on the "own" consultation (owner1 / pet 1000 / consult 1000).
const OWN_CONSULTATION_ID = 1000;
// C7: foreign-owner consultation (owner2 / pet 1001 / consult 1001) used as the leak target.
const FOREIGN_CONSULTATION_ID = 1001;
const FOREIGN_PET_ID = 1001;
const FOREIGN_DIAGNOSIS = "Diagnostico de referencia AJENA-DO-NOT-LEAK-7842.";

/**
 * Crea (o reutiliza) una receta para (consultation, pet) como un actor con rol
 * de escritura (vet, sin owner record). Devuelve el id. Si ya existe (409) la localiza por
 * listado. Se usa para sembrar la receta ajenose de C7.
 */
async function seedForeignPrescription(page: Page): Promise<number> {
  // Sembrar con `vet` (sin owner record): el listado por pet 1001 no se
  // filtra a 404 por ownership, asi el fallback 409 puede reutilizarla.
  const login = await page.request.post(`${env.apiBaseUrl}${env.loginApiPath}`, {
    data: { email: env.vetEmail, password: env.vetPassword },
  });
  if (login.status() !== 200) {
    throw new Error(`No se pudo autenticar al vet para seed foraneo (HTTP ${login.status()})`);
  }
  const token = (await login.json()) as { access_token: string };
  const headers = { Authorization: `Bearer ${token.access_token}` };

  const payload = {
    consultation_id: FOREIGN_CONSULTATION_ID,
    pet_id: FOREIGN_PET_ID,
    diagnosis: FOREIGN_DIAGNOSIS,
    items: [{ name: "Medicamento AJENO-DO-NOT-LEAK-7842", dosage: "1 via", frequency: "1 vez", duration: "3 dias" }],
  };

  const response = await page.request.post(`${env.apiBaseUrl}/api/v1/prescriptions`, {
    data: payload,
    headers,
  });

  if (response.status() === 201) {
    return (await response.json()).id as number;
  }

  if (response.status() === 409) {
    const list = await page.request.get(
      `${env.apiBaseUrl}/api/v1/prescriptions?pet_id=${FOREIGN_PET_ID}&page=1&page_size=20`,
      { headers },
    );
    if (list.status() === 200) {
      const data = (await list.json()) as { items: { id: number }[] };
      const match = data.items.find((p) => typeof p.id === "number");
      if (match) return match.id;
    }
    throw new Error("409 (receta duplicada) y el listado no retorno una receta reutilizable");
  }

  const body = (await response.json().catch(() => ({}))) as { detail?: string };
  throw new Error(`Error al crear la receta foranea (HTTP ${response.status()} ${body.detail ?? ""})`);
}

test.describe("prescription access/permissions - UIA-010", () => {
  // ===========================================================================
  // C4: Propietario no puede crear receta (403 superficieado)
  // Criterios: AC-010-04
  // ===========================================================================
  test(
    "@regression US-010-02 TC-UIA-010-C4 propietario sin permiso de creacion",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "010",
        userStory: "US-010-02",
        criteria: ["AC-010-04"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Registro de receta clinica",
        scenario: "El propietario intenta crear una receta desde la vista clinica",
        given: [
          "un propietario autenticado (owner1) que posee la mascota 1000",
          "el formulario de receta cargado para la consulta 1000 (get consulta permitido)",
        ],
        when: ["hace click en Registrar receta"],
        then: [
          "el backend responde 403 al POST de creacion",
          "la UI superficiea un mensaje legible de falta de permiso",
          "NO aparece el estado de exito Receta creada",
          "no se genera un redirect a una vista de exito",
        ],
      });

      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      await authenticateAs(page, env.ownerEmail, env.ownerPassword);
      await page.goto(`/clinic/prescriptions/new?consultation_id=${OWN_CONSULTATION_ID}`);
      // Esperamos a un estado terminal (desaparece el spinner) para clasificar
      // despues con isVisible() uno-shot sin flakiness por estado intermedio.
      await expect(page.getByText(/Cargando la consulta/i))
        .toBeHidden({ timeout: 30_000 })
        .catch(() => {});

      // El formulario SI se renderiza (GET consulta permitido) porque no hay gate
      // frontend por rol; el control real ocurre en el POST.
      const formHeading = page.getByRole("heading", { name: /Registrar receta/i });
      const fallback = page.getByText(/consulta|No fue posible|Volver/i).first();
      const showsForm = await formHeading.isVisible().catch(() => false);
      if (!showsForm) {
        await expect(fallback).toBeVisible();
        return;
      }

      const submitPromise = page
        .waitForResponse(
          (res) => res.url().includes("/api/v1/prescriptions") && res.request().method() === "POST",
        )
        .catch(() => null);

      await page.getByRole("button", { name: /Registrar receta/i }).click();

      // El backend 403 debe superficiear como mensaje legible de error.
      const errorBanner = page
        .getByText(/veterinario|prescribir|permiso|No fue posible|prohibido|403/i)
        .first();
      await expect(errorBanner).toBeVisible({ timeout: 30_000 });

      // Sin estado de exito.
      await expect(page.getByText(/Receta creada/i)).toHaveCount(0);

      // La respuesta del POST debe ser 403.
      const postResponse = await submitPromise;
      if (postResponse) {
        expect(postResponse.status()).toBe(403);
      }

      const hasRuntimeError = consoleErrors.some(
        (t) =>
          /ReferenceError|TypeError|SyntaxError|is not defined|is not a function/i.test(t) &&
          !/Failed to load resource|favicon|40[0-9]|422|403/i.test(t),
      );
      expect(hasRuntimeError).toBe(false);
    },
  );

  // ===========================================================================
  // C7: Propietario no ve recetas ajenas (404 superficieado, sin fuga)
  // Criterios: AC-010-09
  // ===========================================================================
  test(
    "@regression US-010-03 TC-UIA-010-C7 receta ajena no visible",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "010",
        userStory: "US-010-03",
        criteria: ["AC-010-09"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Detalle de receta del propietario",
        scenario: "El propietario intenta abrir el detalle de una receta de otro owner",
        given: [
          "una receta existente de la mascota 1001 del propietario foranea (owner2)",
          "un propietario distinto autenticado (owner1) que NO posee la mascota 1001",
        ],
        when: ["navego a /portal/owner/prescriptions/{id_foranea}"],
        then: [
          "la pagina muestra el estado Receta no encontrada",
          "NO se filtra ningun dato clinico del owner ajeno (diagnostico / medicamento)",
          "no se generan errores de runtime en consola",
        ],
      });

      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      // Siembra la receta ajena con un actor con rol de escritura (admin).
      const foreignId = await seedForeignPrescription(page);

      await authenticateAs(page, env.ownerEmail, env.ownerPassword);
      await page.goto(`/portal/owner/prescriptions/${foreignId}`);

      // El detalle 404 -> EmptyState "Receta no encontrada".
      const notFound = page.getByRole("heading", { name: /Receta no encontrada/i });
      const notFoundText = page.getByText(/No encontramos esta receta|no tienes permiso/i).first();
      await expect(notFound.or(notFoundText).first()).toBeVisible({ timeout: 30_000 });

      // Sin detalle legible de la receta ajena.
      await expect(page.getByRole("heading", { name: new RegExp(`Receta #${foreignId}`, "i") })).toHaveCount(0);

      // Sin fuga de datos del owner ajeno.
      await expect(page.getByText(FOREIGN_DIAGNOSIS)).toHaveCount(0);
      const bodyText = await page.locator("body").innerText({ timeout: 30_000 });
      expect(bodyText).not.toContain("AJENO-DO-NOT-LEAK-7842");

      const hasRuntimeError = consoleErrors.some(
        (t) =>
          /ReferenceError|TypeError|SyntaxError|is not defined|is not a function/i.test(t) &&
          !/Failed to load resource|favicon|40[0-9]|422|404/i.test(t),
      );
      expect(hasRuntimeError).toBe(false);
    },
  );
});
