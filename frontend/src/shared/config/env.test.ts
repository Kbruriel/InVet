import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("env", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  afterEach(() => {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;
  });

  it("uses the default API base URL when no environment variable exists", async () => {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;

    const { env } = await import("@/shared/config/env");

    expect(env.apiBaseUrl).toBe("http://localhost:8000");
  });

  it("trims trailing slashes from the configured API base URL", async () => {
    process.env.NEXT_PUBLIC_API_BASE_URL = "https://api.invet.test///";

    const { env } = await import("@/shared/config/env");

    expect(env.apiBaseUrl).toBe("https://api.invet.test");
  });
});
