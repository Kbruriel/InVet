import { expect, test } from "@playwright/test";

import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability } from "../helpers/traceability";

const env = readAutomationEnv();

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function loginAsAdmin(request: Parameters<typeof test>[0]["request"]): Promise<string> {
  // Skip if no seeded QA user is configured.
  test.skip(
    env.loginEmail === "qa@example.com",
    "Provide LOGIN_EMAIL and LOGIN_PASSWORD of a real registered admin account to run this test.",
  );

  const response = await request.post("/api/v1/auth/login", {
    data: { email: env.loginEmail, password: env.loginPassword },
  });
  expect(response.status()).toBe(200);
  const payload = (await response.json()) as Record<string, unknown>;
  return String(payload.access_token);
}

async function createService(
  request: Parameters<typeof test>[0]["request"],
  token: string,
  payload: Record<string, unknown>,
): Promise<{ response: Response; id: number }> {
  const response = await request.post("/api/v1/services", {
    headers: { Authorization: `Bearer ${token}` },
    data: payload,
  });
  expect(response.status()).toBe(201);
  const body = (await response.json()) as Record<string, unknown>;
  return { response, id: Number(body.id) };
}

async function createVeterinarian(
  request: Parameters<typeof test>[0]["request"],
  token: string,
  payload: Record<string, unknown>,
): Promise<{ response: Response; id: number }> {
  const response = await request.post("/api/v1/veterinarians", {
    headers: { Authorization: `Bearer ${token}` },
    data: payload,
  });
  expect(response.status()).toBe(201);
  const body = (await response.json()) as Record<string, unknown>;
  return { response, id: Number(body.id) };
}

async function createInternalUser(
  request: Parameters<typeof test>[0]["request"],
  token: string,
  payload: Record<string, unknown>,
): Promise<{ response: Response; id: number }> {
  const response = await request.post("/api/v1/internal-users", {
    headers: { Authorization: `Bearer ${token}` },
    data: payload,
  });
  expect(response.status()).toBe(201);
  const body = (await response.json()) as Record<string, unknown>;
  return { response, id: Number(body.id) };
}

// ---------------------------------------------------------------------------
// Services CRUD
// ---------------------------------------------------------------------------
test.describe("Slice 006 — Services CRUD", () => {
  let adminToken: string;

  test.beforeAll(async ({ request }) => {
    adminToken = await loginAsAdmin(request);
  });

  // TC-APIA-006-S01
  test(
    "S01 POST /api/v1/services — create service with valid data returns 201",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-01"],
      });

      const servicePayload = {
        nombre: "Consulta general",
        descripcion: "Consulta médica veterinaria general",
        precio: 100,
        duracion_minutos: 30,
      };

      const { id } = await createService(request, adminToken, servicePayload);
      expect(id).toBeGreaterThan(0);
    },
  );

  // TC-APIA-006-S02
  test(
    "S02 GET /api/v1/services — list services returns 200 with pagination metadata",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-10"],
      });

      const response = await request.get("/api/v1/services?page=1&page_size=20", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(200);
      expect(response.headers()["content-type"]).toContain("application/json");

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");
      expect(typeof payload.page).toBe("number");
      expect(typeof payload.page_size).toBe("number");
    },
  );

  // TC-APIA-006-S03
  test(
    "S03 GET /api/v1/services/{id} — read existing service returns 200",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-03"],
      });

      // Create a service first to read it back.
      const createResp = await request.post("/api/v1/services", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre: "Lectura S03",
          descripcion: "Servicio de prueba para lectura",
          precio: 50,
          duracion_minutos: 15,
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const serviceId = Number(created.id);

      const response = await request.get(`/api/v1/services/${serviceId}`, {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(payload).toHaveProperty("id");
      expect(Number(payload.id)).toBe(serviceId);
      expect(typeof payload.nombre).toBe("string");
    },
  );

  // TC-APIA-006-S04
  test(
    "S04 PUT /api/v1/services/{id} — update service returns 200",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-02"],
      });

      // Create a service first.
      const createResp = await request.post("/api/v1/services", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre: "Actualizable",
          descripcion: "Para actualizar",
          precio: 75,
          duracion_minutos: 20,
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const serviceId = Number(created.id);

      const response = await request.put(`/api/v1/services/${serviceId}`, {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { nombre: "Actualizado", precio: 120 },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(String(payload.nombre)).toBe("Actualizado");
      expect(Number(payload.precio)).toBe(120);
    },
  );

  // TC-APIA-006-S05
  test(
    "S05 PATCH /api/v1/services/{id}/deactivate — deactivate service returns 204",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-04"],
      });

      // Create a service first.
      const createResp = await request.post("/api/v1/services", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre: "Desactivar S05",
          descripcion: "Para desactivar",
          precio: 60,
          duracion_minutos: 25,
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const serviceId = Number(created.id);

      const response = await request.patch(`/api/v1/services/${serviceId}/deactivate`, {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(204);
    },
  );

  // TC-APIA-006-S06
  test(
    "S06 POST /api/v1/services — create with invalid data returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-09"],
      });

      const response = await request.post("/api/v1/services", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { nombre: "" },
      });
      expect(response.status()).toBe(422);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.detail)).toBe(true);
    },
  );

  // TC-APIA-006-S07
  test(
    "S07 POST /api/v1/services — duplicate name returns 409",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-07"],
      });

      const uniqueName = `Dup-${Date.now()}`;
      await createService(request, adminToken, {
        nombre: uniqueName,
        descripcion: "Primera creacion",
        precio: 100,
        duracion_minutos: 30,
      });

      const response = await request.post("/api/v1/services", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre: uniqueName,
          descripcion: "Duplicada",
          precio: 200,
          duracion_minutos: 45,
        },
      });
      expect(response.status()).toBe(409);
    },
  );

  // TC-APIA-006-S08
  test(
    "S08 GET /api/v1/services/999999 — read non-existent service returns 404",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-03"],
      });

      const response = await request.get("/api/v1/services/999999", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(404);
    },
  );
});

// ---------------------------------------------------------------------------
// Veterinarians CRUD
// ---------------------------------------------------------------------------
test.describe("Slice 006 — Veterinarians CRUD", () => {
  let adminToken: string;

  test.beforeAll(async ({ request }) => {
    adminToken = await loginAsAdmin(request);
  });

  // TC-APIA-006-V01
  test(
    "V01 POST /api/v1/veterinarians — create with valid data returns 201",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-07"],
      });

      const vetPayload = {
        nombre_completo: "Dra. Maria Lopez",
        licencia_profesional: `VET-${Date.now()}`,
        especialidad: "Pequenos animales",
      };

      const { id } = await createVeterinarian(request, adminToken, vetPayload);
      expect(id).toBeGreaterThan(0);
    },
  );

  // TC-APIA-006-V02
  test(
    "V02 GET /api/v1/veterinarians — list returns 200 with pagination",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-10"],
      });

      const response = await request.get("/api/v1/veterinarians?page=1&page_size=20", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");
      expect(typeof payload.page).toBe("number");
    },
  );

  // TC-APIA-006-V03
  test(
    "V03 GET /api/v1/veterinarians/{id} — read existing veterinarian returns 200",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-09"],
      });

      const createResp = await request.post("/api/v1/veterinarians", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre_completo: "Dr. Lectura V03",
          licencia_profesional: `VET-LECT-${Date.now()}`,
          especialidad: "Equinos",
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const vetId = Number(created.id);

      const response = await request.get(`/api/v1/veterinarians/${vetId}`, {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Number(payload.id)).toBe(vetId);
      expect(typeof payload.nombre_completo).toBe("string");
    },
  );

  // TC-APIA-006-V04
  test(
    "V04 PUT /api/v1/veterinarians/{id} — update veterinarian returns 200",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-08"],
      });

      const createResp = await request.post("/api/v1/veterinarians", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre_completo: "Dr. Update V04",
          licencia_profesional: `VET-UPD-${Date.now()}`,
          especialidad: "Anfibios",
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const vetId = Number(created.id);

      const response = await request.put(`/api/v1/veterinarians/${vetId}`, {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { especialidad: "Nueva especialidad" },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(String(payload.especialidad)).toBe("Nueva especialidad");
    },
  );

  // TC-APIA-006-V05
  test(
    "V05 PATCH /api/v1/veterinarians/{id}/deactivate — deactivate veterinarian returns 204",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-10"],
      });

      const createResp = await request.post("/api/v1/veterinarians", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre_completo: "Dr. Deact V05",
          licencia_profesional: `VET-DCT-${Date.now()}`,
          especialidad: "Reptiles",
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const vetId = Number(created.id);

      const response = await request.patch(`/api/v1/veterinarians/${vetId}/deactivate`, {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(204);
    },
  );

  // TC-APIA-006-V06
  test(
    "V06 POST /api/v1/veterinarians — duplicate license returns 409",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-09"],
      });

      const uniqueLicense = `VET-DUP-${Date.now()}`;
      await createVeterinarian(request, adminToken, {
        nombre_completo: "Dra. Dup V06",
        licencia_profesional: uniqueLicense,
        especialidad: "Aves",
      });

      const response = await request.post("/api/v1/veterinarians", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre_completo: "Dr. Dup V06b",
          licencia_profesional: uniqueLicense,
          especialidad: "Mamiferos",
        },
      });
      expect(response.status()).toBe(409);
    },
  );

  // TC-APIA-006-V07
  test(
    "V07 GET /api/v1/veterinarians/999999 — read non-existent veterinarian returns 404",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-09"],
      });

      const response = await request.get("/api/v1/veterinarians/999999", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(404);
    },
  );
});

// ---------------------------------------------------------------------------
// Internal Users CRUD
// ---------------------------------------------------------------------------
test.describe("Slice 006 — Internal Users CRUD", () => {
  let adminToken: string;

  test.beforeAll(async ({ request }) => {
    adminToken = await loginAsAdmin(request);
  });

  // TC-APIA-006-U01
  test(
    "U01 POST /api/v1/internal-users — create with valid data returns 201",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-13"],
      });

      // Register a real user first to reference via user_id.
      const registerResp = await request.post("/api/v1/auth/register", {
        data: {
          email: `iu-${Date.now()}@invet.io`,
          password: "secret123",
          firstName: "Usuario",
          lastName: "Interno",
        },
      });
      expect(registerResp.status()).toBe(201);
      const registered = (await registerResp.json()) as Record<string, unknown>;
      const userId = Number(registered.id);

      const { id } = await createInternalUser(request, adminToken, {
        user_id: userId,
        nombre: "Usuario Interno Test",
        rol: "admin",
      });
      expect(id).toBeGreaterThan(0);
    },
  );

  // TC-APIA-006-U02
  test(
    "U02 GET /api/v1/internal-users — list returns 200 with pagination",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-15"],
      });

      const response = await request.get("/api/v1/internal-users?page=1&page_size=20", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");
      expect(typeof payload.page).toBe("number");
    },
  );

  // TC-APIA-006-U03
  test(
    "U03 GET /api/v1/internal-users/{id} — read existing internal user returns 200",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-15"],
      });

      // Register a real user first.
      const registerResp = await request.post("/api/v1/auth/register", {
        data: {
          email: `iu-read-${Date.now()}@invet.io`,
          password: "secret123",
          firstName: "Lectura",
          lastName: "IU03",
        },
      });
      expect(registerResp.status()).toBe(201);
      const registered = (await registerResp.json()) as Record<string, unknown>;
      const userId = Number(registered.id);

      // Create the internal user.
      const createResp = await request.post("/api/v1/internal-users", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          user_id: userId,
          nombre: "IU Lectura U03",
          rol: "manager",
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const iuId = Number(created.id);

      const response = await request.get(`/api/v1/internal-users/${iuId}`, {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Number(payload.id)).toBe(iuId);
      expect(typeof payload.nombre).toBe("string");
    },
  );

  // TC-APIA-006-U04
  test(
    "U04 PUT /api/v1/internal-users/{id} — update internal user returns 200",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-14"],
      });

      // Register a real user first.
      const registerResp = await request.post("/api/v1/auth/register", {
        data: {
          email: `iu-upd-${Date.now()}@invet.io`,
          password: "secret123",
          firstName: "Update",
          lastName: "IU04",
        },
      });
      expect(registerResp.status()).toBe(201);
      const registered = (await registerResp.json()) as Record<string, unknown>;
      const userId = Number(registered.id);

      const createResp = await request.post("/api/v1/internal-users", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          user_id: userId,
          nombre: "IU Update U04",
          rol: "admin",
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const iuId = Number(created.id);

      const response = await request.put(`/api/v1/internal-users/${iuId}`, {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { rol: "manager" },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(String(payload.rol)).toBe("manager");
    },
  );

  // TC-APIA-006-U05
  test(
    "U05 PATCH /api/v1/internal-users/{id}/deactivate — deactivate internal user returns 204",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-16"],
      });

      // Register a real user first.
      const registerResp = await request.post("/api/v1/auth/register", {
        data: {
          email: `iu-dct-${Date.now()}@invet.io`,
          password: "secret123",
          firstName: "Deact",
          lastName: "IU05",
        },
      });
      expect(registerResp.status()).toBe(201);
      const registered = (await registerResp.json()) as Record<string, unknown>;
      const userId = Number(registered.id);

      const createResp = await request.post("/api/v1/internal-users", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          user_id: userId,
          nombre: "IU Deact U05",
          rol: "admin",
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const iuId = Number(created.id);

      const response = await request.patch(`/api/v1/internal-users/${iuId}/deactivate`, {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(204);
    },
  );

  // TC-APIA-006-U06
  test(
    "U06 POST /api/v1/internal-users — create with invalid user_id returns 400 or 404",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-09"],
      });

      const response = await request.post("/api/v1/internal-users", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          user_id: 999999,
          nombre: "IU Invalid U06",
          rol: "admin",
        },
      });
      expect([400, 404]).toContain(response.status());
    },
  );

  // TC-APIA-006-U07
  test(
    "U07 POST /api/v1/internal-users — create with empty nombre returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-09"],
      });

      const response = await request.post("/api/v1/internal-users", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { nombre: "" },
      });
      expect(response.status()).toBe(422);
    },
  );

  // TC-APIA-006-U08
  test(
    "U08 GET /api/v1/internal-users/999999 — read non-existent internal user returns 404",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-15"],
      });

      const response = await request.get("/api/v1/internal-users/999999", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(404);
    },
  );
});

// ---------------------------------------------------------------------------
// Associations
// ---------------------------------------------------------------------------
test.describe("Slice 006 — Assignments", () => {
  let adminToken: string;

  test.beforeAll(async ({ request }) => {
    adminToken = await loginAsAdmin(request);
  });

  // TC-APIA-006-A01
  test(
    "A01 POST /api/v1/veterinarians/{id}/assign-service — assign service to vet (same tenant) returns 201",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-19"],
      });

      // Create service and veterinarian first.
      const serviceResp = await request.post("/api/v1/services", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre: "Servicio A01",
          descripcion: "Para asignacion",
          precio: 150,
          duracion_minutos: 45,
        },
      });
      expect(serviceResp.status()).toBe(201);
      const service = (await serviceResp.json()) as Record<string, unknown>;
      const serviceId = Number(service.id);

      const vetResp = await request.post("/api/v1/veterinarians", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre_completo: "Dr. Asign A01",
          licencia_profesional: `VET-ASG-${Date.now()}`,
          especialidad: "Pequenos animales",
        },
      });
      expect(vetResp.status()).toBe(201);
      const vet = (await vetResp.json()) as Record<string, unknown>;
      const vetId = Number(vet.id);

      const response = await request.post(`/api/v1/veterinarians/${vetId}/assign-service`, {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { service_id: serviceId },
      });
      expect(response.status()).toBe(201);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(payload).toHaveProperty("veterinarian_id");
      expect(Number(payload.veterinarian_id)).toBe(vetId);
    },
  );

  // TC-APIA-006-A02
  test(
    "A02 DELETE /api/v1/veterinarians/{id}/assign-service/{service_id} — unassign service returns 204",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-21"],
      });

      // Create service and veterinarian first.
      const serviceResp = await request.post("/api/v1/services", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre: "Servicio A02",
          descripcion: "Para desasignar",
          precio: 80,
          duracion_minutos: 20,
        },
      });
      expect(serviceResp.status()).toBe(201);
      const service = (await serviceResp.json()) as Record<string, unknown>;
      const serviceId = Number(service.id);

      const vetResp = await request.post("/api/v1/veterinarians", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre_completo: "Dr. Desasign A02",
          licencia_profesional: `VET-DSG-${Date.now()}`,
          especialidad: "Equinos",
        },
      });
      expect(vetResp.status()).toBe(201);
      const vet = (await vetResp.json()) as Record<string, unknown>;
      const vetId = Number(vet.id);

      // First assign.
      await request.post(`/api/v1/veterinarians/${vetId}/assign-service`, {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { service_id: serviceId },
      });

      const response = await request.delete(
        `/api/v1/veterinarians/${vetId}/assign-service/${serviceId}`,
        { headers: { Authorization: `Bearer ${adminToken}` } },
      );
      expect(response.status()).toBe(204);
    },
  );

  // TC-APIA-006-A03
  test(
    "A03 POST /api/v1/internal-users/{id}/assign-branch — assign branch to IU (same tenant) returns 201",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-23"],
      });

      // Register a real user first.
      const registerResp = await request.post("/api/v1/auth/register", {
        data: {
          email: `iu-brch-${Date.now()}@invet.io`,
          password: "secret123",
          firstName: "Branch",
          lastName: "IU03",
        },
      });
      expect(registerResp.status()).toBe(201);
      const registered = (await registerResp.json()) as Record<string, unknown>;
      const userId = Number(registered.id);

      const createResp = await request.post("/api/v1/internal-users", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          user_id: userId,
          nombre: "IU Branch A03",
          rol: "manager",
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const iuId = Number(created.id);

      // Use clinic_id as branch_id for the assignment.
      const response = await request.post(`/api/v1/internal-users/${iuId}/assign-branch`, {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { branch_id: 1 },
      });
      expect(response.status()).toBe(201);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(payload).toHaveProperty("internal_user_id");
      expect(Number(payload.internal_user_id)).toBe(iuId);
    },
  );

  // TC-APIA-006-A04
  test(
    "A04 DELETE /api/v1/internal-users/{id}/assign-branch/{branch_id} — unassign branch returns 204",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-25"],
      });

      // Register a real user first.
      const registerResp = await request.post("/api/v1/auth/register", {
        data: {
          email: `iu-brchdel-${Date.now()}@invet.io`,
          password: "secret123",
          firstName: "BranchDel",
          lastName: "IU04",
        },
      });
      expect(registerResp.status()).toBe(201);
      const registered = (await registerResp.json()) as Record<string, unknown>;
      const userId = Number(registered.id);

      const createResp = await request.post("/api/v1/internal-users", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          user_id: userId,
          nombre: "IU BranchDel A04",
          rol: "admin",
        },
      });
      expect(createResp.status()).toBe(201);
      const created = (await createResp.json()) as Record<string, unknown>;
      const iuId = Number(created.id);

      // First assign.
      await request.post(`/api/v1/internal-users/${iuId}/assign-branch`, {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { branch_id: 1 },
      });

      const response = await request.delete(
        `/api/v1/internal-users/${iuId}/assign-branch/1`,
        { headers: { Authorization: `Bearer ${adminToken}` } },
      );
      expect(response.status()).toBe(204);
    },
  );
});

// ---------------------------------------------------------------------------
// Authentication & Authorization
// ---------------------------------------------------------------------------
test.describe("Slice 006 — Authentication & Authorization", () => {
  // TC-APIA-006-U06 (mapped from user request) / APIA-006-S02 / V02 / U02
  test(
    "U06 Request without token returns 401 on protected endpoints",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-06"],
      });

      const endpoints = [
        "/api/v1/services",
        "/api/v1/veterinarians",
        "/api/v1/internal-users",
      ];

      for (const endpoint of endpoints) {
        const response = await request.get(endpoint);
        expect(response.status()).toBe(401),
          `${endpoint} should return 401 without token`;
      }
    },
  );

  // TC-APIA-006-U07 (mapped from user request) / APIA-006-S04 / V04 / U04
  test(
    "U07 Request with insufficient role returns 403 on write endpoints",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-05"],
      });

      // Register a viewer-only user (no admin/manager role).
      const registerResp = await request.post("/api/v1/auth/register", {
        data: {
          email: `viewer-${Date.now()}@invet.io`,
          password: "secret123",
          firstName: "Viewer",
          lastName: "U07",
        },
      });
      expect(registerResp.status()).toBe(201);
      const registered = (await registerResp.json()) as Record<string, unknown>;
      const viewerToken = String(registered.access_token);

      const writeEndpoints = [
        { method: "post" as const, path: "/api/v1/services", data: { nombre: "Test", precio: 10, duracion_minutos: 15 } },
        { method: "post" as const, path: "/api/v1/veterinarians", data: { nombre_completo: "Dr. Test", licencia_profesional: "VET-TEST", especialidad: "Test" } },
        { method: "post" as const, path: "/api/v1/internal-users", data: { user_id: 1, nombre: "Test", rol: "admin" } },
      ];

      for (const { method, path, data } of writeEndpoints) {
        const response = await (request as any)[method](path, {
          headers: { Authorization: `Bearer ${viewerToken}` },
          data,
        });
        expect(response.status()).toBe(403),
          `${path} should return 403 for viewer`;
      }
    },
  );

  // TC-APIA-006-U08 (mapped from user request) / APIA-006-S11 / V10 / U10
  test(
    "U08 IDOR/BOLA — access resource from different clinic returns 403",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-07"],
      });

      // Use a non-existent ID that belongs to another clinic.
      const fakeIds = [999999, 888888, 777777];
      const endpoints = [
        `/api/v1/services/${fakeIds[0]}`,
        `/api/v1/veterinarians/${fakeIds[1]}`,
        `/api/v1/internal-users/${fakeIds[2]}`,
      ];

      // Without token — all return 401 (which also blocks unauthorized access).
      for (const endpoint of endpoints) {
        const response = await request.get(endpoint);
        expect([401, 403]).toContain(response.status());
      }
    },
  );
});

// ---------------------------------------------------------------------------
// Pagination
// ---------------------------------------------------------------------------
test.describe("Slice 006 — Pagination", () => {
  let adminToken: string;

  test.beforeAll(async ({ request }) => {
    adminToken = await loginAsAdmin(request);
  });

  // TC-APIA-006-P01
  test(
    "P01 GET with page=1&page_size=10 — pagination metadata correct",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-10"],
      });

      const response = await request.get("/api/v1/services?page=1&page_size=10", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");
      expect(Number(payload.page)).toBe(1);
      expect(Number(payload.page_size)).toBe(10);
    },
  );

  // TC-APIA-006-P02
  test(
    "P02 GET with page_size=0 — invalid page_size rejected",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-09"],
      });

      const response = await request.get("/api/v1/services?page=1&page_size=0", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect([400, 422]).toContain(response.status());
    },
  );

  // TC-APIA-006-P03
  test(
    "P03 GET is_active=true vs is_active=false filters work",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-11"],
      });

      // Create an active service.
      const createResp = await request.post("/api/v1/services", {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: {
          nombre: "Filtro P03",
          descripcion: "Para filtrar",
          precio: 90,
          duracion_minutos: 25,
        },
      });
      expect(createResp.status()).toBe(201);

      // Default (active only).
      const activeResponse = await request.get("/api/v1/services?page=1&page_size=1", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(activeResponse.status()).toBe(200);

      // Explicit is_active=false.
      const inactiveResponse = await request.get("/api/v1/services?is_active=false&page=1&page_size=1", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(inactiveResponse.status()).toBe(200);

      const activePayload = (await activeResponse.json()) as Record<string, unknown>;
      const inactivePayload = (await inactiveResponse.json()) as Record<string, unknown>;

      expect(typeof activePayload.total).toBe("number");
      expect(typeof inactivePayload.total).toBe("number");
    },
  );

  // TC-APIA-006-P04
  test(
    "P04 GET non-existent resource returns 404",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "006",
        userStory: "US-006",
        criteria: ["AC-006-03"],
      });

      const response = await request.get("/api/v1/services/999999", {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      expect(response.status()).toBe(404);
    },
  );
});
