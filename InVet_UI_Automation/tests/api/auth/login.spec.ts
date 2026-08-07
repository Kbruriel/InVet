import { expect, test } from "@playwright/test";

import { readAutomationEnv } from "../../fixtures/env";
import { invalidLoginPayload } from "../../helpers/test-data";
import { annotateTraceability } from "../../helpers/traceability";

const env = readAutomationEnv();

test.describe("login api", () => {
  test.skip(!env.loginApiEnabled, "LOGIN_API_ENABLED=false.");

  test(
    "@smoke @regression US-002-01 CA-01 invalid credentials are rejected",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-01",
        criteria: ["CA-01"],
      });

      const response = await request.post(env.loginApiPath, {
        data: invalidLoginPayload,
      });

      expect(response.status()).toBe(401);
      expect(response.headers()["content-type"] || "").toContain("application/json");
    },
  );

  test(
    "@regression US-002-01 CA-02 valid credentials return tokens",
    async ({ request }, testInfo) => {
      test.skip(
        env.loginEmail === "qa@example.com",
        "Configure LOGIN_EMAIL and LOGIN_PASSWORD with a seeded QA account.",
      );

      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-01",
        criteria: ["CA-02"],
      });

      const response = await request.post(env.loginApiPath, {
        data: {
          email: env.loginEmail,
          password: env.loginPassword,
        },
      });

      expect(response.status()).toBe(200);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.access_token).toBe("string");
      expect(typeof payload.refresh_token).toBe("string");
      expect(payload.token_type).toBe("bearer");
      expect(payload.password).toBeUndefined();
      expect(payload.hashed_password).toBeUndefined();
    },
  );
});

