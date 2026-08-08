import { expect, test } from "@playwright/test";
import { annotateTraceability } from "../helpers/traceability";

const API_BASE = process.env.API_BASE_URL || "http://127.0.0.1:8000";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function isPublicField(key: string): boolean {
  const sensitiveKeys = [
    "password",
    "hashed_password",
    "owner_id",
    "tenant_id",
    "is_superuser",
    "role",
    "permissions",
    "internal_notes",
    "__config__",
    "__fields__",
  ];
  return !sensitiveKeys.some((k) => key.includes(k));
}

/**
 * Attempt to fetch a valid branch_id from the public list endpoint.
 * Returns null when no branches exist (test will be skipped).
 */
async function getValidBranchId(request: import("@playwright/test").APIRequestContext): Promise<number | null> {
  const response = await request.get("/api/v1/sucursales?page=1&limit=1");
  if (response.status() !== 200) return null;

  const payload = (await response.json()) as Record<string, unknown>;
  const items = payload.items as Array<Record<string, unknown>> | undefined;
  if (!items || items.length === 0) return null;

  return items[0].id as number;
}

// ---------------------------------------------------------------------------
// APIA-004-01  GET /api/v1/clinics/branches/{branch_id} — 200 OK public profile
// ---------------------------------------------------------------------------
test(
  "APIA-004-01 @smoke US-004 AC-004-01 GET /api/v1/clinics/branches/{branch_id} returns 200 without auth",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-01"],
    });

    const branchId = await getValidBranchId(request);
    if (branchId === null) {
      test.skip();
    }

    const response = await request.get(`/api/v1/clinics/branches/${branchId}`);
    expect(response.status()).toBe(200);
    expect(response.headers()["content-type"]).toContain("application/json");

    const payload = (await response.json()) as Record<string, unknown>;

    // Core public fields must be present
    expect(typeof payload.id).toBe("number");
    expect(typeof payload.clinic_id).toBe("number");
    expect(typeof payload.name).toBe("string");
    expect(typeof payload.address).toBe("string");
    expect(typeof payload.city).toBe("string");
    expect(typeof payload.is_active).toBe("boolean");

    // Embedded collections must be arrays
    expect(Array.isArray(payload.services)).toBe(true);
    expect(Array.isArray(payload.schedules)).toBe(true);

    // rating_summary and availability_summary may be null or objects
    if (payload.rating_summary !== null && payload.rating_summary !== undefined) {
      expect(typeof payload.rating_summary).toBe("object");
    }
    if (payload.availability_summary !== null && payload.availability_summary !== undefined) {
      expect(typeof payload.availability_summary).toBe("object");
    }
  },
);

// ---------------------------------------------------------------------------
// APIA-004-02  GET /api/v1/clinics/branches/{clinic_id}/{branch_id} — 401 without auth
// ---------------------------------------------------------------------------
test(
  "APIA-004-02 US-004 AC-004-02 GET /api/v1/clinics/branches/{clinic_id}/{branch_id} returns 401 without auth",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-02"],
    });

    const branchId = await getValidBranchId(request);
    if (branchId === null) {
      test.skip();
    }

    // Use a clinic_id that may or may not exist; the key assertion is 401
    const response = await request.get(`/api/v1/clinics/branches/${branchId}/${branchId}`);
    expect(response.status()).toBe(401);
  },
);

// ---------------------------------------------------------------------------
// APIA-004-03  GET /api/v1/clinics/branches/{clinic_id}/{branch_id} — 403 with valid token but no access
// ---------------------------------------------------------------------------
test(
  "APIA-004-03 US-004 AC-004-02 GET /api/v1/clinics/branches/{clinic_id}/{branch_id} returns 403 or 404 with valid token but no access",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-02"],
    });

    const branchId = await getValidBranchId(request);
    if (branchId === null) {
      test.skip();
    }

    // Use a valid-looking but unauthorized token
    const response = await request.get(`/api/v1/clinics/branches/${branchId}/${branchId}`, {
      headers: {
        Authorization: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
      },
    });

    // The endpoint should reject unauthorized access with 403 or 404 (IDOR-safe)
    expect([403, 404]).toContain(response.status());
  },
);

// ---------------------------------------------------------------------------
// APIA-004-04  GET /api/v1/clinics/branches/{clinic_id}/{branch_id} — 404 for non-existent IDs
// ---------------------------------------------------------------------------
test(
  "APIA-004-04 US-004 AC-004-08 GET /api/v1/clinics/branches/999999/999999 returns 404 for non-existent IDs",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-08"],
    });

    const response = await request.get("/api/v1/clinics/branches/999999/999999");
    expect(response.status()).toBe(404);
  },
);

// ---------------------------------------------------------------------------
// APIA-004-05  Services embedded in public profile are valid
// ---------------------------------------------------------------------------
test(
  "APIA-004-05 US-004 AC-004-03 Services embedded in public profile return valid structure",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-03"],
    });

    const branchId = await getValidBranchId(request);
    if (branchId === null) {
      test.skip();
    }

    const response = await request.get(`/api/v1/clinics/branches/${branchId}`);
    expect(response.status()).toBe(200);

    const payload = (await response.json()) as Record<string, unknown>;
    const services = payload.services as Array<Record<string, unknown>> | undefined;

    if (services && services.length > 0) {
      // Each service should have at least id and name
      for (const service of services) {
        expect(typeof service.id).toBe("number");
        expect(typeof service.name).toBe("string");
      }
    }
  },
);

// ---------------------------------------------------------------------------
// APIA-004-06  Schedules embedded in public profile are valid
// ---------------------------------------------------------------------------
test(
  "APIA-004-06 US-004 AC-004-04 Schedules embedded in public profile return valid structure",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-04"],
    });

    const branchId = await getValidBranchId(request);
    if (branchId === null) {
      test.skip();
    }

    const response = await request.get(`/api/v1/clinics/branches/${branchId}`);
    expect(response.status()).toBe(200);

    const payload = (await response.json()) as Record<string, unknown>;
    const schedules = payload.schedules as Array<Record<string, unknown>> | undefined;

    if (schedules && schedules.length > 0) {
      for (const schedule of schedules) {
        expect(typeof schedule.id).toBe("number");
        expect(typeof schedule.day_of_week).toBe("number");
        // day_of_week should be 0-6
        expect(schedule.day_of_week).toBeGreaterThanOrEqual(0);
        expect(schedule.day_of_week).toBeLessThanOrEqual(6);
      }
    }
  },
);

// ---------------------------------------------------------------------------
// APIA-004-07  Rating summary embedded in public profile is valid
// ---------------------------------------------------------------------------
test(
  "APIA-004-07 US-004 AC-004-05 Rating summary embedded in public profile returns valid average and count",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-05"],
    });

    const branchId = await getValidBranchId(request);
    if (branchId === null) {
      test.skip();
    }

    const response = await request.get(`/api/v1/clinics/branches/${branchId}`);
    expect(response.status()).toBe(200);

    const payload = (await response.json()) as Record<string, unknown>;
    const ratingSummary = payload.rating_summary;

    // rating_summary may be null if no ratings exist — that is valid
    if (ratingSummary !== null && ratingSummary !== undefined) {
      expect(typeof ratingSummary).toBe("object");
      const rs = ratingSummary as Record<string, unknown>;

      // average should be a number (or null)
      if (rs.average !== null && rs.average !== undefined) {
        expect(typeof rs.average).toBe("number");
        expect(rs.average).toBeGreaterThanOrEqual(0);
        expect(rs.average).toBeLessThanOrEqual(5);
      }

      // count should be a number
      if (rs.count !== null && rs.count !== undefined) {
        expect(typeof rs.count).toBe("number");
        expect(rs.count).toBeGreaterThanOrEqual(0);
      }
    }
  },
);

// ---------------------------------------------------------------------------
// APIA-004-08  Availability summary embedded in public profile is valid
// ---------------------------------------------------------------------------
test(
  "APIA-004-08 US-004 AC-004-06 Availability summary embedded in public profile returns valid status",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-06"],
    });

    const branchId = await getValidBranchId(request);
    if (branchId === null) {
      test.skip();
    }

    const response = await request.get(`/api/v1/clinics/branches/${branchId}`);
    expect(response.status()).toBe(200);

    const payload = (await response.json()) as Record<string, unknown>;
    const availabilitySummary = payload.availability_summary;

    // May be null — that is valid
    if (availabilitySummary !== null && availabilitySummary !== undefined) {
      expect(typeof availabilitySummary).toBe("object");
      const av = availabilitySummary as Record<string, unknown>;

      // status should be a string
      if (av.status !== null && av.status !== undefined) {
        expect(typeof av.status).toBe("string");
      }
    }
  },
);

// ---------------------------------------------------------------------------
// APIA-004-09  Invalid branch_id returns 404 without leaking internals
// ---------------------------------------------------------------------------
test(
  "APIA-004-09 US-004 AC-004-08 GET /api/v1/clinics/branches/999999 returns 404 without leaking internals",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-08"],
    });

    const response = await request.get("/api/v1/clinics/branches/999999");
    expect(response.status()).toBe(404);

    const payload = (await response.json()) as Record<string, unknown>;
    // Should have a generic detail message, not a stack trace or internal error
    expect(payload.detail || payload.error).toBeTruthy();

    // Should NOT contain sensitive information
    const responseBody = JSON.stringify(payload);
    expect(responseBody.toLowerCase()).not.toContain("traceback");
    expect(responseBody.toLowerCase()).not.toContain("exception");
    expect(responseBody.toLowerCase()).not.toContain("sqlalchemy");
  },
);

// ---------------------------------------------------------------------------
// APIA-004-10  No sensitive fields exposed in public DTO
// ---------------------------------------------------------------------------
test(
  "APIA-004-10 US-004 AC-004-09 No sensitive fields exposed in public BranchProfileDTO",
  async ({ request }, testInfo) => {
    annotateTraceability(testInfo, {
      slice: "004",
      userStory: "US-004",
      criteria: ["AC-004-09"],
    });

    const branchId = await getValidBranchId(request);
    if (branchId === null) {
      test.skip();
    }

    const response = await request.get(`/api/v1/clinics/branches/${branchId}`);
    expect(response.status()).toBe(200);

    const payload = (await response.json()) as Record<string, unknown>;
    const keys = Object.keys(payload);

    // All top-level keys should be public fields
    for (const key of keys) {
      if (!isPublicField(key)) {
        throw new Error(`Sensitive field '${key}' exposed in BranchPublicProfileDTO`);
      }
    }

    // Verify no sensitive fields in nested services
    const services = payload.services as Array<Record<string, unknown>> | undefined;
    if (services && services.length > 0) {
      for (const service of services) {
        const serviceKeys = Object.keys(service);
        for (const key of serviceKeys) {
          if (!isPublicField(key)) {
            throw new Error(`Sensitive field '${key}' exposed in ServicePublic DTO`);
          }
        }
      }
    }
  },
);
