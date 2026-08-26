/**
 * APIA-012 — Automatización contractual de calificaciones, comentarios y respuesta clínica
 *
 * Casos Playwright API:
 *   C1  crear OK (201 + ReviewRead con branch_id/clinic_id/appt_id)
 *   C2  rating fuera de rango (422)
 *   C3  cita sin completar (422)
 *   C4  repetición cita (segunda 409)
 *   C5  cita ajena (BOLA) no se califica (403)
 *   C6  sin token (401 en todos los endpoints autenticados)
 *   C7  comment overflow (422)
 *   C8  detalle propio (200 ReviewRead)
 *   C9  detalle ajeno IDOR (404 consistente)
 *   C10 listado público paginado anónimo (200 + meta)
 *   C11 listado sucursal inexistente (404)
 *   C12 resumen sucursal en perfil público
 *   C13 respuesta clínico OK (200 + body) + C14 segunda 409
 *   C15 propietario responde (403)
 *   C16 usuario sin rol clínico intenta responder (403/404)
 *   C17 sin token responde (401)
 *   C18 errores sin stack trace / leakage interno
 *   C19 resumen se actualiza tras crear reseña
 *   C20 body vacío (422 por campos faltantes)
 *
 * Cada test es autocontenido e idempotente: los flujos que mutan estado
 * (C1, C13, C19) crean su propia cita COMPLETED con el helper
 * `mintCompletedAppointment` y no dependen de reseñas pre-existentes.
 */

import { test, expect, TestInfo } from "@playwright/test";
import type { APIRequestContext } from "@playwright/test";
import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability } from "../helpers/traceability";

const env = readAutomationEnv();

type JsonRecord = Record<string, unknown>;

// owner2 (pet 1001) es el actor de reseñas: es titular de la cita 1001
// (COMPLETED, sin reseña) sembrada para este slice.
const REVIEW_OWNER_EMAIL = env.foreignOwnerEmail;
const REVIEW_OWNER_PASSWORD = env.foreignOwnerPassword;
const REVIEW_OWNER_PET_ID = 1001;

// owner1 (pet 1000) es titular de citas PENDING (1002/1003) y de la
// reseña pre-existente id 2 (cita 1000) ya respondida.
const PENDING_OWNER_EMAIL = env.ownerEmail;
const PENDING_OWNER_PASSWORD = env.ownerPassword;
const PENDING_APPOINTMENT_ID = 1002;
const SEED_REVIEW_ID = 2;

// Cita 1001: COMPLETED, titular owner2 → usada para BOLA/duplicate/validación.
const SEED_COMPLETED_APPOINTMENT_ID = 1001;

const FOREIGN_OWNER_EMAIL = "owner-clinic2@invet.com";
const FOREIGN_OWNER_PASSWORD = "secret123";
const FOREIGN_PET_ID = 1000;

const CLINIC_ID = 1;
const BRANCH_ID = 1;

async function loginAs(
  request: APIRequestContext,
  email: string,
  password: string,
): Promise<string> {
  const response = await request.post("/api/v1/auth/login", {
    data: { email, password },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as { access_token: string };
  return payload.access_token;
}

function authHeader(token: string) {
  return { Authorization: `Bearer ${token}` };
}

function assertNoLeak(body: JsonRecord): void {
  expect(JSON.stringify(body)).not.toMatch(
    /Traceback|127\.0\.0\.1|psycopg|sqlalchemy|invet-db|pg_/i,
  );
}

/**
 * Creó una cita COMPLETED nueva para el owner dado:
 * owner POST /appointments → vet transiciona approved → confirmed → completed.
 * Devuelve el id de la cita.
 */
async function mintCompletedAppointment(
  request: APIRequestContext,
  ownerEmail: string,
  ownerPassword: string,
  petId: number,
): Promise<number> {
  const ownerToken = await loginAs(request, ownerEmail, ownerPassword);
  const vetToken = await loginAs(request, env.vetEmail, env.vetPassword);

  const scheduledStart = new Date(Date.now() + 14 * 86400_000).toISOString().slice(0, 19);
  const created = await request.post("/api/v1/appointments", {
    headers: authHeader(ownerToken),
    data: {
      pet_id: petId,
      clinic_id: CLINIC_ID,
      branch_id: BRANCH_ID,
      appointment_type: "consultation",
      scheduled_start: scheduledStart,
      duration_minutes: 30,
      reason: "apia-012 fixture",
    },
  });
  expect(created.status(), `crear cita: ${await created.text()}`).toBe(201);
  const appointmentId = ((await created.json()) as { id: number }).id;

  for (const status of ["approved", "confirmed", "completed"]) {
    const transitioned = await request.post(
      `/api/v1/appointments/${appointmentId}/status`,
      {
        headers: authHeader(vetToken),
        data: { status, notes: "apia-012 fixture" },
      },
    );
    expect(
      transitioned.status(),
      `transición ${status}: ${await transitioned.text()}`,
    ).toBe(200);
  }
  return appointmentId;
}

test.describe("Reseñas API contractual — APIA-012", () => {
  test(
    "@contract APIA-012-C1 AC-012-01 crear reseña OK (201 + campos de contexto)",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-01"] });
      const appointmentId = await mintCompletedAppointment(
        request,
        REVIEW_OWNER_EMAIL,
        REVIEW_OWNER_PASSWORD,
        REVIEW_OWNER_PET_ID,
      );
      const token = await loginAs(request, REVIEW_OWNER_EMAIL, REVIEW_OWNER_PASSWORD);
      const res = await request.post("/api/v1/reviews", {
        headers: authHeader(token),
        data: { appointment_id: appointmentId, rating: 4, comment: "Excelente atención" },
      });
      expect(res.status(), await res.text()).toBe(201);
      const body = (await res.json()) as JsonRecord & {
        id: number;
        appointment_id: number;
        branch_id: number;
        clinic_id: number;
        rating: number;
        user_id: number | null;
        comment: string | null;
      };
      expect(body.appointment_id).toBe(appointmentId);
      expect(body.comment).toBe("Excelente atención");
      expect(body.rating).toBe(4);
      expect(body.user_id).toBeTruthy();
      expect(body.branch_id).toBe(BRANCH_ID);
      expect(body.clinic_id).toBe(CLINIC_ID);
    },
  );

  test(
    "@contract APIA-012-C2 AC-012-01 rating fuera de rango devuelve 422",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-01"] });
      const token = await loginAs(request, REVIEW_OWNER_EMAIL, REVIEW_OWNER_PASSWORD);
      for (const rating of [0, 6, -1]) {
        const res = await request.post("/api/v1/reviews", {
          headers: authHeader(token),
          data: { appointment_id: SEED_COMPLETED_APPOINTMENT_ID, rating },
        });
        expect(res.status()).toBe(422);
        assertNoLeak((await res.json()) as JsonRecord);
      }
    },
  );

  test(
    "@contract APIA-012-C3 AC-012-02 cita sin completar devuelve 422",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-02"] });
      const token = await loginAs(request, PENDING_OWNER_EMAIL, PENDING_OWNER_PASSWORD);
      const res = await request.post("/api/v1/reviews", {
        headers: authHeader(token),
        data: { appointment_id: PENDING_APPOINTMENT_ID, rating: 5 },
      });
      expect(res.status()).toBe(422);
      const body = (await res.json()) as JsonRecord;
      expect(body.detail).toBeTruthy();
      assertNoLeak(body);
    },
  );

  test(
    "@contract APIA-012-C4 AC-012-03 segunda reseña por cita devuelve 409",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-03"] });
      const token = await loginAs(request, REVIEW_OWNER_EMAIL, REVIEW_OWNER_PASSWORD);
      // Garantizar que la cita tiene reseña (primer intento 201 o 409, ambos válidos).
      const first = await request.post("/api/v1/reviews", {
        headers: authHeader(token),
        data: { appointment_id: SEED_COMPLETED_APPOINTMENT_ID, rating: 5, comment: "primera" },
      });
      expect([201, 409]).toContain(first.status());
      const second = await request.post("/api/v1/reviews", {
        headers: authHeader(token),
        data: { appointment_id: SEED_COMPLETED_APPOINTMENT_ID, rating: 5, comment: "otro intento" },
      });
      expect(second.status()).toBe(409);
      assertNoLeak((await second.json()) as JsonRecord);
    },
  );

  test(
    "@contract APIA-012-C5 AC-012-04 cita ajena (BOLA) no se califica (403)",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-04", "AC-012-12"] });
      const foreign = await loginAs(request, PENDING_OWNER_EMAIL, PENDING_OWNER_PASSWORD);
      const res = await request.post("/api/v1/reviews", {
        headers: authHeader(foreign),
        data: {
          appointment_id: SEED_COMPLETED_APPOINTMENT_ID,
          rating: 1,
          comment: "BOLA: cita de owner2",
        },
      });
      expect(res.status()).toBe(403);
      assertNoLeak((await res.json()) as JsonRecord);
    },
  );

  test(
    "@contract APIA-012-C6 AC-012-13 sin token en POST /reviews devuelve 401",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-13"] });
      const res = await request.post("/api/v1/reviews", {
        data: { appointment_id: SEED_COMPLETED_APPOINTMENT_ID, rating: 5 },
      });
      expect(res.status()).toBe(401);
    },
  );

  test(
    "@contract APIA-012-C6 AC-012-13 sin token en GET /reviews/{id} devuelve 401",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-13"] });
      const res = await request.get(`/api/v1/reviews/${SEED_REVIEW_ID}`);
      expect(res.status()).toBe(401);
    },
  );

  test(
    "@contract APIA-012-C7 AC-012-15 comment con 2049 caracteres devuelve 422",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-15"] });
      const token = await loginAs(request, REVIEW_OWNER_EMAIL, REVIEW_OWNER_PASSWORD);
      const res = await request.post("/api/v1/reviews", {
        headers: authHeader(token),
        data: {
          appointment_id: SEED_COMPLETED_APPOINTMENT_ID,
          rating: 5,
          comment: "x".repeat(2049),
        },
      });
      expect(res.status()).toBe(422);
      assertNoLeak((await res.json()) as JsonRecord);
    },
  );

  test(
    "@contract APIA-012-C8 AC-012-12 detalle de reseña propia devuelve 200 ReviewRead",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-12"] });
      const token = await loginAs(request, PENDING_OWNER_EMAIL, PENDING_OWNER_PASSWORD);
      const res = await request.get(`/api/v1/reviews/${SEED_REVIEW_ID}`, {
        headers: authHeader(token),
      });
      expect(res.status()).toBe(200);
      const body = (await res.json()) as JsonRecord & {
        id: number;
        rating: number;
        clinic_id: number;
        branch_id: number;
        response: JsonRecord | null;
      };
      expect(body.id).toBe(SEED_REVIEW_ID);
      expect(body.rating).toBeGreaterThanOrEqual(1);
      expect(body.rating).toBeLessThanOrEqual(5);
      expect(body.clinic_id).toBe(CLINIC_ID);
      expect(body.branch_id).toBe(BRANCH_ID);
      expect(body.response).toBeTruthy();
    },
  );

  test(
    "@contract APIA-012-C9 AC-012-12 detalle de reseña ajena (IDOR) devuelve 404",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-12"] });
      const foreign = await loginAs(request, FOREIGN_OWNER_EMAIL, FOREIGN_OWNER_PASSWORD);
      const res = await request.get(`/api/v1/reviews/${SEED_REVIEW_ID}`, {
        headers: authHeader(foreign),
      });
      expect(res.status()).toBe(404);
      const body = (await res.json()) as JsonRecord;
      expect(body.detail).toBeTruthy();
      assertNoLeak(body);
    },
  );

  test(
    "@contract APIA-012-C10 AC-012-07 listado público paginado anónimo con meta",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-03", criteria: ["AC-012-07"] });
      const res = await request.get(`/api/v1/reviews/public/${BRANCH_ID}?page=1&page_size=10`);
      expect(res.status()).toBe(200);
      const body = (await res.json()) as {
        items: JsonRecord[];
        meta: { page: number; page_size: number; total: number; pages: number };
      };
      expect(Array.isArray(body.items)).toBe(true);
      expect(body.items.length).toBeGreaterThan(0);
      expect(body.meta.page).toBe(1);
      expect(body.meta.page_size).toBe(10);
      expect(body.meta.total).toBeGreaterThanOrEqual(body.items.length);
      expect(body.meta.pages).toBeGreaterThanOrEqual(1);
    },
  );

  test(
    "@contract APIA-012-C11 AC-012-07 listing sucursal inexistente devuelve 404",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-03", criteria: ["AC-012-07"] });
      const res = await request.get("/api/v1/reviews/public/999999");
      expect(res.status()).toBe(404);
      assertNoLeak((await res.json()) as JsonRecord);
    },
  );

  test(
    "@contract APIA-012-C12 AC-012-08 perfil público expone rating_summary",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-03", criteria: ["AC-012-08"] });
      const res = await request.get(`/api/v1/clinics/branches/${BRANCH_ID}`);
      expect(res.status()).toBe(200);
      const body = (await res.json()) as JsonRecord & {
        rating_summary: {
          average_rating: number;
          total_reviews: number;
          review_distribution: string | null;
        };
      };
      expect(body.rating_summary).toBeTruthy();
      expect(body.rating_summary.average_rating).toBeGreaterThan(0);
      expect(body.rating_summary.average_rating).toBeLessThanOrEqual(5);
      expect(body.rating_summary.total_reviews).toBeGreaterThan(0);
      const distribution = JSON.parse(
        body.rating_summary.review_distribution ?? "{}",
      ) as Record<string, number>;
      const sum = Object.values(distribution).reduce((a, b) => a + b, 0);
      expect(sum).toBe(body.rating_summary.total_reviews);
    },
  );

  test(
    "@contract APIA-012-C13/C14 AC-012-05 respuesta del clínico OK y segunda 409",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-02", criteria: ["AC-012-05"] });
      const appointmentId = await mintCompletedAppointment(
        request,
        REVIEW_OWNER_EMAIL,
        REVIEW_OWNER_PASSWORD,
        REVIEW_OWNER_PET_ID,
      );
      const ownerToken = await loginAs(request, REVIEW_OWNER_EMAIL, REVIEW_OWNER_PASSWORD);
      const created = await request.post("/api/v1/reviews", {
        headers: authHeader(ownerToken),
        data: {
          appointment_id: appointmentId,
          rating: 3,
          comment: "Bien pero lento",
        },
      });
      expect(created.status(), await created.text()).toBe(201);
      const reviewId = ((await created.json()) as { id: number }).id;

      const vet = await loginAs(request, env.vetEmail, env.vetPassword);
      const responded = await request.post(`/api/v1/reviews/${reviewId}/respond`, {
        headers: authHeader(vet),
        data: { body: "Gracias por su valiosa reseña" },
      });
      expect(responded.status(), await responded.text()).toBe(200);
      const resBody = (await responded.json()) as JsonRecord & {
        id: number;
        review_id: number;
        body: string;
      };
      expect(resBody.review_id).toBe(reviewId);
      expect(resBody.body).toBeTruthy();

      const again = await request.post(`/api/v1/reviews/${reviewId}/respond`, {
        headers: authHeader(vet),
        data: { body: "segunda respuesta" },
      });
      expect(again.status()).toBe(409);
      assertNoLeak((await again.json()) as JsonRecord);
    },
  );

  test(
    "@contract APIA-012-C15 AC-012-06 propietario intenta responder devuelve 403",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-02", criteria: ["AC-012-06"] });
      const token = await loginAs(request, PENDING_OWNER_EMAIL, PENDING_OWNER_PASSWORD);
      const res = await request.post(`/api/v1/reviews/${SEED_REVIEW_ID}/respond`, {
        headers: authHeader(token),
        data: { body: "no debería salir" },
      });
      expect(res.status()).toBe(403);
      assertNoLeak((await res.json()) as JsonRecord);
    },
  );

  test(
    "@contract APIA-012-C16 AC-012-12 usuario ajeno no responde (403/404 consistente)",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-02", criteria: ["AC-012-12"] });
      const foreign = await loginAs(request, FOREIGN_OWNER_EMAIL, FOREIGN_OWNER_PASSWORD);
      const res = await request.post(`/api/v1/reviews/${SEED_REVIEW_ID}/respond`, {
        headers: authHeader(foreign),
        data: { body: "BOLA respond" },
      });
      expect([403, 404]).toContain(res.status());
      assertNoLeak((await res.json()) as JsonRecord);
    },
  );

  test(
    "@contract APIA-012-C17 AC-012-13 sin token en /respond devuelve 401",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-02", criteria: ["AC-012-13"] });
      const res = await request.post(`/api/v1/reviews/${SEED_REVIEW_ID}/respond`, {
        data: { body: "anon" },
      });
      expect(res.status()).toBe(401);
    },
  );

  test(
    "@contract APIA-012-C18 AC-012-15 errores sin leakage interno (stack/ORM/DB)",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-15"] });
      const token = await loginAs(request, PENDING_OWNER_EMAIL, PENDING_OWNER_PASSWORD);
      const res = await request.post("/api/v1/reviews", {
        headers: authHeader(token),
        data: { appointment_id: 99999999, rating: 2 },
      });
      expect([404, 422]).toContain(res.status());
      const body = (await res.json()) as JsonRecord;
      assertNoLeak(body);
    },
  );

  test(
    "@contract APIA-012-C19 AC-012-09 el resumen de la sucursal incluye la nueva reseña",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-03", criteria: ["AC-012-09"] });
      const appointmentId = await mintCompletedAppointment(
        request,
        REVIEW_OWNER_EMAIL,
        REVIEW_OWNER_PASSWORD,
        REVIEW_OWNER_PET_ID,
      );
      const token = await loginAs(request, REVIEW_OWNER_EMAIL, REVIEW_OWNER_PASSWORD);
      const created = await request.post("/api/v1/reviews", {
        headers: authHeader(token),
        data: { appointment_id: appointmentId, rating: 4, comment: "C19" },
      });
      expect(created.status(), await created.text()).toBe(201);
      const createdBody = (await created.json()) as { id: number; branch_id: number };
      expect(createdBody.branch_id).toBe(BRANCH_ID);

      // Race-free en ejecución paralela: la reseña nueva debe aparecer en el
      // listado público y el resumen debe ser coherente con ese listado.
      const list = await request.get(`/api/v1/reviews/public/${BRANCH_ID}?page=1&page_size=100`);
      expect(list.status()).toBe(200);
      const listBody = (await list.json()) as {
        items: { id: number }[];
        meta: { total: number };
      };
      expect(listBody.items.map((item) => item.id)).toContain(createdBody.id);

      const branch = await request.get(`/api/v1/clinics/branches/${BRANCH_ID}`);
      expect(branch.status()).toBe(200);
      const branchBody = (await branch.json()) as {
        rating_summary: { total_reviews: number; average_rating: number };
      };
      expect(branchBody.rating_summary.total_reviews).toBe(listBody.meta.total);
      expect(branchBody.rating_summary.average_rating).toBeGreaterThan(0);
      expect(branchBody.rating_summary.average_rating).toBeLessThanOrEqual(5);
    },
  );

  test(
    "@contract APIA-012-C20 AC-012-15 body vacío devuelve 422 por campo",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["AC-012-15"] });
      const token = await loginAs(request, REVIEW_OWNER_EMAIL, REVIEW_OWNER_PASSWORD);
      const res = await request.post("/api/v1/reviews", {
        headers: authHeader(token),
        data: {},
      });
      expect(res.status()).toBe(422);
      const body = (await res.json()) as { detail: unknown };
      expect(JSON.stringify(body)).toMatch(/appointment_id/);
      assertNoLeak(body as JsonRecord);
    },
  );

  test(
    "@regression APIA-011 pagos siguen operando (sin regresión)",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "012", userStory: "US-012-01", criteria: ["regression-011"] });
      const vet = await loginAs(request, env.vetEmail, env.vetPassword);
      const list = await request.get("/api/v1/payments?page=1&page_size=5", {
        headers: authHeader(vet),
      });
      expect(list.status()).toBe(200);
      const body = (await list.json()) as { meta: { page: number } };
      expect(body.meta.page).toBe(1);
    },
  );
});
