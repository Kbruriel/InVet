import { expect, test } from "@playwright/test";

import { annotateTraceability } from "../helpers/traceability";

test.describe("BE-001 auth/refresh - token refresh flow", () => {
  let originalRefreshToken: string | null = null;
  let registrationEmail = "";

  test.beforeEach(async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "001",
      userStory: "US-001",
      criteria: ["AC-001-03"],
    });

    registrationEmail = `rfrsh-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;
    const registerResponse = await request.post("/api/v1/auth/register", {
      data: {
        email: registrationEmail,
        password: "secret123",
        firstName: "Refresh",
        lastName: "User",
      },
    });
    expect(registerResponse.status()).toBe(201);

    const payload = (await registerResponse.json()) as Record<string, unknown>;
    originalRefreshToken = String(payload.refresh_token);
  });

  test(
    "APIA-006-01 @smoke US-001 CA-001-03 POST /api/v1/auth/refresh with valid refresh token returns new tokens [200]",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/refresh", {
        data: { refresh_token: originalRefreshToken },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.access_token).toBe("string");
      expect(typeof payload.refresh_token).toBe("string");
      expect(String(payload.token_type)).toBe("bearer");
    },
  );

  test(
    "APIA-006-02 US-001 CA-001-03 POST /api/v1/auth/refresh without body returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/refresh");
      expect(response.status()).toBe(422);
    },
  );

  test(
    "APIA-006-03 US-001 CA-001-03 POST /api/v1/auth/refresh with empty string refresh_token returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/refresh", {
        data: { refresh_token: "" },
      });
      expect(response.status()).toBe(422);
    },
  );

  test(
    "APIA-006-04 US-001 CA-001-03 POST /api/v1/auth/refresh with invalid refresh token returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/refresh", {
        data: { refresh_token: "invalid-refresh-token" },
      });
      expect(response.status()).toBe(401);
    },
  );

  test(
    "APIA-006-05 US-001 CA-001-03 POST /api/v1/auth/refresh with access_token as refresh_token returns 401",
    async ({ request }, testInfo) => {
      // Register and grab the access token to use it as refresh token (must fail).
      const registerResponse = await request.post("/api/v1/auth/register", {
        data: {
          email: `misuse-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`,
          password: "secret123",
          firstName: "Misuse",
          lastName: "Test",
        },
      });
      expect(registerResponse.status()).toBe(201);

      const payload = (await registerResponse.json()) as Record<string, unknown>;
      const accessTokenAsRefresh = String(payload.access_token);

      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/refresh", {
        data: { refresh_token: accessTokenAsRefresh },
      });
      expect(response.status()).toBe(401);
    },
  );
});
