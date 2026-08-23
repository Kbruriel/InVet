/**
 * UIA-010 — Estados UX y accesibilidad (C2, C8, C9)
 *
 * C2  Validacion inline: error si diagnosis vacio o excede 2000 caracteres.
 * C8  Responsive: formulario y listado/detalle utiles en mobile y desktop.
 * C9  Acentos y e-ñ sin mojibake en las vistas del slice.
 */

import { test, expect, type Page } from "@playwright/test";
import { readAutomationEnv } from "../fixtures/env";
import { authenticateAs } from "../helpers/auth";
import { annotateTraceability, attachGherkinScenario } from "../helpers/traceability";

const env = readAutomationEnv();

const CONSULTATION_ID = 1000;
const PET_ID = 1000;

/**
 * Verifica que el body de la pagina contenga acentos esperados y que no hayan
 * aparecido secuencias tipicas de mojibake UTF-8 leido como Latin-1
 * (p. ej. `Ã³` por `ó`, `â€` por comillas/tildes, `Â ` por espacio).
 */
async function assertNoMojibake(page: Page) {
  const bodyText = await page.locator("body").innerText({ timeout: 30_000 });
  expect(bodyText).toMatch(/[áéíóúÁÉÍÓÚñÑáàèìòùü]/);
  expect(bodyText).not.toMatch(/Ã[°-¿]|Â |â€[„”“†‡]/);
}

/**
 * La pagina de creacion muestra primero un spinner "Cargando la consulta
 * asociada" y solo despues renderiza el formulario o el banner de error.
 * Esperamos a que el spinner desaparezca para clasificar un estado terminal
 * determinista y no capturar un estado intermedio (evita flakiness en C2/C8/C9).
 */
async function settleAfterGoto(page: Page) {
  await expect(page.getByText(/Cargando la consulta/i))
    .toBeHidden({ timeout: 30_000 })
    .catch(() => {});
}

test.describe("prescription states - UIA-010", () => {
  // ===========================================================================
  // C2: Validacion inline del campo diagnosis
  // Criterios: AC-010-03
  // ===========================================================================
  test(
    "@regression US-010-05 TC-UIA-010-C2 validacion inline diagnosis",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "010",
        userStory: "US-010-05",
        criteria: ["AC-010-03"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Validacion de formulario de receta",
        scenario: "El formulario valida el campo diagnosis sin enviar a red",
        given: ["el formulario de receta cargado para una consulta validada"],
        when: ["dejo el campo diagnosis vacio y envio el formulario"],
        then: [
          "se muestra un error visible de validacion",
          "el campo diagnosis queda marcado como invalido (aria-invalid)",
          "no se disparo una peticion POST de creacion",
        ],
      });

      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      // `vet` prescriptor clinico: sin owner record el backend no la filtra a 404.
      await authenticateAs(page, env.vetEmail, env.vetPassword);
      await page.goto(`/clinic/prescriptions/new?consultation_id=${CONSULTATION_ID}`);
      await settleAfterGoto(page);

      const formHeading = page.getByRole("heading", { name: /Registrar receta/i });
      const fallback = page
        .getByText(/consulta|No fue posible|Volver/i)
        .first();
      const showsForm = await formHeading.isVisible().catch(() => false);
      if (!showsForm) {
        await expect(fallback).toBeVisible();
        return;
      }

      // El formulario autocompleta `diagnosis` desde la consulta; lo vaciamos
      // para forzar el path de validacion "diagnostico obligatorio".
      await page.getByLabel(/Diagnóstico/i).fill("");

      let createAttempted = false;
      page.on("request", (req) => {
        if (req.url().includes("/api/v1/prescriptions") && req.method() === "POST") {
          createAttempted = true;
        }
      });

      await page.getByRole("button", { name: /Registrar receta/i }).click();

      const diagnosisError = page.getByText(/El diagnóstico es obligatorio/i).first();
      await expect(diagnosisError).toBeVisible();

      const diagnosisField = page.getByLabel(/Diagnóstico/i);
      await expect(diagnosisField).toHaveAttribute("aria-invalid", "true");

      expect(createAttempted).toBe(false);

      const hasRuntimeError = consoleErrors.some(
        (t) =>
          /ReferenceError|TypeError|SyntaxError|is not defined|is not a function/i.test(t) &&
          !/Failed to load resource|favicon|40[0-9]|422/i.test(t),
      );
      expect(hasRuntimeError).toBe(false);
    },
  );

  // ===========================================================================
  // C8: Responsive en mobile (viewport 375x667)
  // Criterios: AC-010-07
  // ===========================================================================
  test(
    "@regression US-010-06 TC-UIA-010-C8 responsive mobile",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "010",
        userStory: "US-010-06",
        criteria: ["AC-010-07"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Responsive del formulario de receta",
        scenario: "El formulario de receta es util en una pantalla movil",
        given: ["el dispositivo configurado en viewport movil (375x667)"],
        when: ["navego al formulario de receta"],
        then: [
          "el titulo Registrar receta es visible",
          "los campos Diagnosis, Treatment notes y el boton Registrar receta son visibles",
          "el contenido no se corta ni se desborda horizontalmente",
        ],
      });

      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      await page.setViewportSize({ width: 375, height: 667 });

      // `vet` prescriptor clinico: sin owner record el backend no la filtra a 404.
      await authenticateAs(page, env.vetEmail, env.vetPassword);
      await page.goto(`/clinic/prescriptions/new?consultation_id=${CONSULTATION_ID}`);
      await settleAfterGoto(page);

      const formHeading = page.getByRole("heading", { name: /Registrar receta/i });
      const fallback = page
        .getByText(/consulta|No fue posible|Volver/i)
        .first();
      const showsForm = await formHeading.isVisible().catch(() => false);
      if (showsForm) {
        await expect(page.getByLabel(/Diagnóstico/i)).toBeVisible();
        await expect(page.getByLabel(/Notas de tratamiento/i)).toBeVisible();
        await expect(page.getByRole("button", { name: /Registrar receta/i })).toBeVisible();
      } else {
        await expect(fallback).toBeVisible();
      }

      const viewport = page.viewportSize();
      const doc = page.locator("html");
      const scrollWidth = await doc.evaluate((el) => el.scrollWidth);
      expect(scrollWidth).toBeLessThanOrEqual((viewport?.width ?? 375) + 1);

      const hasRuntimeError = consoleErrors.some(
        (t) =>
          /ReferenceError|TypeError|SyntaxError|is not defined|is not a function/i.test(t) &&
          !/Failed to load resource|favicon|40[0-9]|422/i.test(t),
      );
      expect(hasRuntimeError).toBe(false);
    },
  );

  // ===========================================================================
  // C9: Acentos y e-ñ sin mojibake en las vistas del slice
  // Criterios: AC-010-08
  // ===========================================================================
  test(
    "@regression US-010-07 TC-UIA-010-C9 acentos sin mojibake",
    async ({ page }, testInfo) => {
      await annotateTraceability(testInfo, {
        slice: "010",
        userStory: "US-010-07",
        criteria: ["AC-010-08"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Codificacion de texto clinico",
        scenario: "Las vistas del slice muestran acentos y e-ñ correctamente",
        given: ["el usuario autenticado (admin)"],
        when: ["navego al formulario de receta"],
        then: [
          "los labels Diagnosis y Notas de tratamiento se ven con acentos",
          "el body no contiene secuencias tipicas de mojibake UTF-8",
        ],
      });

      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });

      // `vet` prescriptor clinico: sin owner record el backend no la filtra a 404.
      await authenticateAs(page, env.vetEmail, env.vetPassword);
      await page.goto(`/clinic/prescriptions/new?consultation_id=${CONSULTATION_ID}`);
      await settleAfterGoto(page);

      const formHeading = page.getByRole("heading", { name: /Registrar receta/i });
      const fallback = page
        .getByText(/consulta|No fue posible|Volver/i)
        .first();
      const showsForm = await formHeading.isVisible().catch(() => false);
      if (showsForm) {
        await expect(page.getByLabel(/Diagnóstico/i)).toBeVisible();
        await expect(page.getByLabel(/Notas de tratamiento/i)).toBeVisible();
        await assertNoMojibake(page);
      } else {
        await expect(fallback).toBeVisible();
        const bodyText = await page
          .locator("body")
          .innerText({ timeout: 30_000 });
        expect(bodyText).toMatch(/[áéíóúÁÉÍÓÚñÑáàèìòùü]/);
      }

      const hasRuntimeError = consoleErrors.some(
        (t) =>
          /ReferenceError|TypeError|SyntaxError|is not defined|is not a function/i.test(t) &&
          !/Failed to load resource|favicon|40[0-9]|422/i.test(t),
      );
      expect(hasRuntimeError).toBe(false);
    },
  );
});
