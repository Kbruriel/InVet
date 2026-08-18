/**
 * UIA-003 - Live smoke/regression for the public clinics page.
 *
 * This spec does not mock the clinics API. It is meant to catch real
 * frontend/network failures on the production-like local URL.
 */

import { expect, test } from "@playwright/test";

import { annotateTraceability, attachGherkinScenario } from "../../helpers/traceability";

const expectedFrontendOrigin = "http://localhost:3000";

test.describe("public clinics live smoke - UIA-003", () => {
  test(
    "@smoke @regression US-003 AC-003-05 live public clinics page renders on localhost:3000",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado publico de clinicas",
        scenario: "La pagina de clinicas carga contra el frontend real en localhost:3000",
        given: ["el frontend de InVet esta disponible en http://localhost:3000"],
        when: [
          "la persona visitante navega a /clinicas",
          "la pagina termina de cargar",
        ],
        then: [
          "la URL final queda en http://localhost:3000/clinicas",
          "el encabezado del listado es visible",
          "los chips de categoria son visibles",
          "no aparece un mensaje de error de carga",
          "no se observan fallos de red o errores de pagina asociados al listado",
        ],
      });

      const pageErrors: string[] = [];
      const failedClinicRequests: string[] = [];
      const failedClinicResponses: string[] = [];
      const consoleErrors: string[] = [];

      page.on("pageerror", (error) => {
        pageErrors.push(error.message);
      });

      page.on("requestfailed", (request) => {
        if (request.url().includes("/api/v1/clinicas")) {
          failedClinicRequests.push(
            `${request.method()} ${request.url()} ${request.failure()?.errorText || "request failed"}`
          );
        }
      });

      page.on("response", (response) => {
        if (response.url().includes("/api/v1/clinicas") && response.status() >= 500) {
          failedClinicResponses.push(`${response.status()} ${response.url()}`);
        }
      });

      page.on("console", (msg) => {
        const text = msg.text();
        if (msg.type() === "error" && /clinicas|Failed to load resource|Internal Server Error|ERR_CONNECTION_REFUSED/i.test(text)) {
          consoleErrors.push(text);
        }
      });

      await page.goto("/clinicas");
      await page.waitForTimeout(1000);

      await expect(page).toHaveURL(`${expectedFrontendOrigin}/clinicas`);
      expect(new URL(page.url()).origin).toBe(expectedFrontendOrigin);

      const title = page.getByRole("heading", { name: "Clinicas veterinarias" });
      await expect(title).toBeVisible();

      const chips = page.locator('[aria-label^="Filtrar por"]');
      await expect(chips).toHaveCount(3);

      await expect(page.getByRole("status", { name: "Cargando clinicas" })).toHaveCount(0, {
        timeout: 15_000,
      });

      const clinicCards = page.locator("h3");
      const cardCount = await clinicCards.count();
      if (cardCount > 0) {
        await expect(clinicCards.first()).toBeVisible();
      } else {
        await expect(page.getByText("No se encontraron clinicas")).toBeVisible();
      }

      await expect(page.getByText("No se pudieron cargar las clinicas. Intenta de nuevo.")).toHaveCount(0);
      await expect(page.getByRole("button", { name: "Reintentar" })).toHaveCount(0);

      expect(pageErrors).toHaveLength(0);
      expect(failedClinicRequests).toHaveLength(0);
      expect(failedClinicResponses).toHaveLength(0);
      expect(consoleErrors).toHaveLength(0);
    },
  );
});
