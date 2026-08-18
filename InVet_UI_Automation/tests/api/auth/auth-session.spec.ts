/**
 * APIA-002 - API/HTTP automation for BE-002 / FE-002 (Autenticacion y sesion)
 *
 * Cobertura:
 * - APIA-002-01: Registro devuelve tokens (POST /register → 201)
 * - APIA-002-02: Registro duplicado falla seguro (POST /register → 409)
 * - APIA-002-03: Login valido devuelve bearer (POST /login → 200)
 * - APIA-002-04: Login invalido falla seguro (POST /login → 401)
 * - APIA-002-05: Perfil sin token falla (GET /me → 401)
 * - APIA-002-06: Perfil con access token responde (GET /me → 200)
 * - APIA-002-07: Refresh valido emite tokens (POST /refresh → 200)
 * - APIA-002-08: Refresh rechaza access token (POST /refresh → 401)
 * - APIA-002-09: Logout cierra sesion (POST /logout → 200/204)
 * - APIA-002-10: Recuperacion no enumera correos (POST /password-reset/request → 200)
 * - APIA-002-11: Reset valida token (POST /password-reset/confirm → 200/401)
 * - APIA-002-12: Payload invalido devuelve 422
 *
 * Trazabilidad: AC-002-01, AC-002-02, AC-002-03, AC-002-04, AC-002-05,
 *               AC-002-06, AC-002-07, AC-002-10
 */

import { expect, test } from "@playwright/test";

import { readAutomationEnv } from "../../fixtures/env";
import { annotateTraceability } from "../../helpers/traceability";

const env = readAutomationEnv();

function normalizeText(value: unknown): string {
  return String(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

// ===========================================================================
// APIA-002-01: Registro devuelve tokens (POST /register → 201)
// Criterio: AC-002-01
// Trazabilidad: US-002-01, AC-002-01
// ===========================================================================

test.describe("auth register - APIA-002", () => {
  test(
    "@smoke @regression APIA-002-01 US-002-01 AC-002-01 POST /api/v1/auth/register returns 201 with tokens",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-01",
        criteria: ["AC-002-01"],
      });

      const email = `api-test-reg-${Date.now()}@example.com`;
      const response = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email,
          password: "secret123",
          firstName: "API",
          lastName: "Test",
        },
      });

      expect(response.status()).toBe(201);

      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.access_token).toBe("string");
      expect(typeof payload.refresh_token).toBe("string");
      expect(String(payload.token_type)).toBe("bearer");

      // Guardar tokens para pruebas posteriores
      test.info().annotations.push({
        type: "tokens",
        description: JSON.stringify({ access_token: payload.access_token, refresh_token: payload.refresh_token }),
      });
    },
  );

  // ===========================================================================
  // APIA-002-02: Registro duplicado falla seguro (POST /register → 409)
  // Criterio: AC-002-03
  // Trazabilidad: US-002-03, AC-002-03
  // ===========================================================================

  test(
    "@regression APIA-002-02 US-002-03 AC-002-03 POST /api/v1/auth/register duplicate returns 409",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-03",
        criteria: ["AC-002-03"],
      });

      const email = `api-test-dup-${Date.now()}@example.com`;

      // Primer registro
      const firstResponse = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email,
          password: "secret123",
          firstName: "API",
          lastName: "Test",
        },
      });
      expect(firstResponse.status()).toBe(201);

      // Segundo registro con mismo email
      const secondResponse = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email,
          password: "secret123",
          firstName: "API",
          lastName: "Test",
        },
      });

      expect(secondResponse.status()).toBe(409);
      const payload = (await secondResponse.json()) as Record<string, unknown>;
      expect(typeof payload.detail).toBe("string");
      // No debe exponer detalles internos
      expect(String(payload.detail)).not.toContain("traceback");
      expect(String(payload.detail)).not.toContain("password");
    },
  );

  // ===========================================================================
  // APIA-002-03: Login valido devuelve bearer (POST /login → 200)
  // Criterio: AC-002-02
  // Trazabilidad: US-002-02, AC-002-02
  // ===========================================================================

  test(
    "@regression APIA-002-03 US-002-02 AC-002-02 POST /api/v1/auth/login returns 200 with bearer tokens",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-02",
        criteria: ["AC-002-02"],
      });

      // Registrar usuario primero
      const email = `api-test-login-${Date.now()}@example.com`;
      await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email,
          password: "secret123",
          firstName: "API",
          lastName: "Test",
        },
      });

      // Login
      const response = await request.post(`${env.apiBaseUrl}/api/v1/auth/login`, {
        data: {
          email,
          password: "secret123",
        },
      });

      expect(response.status()).toBe(200);
      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.access_token).toBe("string");
      expect(typeof payload.refresh_token).toBe("string");
      expect(String(payload.token_type)).toBe("bearer");
    },
  );

  // ===========================================================================
  // APIA-002-04: Login invalido falla seguro (POST /login → 401)
  // Criterio: AC-002-03
  // Trazabilidad: US-002-03, AC-002-03
  // ===========================================================================

  test(
    "@regression APIA-002-04 US-002-03 AC-002-03 POST /api/v1/auth/login invalid credentials returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-03",
        criteria: ["AC-002-03"],
      });

      const response = await request.post(`${env.apiBaseUrl}/api/v1/auth/login`, {
        data: {
          email: "invalid@example.com",
          password: "wrongpass",
        },
      });

      expect(response.status()).toBe(401);
      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.detail).toBe("string");
      // No debe enumerar si fallo email o password
      expect(String(payload.detail)).not.toContain("invalid@example.com");
      expect(String(payload.detail)).not.toContain("traceback");
    },
  );

  // ===========================================================================
  // APIA-002-05: Perfil sin token falla (GET /me → 401)
  // Criterio: AC-002-04
  // Trazabilidad: US-002-04, AC-002-04
  // ===========================================================================

  test(
    "@regression APIA-002-05 US-002-04 AC-002-04 GET /api/v1/auth/me without token returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-04",
        criteria: ["AC-002-04"],
      });

      const response = await request.get(`${env.apiBaseUrl}/api/v1/auth/me`);

      expect(response.status()).toBe(401);
    },
  );

  // ===========================================================================
  // APIA-002-06: Perfil con access token responde (GET /me → 200)
  // Criterio: AC-002-04
  // Trazabilidad: US-002-04, AC-002-04
  // ===========================================================================

  test(
    "@regression APIA-002-06 US-002-04 AC-002-04 GET /api/v1/auth/me with valid token returns profile",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-04",
        criteria: ["AC-002-04"],
      });

      // Registrar y obtener token
      const email = `api-test-profile-${Date.now()}@example.com`;
      const registerResponse = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email,
          password: "secret123",
          firstName: "API",
          lastName: "Profile",
        },
      });
      expect(registerResponse.status()).toBe(201);
      const registerPayload = (await registerResponse.json()) as Record<string, unknown>;
      const accessToken = String(registerPayload.access_token);

      // Obtener perfil
      const response = await request.get(`${env.apiBaseUrl}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      expect(response.status()).toBe(200);
      const payload = (await response.json()) as Record<string, unknown>;

      // Verificar estructura del perfil
      expect(typeof payload.id).toBe("number");
      expect(payload.email).toBe(email);
      expect(typeof payload.firstName).toBe("string");
      expect(typeof payload.lastName).toBe("string");
      expect(typeof payload.role).toBe("string");

      // CRITICO: No debe exponer hashed_password ni secretos
      expect(Object.keys(payload)).not.toContain("hashed_password");
      expect(Object.keys(payload)).not.toContain("password");
    },
  );

  // ===========================================================================
  // APIA-002-07: Refresh valido emite tokens (POST /refresh → 200)
  // Criterio: AC-002-05
  // Trazabilidad: US-002-05, AC-002-05
  // ===========================================================================

  test(
    "@regression APIA-002-07 US-002-05 AC-002-05 POST /api/v1/auth/refresh with valid token returns new tokens",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-05",
        criteria: ["AC-002-05"],
      });

      // Registrar y obtener tokens
      const email = `api-test-refresh-${Date.now()}@example.com`;
      const registerResponse = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email,
          password: "secret123",
          firstName: "API",
          lastName: "Refresh",
        },
      });
      expect(registerResponse.status()).toBe(201);
      const registerPayload = (await registerResponse.json()) as Record<string, unknown>;
      const refreshToken = String(registerPayload.refresh_token);

      // Refresh
      const response = await request.post(`${env.apiBaseUrl}/api/v1/auth/refresh`, {
        data: {
          refresh_token: refreshToken,
        },
      });

      expect(response.status()).toBe(200);
      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.access_token).toBe("string");
      expect(typeof payload.refresh_token).toBe("string");
      expect(String(payload.token_type)).toBe("bearer");
    },
  );

  // ===========================================================================
  // APIA-002-08: Refresh rechaza access token (POST /refresh → 401)
  // Criterio: AC-002-05
  // Trazabilidad: US-002-05, AC-002-05
  // ===========================================================================

  test(
    "@regression APIA-002-08 US-002-05 AC-002-05 POST /api/v1/auth/refresh with access token returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-05",
        criteria: ["AC-002-05"],
      });

      // Registrar y obtener access token
      const email = `api-test-reject-${Date.now()}@example.com`;
      const registerResponse = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email,
          password: "secret123",
          firstName: "API",
          lastName: "Reject",
        },
      });
      expect(registerResponse.status()).toBe(201);
      const registerPayload = (await registerResponse.json()) as Record<string, unknown>;
      const accessToken = String(registerPayload.access_token);

      // Intentar usar access token como refresh
      const response = await request.post(`${env.apiBaseUrl}/api/v1/auth/refresh`, {
        data: {
          refresh_token: accessToken,
        },
      });

      expect(response.status()).toBe(401);
      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.detail).toBe("string");
      // Debe indicar que el token es invalido para refresh
      expect(String(payload.detail).toLowerCase()).toContain("invalido");
    },
  );

  // ===========================================================================
  // APIA-002-09: Logout cierra sesion (POST /logout → 200)
  // Criterio: AC-002-06
  // Trazabilidad: US-002-06, AC-002-06
  // ===========================================================================

  test(
    "@regression APIA-002-09 US-002-06 AC-002-06 POST /api/v1/auth/logout returns 200 with generic message",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-06",
        criteria: ["AC-002-06"],
      });

      // Registrar y obtener token
      const email = `api-test-logout-${Date.now()}@example.com`;
      const registerResponse = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email,
          password: "secret123",
          firstName: "API",
          lastName: "Logout",
        },
      });
      expect(registerResponse.status()).toBe(201);
      const registerPayload = (await registerResponse.json()) as Record<string, unknown>;
      const accessToken = String(registerPayload.access_token);
      const refreshToken = String(registerPayload.refresh_token);

      // Logout
      const response = await request.post(`${env.apiBaseUrl}/api/v1/auth/logout`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        data: {
          refresh_token: refreshToken,
        },
      });

      expect(response.status()).toBe(200);
      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.message).toBe("string");
      // Debe ser un mensaje generico sin detalles internos
      expect(String(payload.message)).not.toContain("traceback");
      expect(String(payload.message)).not.toContain("password");
    },
  );

  // ===========================================================================
  // APIA-002-10: Recuperacion no enumera correos (POST /password-reset/request → 200)
  // Criterio: AC-002-07
  // Trazabilidad: US-002-07, AC-002-07
  // ===========================================================================

  test(
    "@regression APIA-002-10 US-002-07 AC-002-07 POST /api/v1/auth/password-reset/request returns generic for existing email",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-07",
        criteria: ["AC-002-07"],
      });

      const email = `api-test-reset-${Date.now()}@example.com`;

      // Registrar usuario primero
      await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email,
          password: "secret123",
          firstName: "API",
          lastName: "Reset",
        },
      });

      // Solicitar reset para email existente
      const existingResponse = await request.post(`${env.apiBaseUrl}/api/v1/auth/password-reset/request`, {
        data: {
          email,
        },
      });

      expect(existingResponse.status()).toBe(200);
      const existingPayload = (await existingResponse.json()) as Record<string, unknown>;
      expect(typeof existingPayload.message).toBe("string");

      // Solicitar reset para email inexistente
      const nonExistingResponse = await request.post(`${env.apiBaseUrl}/api/v1/auth/password-reset/request`, {
        data: {
          email: "nonexistent@example.com",
        },
      });

      expect(nonExistingResponse.status()).toBe(200);
      const nonExistingPayload = (await nonExistingResponse.json()) as Record<string, unknown>;
      expect(typeof nonExistingPayload.message).toBe("string");

      // CRITICO: Ambas respuestas deben ser genericas y NO enumerar correos
      // El mensaje no debe confirmar si el email existe o no
      expect(String(existingPayload.message)).not.toContain(email);
      expect(String(nonExistingPayload.message)).not.toContain("nonexistent@example.com");
      // Ambos mensajes deben ser esencialmente iguales (genericos)
      expect(String(existingPayload.message)).toBe(String(nonExistingPayload.message));
    },
  );

  // ===========================================================================
  // APIA-002-11: Reset valida token (POST /password-reset/confirm → 200/401)
  // Criterio: AC-002-07
  // Trazabilidad: US-002-07, AC-002-07
  // ===========================================================================

  test(
    "@regression APIA-002-11 US-002-07 AC-002-07 POST /api/v1/auth/password-reset/confirm with invalid token returns 401",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-07",
        criteria: ["AC-002-07"],
      });

      // Intentar confirmar reset con token invalido
      const response = await request.post(`${env.apiBaseUrl}/api/v1/auth/password-reset/confirm`, {
        data: {
          reset_token: "invalid_token_abc123",
          new_password: "newsecret123",
        },
      });

      expect(response.status()).toBe(401);
      const payload = (await response.json()) as Record<string, unknown>;
      expect(typeof payload.detail).toBe("string");
      expect(normalizeText(payload.detail)).toContain("invalido");
    },
  );

  // ===========================================================================
  // APIA-002-12: Payload invalido devuelve 422
  // Criterio: AC-002-03
  // Trazabilidad: US-002-03, AC-002-03
  // ===========================================================================

  test(
    "@regression APIA-002-12 US-002-03 AC-002-03 POST /api/v1/auth/register with invalid payload returns 422",
    async ({ request }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-03",
        criteria: ["AC-002-03"],
      });

      // Email invalido
      const response1 = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email: "not-an-email",
          password: "secret123",
          firstName: "API",
          lastName: "Test",
        },
      });
      expect(response1.status()).toBe(422);

      // Password demasiado corto
      const response2 = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email: `api-test-short-${Date.now()}@example.com`,
          password: "short",
          firstName: "API",
          lastName: "Test",
        },
      });
      expect(response2.status()).toBe(422);

      // Campos faltantes
      const response3 = await request.post(`${env.apiBaseUrl}/api/v1/auth/register`, {
        data: {
          email: `api-test-missing-${Date.now()}@example.com`,
          password: "secret123",
        },
      });
      expect(response3.status()).toBe(422);
    },
  );
});
