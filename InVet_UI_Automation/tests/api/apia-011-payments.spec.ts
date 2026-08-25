/**
 * APIA-011 — Automatización contractual del flujo de pagos operativos
 *
 * Casos Playwright API:
 *   C1  crear OK (201 + PaymentRead, status=PAID)
 *   C2  cita inexistente (404/422, sin registro parcial)
 *   C3  servicio inactivo (422)
 *   C4  cambio inválido (422)
 *   C5  sin token (401 en POST/GET/cancel)
 *   C6  propietario crea (403)
 *   C7  clínico ajeno lee (404/403 consistente)
 *   C8  detalle OK (200 PaymentRead completo)
 *   C9  listado paginado (200 + meta)
 *   C10 cancelar OK (200 status=CANCELLED, cancelled_at poblado)
 *   C11 cancelar dos veces (segunda 409)
 *   C12 listado periodo (solo pagos dentro del rango)
 */

import { test, expect, TestInfo } from "@playwright/test";
import type { APIRequestContext } from "@playwright/test";
import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability } from "../helpers/traceability";

const env = readAutomationEnv();

type AuthPayload = { access_token: string };
type JsonRecord = Record<string, unknown>;

async function loginAs(request: APIRequestContext, email: string, password: string): Promise<string> {
  const response = await request.post("/api/v1/auth/login", {
    data: { email, password },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as AuthPayload;
  return payload.access_token;
}

async function vetToken(request: APIRequestContext): Promise<string> {
  return loginAs(request, env.vetEmail, env.vetPassword);
}

async function ownerToken(request: APIRequestContext): Promise<string> {
  return loginAs(request, env.ownerEmail, env.ownerPassword);
}

function authHeader(token: string) {
  return { Authorization: `Bearer ${token}` };
}

test.describe("Pagos API contractual — APIA-011", () => {
  test(
    "@contract APIA-011-C5 AC-011-09 sin token en POST /payments devuelve 401",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-02", criteria: ["AC-011-09"] });
      const res = await request.post("/api/v1/payments", {
        data: { appointment_id: 1000, service_id: 17, method: "cash", amount: 15000, amount_received: 20000 },
      });
      expect(res.status()).toBe(401);
    },
  );

  test(
    "@contract APIA-011-C5 sin token en GET /payments/{id} devuelve 401",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-02", criteria: ["AC-011-09"] });
      const res = await request.get("/api/v1/payments/1");
      expect(res.status()).toBe(401);
    },
  );

  test(
    "@contract APIA-011-C5 sin token en POST /payments/{id}/cancel devuelve 401",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-02", criteria: ["AC-011-09"] });
      const res = await request.post("/api/v1/payments/1/cancel");
      expect(res.status()).toBe(401);
    },
  );

  test(
    "@contract APIA-011-C6 AC-011-04 propietario intenta crear devuelve 403",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-04", criteria: ["AC-011-04"] });
      const token = await ownerToken(request);
      const res = await request.post("/api/v1/payments", {
        headers: authHeader(token),
        data: { appointment_id: 1000, service_id: 17, method: "cash", amount: 15000, amount_received: 20000 },
      });
      expect(res.status()).toBe(403);
    },
  );

  test(
    "@contract APIA-011-C2 cita inexistente devuelve error claro sin registro parcial",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-01", criteria: ["AC-011-01"] });
      const token = await vetToken(request);

      const res = await request.post("/api/v1/payments", {
        headers: authHeader(token),
        data: { appointment_id: 999999999, service_id: 17, method: "cash", amount: 15000, amount_received: 20000 },
      });
      expect([404, 422]).toContain(res.status());
      const body = (await res.json()) as JsonRecord;
      expect(JSON.stringify(body)).not.toMatch(/Traceback|localhost|127\.0\.0\.1/);

      const list = await request.get("/api/v1/payments?page=1&page_size=100", { headers: authHeader(token) });
      expect(list.status()).toBe(200);
      const payload = (await list.json()) as JsonRecord & { items?: JsonRecord[] };
      const items = payload.items ?? [];
      expect(items.some((item) => Number(item.appointment_id) === 999999999)).toBe(false);
    },
  );

  test(
    "@contract APIA-011-C3 servicio inactivo devuelve 422",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-01", criteria: ["AC-011-01"] });
      const token = await vetToken(request);
      const res = await request.post("/api/v1/payments", {
        headers: authHeader(token),
        data: { appointment_id: 1000, service_id: 19, method: "cash", amount: 15000, amount_received: 20000 },
      });
      expect(res.status()).toBe(422);
      const body = (await res.json()) as JsonRecord;
      expect(JSON.stringify(body)).not.toMatch(/Traceback|localhost/);
    },
  );

  test(
    "@contract APIA-011-C4 cambio invalido (amount_received < amount) devuelve 422",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-01", criteria: ["AC-011-02"] });
      const token = await vetToken(request);
      const res = await request.post("/api/v1/payments", {
        headers: authHeader(token),
        data: { appointment_id: 1000, service_id: 17, method: "cash", amount: 15000, amount_received: 5000 },
      });
      expect(res.status()).toBe(422);
    },
  );

  test(
    "@contract APIA-011-C1 AC-011-02 crear OK y C8 detalle 200",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-01", criteria: ["AC-011-02"] });
      const token = await vetToken(request);

      const created = await request.post("/api/v1/payments", {
        headers: authHeader(token),
        data: { appointment_id: 1000, service_id: 17, method: "cash", amount: 15000, amount_received: 20000 },
      });
      expect(created.status()).toBe(201);

      const payment = (await created.json()) as JsonRecord & {
        id: number;
        method: string;
        amount: number;
        amount_received: number;
        change_amount: number;
        status: string;
      };
      expect(payment.amount).toBe(15000);
      expect(payment.amount_received).toBe(20000);
      expect(payment.change_amount).toBe(5000);
      expect(payment.status.toLowerCase()).toBe("paid");

      const detail = await request.get(`/api/v1/payments/${payment.id}`, { headers: authHeader(token) });
      expect(detail.status()).toBe(200);
      const detailBody = (await detail.json()) as JsonRecord & { id: number; status: string };
      expect(detailBody.id).toBe(payment.id);
      expect(detailBody.status.toLowerCase()).toBe("paid");
    },
  );

  test(
    "@contract APIA-011-C9 listado paginado con meta consistente",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-01", criteria: ["AC-011-03"] });
      const token = await vetToken(request);
      const res = await request.get("/api/v1/payments?status_filter=PAID&page=1&page_size=20", {
        headers: authHeader(token),
      });
      expect(res.status()).toBe(200);
      const body = (await res.json()) as { items: unknown[]; meta: { page: number; page_size: number; total: number; pages: number } };
      expect(Array.isArray(body.items)).toBe(true);
      expect(body.meta.page).toBe(1);
      expect(body.meta.page_size).toBe(20);
      expect(body.meta.total).toBeGreaterThanOrEqual(body.items.length);
      expect(body.meta.pages).toBeGreaterThanOrEqual(1);
    },
  );

  test(
    "@contract APIA-011-C12 listado periodo solo pagos dentro del rango",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-01", criteria: ["AC-011-03"] });
      const token = await vetToken(request);
      const res = await request.get(
        "/api/v1/payments?from_date=2000-01-01T00%3A00%3A00Z&to_date=2000-01-02T00%3A00%3A00Z&page=1&page_size=20",
        { headers: authHeader(token) },
      );
      expect(res.status()).toBe(200);
      const body = (await res.json()) as { items: unknown[]; meta: { total: number } };
      expect(body.items).toHaveLength(0);
      expect(body.meta.total).toBe(0);
    },
  );

  test(
    "@contract APIA-011-C10 AC-011-05 cancelar OK y C11 segunda cancelacion 409",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-01", criteria: ["AC-011-05"] });
      const token = await vetToken(request);

      const created = await request.post("/api/v1/payments", {
        headers: authHeader(token),
        data: { appointment_id: 1000, service_id: 17, method: "transfer", amount: 10000 },
      });
      expect(created.status()).toBe(201);
      const paymentId = ((await created.json()) as { id: number }).id;

      const cancelled = await request.post(`/api/v1/payments/${paymentId}/cancel`, {
        headers: authHeader(token),
      });
      expect(cancelled.status()).toBe(200);
      const cancelledBody = (await cancelled.json()) as JsonRecord & { status: string; cancelled_at: string | null };
      expect(cancelledBody.status.toLowerCase()).toBe("cancelled");
      expect(cancelledBody.cancelled_at).toBeTruthy();

      const again = await request.post(`/api/v1/payments/${paymentId}/cancel`, {
        headers: authHeader(token),
      });
      expect(again.status()).toBe(409);
      expect((await again.json())).toBeTruthy();
    },
  );

  test(
    "@contract APIA-011-C7 clinico ajeno no lee pago de otra clinica",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, { slice: "011", userStory: "US-011-04", criteria: ["AC-011-04"] });
      const token = await vetToken(request);
      const created = await request.post("/api/v1/payments", {
        headers: authHeader(token),
        data: { appointment_id: 1000, service_id: 17, method: "transfer", amount: 9000 },
      });
      expect(created.status()).toBe(201);
      const paymentId = ((await created.json()) as { id: number }).id;

      const secondClinicToken = await loginAs(request, "owner-clinic2@invet.com", env.foreignOwnerPassword);
      const res = await request.get(`/api/v1/payments/${paymentId}`, {
        headers: authHeader(secondClinicToken),
      });
      expect([403, 404]).toContain(res.status());
      const body = (await res.json()) as JsonRecord;
      expect(JSON.stringify(body)).not.toMatch(/Traceback|localhost/);
    },
  );
});
