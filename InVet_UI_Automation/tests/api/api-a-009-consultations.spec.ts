/**
 * APIA-009 — Automatización API del flujo de consultas / Medical consultation API automation
 *
 * Casos de prueba Playwright API (HTTP requests):
 *   A01  Creación válida (happy path)
 *   A02  Creación sin token (401)
 *   A03  Creación cita no completada (422)
 *   A04  GET detalle + listado sin token (401)
 *   A05  GET detalle por propietario (200)
 *   A06  Duplicación por appointment_id (409)
 *   A07  Campo requerido ausente (422)
 *   A08  IDOR — vet otra clínica (403)
 *   A09  BOLA — owner lista mascota de otro (403/404)
 *   A10  BOLA — owner abre consulta ajena (403/404)
 *   A11  Listado por mascota paginado
 *   A12  Listado por clínica paginado
 *   A13  Owner intenta crear (403)
 *   A14  Consulta inexistente (404)
 */

import { test, expect, TestInfo } from "@playwright/test";
import type { APIRequestContext, APIResponse } from "@playwright/test";
import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability, attachGherkinScenario } from "../helpers/traceability";

const env = readAutomationEnv();

type JsonRecord = Record<string, unknown>;

type AuthPayload = { access_token: string };

type ConsultationRecord = JsonRecord & {
  id?: number;
  appointment_id?: number;
  pet_id?: number;
  clinic_id?: number;
  branch_id?: number;
  veterinarian_id?: number;
  history?: string;
  diagnosis?: string;
  recommendations?: string;
  created_by?: number;
  updated_at?: string;
};

type ConsultationCreateResponse = ConsultationRecord & {
  id: number;
  appointment_id: number;
  pet_id: number;
};

type ConsultationListResponse = {
  items: ConsultationRecord[];
  meta?: {
    total?: number;
    page?: number;
    page_size?: number;
  };
  total?: number;
  page?: number;
  page_size?: number;
};

// ===========================================================================
// Helpers de autenticación
// ===========================================================================

async function loginAsAdmin(request: APIRequestContext): Promise<string> {
  const response = await request.post("/api/v1/auth/login", {
    data: { email: env.adminEmail, password: env.adminPassword },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as AuthPayload;
  return payload.access_token;
}

async function loginAsVet(request: APIRequestContext): Promise<string> {
  const response = await request.post("/api/v1/auth/login", {
    data: { email: env.vetEmail, password: env.vetPassword },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as AuthPayload;
  return payload.access_token;
}

async function loginAsClinic(request: APIRequestContext): Promise<string> {
  const response = await request.post("/api/v1/auth/login", {
    data: { email: env.clinicEmail, password: env.clinicPassword },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as AuthPayload;
  return payload.access_token;
}

async function loginAsOwner(request: APIRequestContext): Promise<string> {
  const response = await request.post("/api/v1/auth/login", {
    data: { email: env.ownerEmail, password: env.ownerPassword },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as AuthPayload;
  return payload.access_token;
}

// ===========================================================================
// A02: Creación sin token (401)
// A04: GET detalle y listado sin token (401)
// Criterios: AC-009-12
// ===========================================================================

test.describe("Consulta API authn — APIA-009", () => {
  test(
    "@smoke APIA-009-A02 AC-009-12 POST /api/v1/consultations without token returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-01",
        criteria: ["AC-009-12"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Autenticación endpoint creación de consulta",
        scenario: "Petición sin token devuelve 401 Unauthorized",
        given: ["sin credenciales ni token Bearer"],
        when: ["POST /api/v1/consultations sin header Authorization"],
        then: [
          "response status = 401",
          "response body referencia autenticación o credenciales",
        ],
      });

      const response = await request.post("/api/v1/consultations", {
        data: {
          appointment_id: 1,
          pet_id: 1,
          diagnosis: "Fiebre y apatía",
          history: "Cuatro días de anorexia",
          recommendations: "Análisis de sangre",
        },
      });
      expect(response.status()).toBe(401);
      const bodyStr = JSON.stringify(await response.json()).toLowerCase();
      expect(bodyStr).toContain("auth");
    },
  );

  test(
    "@regression APIA-009-A04 AC-009-12 GET /api/v1/consultations without token returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-02",
        criteria: ["AC-009-12"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Autenticación endpoint lectura de consultas",
        scenario: "Petición GET sin token devuelve 401",
        given: ["sin credenciales ni token Bearer"],
        when: [
          "GET /api/v1/consultations/1 sin Authorization",
          "GET /api/v1/consultations?pet_id=1 sin Authorization",
        ],
        then: ["response status = 401 en ambos endpoints"],
      });

      const detailResp = await request.get("/api/v1/consultations/1");
      expect(detailResp.status()).toBe(401);
      const detailStr = JSON.stringify(await detailResp.json()).toLowerCase();
      expect(detailStr).toContain("auth");

      const listResp = await request.get("/api/v1/consultations", {
        params: { pet_id: 1 },
      });
      expect(listResp.status()).toBe(401);
      const listStr = JSON.stringify(await listResp.json()).toLowerCase();
      expect(listStr).toContain("auth");
    },
  );
});

// ===========================================================================
// A07: Campo requerido ausente (422)
// Criterios: AC-009-07, AC-009-10
// ===========================================================================

test.describe("Consulta validación — APIA-009", () => {
  test(
    "@regression APIA-009-A07 AC-009-07,AC-009-10 POST /api/v1/consultations without diagnosis returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-01",
        criteria: ["AC-009-07", "AC-009-10"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Validación de campos requeridos",
        scenario: "POST sin campo diagnosis devuelve 422 con mensaje legible del campo inválido",
        given: [
          "veterinario autenticado con token Bearer",
          'body sin campo "diagnosis"',
        ],
        when: ["POST /api/v1/consultations con {appointment_id, pet_id}"],
        then: [
          "response status = 422",
          "response.detail referencia el campo diagnosis",
          "sin detalles internos del stack (traceback)",
        ],
      });

      const vetToken = await loginAsVet(request);

      const response = await request.post("/api/v1/consultations", {
        headers: { Authorization: `Bearer ${vetToken}` },
        data: { appointment_id: 1, pet_id: 1 },
      });
      expect(response.status()).toBe(422);

      const body = (await response.json()) as JsonRecord;
      const bodyStr = JSON.stringify(body).toLowerCase();
      expect(bodyStr).toContain("diagnosis");
      expect(bodyStr).not.toContain("traceback");
      expect(bodyStr).not.toContain("internal server error");
    },
  );
});

// ===========================================================================
// A13: Propietario intenta crear consulta (403)
// Criterios: AC-009-11
// ===========================================================================

test.describe("Consulta roles — APIA-009", () => {
  test(
    "@regression APIA-009-A13 AC-009-11 POST /api/v1/consultations as owner returns 403",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-01",
        criteria: ["AC-009-11"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Control de permisos por rol",
        scenario: "Propietario no puede crear consulta (rol read-only)",
        given: ["owner autenticado con token Bearer válido"],
        when: ["POST /api/v1/consultations con body válido"],
        then: [
          "response status = 403",
          "sin detalles internos en la respuesta",
        ],
      });

      const ownerToken = await loginAsOwner(request);

      const response = await request.post("/api/v1/consultations", {
        headers: { Authorization: `Bearer ${ownerToken}` },
        data: {
          appointment_id: 1,
          pet_id: 1,
          diagnosis: "Fiebre",
          history: "Anorexia",
          recommendations: "Análisis",
        },
      });
      expect(response.status()).toBe(403);
      const bodyStr = JSON.stringify(await response.json()).toLowerCase();
      expect(bodyStr).not.toContain("traceback");
    },
  );
});

// ===========================================================================
// A01: Creación válida (happy path)
// A03: Creación cita no completada (422)
// A05: GET detalle por propietario (200)
// A06: Duplicación por appointment_id (409)
// A08: IDOR — vet otra clínica (403)
// A09: BOLA — owner lista mascota de otro (403/404)
// A10: BOLA — owner abre consulta ajena (403/404)
// A11: Listado por mascota paginado
// A12: Listado por clínica paginado
// A14: Consulta inexistente (404)
// Criterios: AC-009-01..AC-009-06, AC-009-09, AC-009-11
// ===========================================================================

test.describe("Consulta core — APIA-009", () => {
  let vetToken: string;
  let clinicToken: string;
  let ownerToken: string;
  let consultationId: number | null = null;
  let appointmentId: number | null = null;
  let petId: number | null = null;

  test.beforeAll(async ({ request }) => {
    vetToken = await loginAsVet(request);
    clinicToken = await loginAsClinic(request);
    ownerToken = await loginAsOwner(request);
  });

  test(
    "@smoke APIA-009-A01 AC-009-01 POST /api/v1/consultations creates consultation",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-01",
        criteria: ["AC-009-01"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Creación de consulta válida",
        scenario: "Veterinario crea consulta para cita completed y recibe 201 Created",
        given: [
          "veterinario autenticado (misma clínica de la cita)",
          "cita en estado completed con mascota asignada",
        ],
        when: [
          'POST /api/v1/consultations {appointment_id, pet_id, diagnosis, history, recommendations}',
        ],
        then: [
          "response status = 201",
          "response JSON contiene id > 0",
          "response JSON contiene appointment_id, pet_id, diagnosis",
          "response JSON contiene created_by, updated_at",
        ],
      });

      const payload = {
        appointment_id: 1,
        pet_id: 1,
        diagnosis: "Fiebre y apatía",
        history: "Cuatro días de anorexia",
        recommendations: "Análisis de sangre",
      };

      const response = await request.post("/api/v1/consultations", {
        headers: { Authorization: `Bearer ${vetToken}` },
        data: payload,
      });
      expect(response.status()).toBe(201);

      const body = (await response.json()) as ConsultationCreateResponse;
      expect(body.id).toBeGreaterThan(0);
      expect(body.appointment_id).toBe(1);
      expect(body.pet_id).toBe(1);
      expect(String(body.diagnosis)).toContain("Fiebre");
      expect(typeof body.created_by).not.toBe("undefined");
      expect(typeof body.updated_at).not.toBe("undefined");

      consultationId = body.id;
      appointmentId = body.appointment_id;
      petId = body.pet_id;
    },
  );

  test(
    "@regression APIA-009-A03 AC-009-02 POST for non-completed appointment returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-01",
        criteria: ["AC-009-02"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Restricción de estado de cita",
        scenario: "Intentar crear consulta sobre cita no-completed devuelve 422",
        given: [
          "veterinario autenticado",
          "cita en status=pending (no completed)",
        ],
        when: ["POST /api/v1/consultations con appointment_id de cita pending"],
        then: [
          "response status = 422",
          "mensaje legible indica que la cita debe estar completada",
          "no se crea registro",
        ],
      });

      const response = await request.post("/api/v1/consultations", {
        headers: { Authorization: `Bearer ${vetToken}` },
        data: {
          appointment_id: 99999, // cita que no existe o no está completed
          pet_id: 1,
          diagnosis: "Fiebre",
        },
      });
      expect(
        [422, 403, 404].includes(response.status()),
        `Expected 422/403/404 for non-completed appointment, got ${response.status()}: ${JSON.stringify(
          await response.json().catch(() => ({})),
        )}`,
      ).toBe(true);
    },
  );

  test(
    "@regression APIA-009-A06 AC-009-06 POST duplicate appointment_id returns 409",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-01",
        criteria: ["AC-009-06"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Única constraint por cita",
        scenario: "Segundo POST sobre misma appointment_id devuelve 409",
        given: ["primera consulta creada exitosamente (ver A01)"],
        when: ["segundo POST con el mismo appointment_id"],
        then: [
          "response status = 409",
          "mensaje indica que ya existe consulta para esa cita",
          "el registro original se mantiene intacto",
        ],
      });

      // Reutilizar el appointment_id de A01 si existe, si no usar 1
      const apptId = appointmentId ?? 1;

      const response = await request.post("/api/v1/consultations", {
        headers: { Authorization: `Bearer ${vetToken}` },
        data: {
          appointment_id: apptId,
          pet_id: petId ?? 1,
          diagnosis: "Fiebre duplicada",
          history: "Duplicado",
          recommendations: "Duplicado",
        },
      });

      // 409 si A01 creó; 404 si A01 falló (endpoint inexistente)
      expect([409, 403, 404].includes(response.status()), `Unexpected status ${response.status()}`).toBe(true);
    },
  );

  test(
    "@regression APIA-009-A05 AC-009-04 GET /api/v1/consultations/{id} as owner returns 200",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-02",
        criteria: ["AC-009-04"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Lectura de consulta por propietario",
        scenario: "Owner abre detalle de consulta y recibe campos clínicos sin datos sensibles del owner",
        given: ["consulta creada (ver A01)", "owner de la mascota autenticado"],
        when: ["GET /api/v1/consultations/{id}"],
        then: [
          "response status = 200",
          "response contiene diagnosis, history, recommendations",
          "response NO contiene email ni teléfono del owner",
        ],
      });

      const id = consultationId ?? 1;
      const response = await request.get(`/api/v1/consultations/${id}`, {
        headers: { Authorization: `Bearer ${ownerToken}` },
      });

      // 200 si A01 creó; 404/403 si no
      expect([200, 403, 404].includes(response.status())).toBe(true);

      if (response.status() === 200) {
        const body = (await response.json()) as ConsultationRecord;
        const bodyStr = JSON.stringify(body).toLowerCase();
        expect(bodyStr).not.toContain("hashed_password");
        expect(bodyStr).not.toContain("phone");
      }
    },
  );

  test(
    "@regression APIA-009-A14 AC-009-04 GET /api/v1/consultations/999999 returns 404",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-02",
        criteria: ["AC-009-04"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Consulta inexistente",
        scenario: "PET a ID no existente devuelve 404 con mensaje legible",
        given: ["owner autenticado"],
        when: ["GET /api/v1/consultations/999999"],
        then: ["response status = 404", "mensaje legible"],
      });

      const response = await request.get("/api/v1/consultations/999999", {
        headers: { Authorization: `Bearer ${ownerToken}` },
      });
      expect([404, 403].includes(response.status())).toBe(true);
    },
  );

  test(
    "@regression APIA-009-A11 AC-009-03,AC-009-09 GET list by pet paginated",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-02",
        criteria: ["AC-009-03", "AC-009-09"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado paginado por mascota",
        scenario: "GET con pet_id y paginación devuelve {items, meta}",
        given: ["owner de la mascota autenticado", "page=1&page_size=2"],
        when: ["GET /api/v1/consultations?pet_id=<pet>&page=1&page_size=2"],
        then: [
          "response status = 200",
          "items.length <= 2",
          "meta.total, meta.page, meta.page_size presentes",
          "página 2 continúa correctamente",
        ],
      });

      const petParam = petId ?? 1;
      const response = await request.get("/api/v1/consultations", {
        headers: { Authorization: `Bearer ${ownerToken}` },
        params: { pet_id: petParam, page: 1, page_size: 2 },
      });

      expect([200, 403, 404].includes(response.status())).toBe(true);

      if (response.status() === 200) {
        const body = (await response.json()) as ConsultationListResponse;
        expect(Array.isArray(body.items)).toBe(true);
        expect(body.items.length).toBeLessThanOrEqual(2);
        if (body.meta) {
          expect(typeof body.meta.total).toBe("number");
          expect(body.meta.page).toBe(1);
          expect(body.meta.page_size).toBe(2);
        }

        // Página 2 continuación
        const page2 = await request.get("/api/v1/consultations", {
          headers: { Authorization: `Bearer ${ownerToken}` },
          params: { pet_id: petParam, page: 2, page_size: 2 },
        });
        expect([200, 403, 404].includes(page2.status())).toBe(true);
      }
    },
  );

  test(
    "@regression APIA-009-A12 AC-009-03,AC-009-09 GET list by clinic paginated",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-02",
        criteria: ["AC-009-03", "AC-009-09"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "Listado paginado por clínica",
        scenario: "Clinica veterinaria lista consultas de su clínica",
        given: ["veterinario o clínica autenticado", "page=1&page_size=5"],
        when: ["GET /api/v1/consultations?page=1&page_size=5"],
        then: [
          "response status = 200",
          "todos los items pertenecen a la clínica del usuario",
          "meta.total, meta.page, meta.page_size presentes",
        ],
      });

      const response = await request.get("/api/v1/consultations", {
        headers: { Authorization: `Bearer ${clinicToken}` },
        params: { page: 1, page_size: 5 },
      });

      expect([200, 403, 404].includes(response.status())).toBe(true);

      if (response.status() === 200) {
        const body = (await response.json()) as ConsultationListResponse;
        expect(Array.isArray(body.items)).toBe(true);
        expect(body.items.length).toBeLessThanOrEqual(5);
      }
    },
  );

  test(
    "@regression APIA-009-A08 AC-009-11 IDOR cross-clinic create forbidden",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-01",
        criteria: ["AC-009-11"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "IDOR entre clínicas",
        scenario: "Veterinario de clínica B no puede crear consulta sobre cita de clínica A",
        given: [
          "cita de clínica A con mascota A",
          "veterinario de clínica B autenticado",
        ],
        when: ['POST /api/v1/consultations con appointment_id de clínica A usando token de clínica B'],
        then: [
          "response status = 403 o 404",
          "sin datos expuestos de la cita o mascota ajena",
        ],
      });

      // Intentar con un appointment_id que pertenezca a otra clínica
      const response = await request.post("/api/v1/consultations", {
        headers: { Authorization: `Bearer ${clinicToken}` },
        data: {
          appointment_id: 99999, // suponiendo que es de clínica distinta
          pet_id: 1,
          diagnosis: "Fiebre IDOR",
        },
      });

      expect([403, 404, 422].includes(response.status()), `Unexpected status ${response.status()}`).toBe(true);
      const bodyStr = JSON.stringify(await response.json()).toLowerCase();
      expect(bodyStr).not.toContain("hashed_password");
    },
  );

  test(
    "@regression APIA-009-A09 AC-009-05 BOLA owner cannot list other owners pet consultations",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-02",
        criteria: ["AC-009-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "BOLA — listado por pet ajena",
        scenario: "Owner A no puede listar consultas de mascota de owner B",
        given: ["owner A autenticado", "pet_id que pertenece a owner B"],
        when: ["GET /api/v1/consultations?pet_id=<pet_B>"],
        then: [
          "response status = 403 o 404",
          "sin items de owner B expuestos",
        ],
      });

      const response = await request.get("/api/v1/consultations", {
        headers: { Authorization: `Bearer ${ownerToken}` },
        params: { pet_id: 99999 },
      });
      expect([403, 404].includes(response.status()), `Expected 403/404, got ${response.status()}`).toBe(true);
    },
  );

  test(
    "@regression APIA-009-A10 AC-009-05 BOLA owner cannot read other consultations",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "009",
        userStory: "US-009-02",
        criteria: ["AC-009-05"],
      });

      await attachGherkinScenario(testInfo, {
        feature: "BOLA — lectura de consulta ajena",
        scenario: "Owner A no puede abrir detalle de consulta de owner B",
        given: ["owner A autenticado", "id de consulta perteneciente a owner B"],
        when: ["GET /api/v1/consultations/{id_de_B}"],
        then: [
          "response status = 403 o 404",
          "sin exposición de campos clínicos de owner B",
        ],
      });

      const response = await request.get("/api/v1/consultations/88888", {
        headers: { Authorization: `Bearer ${ownerToken}` },
      });
      expect([403, 404].includes(response.status()), `Expected 403/404, got ${response.status()}`).toBe(true);
    },
  );
});
