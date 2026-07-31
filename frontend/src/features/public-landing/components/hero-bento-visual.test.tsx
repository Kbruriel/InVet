import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HeroBentoVisual } from "@/features/public-landing/components/hero-bento-visual";

vi.mock("@/features/public-landing/components/api-status-card", () => ({
  ApiStatusCard: () => <div>Estado API</div>,
}));

describe("HeroBentoVisual", () => {
  it("renders the FE-001 highlights and embeds API status", () => {
    render(<HeroBentoVisual />);

    expect(screen.getByText("Rutas reales")).toBeInTheDocument();
    expect(screen.getByText("Shared UI")).toBeInTheDocument();
    expect(screen.getByText("Estado API")).toBeInTheDocument();
  });
});
