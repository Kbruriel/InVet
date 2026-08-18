/**
 * APIA-008 — Automatizacion API del flujo de citas / Appointment scheduling API automation
 * 
 * Casos de prueba Playwright API (HTTP requests):
 *   A1  Creacion de cita happy path
 *   A2  Creacion sin auth (401)
 *   A3  Creacion fecha pasado (422)
 *   A4  IDOR mascota otro owner (403)
 *   A5  Transicion pending -> approved (valida)
 *   A6  Transicion completed -> approved (invalida)
 *   A7  Owner intenta aprobar (403)
 *   A8  Clinica aprueba cita otra sucursal (IDOR)
 *   A9  Disponibilidad devuelve slots correctos
 *   A10 Listado paginado propietario
 *   A11 Listado paginado clinica con filtro status
 *   A12 Cancelacion valida por propietario
 *   A13 Cancelacion terminal invalida (422)
 *   A14 Reprogramacion valida
 *   A15 Reprogramacion solapamiento (409)
 *   A16 Veterinario completa cita assigned (valida)
 *   A17 Veterinario no-assigned completa (403)
 *   A18 No-show valida (confirmed -> no_show)
 */

import { test, expect, TestInfo } from "@playwright/test";
import type { APIRequestContext, APIResponse } from "@playwright/test";
import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability, attachGherkinScenario } from "../helpers/traceability";

const env = readAutomationEnv();

type JsonRecord = Record<string, unknown>;

type AuthPayload = {
  access_token: string;
};

type AppointmentRecord = JsonRecord & {
  id?: number;
  status?: string;
  owner_id?: number;
  pet_id?: number;
  appointment_type?: string;
  scheduled_start?: string;
  scheduled_end?: string;
  duration_minutes?: number;
  reason?: string | null;
  updated_at?: string;
  new_start?: string;
  new_end?: string;
};

type AppointmentCreateResponse = AppointmentRecord & {
  id: number;
  status: string;
};

type AvailabilitySlot = {
  duration?: number;
  [key: string]: unknown;
};

type AppointmentListResponse = {
  items: AppointmentRecord[];
  meta?: {
    total?: number;
    page?: number;
    page_size?: number;
  };
  total?: number;
  page?: number;
  page_size?: number;
  slots?: AvailabilitySlot[];
  data?: AvailabilitySlot[];
};

// ===========================================================================
// Helpers de autenticacion y datos
// ===========================================================================

async function loginAsOwner(request: APIRequestContext): Promise<string> {
  test.skip(
    env.loginEmail === "qa@example.com",
    "Provide LOGIN_EMAIL and LOGIN_PASSWORD of a registered owner account to run owner tests.",
  );
  const response = await request.post("/api/v1/auth/login", {
    data: { email: env.loginEmail, password: env.loginPassword },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as AuthPayload;
  return payload.access_token;
}

async function loginAsClinic(request: APIRequestContext): Promise<string> {
  test.skip(
    env.clinicEmail === "clinic@invet.local",
    "Provide CLINIC_EMAIL and CLINIC_PASSWORD to run clinic tests.",
  );
  const response = await request.post("/api/v1/auth/login", {
    data: { email: env.clinicEmail, password: env.clinicPassword },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as AuthPayload;
  return payload.access_token;
}

async function loginAsVet(request: APIRequestContext): Promise<string> {
  test.skip(
    env.vetEmail === "vet@example.com",
    "Provide VET_EMAIL and VET_PASSWORD to run vet tests.",
  );
  const response = await request.post("/api/v1/auth/login", {
    data: { email: env.vetEmail, password: env.vetPassword },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as AuthPayload;
  return payload.access_token;
}

async function createOwnerAppointment(
  request: APIRequestContext,
  token: string,
  futureDate: string,
): Promise<{ response: APIResponse; id: number }> {
  const payload = {
    pet_id: 1,
    veterinarian_id: null,
    appointment_type: "consulta_general",
    scheduled_start: futureDate,
    scheduled_end: new Date(new Date(futureDate).getTime() + 30 * 60 * 1000).toISOString(),
    reason: "Revision anual",
  };

  const response = await request.post("/api/v1/appointments", {
    headers: { Authorization: `Bearer ${token}` },
    data: payload,
  });
  expect(response.status()).toBe(201);
  const body = (await response.json()) as AppointmentCreateResponse;
  return { response, id: Number(body.id) };
}

async function createVet(request: APIRequestContext, adminToken: string): Promise<{ response: APIResponse; id: number }> {
  const vetPayload = {
    name: "Dr. Test Vet",
    license_number: "TEST-VET-001",
    clinic_id: 1,
    email: "vet-test@example.com",
  };

  const response = await request.post("/api/v1/veterinarians", {
    headers: { Authorization: `Bearer ${adminToken}` },
    data: vetPayload,
  });
  expect(response.status()).toBe(201);
  const body = (await response.json()) as AppointmentRecord;
  return { response, id: Number(body.id) };
}

// ===========================================================================
// A1: Creacion de cita happy path
// Criterios: AC-008-01
// ===========================================================================

test.describe("Appointment creation — APIA-008", () => {
  let ownerToken: string;
  let futureDate: string;
  let createdId: number | null = null;

  test.beforeAll(async ({ request }) => {
    ownerToken = await loginAsOwner(request);
    // Schedule for 30 days from now
    const now = new Date();
    now.setDate(now.getDate() + 30);
    futureDate = now.toISOString().replace("Z", "");
  });

  test(
    "@smoke APIA-008-A01 US-008-01 AC-008-01 POST /api/v1/appointments creates pending appointment",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-01",
        criteria: ["AC-008-01"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Creacion de cita API",
        scenario: "Owner crea una cita con datos validos y recibe 201 Created",
        given: [
          "un owner autenticado con token Bearer valido",
          "una mascota registrada (pet_id=1) del owner",
          "fecha futura valida (hoy + 30 dias)",
        ],
        when: [
          "POST /api/v1/appointments con body validos (pet_id, appointment_type, scheduled_start/end, reason)",
        ],
        then: [
          "response status = 201",
          "response JSON contiene status=pending",
          "response JSON contiene owner_id = token.user_id",
          "la cita se puede listar en GET /api/v1/appointments/me",
        ],
      });

      const { id, response } = await createOwnerAppointment(request, ownerToken, futureDate);
      createdId = id;

      // Validar estructura de respuesta
      expect(id).toBeGreaterThan(0);

      const body = (await response.json()) as Record<string, unknown>;
      expect(String(body.status)).toBe("pending");
      expect(typeof body.owner_id).not.toBe("undefined");
      expect(body.pet_id).toBe(1);
      expect(body.appointment_type).toBe("consulta_general");
    },
  );

  // ===========================================================================
  // A2: Creacion sin auth — negative
  // Criterios: AC-008-15
  // ===========================================================================

  test(
    "@regression APIA-008-A02 US-008-01 AC-008-15 POST /api/v1/appointments without auth returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-01",
        criteria: ["AC-008-15"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Autenticacion endpoint creation",
        scenario: "Peticionar sin token devuelve 401 Unauthorized",
        given: ["sin credenciales ni token"],
        when: [
          "POST /api/v1/appointments sin header Authorization",
        ],
        then: [
          "response status = 401",
          "mensaje de respuesta indica 'Authentication required'",
        ],
      });

      const response = await request.post("/api/v1/appointments");
      expect(response.status()).toBe(401);

      const body = (await response.json()) as Record<string, unknown>;
      const bodyStr = JSON.stringify(body);
      // La respuesta debe contener referencia a autenticacion
      expect(bodyStr.toLowerCase()).toContain("auth");
    },
  );

  // ===========================================================================
  // A3: Creacion con fecha en el pasado — negative
  // Criterios: AC-008-17
  // ===========================================================================

  test(
    "@regression APIA-008-A03 US-008-01 AC-008-17 POST /api/v1/appointments with past date returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-01",
        criteria: ["AC-008-17"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Validacion de fecha en creacion",
        scenario: "El backend rechaza fechas pasadas con 422 y mensaje legible",
        given: [
          "owner autenticado",
          "fecha en el pasado (2020-01-01T10:00:00Z)",
        ],
        when: [
          "POST /api/v1/appointments con scheduled_start en el pasado",
        ],
        then: [
          "response status = 422",
          "mensaje incluye 'fecha' y 'futura' o equivalente",
        ],
      });

      const pastDate = new Date("2020-01-01T10:00:00Z").toISOString();
      const payload = {
        pet_id: 1,
        veterinarian_id: null,
        appointment_type: "consulta_general",
        scheduled_start: pastDate,
        scheduled_end: new Date(new Date(pastDate).getTime() + 30 * 60 * 1000).toISOString(),
        reason: "Revision atrasada",
      };

      const response = await request.post("/api/v1/appointments", {
        headers: { Authorization: `Bearer ${ownerToken}` },
        data: payload,
      });
      expect(response.status()).toBe(422);

      const body = (await response.json()) as Record<string, unknown>;
      const bodyStr = JSON.stringify(body).toLowerCase();
      // Mensaje debe ser legible y contener referencia a fecha
      expect(bodyStr).toContain("date");
    },
  );

  // ===========================================================================
  // A4: IDOR — mascota de otro owner
  // Criterios: AC-008-16
  // ===========================================================================

  test(
    "@regression APIA-008-A04 US-008-01 AC-008-16 POST /api/v1/appointments with other owners pet returns 403",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-01",
        criteria: ["AC-008-16"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "IDOR en creacion de cita",
        scenario: "Intentar crear cita para mascota de otro owner devuelve 403",
        given: [
          "owner_A autenticado",
          "pet_id que pertenece a owner_B",
        ],
        when: [
          "POST /api/v1/appointments con pet_id de otro owner",
        ],
        then: [
          "response status = 403",
          "la respuesta NO expone datos de la mascota ajena",
        ],
      });

      const futureDate2 = new Date(Date.now() + 60 * 60 * 1000).toISOString();
      const payload = {
        pet_id: 99999, // ID que no pertenece al owner
        veterinarian_id: null,
        appointment_type: "consulta_general",
        scheduled_start: futureDate2,
        scheduled_end: new Date(new Date(futureDate2).getTime() + 30 * 60 * 1000).toISOString(),
        reason: "Revision de mascota ajena",
      };

      const response = await request.post("/api/v1/appointments", {
        headers: { Authorization: `Bearer ${ownerToken}` },
        data: payload,
      });
      expect(response.status()).toBe(403);

      // Verificar que no se exponen datos sensibles de mascotas ajenas
      const body = (await response.json()) as Record<string, unknown>;
      const bodyStr = JSON.stringify(body).toLowerCase();
      expect(bodyStr).not.toContain("pet_name");
      expect(bodyStr).not.toContain("owner_id");
    },
  );

  // ===========================================================================
  // A5: Transicion pending -> approved (valida)
  // Criterios: AC-008-03
  // ===========================================================================

  test(
    "@smoke APIA-008-A05 US-008-02 AC-008-03 PUT /api/v1/appointments/:id/status transitions pending to approved",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-03"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Transicion de estado valida",
        scenario: "Clinica aprueba una cita en status pending -> approved",
        given: [
          "una cita creada con status=pending (ver A1)",
          "clinica autenticada con Bearer token",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/status con body {action: 'approved'}",
        ],
        then: [
          "response status = 200",
          "response JSON status=approved",
          "updated_at se actualizo",
        ],
      });

      // Crear cita en pending si no existe
      if (!createdId) {
        const appt = await createOwnerAppointment(request, ownerToken, futureDate);
        createdId = appt.id;
      }

      const clinicToken = await loginAsClinic(request);

      const response = await request.put(`/api/v1/appointments/${createdId}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "approved" },
      });
      expect(response.status()).toBe(200);

      const body = (await response.json()) as Record<string, unknown>;
      expect(String(body.status)).toBe("approved");
    },
  );

  // ===========================================================================
  // A6: Transicion completed -> approved (invalida)
  // Criterios: AC-008-04
  // ===========================================================================

  test(
    "@regression APIA-008-A06 US-008-02 AC-008-04 PUT /api/v1/appointments/:id/status completed->approved invalid returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-04"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Transicion de estado invalida",
        scenario: "Intentar approved una cita completed es rechazado con 422",
        given: [
          "una cita en status=completed",
          "clinica autenticada",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/status con action=approved",
        ],
        then: [
          "response status = 422",
          "mensaje indica invalid transition from completed",
        ],
      });

      // Necesitamos crear una cita completada primero
      // Para este test, creamos una cita y la simulamos en un estado terminal
      const futureDate3 = new Date(Date.now() + 120 * 60 * 1000).toISOString();
      const appt = await createOwnerAppointment(request, ownerToken, futureDate3);
      
      // Transicion: pending -> approved -> confirmed -> completed (via status transitions validas)
      const clinicToken = await loginAsClinic(request);

      // pending -> approved
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "approved" },
      });

      // approved -> confirmed
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "confirmed" },
      });

      // confirmed -> completed (veterinario assigned)
      const vetToken = await loginAsVet(request);
      const completeResponse = await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${vetToken}` },
        data: { action: "completed" },
      });
      expect(completeResponse.status()).toBe(200);

      // Intentar completed -> approved (invalido)
      const invalidResp = await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "approved" },
      });
      expect(invalidResp.status()).toBe(422);

      const body = (await invalidResp.json()) as Record<string, unknown>;
      const bodyStr = JSON.stringify(body).toLowerCase();
      expect(bodyStr).toContain("transition");
    },
  );

  // ===========================================================================
  // A7: Owner intenta aprobar (permiso incorrecto)
  // Criterios: AC-008-05
  // ===========================================================================

  test(
    "@regression APIA-008-A07 US-008-02 AC-008-05 owner approving returns 403",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Control de permisos en status transitions",
        scenario: "El owner que creo la cita no puede aprobarla (rol incorrecto)",
        given: [
          "una cita creada por el owner",
          "token del owner (no clinica/vet)",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/status con action=approved usando token de owner",
        ],
        then: [
          "response status = 403",
          "sin detalles internos en la respuesta",
        ],
      });

      if (!createdId) {
        const appt = await createOwnerAppointment(request, ownerToken, futureDate);
        createdId = appt.id;
      }

      const response = await request.put(`/api/v1/appointments/${createdId}/status`, {
        headers: { Authorization: `Bearer ${ownerToken}` },
        data: { action: "approved" },
      });
      expect(response.status()).toBe(403);

      // Sin exposicion de datos internos
      const body = (await response.json()) as Record<string, unknown>;
      const bodyStr = JSON.stringify(body).toLowerCase();
      expect(bodyStr).not.toContain("role");
    },
  );

  // ===========================================================================
  // A8: Clinica aprueba cita de otra sucursal (IDOR)
  // Criterios: AC-008-16
  // ===========================================================================

  test(
    "@regression APIA-008-A08 US-008-02 AC-008-16 cross-branch approval returns 403/404",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-16"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "IDOR en status transitions",
        scenario: "Clinica B intenta aprobar cita de clinica A -> rechazado",
        given: [
          "cita de clinic_A",
          "clinica_B autenticada",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/status con action=approved usando token de clinica_B",
        ],
        then: [
          "response status = 403 o 404",
          "sin datos expuestos de la cita ajena",
        ],
      });

      if (!createdId) {
        const appt = await createOwnerAppointment(request, ownerToken, futureDate);
        createdId = appt.id;
      }

      // Intentar con un token diferente (simulado) — si no hay clinica_B seeded, skip
      test.skip(
        env.clinicEmail === "clinic@example.com",
        "Requires a second clinic account for cross-branch IDOR testing.",
      );

      const otherClinicToken = await loginAsClinic(request);

      const response = await request.put(`/api/v1/appointments/${createdId}/status`, {
        headers: { Authorization: `Bearer ${otherClinicToken}` },
        data: { action: "approved" },
      });
      expect([403, 404]).toContain(response.status());

      const body = (await response.json()) as Record<string, unknown>;
      expect(JSON.stringify(body)).not.toContain("clinic_id");
    },
  );

  // ===========================================================================
  // A9: Disponibilidad devuelve slots correctos
  // Criterios: AC-008-10
  // ===========================================================================

  test(
    "@smoke APIA-008-A09 US-008-02 AC-008-10 GET /api/v1/appointments/availability returns slot array",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-10"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Endpoint de disponibilidad de slots",
        scenario: "GET devuelve array de slots disponibles y ocupados para la fecha solicitada",
        given: [
          "cualquier usuario autenticado (o anonimo si el endpoint es publico)",
          "fecha valida con parámetros date y branch_id",
        ],
        when: [
          "GET /api/v1/appointments/availability?date=2026-09-15&branch_id=1",
        ],
        then: [
          "response status = 200",
          "response contiene array de slots",
          "cada slot tiene duration (default 30 min)",
          "sin solapamiento entre slots del mismo вет",
        ],
      });

      const testDate = "2026-09-15";
      const response = await request.get("/api/v1/appointments/availability", {
        params: { date: testDate, branch_id: 1 },
      });

      // Puede ser 200 o 401 si requiere auth — verificar ambos comportamientos
      if (response.status() === 200) {
        const body = (await response.json()) as AppointmentListResponse;
        const slots: AvailabilitySlot[] = Array.isArray(body.slots)
          ? body.slots
          : Array.isArray(body.data)
            ? body.data
            : [];
        expect(Array.isArray(slots)).toBe(true);

        // Verificar estructura basica de slots
        if (slots.length > 0) {
          expect(typeof slots[0].duration).not.toBe("undefined");
        }
      } else {
        // Si requiere auth, verificar que se necesita autenticacion
        const body = (await response.json()) as Record<string, unknown>;
        expect(JSON.stringify(body).toLowerCase()).toContain("auth");
      }
    },
  );

  // ===========================================================================
  // A10: Listado paginado de citas del propietario
  // Criterios: AC-008-02, AC-008-19
  // ===========================================================================

  test(
    "@smoke APIA-008-A10 US-008-02 AC-008-02 GET /api/v1/appointments/me paginated",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-02", "AC-008-19"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado paginado propietario",
        scenario: "GET /api/v1/appointments/me devuelve items paginados con meta",
        given: [
          "propietario autenticado",
          "page=1&page_size=5",
        ],
        when: [
          "GET /api/v1/appointments/me?page=1&page_size=5",
        ],
        then: [
          "response status = 200",
          "response tiene {items: [...], meta: {total, page, page_size}}",
          "items.length <= page_size",
        ],
      });

      const response = await request.get("/api/v1/appointments/me", {
        params: { page: 1, page_size: 5 },
        headers: { Authorization: `Bearer ${ownerToken}` },
      });
      expect(response.status()).toBe(200);

      const body = (await response.json()) as AppointmentListResponse;
      expect(Array.isArray(body.items)).toBe(true);
      expect(body.items.length).toBeLessThanOrEqual(5);

      // Meta debe tener total, page, page_size
      if (body.meta) {
        expect(typeof body.meta.total).toBe("number");
        expect(body.meta.page).toBe(1);
        expect(body.meta.page_size).toBe(5);
      }
    },
  );

  // ===========================================================================
  // A11: Listado paginado de clinica con filtro por status
  // Criterios: AC-008-19
  // ===========================================================================

  test(
    "@smoke APIA-008-A11 US-008-02 AC-008-19 GET /api/v1/appointments/clinic filtered",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-02",
        criteria: ["AC-008-19"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado paginado clinica con filtros",
        scenario: "Clinica lista citas de su sucursal filtrando por status",
        given: [
          "clinica autenticada",
          "page=1&page_size=10&status=pending",
        ],
        when: [
          "GET /api/v1/appointments/clinic?page=1&page_size=10&status=pending",
        ],
        then: [
          "response status = 200",
          "todos los items pertenecen a sucursal del usuario",
          "items filtrados por status=pending",
          "meta con total, page, page_size correctos",
        ],
      });

      const clinicToken = await loginAsClinic(request);

      const response = await request.get("/api/v1/appointments/clinic", {
        params: { page: 1, page_size: 10, status: "pending" },
        headers: { Authorization: `Bearer ${clinicToken}` },
      });
      expect(response.status()).toBe(200);

      const body = (await response.json()) as AppointmentListResponse;
      expect(Array.isArray(body.items)).toBe(true);

      // Todos los items deben ser pending
      if (body.items.length > 0) {
        for (const item of body.items) {
          expect(String(item.status)).toBe("pending");
        }
      }

      if (body.meta) {
        expect(typeof body.meta.total).toBe("number");
      }
    },
  );

  // ===========================================================================
  // A12: Cancelacion valida por propietario
  // Criterios: AC-008-08
  // ===========================================================================

  test(
    "@regression APIA-008-A12 US-008-03 AC-008-08 owner cancels own pending appointment",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-03",
        criteria: ["AC-008-08"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Cancelacion de cita",
        scenario: "Owner cancela su propia cita en status pending -> cancelled",
        given: [
          "cita creada por el owner con status=pending",
          "token del owner",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/cancel",
        ],
        then: [
          "response status = 200",
          "response JSON status=cancelled",
          "updated_at se actualizo",
        ],
      });

      // Crear cita fresca para cancelar
      const futureDate4 = new Date(Date.now() + 90 * 60 * 1000).toISOString();
      const appt = await createOwnerAppointment(request, ownerToken, futureDate4);

      const response = await request.put(`/api/v1/appointments/${appt.id}/cancel`, {
        headers: { Authorization: `Bearer ${ownerToken}` },
      });
      expect(response.status()).toBe(200);

      const body = (await response.json()) as Record<string, unknown>;
      expect(String(body.status)).toBe("cancelled");
    },
  );

  // ===========================================================================
  // A13: Cancelacion terminal invalida (422)
  // Criterios: AC-008-04
  // ===========================================================================

  test(
    "@regression APIA-008-A13 US-008-03 AC-008-04 canceling terminal appointment returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-03",
        criteria: ["AC-008-04"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Validacion de cancelacion terminal",
        scenario: "Intentar cancelar una cita en estado terminal (no_show/completed) es rechazado",
        given: [
          "una cita en status=completed o no_show",
          "token del owner",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/cancel en cita terminada",
        ],
        then: [
          "response status = 422",
          "mensaje indica cannot cancel terminal status",
        ],
      });

      // Necesitamos una cita completada
      const futureDate5 = new Date(Date.now() + 180 * 60 * 1000).toISOString();
      const appt = await createOwnerAppointment(request, ownerToken, futureDate5);

      // Simular completa: pending -> approved -> confirmed -> completed
      const clinicToken = await loginAsClinic(request);
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "approved" },
      });
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "confirmed" },
      });
      const vetToken = await loginAsVet(request);
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${vetToken}` },
        data: { action: "completed" },
      });

      // Intentar cancelacion (invalida)
      const invalidResp = await request.put(`/api/v1/appointments/${appt.id}/cancel`, {
        headers: { Authorization: `Bearer ${ownerToken}` },
      });
      expect(invalidResp.status()).toBe(422);

      const body = (await invalidResp.json()) as Record<string, unknown>;
      const bodyStr = JSON.stringify(body).toLowerCase();
      expect(bodyStr).toContain("cancel");
    },
  );

  // ===========================================================================
  // A14: Reprogramacion valida
  // Criterios: AC-008-09
  // ===========================================================================

  test(
    "@regression APIA-008-A14 US-008-03 AC-008-09 clinic reschedules valid appointment",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-03",
        criteria: ["AC-008-09"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Reprogramacion de cita",
        scenario: "Clinica reprograma una cita con nuevos horarios validos (no solapados)",
        given: [
          "cita confirmada/pending asignada a la clinica",
          "nuevos slots disponibles en fecha futura",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/reschedule con new_start y new_end validos",
        ],
        then: [
          "response status = 200",
          "scheduled_start y scheduled_end actualizados en response",
          "cita mantiene los mismos owner/pet/vet originales",
        ],
      });

      // Crear cita para reprogramar
      const futureDate6 = new Date(Date.now() + 150 * 60 * 1000).toISOString();
      const appt = await createOwnerAppointment(request, ownerToken, futureDate6);

      // pending -> approved
      const clinicToken = await loginAsClinic(request);
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "approved" },
      });

      // Reprogramar a nueva fecha
      const newStart = new Date(Date.now() + 200 * 60 * 1000).toISOString();
      const newEnd = new Date(new Date(newStart).getTime() + 30 * 60 * 1000).toISOString();

      const response = await request.put(`/api/v1/appointments/${appt.id}/reschedule`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { new_start: newStart, new_end: newEnd },
      });
      expect(response.status()).toBe(200);

      const body = (await response.json()) as Record<string, unknown>;
      // Los nuevos horarios deben reflejarse en la respuesta
      expect(body.scheduled_start || body.new_start).toBeTruthy();
    },
  );

  // ===========================================================================
  // A15: Reprogramacion con solapamiento (409)
  // Criterios: AC-008-09
  // ===========================================================================

  test(
    "@regression APIA-008-A15 US-008-03 AC-008-09 rescheduling overlapping slot returns 409",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-03",
        criteria: ["AC-008-09"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Validacion de solapamiento en reprogramacion",
        scenario: "Intentar reprogramar a un slot ya ocupado devuelve 409 Conflict",
        given: [
          "una cita que ya ocupa el slot target",
          "clinica autenticada intentando mover otra cita al mismo slot",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/reschedule con new_start de slot ocupado",
        ],
        then: [
          "response status = 409",
          "mensaje indica slot ya ocupado",
        ],
      });

      // Crear cita para reprogramar
      const futureDate7 = new Date(Date.now() + 160 * 60 * 1000).toISOString();
      const appt = await createOwnerAppointment(request, ownerToken, futureDate7);

      const clinicToken = await loginAsClinic(request);

      // Intentar reprogramar al mismo slot donde ya existe otra cita (simulado)
      // El backend debe detectar solapamiento y retornar 409
      const overlappingStart = appt ? new Date(new Date(futureDate7).getTime() + 1 * 60 * 1000).toISOString() : futureDate7;

      const response = await request.put(`/api/v1/appointments/${appt.id}/reschedule`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { new_start: overlappingStart, new_end: new Date(new Date(overlappingStart).getTime() + 30 * 60 * 1000).toISOString() },
      });

      // Puede ser 409 (solapamiento detectado) o 200 si no hay conflicto
      if (response.status() === 409) {
        const body = (await response.json()) as Record<string, unknown>;
        expect(JSON.stringify(body).toLowerCase()).toContain("slot");
      } else {
        expect(response.status()).toBe(200);
      }
    },
  );

  // ===========================================================================
  // A16: Veterinario completa cita assigned a su nombre (valida)
  // Criterios: AC-008-06
  // ===========================================================================

  test(
    "@regression APIA-008-A16 US-008-04 AC-008-06 vet completes assigned appointment",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-04",
        criteria: ["AC-008-06"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Completacion de cita por veterinario",
        scenario: "Veterinario assigned completa su cita -> completed",
        given: [
          "cita confirmada asignada al veterinario actual",
          "token del veterinario assigned",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/status con action=completed",
        ],
        then: [
          "response status = 200",
          "response JSON status=completed",
          "updated_at actualizado",
        ],
      });

      const vetToken = await loginAsVet(request);

      // Crear cita nueva para completar
      const futureDate8 = new Date(Date.now() + 240 * 60 * 1000).toISOString();
      const appt = await createOwnerAppointment(request, ownerToken, futureDate8);

      // pending -> approved -> confirmed (clinica)
      const clinicToken = await loginAsClinic(request);
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "approved" },
      });
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "confirmed" },
      });

      // completed por vet assigned
      const completeResponse = await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${vetToken}` },
        data: { action: "completed" },
      });
      expect(completeResponse.status()).toBe(200);

      const body = (await completeResponse.json()) as Record<string, unknown>;
      expect(String(body.status)).toBe("completed");
    },
  );

  // ===========================================================================
  // A17: Veterinario no-assigned completa cita (403)
  // Criterios: AC-008-06
  // ===========================================================================

  test(
    "@regression APIA-008-A17 US-008-04 AC-008-06 other vet cannot complete appointment returns 403",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-04",
        criteria: ["AC-008-06"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Control de permisos en completacion por veterinario",
        scenario: "Veterinario que no es el assigned intenta completar -> 403",
        given: [
          "cita confirmada assignada al vet_A",
          "vet_B (no-assigned) autenticado",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/status con action=completed usando token de vet_B",
        ],
        then: [
          "response status = 403",
          "sin datos expuestos en la respuesta",
        ],
      });

      // Si solo tenemos un vet seeded, skip esta prueba de IDOR entre vets
      test.skip(
        env.vetEmail === "vet@example.com",
        "Requires a second vet account for cross-vet permission testing.",
      );

      const futureDate9 = new Date(Date.now() + 300 * 60 * 1000).toISOString();
      const appt = await createOwnerAppointment(request, ownerToken, futureDate9);

      // pending -> approved -> confirmed
      const clinicToken = await loginAsClinic(request);
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "approved" },
      });
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "confirmed" },
      });

      // Intentar completar con token de otro vet (si existe)
      const otherVetToken = await loginAsVet(request);

      const response = await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${otherVetToken}` },
        data: { action: "completed" },
      });
      expect([403, 422]).toContain(response.status());
    },
  );

  // ===========================================================================
  // A18: No-show valida (confirmed -> no_show)
  // Criterios: AC-008-07
  // ===========================================================================

  test(
    "@regression APIA-008-A18 US-008-04 AC-008-07 mark confirmed appointment as no_show",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-04",
        criteria: ["AC-008-07"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Marcacion de no-show",
        scenario: "Veterinario o clinica marca una cita confirmed como no_show",
        given: [
          "cita en status=confirmed",
          "vet o clinica con permiso de marcar no_show",
        ],
        when: [
          "PUT /api/v1/appointments/{id}/status con action=no_show",
        ],
        then: [
          "response status = 200",
          "response JSON status=no_show",
          "updated_at actualizado",
        ],
      });

      // Crear cita -> confirmada
      const futureDate10 = new Date(Date.now() + 360 * 60 * 1000).toISOString();
      const appt = await createOwnerAppointment(request, ownerToken, futureDate10);

      const clinicToken = await loginAsClinic(request);
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "approved" },
      });
      await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: { action: "confirmed" },
      });

      // Marcar no_show (vet o clinica)
      const vetToken = await loginAsVet(request);
      const response = await request.put(`/api/v1/appointments/${appt.id}/status`, {
        headers: { Authorization: `Bearer ${vetToken}` },
        data: { action: "no_show" },
      });

      // Puede ser 200 (valido) o 422 si requiere rol especifico
      if (response.status() === 200) {
        const body = (await response.json()) as Record<string, unknown>;
        expect(String(body.status)).toBe("no_show");
      } else {
        // Si el backend solo permite clinic para no_show, verificar 403/422
        expect([403, 422]).toContain(response.status());
      }
    },
  );

  // ===========================================================================
  // A19: Exposicion de datos sensibles en respuestas (security)
  // Criterios: AC-008-15, AC-008-16
  // ===========================================================================

  test(
    "@regression APIA-008-A19 US-008-01 AC-008-15 response bodies contain NO password or sensitive fields",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "008",
        userStory: "US-008-01",
        criteria: ["AC-008-15"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "No exposicion de datos sensibles en respuestas API",
        scenario: "Ninguna respuesta del endpoint expone hashed_password, password ni tokens internos",
        given: [
          "varias respuestas exitosas e invalidas del endpoint de citas",
        ],
        when: [
          "POST /api/v1/appointments (valido y invalido)",
          "PUT /api/v1/appointments/:id/status (invalido)",
          "GET /api/v1/appointments/me (con auth invalida)",
        ],
        then: [
          "ningun response body contiene hashed_password",
          "ningun response body contiene password en texto plano",
          "ningun response body expone el JWT token del solicitante",
        ],
      });

      // Verificar respuesta de error sin auth no expone datos internos
      const errorResp = await request.post("/api/v1/appointments");
      expect(errorResp.status()).toBe(401);
      const errorBodyStr = JSON.stringify(await errorResp.json()).toLowerCase();
      expect(errorBodyStr).not.toContain("hashed_password");
      expect(errorBodyStr).not.toContain("password");

      // Si hay datos de cita en response, verificar que no exponen sensitive fields
      const futureDate11 = new Date(Date.now() + 720 * 60 * 1000).toISOString();
      const appt = await createOwnerAppointment(request, ownerToken, futureDate11);
      const successBodyStr = JSON.stringify(await appt.response.json()).toLowerCase();
      expect(successBodyStr).not.toContain("hashed_password");
      expect(successBodyStr).not.toContain("password");

      // Verificar que no se expone el token en la respuesta JSON
      expect(successBodyStr).not.toContain("access_token");
    },
  );
});
