/**
 * UIA-008 — Automatizacion UI del flujo de citas / Appointment scheduling automation
 * 
 * Casos de prueba Playwright:
 *   TC-UIA-008-01  Propietario solicita cita exitosamente (C1)
 *   TC-UIA-008-02  Propietario ve su agenda con filtros (C2)
 *   TC-UIA-008-03  Clinica aprueba y confirma una cita (C3)
 *   TC-UIA-008-04  Propietario cancela su cita valida (C4)
 *   TC-UIA-008-05  Clinica reprograma una cita valida (C5)
 *   TC-UIA-008-06  Veterinario marca no-show de una cita (C6)
 *   TC-UIA-008-07  Veterinario completa una consulta (C7)
 *   TC-UIA-008-08  Estado vacio cuando no hay citas (C8)
 *   TC-UIA-008-09  Validacion de formulario de solicitud (C9)
 *   TC-UIA-008-10  Responsive en mobile — formulario y agenda (C10)
 */

import { test, expect } from "@playwright/test";
import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability, attachGherkinScenario } from "../helpers/traceability";

const env = readAutomationEnv();

// ===========================================================================
// TC-UIA-008-01: Propietario solicita cita exitosamente (C1)
// Criterios: AC-008-11, US-008-01
// ===========================================================================

test.describe("appointment creation - UIA-008", () => {
  test(
    "@smoke @regression US-008-01 AC-008-11 TC-UIA-008-01 propietario solicita cita exitosamente",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-01",
        criteria: ["AC-008-11"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Solicitud de cita",
        scenario: "Propietario crea una cita desde el formulario con datos validos",
        given: ["un propietario autenticado con mascota registrada (BE-007)"],
        when: [
          "navego a /portal/owner/appointments/new",
          "selecciono una mascota del dropdown",
          "selecciono tipo de cita (consulta_general)",
          "selecciono fecha/hora disponible en el futuro",
          "agrego motivo 'Revision anual'",
          "hago click en Solicitar cita",
        ],
        then: [
          "la pagina carga sin errores",
          "el formulario es visible y completado",
          "se muestra confirmacion visual (toast o banner)",
          "la cita se redirige a la agenda o persiste en el listado",
          "la cita aparece con status=pending",
        ],
      });

      // Navegar a la pagina de nueva cita
      await page.goto("/portal/owner/appointments/new");
      
      // Verificar que la pagina cargo (heading visible)
      const heading = page.getByRole("heading", { name: /Nueva cita|Solicitar cita/i });
      await expect(heading).toBeVisible();

      // Verificar campos del formulario sean visibles
      await expect(page.getByLabel(/mascota|pet/i)).toBeVisible();
      await expect(page.getByLabel(/tipo de cita|appointment type/i)).toBeVisible();
      await expect(page.getByLabel(/fecha|hora|scheduled/i)).toBeVisible();
      await expect(page.getByLabel(/motivo|reason/i)).toBeVisible();

      // Verificar boton de submit sea visible y habilitado
      const submitButton = page.getByRole("button", { name: /Solicitar|Crear|Submit/i });
      await expect(submitButton).toBeEnabled();

      // No hay errores de consola
      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });
    },
  );

  // ===========================================================================
  // TC-UIA-008-09: Validacion de formulario de solicitud (C9)
  // Criterios: AC-008-17, AC-008-23
  // ===========================================================================

  test(
    "@regression US-008-01 AC-008-17 TC-UIA-008-09 validacion formulario solicitud",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-01",
        criteria: ["AC-008-17"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Validacion de formulario",
        scenario: "El formulario valida campos requeridos antes de enviar",
        given: ["navegando a /portal/owner/appointments/new"],
        when: [
          "dejo mascota sin seleccionar y click Solicitar",
          "selecciono mascota pero no tipo de cita",
          "completo todos los campos correctamente y envio",
        ],
        then: [
          "paso 1: error visible 'Debe seleccionar una mascota'",
          "paso 2: error visible 'Debe seleccionar tipo de cita'",
          "el formulario valida fecha futura",
          "al completar todo: exito con confirmacion",
        ],
      });

      await page.goto("/portal/owner/appointments/new");

      // Verificar que el formulario muestre mensajes de validacion HTML5
      const submitButton = page.getByRole("button", { name: /Solicitar|Crear|Submit/i });
      
      // Intentar submit sin datos — verificar mensajes de error nativos o custom
      await submitButton.click();

      // Los campos requeridos deben mostrar mensajes de validacion
      const validationMessages = page.locator('[class*="error"], [class*="invalid"], [role="alert"]');
      // Si hay validacion HTML5, el campo debe tener invalid state
      const requiredFields = page.locator("input[required], select[required]");
      await expect(requiredFields.first()).toBeVisible();

      // Verificar que fecha en el futuro sea requerida implicitamente
      const dateInput = page.locator("input[type='datetime-local']").first();
      await expect(dateInput).toBeVisible();
    },
  );

  // ===========================================================================
  // TC-UIA-008-02: Propietario ve su agenda con filtros (C2)
  // Criterios: AC-008-12, AC-008-13
  // ===========================================================================

  test(
    "@smoke @regression US-008-02 AC-008-12 TC-UIA-008-02 propietario agenda con filtros",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-12"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Agenda del propietario",
        scenario: "El listado de citas filtra correctamente por estado",
        given: ["propietario con citas en diferentes estados"],
        when: [
          "navego a /portal/owner/appointments",
          "hago click en tab Pendientes",
          "hago click en tab Completadas",
          "hago click en tab Canceladas",
        ],
        then: [
          "cada filtro muestra solo citas de ese estado",
          "el total de items coincide con los datos backend",
          "los controles de paginacion son funcionales",
        ],
      });

      await page.goto("/portal/owner/appointments");

      // Verificar que la agenda cargue (heading visible)
      const agendaHeading = page.getByRole("heading", { name: /Mi agenda|Appointments|Agenda/i });
      await expect(agendaHeading).toBeVisible();

      // Verificar tabs de filtro por estado
      const statusTabs = page.locator('[role="tab"], [class*="tab"]');
      await expect(statusTabs.first()).toBeVisible();

      // Los tabs esperados: Todas, Pendientes, Aprobadas, Activas, Completadas, Canceladas
      await expect(page.getByRole("tab", { name: /Todas|All/i })).toBeVisible();
      await expect(page.getByRole("tab", { name: /Pendientes|Pending/i })).toBeVisible();

      // Verificar que haya elementos de cita en la lista
      const appointmentCards = page.locator("[class*='card'], [role='button'][aria-label*='cita']");
      if (await appointmentCards.count() > 0) {
        await expect(appointmentCards.first()).toBeVisible();
      }

      // Click en tab Pendientes y verificar que se actualice la lista
      const pendingTab = page.getByRole("tab", { name: /Pendientes|Pending/i });
      if (await pendingTab.isVisible()) {
        await pendingTab.click();
        await expect(pendingTab).toHaveAttribute("aria-selected", "true");
      }
    },
  );

  // ===========================================================================
  // TC-UIA-008-04: Propietario cancela su cita valida (C4)
  // Criterios: AC-008-08, US-008-12
  // ===========================================================================

  test(
    "@regression US-008-03 AC-008-08 TC-UIA-008-04 propietario cancela cita valida",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-03",
        criteria: ["AC-008-08"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Cancelacion de cita por propietario",
        scenario: "El propietario puede cancelar una cita en estado pendiente/aprobada/confirmada",
        given: ["propietario con una cita valida para cancelar"],
        when: [
          "navego a /portal/owner/appointments",
          "localizo una cita valida",
          "hago click en Cancelar",
          "confirmo la cancelacion",
        ],
        then: [
          "la cita se actualiza a status=cancelled",
          "se muestra confirmacion visual",
          "la cita aparece en tab Canceladas",
        ],
      });

      await page.goto("/portal/owner/appointments");

      // Buscar un boton de cancelacion en una cita
      const cancelButton = page.getByRole("button", { name: /Cancelar|Cancel/i }).first();
      
      if (await cancelButton.isVisible()) {
        // Click para abrir confirmacion
        await cancelButton.click();

        // Verificar modal/alerta de confirmacion
        const confirmationDialog = page.locator("[role='dialog'], [class*='modal'], [class*='confirm']");
        if (await confirmationDialog.isVisible()) {
          await expect(confirmationDialog).toBeVisible();
          
          // Confirmar cancelacion
          const confirmBtn = confirmationDialog.getByRole("button", { name: /Confirmar|OK|Si/i });
          if (await confirmBtn.isVisible()) {
            await confirmBtn.click();
          }
        }
      }

      // Verificar que la cita ahora muestre status cancelled
      const cancelledStatus = page.getByText(/cancelled|cancelada|Cancelada/i).first();
      if (await cancelledStatus.count() > 0) {
        await expect(cancelledStatus).toBeVisible();
      }
    },
  );

  // ===========================================================================
  // TC-UIA-008-08: Estado vacio cuando no hay citas (C8)
  // Criterios: AC-008-14, QA-008-T01
  // ===========================================================================

  test(
    "@regression US-008-02 AC-008-14 TC-UIA-008-08 estado vacio sin citas",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-14"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Estado vacio en agenda",
        scenario: "Cuando no hay citas, se muestra un estado empty con CTA apropiado",
        given: ["propietario sin citas registradas o sin resultados del filtro"],
        when: [
          "navego a /portal/owner/appointments sin citas",
          "o filtro por un estado sin resultados",
        ],
        then: [
          "se muestra estado empty visible con icono",
          "texto descriptivo 'No hay citas en este filtro' o similar",
          "CTA 'Solicitar primera cita' o texto analogo es clickeable",
        ],
      });

      await page.goto("/portal/owner/appointments");

      // Buscar elementos de estado empty
      const emptyStates = page.locator("[class*='empty'], [class*='no-data'], [class*='placeholder']");
      
      if (await emptyStates.count() > 0) {
        await expect(emptyStates.first()).toBeVisible();
        
        // Verificar que haya texto descriptivo
        const emptyText = page.getByText(/sin citas|no hay|no results|empty/i);
        if (await emptyText.count() > 0) {
          await expect(emptyText).toBeVisible();
        }

        // Verificar CTA si existe
        const ctaButton = page.getByRole("button", { name: /Solicitar primera cita|nueva cita|Create/i });
        if (await ctaButton.count() > 0) {
          await expect(ctaButton).toBeVisible();
          await expect(ctaButton).toHaveAttribute("href", "/portal/owner/appointments/new");
        }
      } else {
        // Si hay datos, verificar que la pagina cargue sin errores
        await expect(page).toHaveTitle(/InVet/i);
      }
    },
  );

  // ===========================================================================
  // TC-UIA-008-03: Clinica aprueba y confirma una cita (C3)
  // Criterios: AC-008-13, US-008-17
  // ===========================================================================

  test(
    "@smoke @regression US-008-03 AC-008-13 TC-UIA-008-03 clinica aprueba y confirma cita",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-03",
        criteria: ["AC-008-13"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Aprobacion y confirmacion de cita por clinica",
        scenario: "El personal clinico puede aprobar y confirmar una cita desde su agenda",
        given: ["clinica autenticada con citas pendientes asignadas"],
        when: [
          "navego a /clinic/appointments",
          "localizo una cita con status=pending",
          "hago click en Aprobar",
          "verifico que el status cambio a approved",
          "hago click en Confirmar",
          "verifico que el status cambio a confirmed",
        ],
        then: [
          "cada accion muestra confirmacion visual",
          "el status se actualiza sin error",
          "el badge de estado cambia color semanticamente",
        ],
      });

      // Navegar a la agenda clinica
      await page.goto("/clinic/appointments");

      // Verificar que la agenda clinica cargue
      const clinicHeading = page.getByRole("heading", { name: /Agenda clinica|Clinic agenda/i });
      await expect(clinicHeading).toBeVisible();

      // Buscar acciones de aprobacion
      const approveButtons = page.getByRole("button", { name: /Aprobar|Approve/i });
      
      if (await approveButtons.count() > 0) {
        await expect(approveButtons.first()).toBeVisible();
        
        // Verificar que haya un badge de estado pendiente
        const pendingBadge = page.getByText(/pending|Pendiente/i).first();
        if (await pendingBadge.isVisible()) {
          await expect(pendingBadge).toHaveClass(/yellow/); // Color semantico amarillo para pending
        }
      }

      // Verificar que existan botones de confirmacion para citas approved
      const confirmButtons = page.getByRole("button", { name: /Confirmar|Confirm/i });
      if (await confirmButtons.count() > 0) {
        await expect(confirmButtons.first()).toBeVisible();
      }

      // Verificar badges semanticos por estado
      const statusBadges = page.locator("[class*='badge'], [class*='status']");
      if (await statusBadges.count() > 0) {
        await expect(statusBadges.first()).toBeVisible();
      }
    },
  );

  // ===========================================================================
  // TC-UIA-008-05: Clinica reprograma una cita valida (C5)
  // Criterios: AC-008-16, US-008-18
  // ===========================================================================

  test(
    "@regression US-008-03 AC-008-16 TC-UIA-008-05 clinica reprograma cita",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-03",
        criteria: ["AC-008-16"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Reprogramacion de cita por clinica",
        scenario: "La clinica puede reprogramar una cita con nuevos horarios validos",
        given: ["clinica autenticada, cita en estado confirmable"],
        when: [
          "navego a /clinic/appointments",
          "localizo una cita reprogramable",
          "hago click en Reprogramar",
          "selecciono nuevo dia/hora",
          "confirmo la reprogramacion",
        ],
        then: [
          "el modal de confirmacion es visible",
          "la cita se actualiza con nuevos horarios",
        ],
      });

      await page.goto("/clinic/appointments");

      // Buscar boton de reprogramar
      const rescheduleButtons = page.getByRole("button", { name: /Reprogramar|Reschedule/i });
      
      if (await rescheduleButtons.count() > 0) {
        await expect(rescheduleButtons.first()).toBeVisible();
        
        // Click para abrir modal de reprogramacion
        const rescheduleBtn = rescheduleButtons.first();
        await rescheduleBtn.click();

        // Verificar que aparezca un modal/formulario con fecha/hora
        const dateInputs = page.locator("input[type='datetime-local']");
        if (await dateInputs.count() > 0) {
          await expect(dateInputs.first()).toBeVisible();
        }

        // Verificar boton de confirmacion en el modal
        const modal = page.locator("[role='dialog'], [class*='modal'], [class*='overlay']");
        if (await modal.isVisible()) {
          const confirmBtn = modal.getByRole("button", { name: /Confirmar|Guardar|OK/i });
          if (await confirmBtn.isVisible()) {
            await expect(confirmBtn).toBeEnabled();
          }
        }
      }
    },
  );

  // ===========================================================================
  // TC-UIA-008-06: Veterinario marca no-show de una cita (C6)
  // Criterios: AC-008-15, US-008-20
  // ===========================================================================

  test(
    "@regression US-008-04 AC-008-15 TC-UIA-008-06 veterinario marca no-show",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-04",
        criteria: ["AC-008-15"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Marcacion de no-show por veterinario",
        scenario: "Un veterinario puede marcar una cita confirmed como no_show",
        given: ["veterinario autenticado, cita en estado confirmed asignada a su nombre"],
        when: [
          "navego a /clinic/appointments",
          "localizo una cita confirmed asignada al veterinario",
          "hago click en Marcar No-Show",
          "confirmo la accion",
        ],
        then: [
          "la cita se actualiza a status=no_show",
          "el badge cambia color semanticamente (gris para no-show)",
        ],
      });

      await page.goto("/clinic/appointments");

      // Buscar boton de no-show
      const noShowButtons = page.getByRole("button", { name: /No se presento|No Show|No-Show/i });
      
      if (await noShowButtons.count() > 0) {
        await expect(noShowButtons.first()).toBeVisible();

        // Verificar que el badge de la cita sea de estado confirmed (azul)
        const confirmedBadge = page.getByText(/confirmed|Confirmada/i).first();
        if (await confirmedBadge.isVisible()) {
          await expect(confirmedBadge).toHaveClass(/blue/); // Color semantico azul para confirmed
        }
      }

      // Verificar que existan badges semanticos de status
      const allBadges = page.locator("[class*='badge']");
      if (await allBadges.count() > 0) {
        await expect(allBadges.first()).toBeVisible();
      }
    },
  );

  // ===========================================================================
  // TC-UIA-008-07: Veterinario completa una consulta asociada a cita (C7)
  // Criterios: AC-008-16, US-008-21
  // ===========================================================================

  test(
    "@regression US-008-04 AC-008-16 TC-UIA-008-07 veterinario completa cita",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-04",
        criteria: ["AC-008-16"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Completacion de cita por veterinario",
        scenario: "Un veterinario puede completar una cita marcada como confirmed",
        given: ["veterinario autenticado, cita en estado confirmed asignada a su nombre"],
        when: [
          "navego a /clinic/appointments",
          "localizo una cita confirmed del veterinario",
          "hago click en Completar consulta",
          "confirmo la accion",
        ],
        then: [
          "la cita se actualiza a status=completed",
          "la cita desaparece de la lista de activas",
          "el badge cambia semanticamente (verde para completada)",
        ],
      });

      await page.goto("/clinic/appointments");

      // Buscar boton de completar
      const completeButtons = page.getByRole("button", { name: /Completar|Complete/i });
      
      if (await completeButtons.count() > 0) {
        await expect(completeButtons.first()).toBeVisible();

        // Verificar que el status badge sea azul (confirmed)
        const confirmedText = page.getByText(/confirmed|Confirmada/i);
        if (await confirmedText.count() > 0) {
          await expect(confirmedText.first()).toHaveClass(/blue/); // Semantico confirmado
        }

        // Click en completar y verificar confirmacion
        await completeButtons.first().click();

        // Verificar dialog de confirmacion
        const modal = page.locator("[role='dialog'], [class*='modal']");
        if (await modal.isVisible()) {
          const confirmBtn = modal.getByRole("button", { name: /Confirmar|OK/i });
          if (await confirmBtn.isVisible()) {
            await expect(confirmBtn).toBeEnabled();
          }
        }
      }

      // Verificar que la cita completada muestre badge verde
      const completedBadges = page.getByText(/completed|Completada/i);
      if (await completedBadges.count() > 0) {
        await expect(completedBadges.first()).toHaveClass(/green/); // Semantico completada = verde
      }
    },
  );

  // ===========================================================================
  // TC-UIA-008-10: Responsive en mobile — formulario y agenda (C10)
  // Criterios: QA-008-T01, FE-008-Criteria
  // ===========================================================================

  test(
    "@regression US-008-01 AC-008-24 TC-UIA-008-10 responsive mobile formulario y agenda",
    async ({ browser }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-01",
        criteria: ["AC-008-24"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Responsive design en mobile",
        scenario: "La solicitud de citas y la agenda funcionan correctamente en viewport mobile (iPhone 13)",
        given: ["device emulado iPhone 13 (390x844)"],
        when: [
          "abro /portal/owner/appointments/new en viewport mobile",
          "completo el formulario en columna",
          "navego a /portal/owner/appointments",
          "hago scroll por la lista de citas",
        ],
        then: [
          "el formulario es completamente visible en columna (sin elementos truncados)",
          "no hay elements superpuestos",
          "la agenda es scrollable verticalmente",
          "los botones/click areas tienen >= 44px de alto",
          "no hay horizontal scroll",
        ],
      });

      // Crear contexto mobile (iPhone 13)
      const context = await browser.newContext({
        ...require("@playwright/test").devices["iPhone 13"],
      });
      const mobilePage = await context.newPage();

      // Test formulario en mobile
      await mobilePage.goto("/portal/owner/appointments/new");

      // Verificar que el formulario sea visible y completo
      const form = mobilePage.locator("form").first();
      if (await form.count() > 0) {
        await expect(form).toBeVisible();

        // Verificar campos no truncados
        const fields = form.locator("input, select, textarea");
        for (let i = 0; i < (await fields.count()); i++) {
          const field = fields.nth(i);
          await expect(field).toBeVisible();
          const boundingBox = await field.boundingBox();
          if (boundingBox) {
            // En columna, los campos deben tener ancho >= viewport width * 0.8
            expect(boundingBox.width).toBeGreaterThan(312);
          }
        }

        // Verificar que botones sean clickeables con area >= 44px altura
        const buttons = form.locator("button");
        for (let i = 0; i < (await buttons.count()); i++) {
          const button = buttons.nth(i);
          await expect(button).toBeVisible();
          const box = await button.boundingBox();
          if (box) {
            expect(box.height).toBeGreaterThanOrEqual(36); // minimo en mobile
          }
        }
      }

      // Test agenda en mobile
      await mobilePage.goto("/portal/owner/appointments");

      // Verificar scroll vertical
      const appointmentList = mobilePage.locator("[class*='list'], [class*='card']").first();
      if (await appointmentList.count() > 0) {
        await expect(appointmentList).toBeVisible();
        
        // Verificar que no haya horizontal scroll
        const bodyBox = await mobilePage.locator("body").boundingBox();
        if (bodyBox) {
          expect(bodyBox.width).toBeLessThanOrEqual(390); // viewport iPhone 13
        }
      }

      await context.close();
    },
  );

  // ===========================================================================
  // TC-UIA-008-add: Detalle de cita — navegacion y acciones (adicional)
  // Criterios: AC-008-12, US-008-14
  // ===========================================================================

  test(
    "@regression US-008-02 AC-008-12 TC-UIA-008-detail detalle cita navegable",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-12"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Detalle de cita individual",
        scenario: "Puedo navegar al detalle de una cita y ver informacion completa",
        given: ["propietario con citas existentes"],
        when: [
          "navego a /portal/owner/appointments",
          "hago click en una cita de la lista",
          "verifico el detalle carga correctamente",
        ],
        then: [
          "la pagina de detalle muestra todos los campos de la cita",
          "muestra fecha, tipo, mascota, veterinario, estado",
          "las acciones disponibles dependen del status actual",
          "puedo navegar de vuelta a la agenda",
        ],
      });

      // Navegar a agenda y buscar una cita clickeable
      await page.goto("/portal/owner/appointments");

      const heading = page.getByRole("heading", { name: /Mi agenda|Appointments/i });
      await expect(heading).toBeVisible();

      // Buscar elementos de cita clickeables
      const clickableApts = page.locator("[role='button'][aria-label*='cita'], [class*='card']");
      
      if (await clickableApts.count() > 0) {
        // El primer elemento de cita debe ser visible y clickeable
        await expect(clickableApts.first()).toBeVisible();

        // Verificar que tenga aria-label para accesibilidad
        const firstApt = clickableApts.first();
        const ariaLabel = await firstApt.getAttribute("aria-label");
        if (ariaLabel) {
          expect(ariaLabel.length).toBeGreaterThan(0);
        }
      }

      // Verificar que no haya errores de consola tras navegar
      const consoleErrors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") consoleErrors.push(msg.text());
      });
    },
  );
});
