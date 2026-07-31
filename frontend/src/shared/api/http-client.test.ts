import { afterEach, describe, expect, it, vi } from "vitest";
import { apiGet, getApiRoot } from "@/shared/api/http-client";

describe("http-client", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("calls the API root with a normalized absolute URL", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(
        new Response(JSON.stringify({ message: "API lista" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      );

    await expect(getApiRoot()).resolves.toEqual({ message: "API lista" });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/",
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({ Accept: "application/json" }),
      }),
    );
  });

  it("raises ApiError with backend detail when the request fails", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "Token invalido" }), {
        status: 401,
        headers: { "content-type": "application/json" },
      }),
    );

    await expect(apiGet("/private")).rejects.toMatchObject(
      expect.objectContaining({
        name: "ApiError",
        status: 401,
        message: "Token invalido",
        payload: { detail: "Token invalido" },
      }),
    );
  });
});
