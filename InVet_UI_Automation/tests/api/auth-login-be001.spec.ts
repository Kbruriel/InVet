import { expect, test } from "@playwright/test";

import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability } from "../helpers/traceability";

const env = readAutomationEnv();

test.describe("BE-001 login API - positive & negative", () => {
  test(
    "APIA-002-01 @smoke US-001 AC-001-03 POST /api/v1/auth/login with invalid payload returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/login");
      expect(response.status()).toBe(422);
    },
  );

  test(
    "APIA-002-02 US-001 AC-001-03 POST /api/v1/auth/login with email format rejected returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/login", {
        data: { email: "not-an-email", password: "secret123" },
      });
      expect(response.status()).toBe(422);
    },
  );

  test(
    "APIA-002-03 US-001 AC-001-03 POST /api/v1/auth/login with password below minimum returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/login", {
        data: { email: "a@b.com", password: "short" },
      });
      expect(response.status()).toBe(422);
    },
  );

  test(
    "APIA-002-04 US-001 AC-001-03 POST /api/v1/auth/login with invalid credentials returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/login", {
        data: { email: "nomatch@invet.io", password: "wrongpass" },
      });
      expect(response.status()).toBe(401);
    },
  );

  test(
    "APIA-002-05 US-001 AC-001-03 POST /api/v1/auth/login with valid credentials returns access_token, refresh_token and bearer",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/login", {
        data: { email: env.loginEmail, password: env.loginPassword },
      });
      expect(response.status()).toBe(200);
      expect(response.headers()["content-type"]).toContain("application/json");

      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.access_token).toBe("string");
      expect(typeof payload.refresh_token).toBe("string");
      expect(String(payload.token_type)).toBe("bearer");
    },
  );

  test(
    "APIA-002-06 US-001 CA-001-03 POST /api/v1/auth/login response contains NO password or hashed_password [US-001 security]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      // Even without a real user, the 422 payload is checked for sensitivity.
      const response = await request.post("/api/v1/auth/login", {
        data: { email: "a@b.com", password: "secret123" },
      });

      const bodyString = JSON.stringify(await response.json());
      expect(bodyString).not.toContain("hashed_password");
      expect(bodyString.toLowerCase()).not.toContain("secret123");
    },
  );
});
