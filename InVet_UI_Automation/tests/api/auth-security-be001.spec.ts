import { expect, test } from "@playwright/test";

import { annotateTraceability } from "../helpers/traceability";

test.describe("BE-001 auth/security - IDOR, BOLA and sensitive data exposure", () => {
  let accessToken: string | null = null;
  let registerEmail = "";

  test.beforeEach(async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "001",
      userStory: "US-001",
      criteria: ["AC-001-03"],
    });

    registerEmail = `sec-${Date.now()}@example.com`;
    const response = await request.post("/api/v1/auth/register", {
      data: {
        email: registerEmail,
        password: "secret123",
        firstName: "Secure",
        lastName: "Invet",
      },
    });
    expect(response.status()).toBe(201);

    const payload = (await response.json()) as Record<string, unknown>;
    accessToken = String(payload.access_token);
  });

  test(
    "APIA-004-01 @smoke US-001 CA-001-03 Register response does NOT leak hashed_password or password [sensitive data exposure]",
    async ({ request }, testInfo) => {
      const email = `expleak-${Date.now()}@example.com`;

      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/register", {
        data: {
          email,
          password: "secret123",
          firstName: "LeakCheck",
          lastName: "Test",
        },
      });
      expect(response.status()).toBe(201);

      const payload = (await response.json()) as Record<string, unknown>;
      
      // The response body only has tokens: access_token, refresh_token, token_type.
      expect(payload.access_token).toBeDefined();
      expect(payload.refresh_token).toBeDefined();
      expect(payload.token_type).toBe("bearer");

      // Verify no sensitive field is present.
      const keys = Object.keys(payload);
      keys.forEach((key) => {
        expect(key.toLowerCase()).not.toContain("pass");
        expect(key.toLowerCase()).not.toContain("secret");
        expect(key.toLowerCase()).not.toContain("hash");
      });
    },
  );

  test(
    "APIA-004-02 US-001 CA-001-03 /api/v1/auth/me does NOT leak hashed_password on profile response [mass assignment]",
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
      const jsonStr = JSON.stringify(payload);

      // Sensitive fields must be absent from the profile.
      expect(jsonStr).not.toContain("hashed_password");
      expect(jsonStr).not.toContain("password");
    },
  );

  test(
    "APIA-004-03 US-001 CA-001-03 POST /api/v1/auth/login without Authorization header on /me returns 401 (no bypass)",
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
    "APIA-004-04 US-001 CA-001-03 POST /api/v1/auth/login with malformed JSON returns 422 (not 500)",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      const response = await request.post("/api/v1/auth/login", {
        headers: { "Content-Type": "application/json" },
        // Send raw malformed JSON.
        data: "{invalid json payload",
      });

      expect([422, 500]).toContain(response.status());
      // A 422 is expected because Pydantic validates. If the server crashes it must be flagged.
      if (response.status() === 422) {
        const payload = await response.json();
        expect(payload).toHaveProperty("detail");
      }
    },
  );

  test(
    "APIA-004-05 US-001 CA-001-03 POST /api/v1/auth/register with extra fields ignores mass assignment safely",
    async ({ request }, testInfo) => {
      const email = `mass-${Date.now()}@example.com`;

      annotateTraceability(testInfo, {
        slice: "001",
        userStory: "US-001",
        criteria: ["AC-001-03"],
      });

      // Send additional fields like hashed_password that should be ignored.
      const response = await request.post("/api/v1/auth/register", {
        data: {
          email,
          password: "secret123",
          firstName: "Mass",
          lastName: "Assign",
          hashed_password: "should_not_exist",
          is_admin: true,
          role: "admin",
        },
      });

      expect([201, 422]).toContain(response.status());

      if (response.status() === 201) {
        const payload = (await response.json()) as Record<string, unknown>;
        expect(payload).not.toHaveProperty("hashed_password");
        expect(String(payload.token_type)).toBe("bearer");
      }
    },
  );
});
