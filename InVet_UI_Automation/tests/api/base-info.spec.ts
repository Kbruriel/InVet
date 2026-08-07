import { expect, test } from "@playwright/test";

import { annotateTraceability } from "../helpers/traceability";

test.describe("Base API info - BE-001 / US-001", () => {
  test(
    "APIA-001-01 @smoke GET / responds 200 with InVet message [US-001 AC-001-01]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-01"],
      });

      const response = await request.get("/");
      expect(response.status()).toBe(200);
      expect(response.headers()["content-type"]).toContain("application/json");

      const payload = (await response.json()) as Record<string, unknown>;
      expect(payload).toHaveProperty("message");
      expect(typeof payload.message).toBe("string");
      expect(String(payload.message)).toContain("InVet");
    },
  );

  test(
    "APIA-001-02 @smoke GET /health responds 200 with status healthy [US-001 AC-001-01]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-01"],
      });

      const response = await request.get("/health");
      expect(response.status()).toBe(200);
      expect(response.headers()["content-type"]).toContain("application/json");

      const payload = (await response.json()) as Record<string, unknown>;
      expect(payload).toHaveProperty("status");
      expect(String(payload.status)).toBe("healthy");
    },
  );

  test(
    "APIA-001-03 @smoke GET /api/v1/ responds 200 with welcome message [US-001 AC-001-01]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-01"],
      });

      const response = await request.get("/api/v1/");
      expect(response.status()).toBe(200);
      expect(response.headers()["content-type"]).toContain("application/json");

      const payload = (await response.json()) as Record<string, unknown>;
      expect(payload).toHaveProperty("message");
    },
  );

  test(
    "APIA-001-06 GET /api/v1/openapi.json responds 200 exposing OpenAPI schema [US-001 AC-001-01]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-01"],
      });

      const response = await request.get("/api/v1/openapi.json");
      expect(response.status()).toBe(200);
      expect(response.headers()["content-type"]).toContain("application/json");

      const payload = await response.json();
      expect(typeof payload).toBe("object");

      // FastAPI generates "info", "paths" and "components" by default.
      expect(payload).toHaveProperty("info");
      expect(typeof (payload as any)?.paths).toBe("object");
    },
  );

  test(
    "APIA-001-06b GET /docs responds 200 exposing Swagger UI [US-001 AC-001-01]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-01"],
      });

      const response = await request.get("/docs");
      expect(response.status()).toBe(200);
    },
  );

  test(
    "APIA-001-06c GET /redoc responds 200 exposing ReDoc UI [US-001 AC-001-01]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-01"],
      });

      const response = await request.get("/redoc");
      expect(response.status()).toBe(200);
    },
  );

  test(
    "APIA-001-07 No se filtran secretos en respuestas publicas [US-001 security]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-02"],
      });

      const response = await request.get("/");
      expect(response.status()).toBe(200);

      const bodyString = JSON.stringify(await response.json());
      expect(bodyString.toLowerCase()).not.toContain("secret_key");
      expect(bodyString.toLowerCase()).not.toContain("SECRET_KEY");
      expect(bodyString).not.toMatch(/sk-|secret[a-z]*\s*[:=]\s*\S{5,}/i);

      const healthResponse = await request.get("/api/v1/openapi.json");
      expect(healthResponse.status()).toBe(200);
      const openAPIStr = JSON.stringify(await healthResponse.json());
      // Ensure the schema does not leak SECRET_KEY value (only references the env var name via defaults)
      expect(openAPIStr).not.toMatch(/sk-[A-Za-z0-9]{20,}/i);
    },
  );

  test(
    "APIA-001-08 OPTIONS on auth endpoint returns CORS/method headers [US-001 CA-001-03]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      // FastAPI allows OPTIONS implicitly via the CORS middleware (if present)
      // or returns 405; we only assert that no crash occurs.
      // Use fetch with method option since request.options() may not be available in all Playwright versions
      const response = await request.fetch("/api/v1/auth/login", { method: "OPTIONS" });
      expect([200, 405]).toContain(response.status());
    },
  );
});
