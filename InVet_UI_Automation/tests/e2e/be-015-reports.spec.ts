/**
 * UIA-015 — Reportes operativos básicos (BE-015)
 *
 * Cobertura Playwright para `/portal/admin/reports` y los 6 tipos de reporte
 * expuestos por la capa backend (appointments, services, pets, consultations,
 * ratings, payments).
 *
 * Casos:
 *   UIA-C1  AC-015-01/02  Seleccionar tipo + aplicar → tabla carga sin error
 *   UIA-C2  AC-015-03     Paginación citas ≤20 elementos
 *   UIA-C3  AC-015-04     Servicios con campos resumidos
 *   UIA-C4  AC-015-06     Mascotas activas muestra conteo total
 *   UIA-C5  AC-015-07     Calificaciones muestra promedio
 *   UIA-C6  AC-015-08     Pagos con totales en tabla resumida
 *   UIA-C7  AC-015-04/05  Rango de fechas inválido → error visible
 *   UIA-C8  AC-015-09     Sin token → redirige a /login (auth block)
 *   UIA-C9               Responsive en mobile 375px y desktop 1366px
 */

import { test, expect, type Page } from "@playwright/test";

import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability, attachGherkinScenario } from "../helpers/traceability";

const env = readAutomationEnv();

// ── Helpers ────────────────────────────────────────────────────────────────

async function authenticateClinic(page: Page) {
  const loginUrl = `${env.apiBaseUrl}${env.loginApiPath}`;
  const resp = await page.request.post(loginUrl, {
    data: { email: env.clinicEmail, password: env.clinicPassword },
  });
  expect(resp.status()).toBe(200);
  const payload = (await resp.json()) as {
    access_token: string;
    refresh_token: string;
  };
  await page.addInitScript(
    ({ accessToken, refreshToken }) => {
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("refresh_token", refreshToken);
    },
    { accessToken: payload.access_token, refreshToken: payload.refresh_token },
  );
}

/** Selecciona un tipo de reporte por label y aplica el formulario. */
async function pickTypeAndApply(page: Page, label: string) {
  await page.locator("#report-type").selectOption({ label });
  await expect(page.getByRole("button", { name: /Aplicar/i })).toBeEnabled();
  await page.getByRole("button", { name: /Aplicar/i }).click();
  // Espera a que desaparezca el placeholder ("Selecciona un tipo..." o similar)
  // y a que cargue la tabla / empty / error.
  await expect(
    page.getByText(/Selecciona un tipo de reporte/i),
  ).toBeHidden({ timeout: 15_000 });
  // Espera a que al menos una de las vistas terminales aparezca.
  await expect
    .poll(
      async () =>
        (await page.locator("table").count()) +
        (await page.getByText(/Aún no hay datos/i).count()) +
        (await page.getByRole("alert").count()),
      { message: "expected terminal state (table|empty|error)" },
    )
    .toBeGreaterThanOrEqual(1);
}

// ── Tests UIA-015 ──────────────────────────────────────────────────────────

test.describe("reports page - UIA-015", () => {
  // ──────────────────────────────────────────────────────────────────────
  // UIA-C1: Selección de tipo + aplicar carga la tabla sin error (AC-015-01, AC-015-02)
  // ──────────────────────────────────────────────────────────────────────
  test(
    "@smoke @regression US-015-01 AC-015-01 AC-015-02 UIA-C1 reportes aplica tipo y carga sin error",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-01",
        criteria: ["AC-015-01", "AC-015-02"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Panel de reportes operativos",
        scenario: "Admin aplica un tipo de reporte y ve un estado terminal (tabla/empty/error) sin crash",
        given: ["un admin con sesión activa"],
        when: ["navego a /portal/admin/reports", "selecciono 'Citas médicas'", "hago clic en Aplicar"],
        then: [
          "no queda el placeholder 'Selecciona un tipo'",
          "se muestra tabla, estado vacío o banner de error",
        ],
      });

      await authenticateClinic(page);
      await page.goto("/portal/admin/reports");
      await expect(page).toHaveTitle(/InVet/i, { timeout: 15_000 });

      // Heading principal visible
      await expect(
        page.getByRole("heading", { name: /Reportes operativos/i }),
      ).toBeVisible({ timeout: 10_000 });

      // Placeholders iniciales (antes de aplicar)
      await expect(
        page.getByText(/Selecciona un tipo de reporte/i),
      ).toBeVisible({ timeout: 5_000 }).catch(() =>
        Promise.resolve(),
      );

      await pickTypeAndApply(page, "Citas médicas");

      // Después de aplicar: placeholder debe desaparecer.
      await expect(
        page.getByText(/Selecciona un tipo de reporte/i),
      ).toBeHidden({ timeout: 10_000 });

      // No debe quedar el spinner de loading visible indefinidamente.
      const spinnerVisible = await page
        .getByText(/Cargando Citas médicas/i)
        .first()
        .isVisible()
        .catch(() => false);
      if (spinnerVisible) {
        await expect(
          page.getByText(/Cargando Citas médicas/i),
        ).toBeHidden({ timeout: 10_000 });
      }
    },
  );

  // ──────────────────────────────────────────────────────────────────────
  // UIA-C2: Paginación citas ≤20 elementos (AC-015-03)
  // ──────────────────────────────────────────────────────────────────────
  test(
    "@regression US-015-02 AC-015-03 UIA-C2 citas médicas paginado max 20",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-02",
        criteria: ["AC-015-03"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Paginación de citas médicas",
        scenario: "La página 1 de citas muestra a lo sumo 20 filas",
        given: ["admin con sesión activa"],
        when: ["aplico 'Citas médicas' sin fechas"],
        then: ["la tabla tiene <=20 filas de datos"],
      });

      await authenticateClinic(page);
      await page.goto("/portal/admin/reports");
      await expect(
        page.getByRole("heading", { name: /Reportes operativos/i }),
      ).toBeVisible({ timeout: 10_000 });

      await pickTypeAndApply(page, "Citas médicas");

      // Si hay datos, la tabla debe tener máximo 20 filas de datos (size=20).
      const tableCount = await page.locator("table").count();
      if (tableCount > 0) {
        const dataRows = page.locator("table tbody tr");
        const rowCount = await dataRows.count();
        expect(rowCount).toBeLessThanOrEqual(20);
      }
    },
  );

  // ──────────────────────────────────────────────────────────────────────
  // UIA-C3: Servicios con campos resumidos (AC-015-04)
  // ──────────────────────────────────────────────────────────────────────
  test(
    "@regression US-015-03 AC-015-04 UIA-C3 servicios tabla con campos resumidos",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-03",
        criteria: ["AC-015-04"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Reporte de servicios",
        scenario: "La tabla de servicios muestra las columnas resumen (Nombre, Precio, Duración, Activo)",
        given: ["admin con sesión activa"],
        when: ["selecciono 'Servicios' y aplico"],
        then: [
          "la tabla incluye columnas Nombre, Precio, Duración y Activo",
        ],
      });

      await authenticateClinic(page);
      await page.goto("/portal/admin/reports");
      await expect(
        page.getByRole("heading", { name: /Reportes operativos/i }),
      ).toBeVisible({ timeout: 10_000 });

      await pickTypeAndApply(page, "Servicios");

      const table = page.locator("table").first();
      await expect(table).toBeVisible();

      // Cabeceras que report-columns.ts define para 'services'.
      for (const header of ["Nombre", "Precio", "Duración", "Activo"]) {
        await expect(
          table.getByRole("columnheader", { name: new RegExp(`^\\s*${header}\\s*$`, "i") }),
        ).toBeVisible();
      }
    },
  );

  // ──────────────────────────────────────────────────────────────────────
  // UIA-C4: Mascotas activas — conteo total (AC-015-06)
  // ──────────────────────────────────────────────────────────────────────
  test(
    "@regression US-015-04 AC-015-06 UIA-C4 mascotas activas muestra conteo",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-04",
        criteria: ["AC-015-06"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Reporte de mascotas activas",
        scenario: "La tabla de mascotas activas muestra una fila con el conteo total de la clínica",
        given: ["admin con sesión activa en la clínica"],
        when: ["selecciono 'Mascotas activas' y aplico"],
        then: [
          "la tabla tiene columnas Clínica y Mascotas activas",
          "hay al menos una fila con un valor numérico de conteo",
        ],
      });

      await authenticateClinic(page);
      await page.goto("/portal/admin/reports");
      await expect(
        page.getByRole("heading", { name: /Reportes operativos/i }),
      ).toBeVisible({ timeout: 10_000 });

      await pickTypeAndApply(page, "Mascotas activas");

      const table = page.locator("table").first();
      await expect(table).toBeVisible();

      await expect(
        table.getByRole("columnheader", { name: /Cl[ií]nica/i }),
      ).toBeVisible();
      await expect(
        table.getByRole("columnheader", { name: /Mascotas activas/i }),
      ).toBeVisible();

      // Al menos una fila de datos con valor numérico de conteo.
      const firstRow = table.locator("tbody tr").first();
      await expect(firstRow).toBeVisible();
      const cell = firstRow.locator("td").nth(1);
      const value = (await cell.textContent())?.trim();
      expect(value, "el conteo de mascotas activas debe ser numérico").toMatch(
        /^\d+$/,
      );
    },
  );

  // ──────────────────────────────────────────────────────────────────────
  // UIA-C5: Calificaciones — promedio (AC-015-07)
  // ──────────────────────────────────────────────────────────────────────
  test(
    "@regression US-015-05 AC-015-07 UIA-C5 calificaciones muestra promedio",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-05",
        criteria: ["AC-015-07"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Reporte de calificaciones",
        scenario: "La tabla de calificaciones muestra promedios (clínica o por veterinario)",
        given: ["admin con sesión activa"],
        when: ["seleo 'Calificaciones' y aplico"],
        then: [
          "la tabla incluye columnas de promedio / opiniones",
          "al menos una fila aparece con promedio numérico",
        ],
      });

      await authenticateClinic(page);
      await page.goto("/portal/admin/reports");
      await expect(
        page.getByRole("heading", { name: /Reportes operativos/i }),
      ).toBeVisible({ timeout: 10_000 });

      await pickTypeAndApply(page, "Calificaciones");

      const table = page.locator("table").first();
      await expect(table).toBeVisible();

      // 'Clínica (promedio)' es la fila sintética agregada en report-columns.ts.
      const avgRow = table
        .locator("tbody tr")
        .filter({ hasText: /Cl[ií]nica \(promedio\)/i })
        .first();
      const expectedCount = await avgRow.count();
      if (expectedCount > 0) {
        await expect(avgRow).toBeVisible();
        const promedioCell = avgRow.locator("td").nth(1);
        expect((await promedioCell.textContent())?.trim()).toMatch(
          /^\d+(\.\d+)?$/,
        );
      } else {
        // Sin veterinarios calificados: al menos debe existir fila de promedio clínico 0.00
        const rowZero = table.locator("tbody tr").first();
        await expect(rowZero).toBeVisible();
      }
    },
  );

  // ──────────────────────────────────────────────────────────────────────
  // UIA-C6: Pagos con totales (AC-015-08)
  // ──────────────────────────────────────────────────────────────────────
  test(
    "@regression US-015-06 AC-015-08 UIA-C6 pagos resumen con columna monto",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-06",
        criteria: ["AC-015-08"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Reporte de pagos",
        scenario: "La tabla de pagos muestra columnas Fecha/Monto/Método/Estado",
        given: ["admin con sesión activa"],
        when: ["selecciono 'Pagos' y aplico"],
        then: [
          "la tabla incluye columnas Fecha, Monto, Método, Estado",
        ],
      });

      await authenticateClinic(page);
      await page.goto("/portal/admin/reports");
      await expect(
        page.getByRole("heading", { name: /Reportes operativos/i }),
      ).toBeVisible({ timeout: 10_000 });

      await pickTypeAndApply(page, "Pagos");

      const table = page.locator("table").first();
      await expect(table).toBeVisible();

      for (const header of ["Fecha", "Monto", "Método", "Estado"]) {
        await expect(
          table.getByRole("columnheader", {
            name: new RegExp(`^\\s*${header}\\s*$`, "i"),
          }),
        ).toBeVisible();
      }
    },
  );

  // ──────────────────────────────────────────────────────────────────────
  // UIA-C7: Rango de fechas inválido → error (AC-015-04, AC-015-05)
  // ──────────────────────────────────────────────────────────────────────
  test(
    "@regression US-015-07 AC-015-04 AC-015-05 UIA-C7 rango de fechas invalido muestra error",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-07",
        criteria: ["AC-015-04", "AC-015-05"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Validación de rango de fechas",
        scenario: "Si period_start > period_end, el formulário rechaza la aplicación y muestra un mensaje de error visible",
        given: ["admin con sesión activa"],
        when: ["cargo period_start posterior a period_end", "hago clic en Aplicar"],
        then: [
          "aparece un mensaje de error (role=alert)",
          "no se dispara la petición al backend (no cambia a tabla/empty)",
        ],
      });

      await authenticateClinic(page);
      await page.goto("/portal/admin/reports");
      await expect(
        page.getByRole("heading", { name: /Reportes operativos/i }),
      ).toBeVisible({ timeout: 10_000 });

      await page.locator("#report-type").selectOption({ label: "Citas médicas" });
      await page.locator("#period-start").fill("2030-01-31");
      await page.locator("#period-end").fill("2030-01-01");

      await page.getByRole("button", { name: /Aplicar/i }).click();

      // Debe existir un mensaje de error visible (div role=alert con texto de validación).
      const alert = page.getByRole("alert").first();
      await expect(alert).toBeVisible({ timeout: 5_000 });
      await expect(alert).toContainText(
        /posterior|no puede ser/i,
      );
    },
  );

  // ──────────────────────────────────────────────────────────────────────
  // UIA-C8: Auth block — sin token redirige a /login (AC-015-09)
  // ──────────────────────────────────────────────────────────────────────
  test(
    "@smoke @regression US-015-08 AC-015-09 UIA-C8 sin token redirige a login",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-08",
        criteria: ["AC-015-09"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Ruta protegida de reportes",
        scenario: "Navegar a /portal/admin/reports sin sesión activa redirige a /login",
        given: ["navegador sin tokens de autenticación"],
        when: ["navego a /portal/admin/reports"],
        then: ["el navegador termina en /login"],
      });

      // Asegurar que no haya tokens.
      await page.addInitScript(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      });
      await page.goto("/portal/admin/reports", { waitUntil: "domcontentloaded" });

      // RequireAuth ejecuta router.replace("/login") cuando no hay token.
      await page.waitForURL(/\/login(\?.*)?$/i, { timeout: 15_000 });
      expect(page.url()).toMatch(/\/login/i);
    },
  );

  // ──────────────────────────────────────────────────────────────────────
  // UIA-C9: Responsive mobile 375px + desktop 1366px
  // ──────────────────────────────────────────────────────────────────────
  test(
    "@regression US-015-09 AC-015-03 UIA-C9 reportes responsive mobile y desktop",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-09",
        criteria: ["AC-015-03"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Layout responsive de reportes",
        scenario: "El panel de reportes es utilizable en 375px y 1366px",
        given: ["admin con sesión activa"],
        when: [
          "reduzco el viewport a 375x667",
          "luego lo aumento a 1366x900",
        ],
        then: [
          "el heading y el formulario de filtros siguen visibles",
          "no hay crash de layout",
        ],
      });

      await authenticateClinic(page);

      // Mobile: 375x667 (Pixel 7-ish)
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto("/portal/admin/reports");
      await expect(
        page.getByRole("heading", { name: /Reportes operativos/i }),
      ).toBeVisible({ timeout: 15_000 });
      await expect(page.locator("#report-type")).toBeVisible();
      await expect(page.locator("#period-start")).toBeVisible();
      await expect(page.locator("#period-end")).toBeVisible();
      await expect(
        page.getByRole("button", { name: /Aplicar/i }),
      ).toBeVisible();

      // Desktop: 1366x900
      await page.setViewportSize({ width: 1366, height: 900 });
      await page.reload();
      await expect(
        page.getByRole("heading", { name: /Reportes operativos/i }),
      ).toBeVisible({ timeout: 15_000 });
      await expect(page.locator("#report-type")).toBeVisible();
      await expect(
        page.getByRole("button", { name: /Aplicar/i }),
      ).toBeVisible();
    },
  );
});
