import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiStatusCard } from "@/features/public-landing/components/api-status-card";

const { getApiRoot } = vi.hoisted(() => ({
  getApiRoot: vi.fn(),
}));

vi.mock("@/shared/api/http-client", () => {
  class ApiError extends Error {
    status: number;
    payload: unknown;

    constructor(status: number, message: string, payload: unknown) {
      super(message);
      this.name = "ApiError";
      this.status = status;
      this.payload = payload;
    }
  }

  return {
    ApiError,
    getApiRoot,
  };
});

describe("ApiStatusCard", () => {
  beforeEach(() => {
    getApiRoot.mockReset();
  });

  it("renders the API success state", async () => {
    getApiRoot.mockResolvedValue({ message: "API lista" });

    render(<ApiStatusCard />);

    expect(screen.getByText("Cargando estado")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Conexion preparada")).toBeInTheDocument();
    });

    expect(screen.getByText("API lista")).toBeInTheDocument();
  });

  it("renders the API error state when the request fails", async () => {
    getApiRoot.mockRejectedValue(new Error("Fallo inesperado"));

    render(<ApiStatusCard />);

    await waitFor(() => {
      expect(
        screen.getByText("Backend no disponible en este momento"),
      ).toBeInTheDocument();
    });

    expect(
      screen.getByText("No fue posible leer el estado base del API."),
    ).toBeInTheDocument();
  });
});
