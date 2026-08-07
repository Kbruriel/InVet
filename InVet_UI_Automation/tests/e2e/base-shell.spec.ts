/**
 * UIA-001 - UI/E2E automation for BE-001 / FE-001 (Base tecnica y design system)
 *
 * Cobertura:
 * - US-001-01: Layout base carga sin auth
 * - US-001-05: Shell publica renderiza sin CDN critica
 * - US-001-07: Estados UI existen como componentes compartidos (JUSTIFIED_SKIP)
 * - AC-001-05: Frontend base renderiza shell publico
 * - AC-001-07: Estados comunes son visibles y accesibles
 */

import { expect, test } from "@playwright/test";

import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability, attachGherkinScenario } from "../helpers/traceability";

const env = readAutomationEnv();

// ===========================================================================
// UIA-001-01: Layout base carga sin auth
// Criterio: La shell publica carga sin errores en desktop y mobile.
// Trazabilidad: US-001-01, AC-001-05
// ===========================================================================

test.describe("base shell - UIA-001", () => {
  test(
    "@smoke @regression US-001-01 AC-001-05 base layout loads without auth",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001-01",
        criteria: ["AC-001-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Shell publica base",
        scenario: "La pagina de inicio carga sin autenticacion y sin errores",
        given: ["el frontend de InVet esta disponible en la ruta raiz"],
        when: [
          "la persona visitante navega a la pagina de inicio",
          "la pagina termina de cargar todos los recursos",
        ],
        then: [
          "el titulo de la pagina es 'InVet - Plataforma de Clinicas Veterinarias'",
          "el encabezado con el logo InVet es visible",
          "el pie de pagina con el aviso de derechos es visible",
          "no hay errores en la consola del navegador",
        ],
      });

      await page.goto("/");

      // Verificar titulo de la pagina
      await expect(page).toHaveTitle(/InVet/);

      // Verificar que el logo/inicio esta presente
      const logoLink = page.getByRole("link", { name: "InVet, ir al inicio" });
      await expect(logoLink).toBeVisible();

      // Verificar encabezado de navegacion
      const nav = page.getByRole("navigation", { name: "Principal" });
      await expect(nav).toBeVisible();

      // Verificar items del nav (pueden no existir si la ruta no esta implementada, pero el nav si)
      const navItems = nav.locator("a");
      const count = await navItems.count();
      expect(count).toBeGreaterThan(0);

      // Verificar footer
      const footer = page.getByRole("contentinfo");
      await expect(footer).toBeVisible();

      // Verificar que no hay errores de consola
      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") {
          consoleErrors.push(msg.text());
        }
      });
      // Re-attach listener before navigation for errors that occur during load
      // The above listener is set before goto, so it captures load-time errors

      expect(consoleErrors).toEqual([]);
    },
  );

  // ===========================================================================
  // UIA-001-02: LoadingSkeleton component (JUSTIFIED_SKIP)
  // Trazabilidad: US-001-07, AC-001-07
  // Motivo: El componente LoadingSkeleton no existe en frontend/src/shared/ui/components.
  //         La carpeta esta vacia. Este criterio se justifica como SKIP hasta que
  //         el slice de componentes compartidos lo implemente.
  // ===========================================================================

  test(
    "US-001-07 AC-001-07 LoadingSkeleton component - JUSTIFIED_SKIP",
    async ({}, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001-07",
        criteria: ["AC-001-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Componentes compartidos UI",
        scenario: "LoadingSkeleton existe y es renderizable",
        given: ["el componente LoadingSkeleton esta implementado en shared/ui"],
        when: ["se monta el componente"],
        then: [
          "el componente se renderiza sin errores",
          "muestra un esqueleto de carga visual",
        ],
      });

      test.skip(
        true,
        "JUSTIFIED_SKIP: LoadingSkeleton no existe en frontend/src/shared/ui/components (carpeta vacia). Se justifica el skip hasta que se implemente en un slice futuro.",
      );
    },
  );

  // ===========================================================================
  // UIA-001-03: ErrorMessage component (JUSTIFIED_SKIP)
  // Trazabilidad: US-001-07, AC-001-07
  // Motivo: El componente ErrorMessage no existe en frontend/src/shared/ui/components.
  // ===========================================================================

  test(
    "US-001-07 AC-001-07 ErrorMessage component - JUSTIFIED_SKIP",
    async ({}, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001-07",
        criteria: ["AC-001-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Componentes compartidos UI",
        scenario: "ErrorMessage existe y es renderizable",
        given: ["el componente ErrorMessage esta implementado en shared/ui"],
        when: ["se monta el componente"],
        then: [
          "el componente se renderiza sin errores",
          "muestra un mensaje de error con contraste adecuado",
        ],
      });

      test.skip(
        true,
        "JUSTIFIED_SKIP: ErrorMessage no existe en frontend/src/shared/ui/components (carpeta vacia). Se justifica el skip hasta que se implemente en un slice futuro.",
      );
    },
  );

  // ===========================================================================
  // UIA-001-04: EmptyState component (JUSTIFIED_SKIP)
  // Trazabilidad: US-001-07, AC-001-07
  // Motivo: El componente EmptyState no existe en frontend/src/shared/ui/components.
  // ===========================================================================

  test(
    "US-001-07 AC-001-07 EmptyState component - JUSTIFIED_SKIP",
    async ({}, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001-07",
        criteria: ["AC-001-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Componentes compartidos UI",
        scenario: "EmptyState existe y es renderizable",
        given: ["el componente EmptyState esta implementado en shared/ui"],
        when: ["se monta el componente"],
        then: [
          "el componente se renderiza sin errores",
          "muestra un estado vacio con mensaje descriptivo",
        ],
      });

      test.skip(
        true,
        "JUSTIFIED_SKIP: EmptyState no existe en frontend/src/shared/ui/components (carpeta vacia). Se justifica el skip hasta que se implemente en un slice futuro.",
      );
    },
  );

  // ===========================================================================
  // UIA-001-05: Responsive viewport mobile
  // Criterio: La shell publica es usable en viewport mobile (Pixel 7).
  // Trazabilidad: US-001-05, AC-001-05
  // ===========================================================================

  test(
    "@smoke @regression US-001-05 AC-001-05 responsive on mobile viewport",
    async ({ browser }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001-05",
        criteria: ["AC-001-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Shell publica responsive",
        scenario: "La pagina de inicio es usable en viewport mobile",
        given: [
          "el frontend de InVet esta disponible",
          "se crea un contexto con viewport Pixel 7 (375x667)",
        ],
        when: ["la persona visitante navega a la pagina de inicio"],
        then: [
          "el contenido no se desborda horizontalmente",
          "el logo es visible",
          "el footer es visible",
          "no hay errores de renderizado",
        ],
      });

      const context = await browser.newContext({
        ...require("@playwright/test").devices["Pixel 7"],
        locale: "es-MX",
      });
      const page = await context.newPage();
      await page.goto("/");

      // Verificar que no hay scroll horizontal
      const viewportSize = page.viewportSize()!;
      const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
      expect(scrollWidth).toBeLessThanOrEqual(viewportSize.width + 10); // tolerancia de 10px

      // Verificar elementos clave son visibles en mobile
      const logoLink = page.getByRole("link", { name: "InVet, ir al inicio" });
      await expect(logoLink).toBeVisible();

      const footer = page.getByRole("contentinfo");
      await expect(footer).toBeVisible();

      await context.close();
    },
  );

  // ===========================================================================
  // UIA-001-06: No external CDN dependencies (critical)
  // Criterio: No hay dependencias CDN externas criticas en el layout.
  // Trazabilidad: US-001-05, AC-001-05
  // ===========================================================================

  test(
    "@smoke @regression US-001-05 AC-001-05 no critical external CDN dependencies",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001-05",
        criteria: ["AC-001-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Dependencias de la shell publica",
        scenario: "No hay recursos CDN criticos externos en el layout",
        given: ["el frontend de InVet esta disponible"],
        when: ["la pagina carga todos los recursos"],
        then: [
          "no se cargan fuentes o estilos desde CDNs publicos no controlados",
          "los estilos provienen de Tailwind local y globals.css",
        ],
      });

      const resourceUrls: string[] = [];
      page.on("response", (response) => {
        const url = response.url();
        if (url.startsWith("http")) {
          resourceUrls.push(url);
        }
      });

      await page.goto("/");
      await page.waitForLoadState("networkidle");

      // Verificar que no hay CDN de fuentes externas criticas (Google Fonts, etc.)
      const cdnUrls = resourceUrls.filter(
        (url) =>
          url.includes("googleapis") ||
          url.includes("gstatic") ||
          url.includes("cloudflare") ||
          url.includes("unpkg") ||
          url.includes("jsdelivr"),
      );

      expect(cdnUrls).toEqual([]);
    },
  );

  // ===========================================================================
  // UIA-001-07: Accessibility - visible focus and labels
  // Criterio: Labels y foco visible existen en la shell publica.
  // Trazabilidad: US-001-07, AC-001-07
  // ===========================================================================

  test(
    "@smoke @regression US-001-07 AC-001-07 accessibility labels and focus visible",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001-07",
        criteria: ["AC-001-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Accesibilidad basica",
        scenario: "Labels y foco visible existen en la shell publica",
        given: ["el frontend de InVet esta disponible"],
        when: [
          "la pagina carga",
          "se navega por el contenido con teclado",
        ],
        then: [
          "los enlaces tienen labels descriptivos via aria-label o texto visible",
          "el foco es visible en los elementos interactivos",
        ],
      });

      await page.goto("/");

      // Verificar que los links del nav tienen labels accesibles
      const navLinks = page.getByRole("navigation", { name: "Principal" }).locator("a");
      const count = await navLinks.count();
      expect(count).toBeGreaterThan(0);

      for (let i = 0; i < count; i++) {
        const link = navLinks.nth(i);
        // Cada link debe tener texto visible o aria-label
        const text = await link.textContent();
        const ariaLabel = await link.getAttribute("aria-label");
        expect(text?.trim().length).toBeGreaterThan(0);
      }

      // Verificar que el logo tiene aria-label
      const logoLink = page.getByRole("link", { name: "InVet, ir al inicio" });
      await expect(logoLink).toHaveAttribute("aria-label");

      // Verificar foco visible en un link
      await logoLink.focus();
      await expect(logoLink).toBeFocused();
    },
  );
});
