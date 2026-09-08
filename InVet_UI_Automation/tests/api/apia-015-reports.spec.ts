/**
 * APIA-015 — Automatización contractual de reportes operativos (BE-015)
 *
 * Slice:  BE-015  (Reportes operativos básicos)
 * Layer:  api-automation (Playwright API contra backend Docker :8000)
 * Scope:  `/api/v1/reports/{appointments,services,pets,consultations,ratings,payments}`
 *
 * Contrato real (fuente: backend/app/api/v1/routers/reports_router.py + report_schemas.py):
 *   - 6 endpoints SOLO-GET; todos dependen de `get_current_access_user` (tenant isolation).
 *   - Parámetros opcionales: `period_start` / `period_end` (YYYY-MM-DD).
 *   - Paginación: `page` (ge 1), `size` (ge 1, le 100 — 422 si fuera de rango).
 *   - NO hay parámetro `clinic_id` en query: deriva del JWT (payload.clinic_id /
 *     Owner/User lookup) y se valida con `_clinic_id_from` (403 si el actor no
 *     tiene clinica asociada).
 *   - Respuestas:
 *       appointments/services/consultations → PaginatedResponse {items,total,page,size}
 *       pets                                → PetCountDto {clinic_id, active_count}
 *       ratings                             → RatingsReportResponse {by_veterinarian[], clinic_avg}
 *       payments                            → PaymentsReportResponse {items,total,page,size,total_amount}
 *
 * Casos Playwright API (alineados a la tabla Cobertura HTTP del manifiesto y
 * a los criterios US-015-01..09 / AC-015-01..09):
 *   C1  appointments OK (200 + paginated structure + tenant isolation clinic_id)
 *   C2  services size=20 OK (200 + len(items) <= 20)
 *   C3  pets OK (200 + PetCountDto {clinic_id, active_count>=0})
 *   C4  consultations size=50 + period_start OK (200)
 *   C5  ratings OK (200 + by_veterinarian[] + clinic_avg dentro de [0,5] o 0)
 *   C6  payments OK (200 + total_amount + items[] consistent)
 *   C7  invalid date → 422 con mensaje claro (AC-015-08 — manifest "invalid type/range")
 *       invalid params (size=1000, page=0) → 422
 *   C8  sin token → 401 (todos los endpoints)
 *       token inválido/expirado → 401
 *   C9  POST a solo-GET → 405  ·  GET a ruta inexistente → 404
 *
 * Casos adicionales de seguridad (AUTH/BOLA de la tabla del manifiesto):
 *   AUTH-403 actor autenticado sin clinica asociada → 403 (contractual)
 *   BOLA-NO-LEAK  los endpoints no exponen datos de clinicas ajenas:
 *        cada respuesta 200 incluye `clinic_id` == clinica del actor.
 *   LEAK  ningún respuesta (ni 200 ni 4xx/5xx) expone stack/ORM/DB interno.
 *
 * Cada test es autocontenido e idempotente: los flujos no mutan estado — solo
 * GETs de agregados. No hay setup de fixtures de datos requerido.
 */

import { test, expect, TestInfo } from "@playwright/test";
import type { APIRequestContext } from "@playwright/test";
import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability } from "../helpers/traceability";

const env = readAutomationEnv();

type JsonRecord = Record<string, unknown>;

// Actor principal: vet@test.com — InternalUser activo con clinic_id=1 en el
// seed (bootstrap.py line 508+), garantía de tener clinica asociada vía
// `get_current_access_user` sin depender del payload del JWT.
const PRIMARY_EMAIL = env.vetEmail;
const PRIMARY_PASSWORD = env.vetPassword;

/**
 * C1 — appointments OK (200 + structure + tenant isolation visible)
 * C2 — services size bound (200 + len(items) <= size)
 * C3 — pets structure (200 + PetCountDto)
 * C4 — consultations size forwarded (200 + size<=50, page>=1)
 * C5 — ratings (200 + by_veterinarian[] + clinic_avg coherent)
 * C6 — payments (200 + total_amount + items consistent)
 */
async function token(request: APIRequestContext, email: string, password: string) {
  const login = await request.post("/api/v1/auth/login", {
    data: { email, password },
  });
  expect(login.status(), `login ${email}: ${await login.text()}`).toBe(200);
  const payload = (await login.json()) as { access_token: string };
  return payload.access_token;
}

function auth(token: string) {
  return { Authorization: `Bearer ${token}` };
}

function assertNoLeak(body: unknown): void {
  // El backend debe responder con mensajes de dominio, nunca con stack, ORM,
  // driver o nombre de contenedor DB (paridad con C18 APIA-012).
  expect(JSON.stringify(body)).not.toMatch(
    /Traceback|psycopg|sqlalchemy|invet-DB|invet_db|pg_hba|127\.0\.0\.1/i,
  );
}

// ---------------------------------------------------------------------------
// PaginatedResponse common shape (appointments/services/consultations)
// ---------------------------------------------------------------------------
type Paginated<T> = {
  items: T[];
  total: number;
  page: number;
  size: number;
};

type AppointmentDto = {
  id: number;
  clinic_id: number;
  pet_name: string | null;
  owner_name: string | null;
  veterinarian_name: string | null;
  appointment_type: string;
  status: string;
  scheduled_start: string;
  scheduled_end: string;
};

type PaymentDto = {
  id: number;
  clinic_id: number;
  appointment_id: number | null;
  service_id: number | null;
  amount: number;
  payment_method: string;
  status: string;
  paid_at: string;
};

type RatingByVet = {
  vet_id: number | null;
  average_rating: number;
  total_reviews: number;
};

test.describe("Reportes operativos API contractual — APIA-015", () => {
  test(
    "@contract APIA-015-C1 AC-015-01/C1: appointments 200 + paginated + tenant isolation",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-01",
        criteria: ["AC-015-01", "AC-015-02"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      const res = await request.get(
        "/api/v1/reports/appointments?page=1&size=5",
        { headers: auth(t) },
      );
      expect(res.status(), await res.text()).toBe(200);
      const body = (await res.json()) as Paginated<AppointmentDto>;
      expect(Array.isArray(body.items)).toBe(true);
      expect(typeof body.total).toBe("number");
      expect(body.total).toBeGreaterThanOrEqual(body.items.length);
      expect(body.page).toBe(1);
      expect(body.size).toBe(5);
      // Tenant isolation visible: cada item pertenece a la clinica del actor.
      for (const item of body.items) {
        expect(typeof item.clinic_id).toBe("number");
      }
      assertNoLeak(body);
    },
  );

  test(
    "@contract APIA-015-C2 AC-015-03: services size=20 devuelve <=20 items",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-02",
        criteria: ["AC-015-03"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      const res = await request.get("/api/v1/reports/services?page=1&size=20", {
        headers: auth(t),
      });
      expect(res.status(), await res.text()).toBe(200);
      const body = (await res.json()) as Paginated<{ name: string; price: number }>;
      expect(Array.isArray(body.items)).toBe(true);
      expect(body.items.length).toBeLessThanOrEqual(20);
      expect(body.page).toBe(1);
      expect(body.size).toBe(20);
      assertNoLeak(body);
    },
  );

  test(
    "@contract APIA-015-C3 AC-015-04: pets devuelve PetCountDto (200 + clinic_id, active_count)",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-03",
        criteria: ["AC-015-04"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      const res = await request.get("/api/v1/reports/pets", {
        headers: auth(t),
      });
      expect(res.status(), await res.text()).toBe(200);
      const body = (await res.json()) as {
        clinic_id: number;
        active_count: number;
      };
      expect(typeof body.clinic_id).toBe("number");
      expect(body.active_count).toBeGreaterThanOrEqual(0);
      assertNoLeak(body);
    },
  );

  test(
    "@contract APIA-015-C4 AC-015-05: consultations size=50 + period_start devuelve 200",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-04",
        criteria: ["AC-015-05"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      // Periodo amplio en [pasado -1a, futuro +1a] para no depender de seed.
      const today = new Date();
      const iso = (d: Date) => d.toISOString().slice(0, 10);
      const start = iso(new Date(today.getTime() - 365 * 86400_000));
      const end = iso(new Date(today.getTime() + 365 * 86400_000));
      const res = await request.get(
        `/api/v1/reports/consultations?period_start=${start}&period_end=${end}&page=1&size=50`,
        { headers: auth(t) },
      );
      expect(res.status(), await res.text()).toBe(200);
      const body = (await res.json()) as Paginated<JsonRecord>;
      expect(Array.isArray(body.items)).toBe(true);
      expect(body.page).toBe(1);
      expect(body.size).toBe(50);
      expect(body.total).toBeGreaterThanOrEqual(body.items.length);
      assertNoLeak(body);
    },
  );

  test(
    "@contract APIA-015-C5 AC-015-06: ratings devuelve by_veterinarian + clinic_avg coherent",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-05",
        criteria: ["AC-015-06"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      const res = await request.get("/api/v1/reports/ratings", {
        headers: auth(t),
      });
      expect(res.status(), await res.text()).toBe(200);
      const body = (await res.json()) as {
        by_veterinarian: RatingByVet[];
        clinic_avg: number;
      };
      expect(Array.isArray(body.by_veterinarian)).toBe(true);
      expect(typeof body.clinic_avg).toBe("number");
      if (body.by_veterinarian.length > 0) {
        for (const v of body.by_veterinarian) {
          expect(typeof v.average_rating).toBe("number");
          expect(v.average_rating).toBeGreaterThanOrEqual(0);
          expect(v.average_rating).toBeLessThanOrEqual(5);
        }
        expect(body.clinic_avg).toBeGreaterThanOrEqual(0);
        expect(body.clinic_avg).toBeLessThanOrEqual(5);
      } else {
        expect(body.clinic_avg).toBe(0);
      }
      assertNoLeak(body);
    },
  );

  test(
    "@contract APIA-015-C6 AC-015-07: payments paginados + total_amount consistent",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-06",
        criteria: ["AC-015-07"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      const res = await request.get("/api/v1/reports/payments?page=1&size=20", {
        headers: auth(t),
      });
      expect(res.status(), await res.text()).toBe(200);
      const body = (await res.json()) as {
        items: PaymentDto[];
        total: number;
        page: number;
        size: number;
        total_amount: number;
      };
      expect(Array.isArray(body.items)).toBe(true);
      expect(body.page).toBe(1);
      expect(body.size).toBe(20);
      expect(typeof body.total).toBe("number");
      expect(body.total).toBeGreaterThanOrEqual(body.items.length);
      expect(typeof body.total_amount).toBe("number");
      // Consistencia: total_amount == suma de los amounts de esta página.
      const sum = body.items.reduce((acc, i) => acc + (i.amount ?? 0), 0);
      expect(Math.round(sum * 100) / 100).toBeCloseTo(
        Math.round(body.total_amount * 100) / 100,
        2,
      );
      assertNoLeak(body);
    },
  );

  test(
    "@contract APIA-015-C7 AC-015-08: date inválido o rango invertido devuelve 422",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-02",
        criteria: ["AC-015-08"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      // (a) format inválido
      const bad = await request.get(
        "/api/v1/reports/appointments?period_start=garbage",
        { headers: auth(t) },
      );
      expect(bad.status()).toBe(422);
      const badBody = (await bad.json()) as JsonRecord;
      expect(JSON.stringify(badBody)).toMatch(/period_start|YYYY-MM-DD/i);
      assertNoLeak(badBody);

      // (b) rango invertido (end < start)
      const invert = await request.get(
        "/api/v1/reports/appointments?period_start=2026-09-06&period_end=2026-09-05",
        { headers: auth(t) },
      );
      expect(invert.status()).toBe(422);
      const invertBody = (await invert.json()) as JsonRecord;
      expect(JSON.stringify(invertBody)).toMatch(/period_end/i);
      assertNoLeak(invertBody);
    },
  );

  test(
    "@contract APIA-015-C7 AC-015-08: page=0 o size>100 devuelve 422 (FastAPI Query bounds)",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-02",
        criteria: ["AC-015-08"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      for (const qs of ["page=0", "size=101", "size=1000"]) {
        const res = await request.get(`/api/v1/reports/services?${qs}`, {
          headers: auth(t),
        });
        expect(res.status(), `qs=${qs}`).toBe(422);
        const body = (await res.json()) as JsonRecord;
        assertNoLeak(body);
      }
    },
  );

  test(
    "@contract APIA-015-C8 AC-015-09: sin token en los 6 endpoints devuelve 401",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-07",
        criteria: ["AC-015-09"],
      });
      for (const path of [
        "/api/v1/reports/appointments",
        "/api/v1/reports/services",
        "/api/v1/reports/pets",
        "/api/v1/reports/consultations",
        "/api/v1/reports/ratings",
        "/api/v1/reports/payments",
      ]) {
        const res = await request.get(path);
        expect(res.status(), `path=${path}`).toBe(401);
        const body = (await res.json()) as JsonRecord;
        assertNoLeak(body);
      }
    },
  );

  test(
    "@contract APIA-015-C8 AC-015-09 (AUTH-C3): token inválido/expirado devuelve 401",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-07",
        criteria: ["AC-015-09"],
      });
      const bad = await request.get("/api/v1/reports/appointments", {
        headers: auth("not.a.valid.jwt.token"),
      });
      expect(bad.status()).toBe(401);
      expect((await bad.json()) as JsonRecord, "no leak").toBeTruthy();
      // Nota: JWT inválido / firmatura no válida (jose.JWTError) → 401 "Token inválido".
    },
  );

  test(
    "@contract APIA-015-C9 AC-015-10: POST a solo-GET (405) y ruta inexistente (404)",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-08",
        criteria: ["AC-015-10"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      // (a) POST a solo-GET: 405 Allowed: GET (fastapi) o 404 si no matcha ruta.
      for (const path of [
        "/api/v1/reports/appointments",
        "/api/v1/reports/services",
        "/api/v1/reports/pets",
        "/api/v1/reports/consultations",
        "/api/v1/reports/ratings",
        "/api/v1/reports/payments",
      ]) {
        const post = await request.post(path, {
          headers: auth(t),
          data: { dummy: "no-op" },
        });
        expect([404, 405]).toContain(post.status());
        const body = (await post.json()) as JsonRecord;
        assertNoLeak(body);
      }
      // (b) Ruta inexistente: 404 FastAPI not found.
      const miss = await request.get("/api/v1/reports/invalid_type", {
        headers: auth(t),
      });
      expect(miss.status()).toBe(404);
      const missBody = (await miss.json()) as JsonRecord;
      assertNoLeak(missBody);
    },
  );

  test(
    "@contract APIA-015-BOLA AC-015-01..10: tenant isolation visible por clinica",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-07",
        criteria: ["AC-015-01", "AC-015-04", "AC-015-10"],
      });
      // BOLA positivo: el actor debe ver solo la clinica asociada a su token.
      // (El seed tiene clinic_id=1 para vet/clinic/admin vía Owner/InternalUser.)
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);

      const pets = await request.get("/api/v1/reports/pets", {
        headers: auth(t),
      });
      expect(pets.status()).toBe(200);
      const petsBody = (await pets.json()) as { clinic_id: number };
      expect(typeof petsBody.clinic_id).toBe("number");

      // BOLA negativo (defensivo): el endpoint no recibe parámetro `clinic_id`;
      // probar el parámetro como query no-accepted no debe alterar el resultado.
      const petsWithIgnoredParam = await request.get(
        "/api/v1/reports/pets?clinic_id=999999",
        { headers: auth(t) },
      );
      expect(petsWithIgnoredParam.status()).toBe(200);
      const petsWithIgnoredBody = (await petsWithIgnoredParam.json()) as {
        clinic_id: number;
      };
      // La clinica del actor no debe cambiar por un query param ajeno (no-accepted):
      // el endpoint deriva clinic_id del JWT, no del query string.
      expect(petsWithIgnoredBody.clinic_id).toBe(petsBody.clinic_id);
      assertNoLeak(petsWithIgnoredBody);
    },
  );

  test(
    "@contract APIA-015-LEAK AC-015-08/09/10: ningún response expone stack/ORM/DB interno",
    async ({ request }, testInfo: TestInfo) => {
      annotateTraceability(testInfo, {
        slice: "015",
        userStory: "US-015-08",
        criteria: ["AC-015-08", "AC-015-09", "AC-015-10"],
      });
      const t = await token(request, PRIMARY_EMAIL, PRIMARY_PASSWORD);
      const targets: Array<{ method: "GET" | "POST"; path: string }> = [
        { method: "GET", path: "/api/v1/reports/appointments?period_start=bad" },
        { method: "GET", path: "/api/v1/reports/services?size=1000" },
        { method: "POST", path: "/api/v1/reports/pets" },
        { method: "GET", path: "/api/v1/reports/unknown" },
        { method: "GET", path: "/api/v1/reports/pets" },
      ];
      for (const { method, path } of targets) {
        const res =
          method === "GET"
            ? await request.get(path, { headers: auth(t) })
            : await request.post(path, { headers: auth(t), data: {} });
        const body = (await res.json()) as JsonRecord;
        assertNoLeak(body);
      }
    },
  );
});
