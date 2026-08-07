import { expect, test } from "@playwright/test";

import { readAutomationEnv } from "../fixtures/env";
import { annotateTraceability } from "../helpers/traceability";

const env = readAutomationEnv();

test.describe("BE-001 register API - positive & negative", () => {
  const emailPrefix = "invet-reg";

  function generateEmail(): string {
    return `${emailPrefix}-${Date.now()}@example.com`;
  }

  test(
    "APIA-003-01 @smoke US-001 CA-001-03 POST /api/v1/auth/register accepts valid payload and returns 201",
    async ({ request }, testInfo) => {
      const email = generateEmail();

      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/register", {
        data: {
          email,
          password: "secret123",
          firstName: "Test",
          lastName: "Invet",
        },
      });
      expect(response.status()).toBe(201);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.access_token).toBe("string");
      expect(typeof payload.refresh_token).toBe("string");
      expect(String(payload.token_type)).toBe("bearer");
    },
  );

  test(
    "APIA-003-02 US-001 CA-001-03 POST /api/v1/auth/register without body returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/register");
      expect(response.status()).toBe(422);
    },
  );

  test(
    "APIA-003-03 US-001 CA-001-03 POST /api/v1/auth/register with invalid email returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/register", {
        data: {
          email: "not-an-email",
          password: "secret123",
          firstName: "Test",
          lastName: "Invet",
        },
      });
      expect(response.status()).toBe(422);
    },
  );

  test(
    "APIA-003-04 US-001 CA-001-03 POST /api/v1/auth/register with short password returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/register", {
        data: {
          email: generateEmail(),
          password: "abc",
          firstName: "Test",
          lastName: "Invet",
        },
      });
      expect(response.status()).toBe(422);

      const payload = await response.json();
      expect(payload).toHaveProperty("detail");
    },
  );

  test(
    "APIA-003-05 US-001 CA-001-03 POST /api/v1/auth/register with camelCase fields (firstName/lastName) is accepted",
    async ({ request }, testInfo) => {
      const email = generateEmail();

      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/register", {
        data: { email, password: "secret123", firstName: "Camel", lastName: "Case" },
      });
      expect(response.status()).toBe(201);
    },
  );

  test(
    "APIA-003-06 US-001 CA-001-03 POST /api/v1/auth/register with snake_case fields (first_name/last_name) is accepted via populate_by_name=True",
    async ({ request }, testInfo) => {
      const email = generateEmail();

      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      // populate_by_name=True allows both camelCase and snake_case.
      const response = await request.post("/api/v1/auth/register", {
        data: { email, password: "secret123", first_name: "Snake", last_name: "Case" },
      });

      expect(response.status()).toBe(201);
    },
  );

  test(
    "APIA-003-07 US-001 CA-001-03 POST /api/v1/auth/register missing fields returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/register", {
        data: { email: generateEmail() },
      });
      expect(response.status()).toBe(422);
    },
  );
});
