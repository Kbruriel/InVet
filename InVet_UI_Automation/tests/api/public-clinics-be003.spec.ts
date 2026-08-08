import { expect, test } from "@playwright/test";
import { annotateTraceability } from "../helpers/traceability";

const API_BASE = process.env.API_BASE_URL || "http://127.0.0.1:8000";

function isPublicField(key: string): boolean {
  const sensitiveKeys = [
    "password",
    "hashed_password",
    "owner_id",
    "tenant_id",
    "is_active",
    "is_superuser",
    "role",
    "permissions",
    "created_at",
    "updated_at",
    "__config__",
    "__fields__",
  ];
  return !sensitiveKeys.some((k) => key.includes(k));
}

test.describe("BE-003 public clinics - anonymous access", () => {
  // -----------------------------------------------------------------------
  // APIA-003-01  GET /api/v1/clinicas — 200 OK with paginated response
  // -----------------------------------------------------------------------
  test(
    "APIA-003-01 @smoke US-003 AC-003-01 GET /api/v1/clinicas returns 200 without auth",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-01"],
      });

      const response = await request.get("/api/v1/clinicas");
      expect(response.status()).toBe(200);
      expect(response.headers()["content-type"]).toContain("application/json");

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");
      expect(typeof payload.page).toBe("number");
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-02  GET /api/v1/clinicas?search=nombre — filters work
  // -----------------------------------------------------------------------
  test(
    "APIA-003-02 US-003 AC-003-02 GET /api/v1/clinicas?search= filters correctly",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-02"],
      });

      const response = await request.get("/api/v1/clinicas?search=test");
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");

      // Every returned item should contain the search term in a public field
      for (const item of payload.items as Array<Record<string, unknown>>) {
        const combined = Object.values(item)
          .filter((v): v is string => typeof v === "string")
          .join(" ")
          .toLowerCase();
        // If search term is provided and items exist, at least one field should match
        if (payload.total > 0) {
          expect(combined).toContain("test");
        }
      }
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-03  GET /api/v1/clinicas?invalid_param — returns 422
  // -----------------------------------------------------------------------
  test(
    "APIA-003-03 US-003 AC-003-02 GET /api/v1/clinicas?invalid_param returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-02"],
      });

      const response = await request.get("/api/v1/clinicas?invalid_param=x");
      expect(response.status()).toBe(422);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.detail)).toBe(true);
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-04  GET /api/v1/clinicas/{id} — 200 OK with PublicClinicDTO
  // -----------------------------------------------------------------------
  test(
    "APIA-003-04 US-003 AC-003-01 GET /api/v1/clinicas/{id} returns 200 with PublicClinicDTO",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-01"],
      });

      // First get a valid clinic id from the list endpoint
      const listResponse = await request.get("/api/v1/clinicas?page=1&limit=1");
      expect(listResponse.status()).toBe(200);
      const listPayload = (await listResponse.json()) as Record<string, unknown>;

      if ((listPayload.items as Array<Record<string, unknown>>).length === 0) {
        test.skip();
      }

      const clinicId = (listPayload.items as Array<Record<string, unknown>>)[0].id;
      const detailResponse = await request.get(`/api/v1/clinicas/${clinicId}`);
      expect(detailResponse.status()).toBe(200);
      expect(detailResponse.headers()["content-type"]).toContain("application/json");

      const payload = (await detailResponse.json()) as Record<string, unknown>;

      // PublicClinicDTO should have public fields
      expect(typeof payload.id).toBe("number");
      expect(typeof payload.nombre || payload.name).toBeTruthy();

      // Verify no sensitive ORM fields are exposed
      const keys = Object.keys(payload);
      for (const key of keys) {
        if (!isPublicField(key)) {
          throw new Error(`Sensitive field '${key}' exposed in PublicClinicDTO`);
        }
      }
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-05  GET /api/v1/clinicas/{invalid_id} — 404
  // -----------------------------------------------------------------------
  test(
    "APIA-003-05 US-003 AC-003-06 GET /api/v1/clinicas/{invalid_id} returns 404",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-06"],
      });

      const response = await request.get("/api/v1/clinicas/999999");
      expect(response.status()).toBe(404);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(payload.detail || payload.error).toBeTruthy();
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-06  GET /api/v1/sucursales — 200 OK with paginated response
  // -----------------------------------------------------------------------
  test(
    "APIA-003-06 US-003 AC-003-03 GET /api/v1/sucursales returns 200 with pagination",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-03"],
      });

      const response = await request.get("/api/v1/sucursales");
      expect(response.status()).toBe(200);
      expect(response.headers()["content-type"]).toContain("application/json");

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");
      expect(typeof payload.page).toBe("number");
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-07  GET /api/v1/sucursales?clinica_id=X — filters work
  // -----------------------------------------------------------------------
  test(
    "APIA-003-07 US-003 AC-003-03 GET /api/v1/sucursales?clinica_id=X filters correctly",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-03"],
      });

      // Get a valid clinic_id from the clinics list
      const clinicsResponse = await request.get("/api/v1/clinicas?page=1&limit=1");
      expect(clinicsResponse.status()).toBe(200);
      const clinicsPayload = (await clinicsResponse.json()) as Record<string, unknown>;

      if ((clinicsPayload.items as Array<Record<string, unknown>>).length === 0) {
        test.skip();
      }

      const clinicId = (clinicsPayload.items as Array<Record<string, unknown>>)[0].id;
      const response = await request.get(`/api/v1/sucursales?clinica_id=${clinicId}`);
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");

      // All returned branches should belong to the requested clinic
      for (const item of payload.items as Array<Record<string, unknown>>) {
        expect(item.clinica_id || item.clinic_id).toBe(clinicId);
      }
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-08  GET /api/v1/servicios — 200 OK with paginated response
  // -----------------------------------------------------------------------
  test(
    "APIA-003-08 US-003 AC-003-04 GET /api/v1/servicios returns 200 with pagination",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-04"],
      });

      const response = await request.get("/api/v1/servicios");
      expect(response.status()).toBe(200);
      expect(response.headers()["content-type"]).toContain("application/json");

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");
      expect(typeof payload.page).toBe("number");
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-09  GET /api/v1/servicios?sucursal_id=X&clinica_id=Y — combined filters
  // -----------------------------------------------------------------------
  test(
    "APIA-003-09 US-003 AC-003-04 GET /api/v1/servicios with combined filters works",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-04"],
      });

      // Get valid IDs from previous endpoints
      const clinicsResponse = await request.get("/api/v1/clinicas?page=1&limit=1");
      expect(clinicsResponse.status()).toBe(200);
      const clinicsPayload = (await clinicsResponse.json()) as Record<string, unknown>;

      if ((clinicsPayload.items as Array<Record<string, unknown>>).length === 0) {
        test.skip();
      }

      const clinicId = (clinicsPayload.items as Array<Record<string, unknown>>)[0].id;

      const branchesResponse = await request.get(`/api/v1/sucursales?clinica_id=${clinicId}&page=1&limit=1`);
      expect(branchesResponse.status()).toBe(200);
      const branchesPayload = (await branchesResponse.json()) as Record<string, unknown>;

      if ((branchesPayload.items as Array<Record<string, unknown>>).length === 0) {
        test.skip();
      }

      const branchId = (branchesPayload.items as Array<Record<string, unknown>>)[0].id;

      const response = await request.get(`/api/v1/servicios?sucursal_id=${branchId}&clinica_id=${clinicId}`);
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(Array.isArray(payload.items)).toBe(true);
      expect(typeof payload.total).toBe("number");
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-10  IDOR/BOLA — no private data leaks in public endpoints
  // -----------------------------------------------------------------------
  test(
    "APIA-003-10 US-003 AC-003-06 IDOR/BOLA no private data leaks in public endpoints",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-06"],
      });

      // Test clinics endpoint for sensitive field leaks
      const clinicsResponse = await request.get("/api/v1/clinicas?page=1&limit=5");
      expect(clinicsResponse.status()).toBe(200);
      const clinicsPayload = (await clinicsResponse.json()) as Record<string, unknown>;

      for (const item of clinicsPayload.items as Array<Record<string, unknown>>) {
        const keys = Object.keys(item);
        for (const key of keys) {
          expect(isPublicField(key)).toBeTruthy();
        }
      }

      // Test sucursales endpoint for sensitive field leaks
      const branchesResponse = await request.get("/api/v1/sucursales?page=1&limit=5");
      expect(branchesResponse.status()).toBe(200);
      const branchesPayload = (await branchesResponse.json()) as Record<string, unknown>;

      for (const item of branchesPayload.items as Array<Record<string, unknown>>) {
        const keys = Object.keys(item);
        for (const key of keys) {
          expect(isPublicField(key)).toBeTruthy();
        }
      }

      // Test servicios endpoint for sensitive field leaks
      const servicesResponse = await request.get("/api/v1/servicios?page=1&limit=5");
      expect(servicesResponse.status()).toBe(200);
      const servicesPayload = (await servicesResponse.json()) as Record<string, unknown>;

      for (const item of servicesPayload.items as Array<Record<string, unknown>>) {
        const keys = Object.keys(item);
        for (const key of keys) {
          expect(isPublicField(key)).toBeTruthy();
        }
      }
    },
  );

  // -----------------------------------------------------------------------
  // APIA-003-11  Response structure — no ORM models exposed, consistent errors
  // -----------------------------------------------------------------------
  test(
    "APIA-003-11 US-003 AC-003-06 Response structure valid: no ORM models, consistent errors",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "003",
        userStory: "US-003",
        criteria: ["AC-003-06"],
      });

      // Verify error format consistency across endpoints
      const invalidEndpoints = [
        "/api/v1/clinicas?invalid_param=x",
        "/api/v1/sucursales?invalid_param=x",
        "/api/v1/servicios?invalid_param=x",
        "/api/v1/clinicas/999999",
      ];

      for (const endpoint of invalidEndpoints) {
        const response = await request.get(endpoint);
        const status = response.status();

        if (status === 422 || status === 404) {
          const payload = (await response.json()) as Record<string, unknown>;
          // FastAPI returns 'detail' for validation errors
          expect(payload.detail || payload.error).toBeTruthy();
          expect(typeof payload.detail || typeof payload.error).toBe("string");
        }
      }

      // Verify no ORM-specific fields in list responses
      const checkEndpoints = [
        "/api/v1/clinicas?page=1&limit=1",
        "/api/v1/sucursales?page=1&limit=1",
        "/api/v1/servicios?page=1&limit=1",
      ];

      for (const endpoint of checkEndpoints) {
        const response = await request.get(endpoint);
        expect(response.status()).toBe(200);
        const payload = (await response.json()) as Record<string, unknown>;

        if (Array.isArray(payload.items)) {
          for (const item of payload.items as Array<Record<string, unknown>>) {
            const keys = Object.keys(item);
            for (const key of keys) {
              expect(isPublicField(key)).toBeTruthy();
            }
          }
        }
      }
    },
  );
});
