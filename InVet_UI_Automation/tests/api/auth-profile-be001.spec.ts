import { expect, test } from "@playwright/test";

import { annotateTraceability } from "../helpers/traceability";

test.describe("BE-001 auth/profile - authenticated and unauthenticated access", () => {
  let accessToken: string | null = null;

  // Register a fresh user so /me can be tested with real credentials.
  test.beforeEach(async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "001",
      userStory: "US-001",
      criteria: ["AC-001-03"],
    });

    const email = `prof-${Date.now()}@example.com`;
    const registerResponse = await request.post("/api/v1/auth/register", {
      data: { email, password: "secret123", firstName: "Profile", lastName: "User" },
    });
    expect(registerResponse.status()).toBe(201);

    const payload = (await registerResponse.json()) as Record<string, unknown>;
    accessToken = String(payload.access_token);
  });

  test(
    "APIA-005-01 @smoke US-001 CA-001-03 GET /api/v1/auth/me without token returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.get("/api/v1/auth/me");
      expect(response.status()).toBe(401);
    },
  );

  test(
    "APIA-005-02 US-001 CA-001-03 GET /api/v1/auth/me with invalid bearer token returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.get("/api/v1/auth/me", {
        headers: { Authorization: "Bearer invalid-token" },
      });
      expect(response.status()).toBe(401);
    },
  );

  test(
    "APIA-005-03 US-001 CA-001-03 GET /api/v1/auth/me with valid token returns profile without sensitive fields",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.get("/api/v1/auth/me", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.id).toBe("number");
      expect(typeof payload.email).toBe("string");
      expect("firstName" in payload || "first_name" in payload).toBe(true);
      expect("lastName" in payload || "last_name" in payload).toBe(true);
      expect(typeof payload.role).toBe("string");

      // Security: sensitive fields must NOT be in response.
      expect(payload).not.toHaveProperty("hashed_password");
      expect(payload).not.toHaveProperty("password");
    },
  );
});
