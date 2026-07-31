import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PublicShell } from "@/shared/layout/public-shell";

vi.mock("@/features/public-landing/components/public-header", () => ({
  PublicHeader: () => <div>Header publico</div>,
}));

vi.mock("@/features/public-landing/components/public-footer", () => ({
  PublicFooter: () => <div>Footer publico</div>,
}));

describe("PublicShell", () => {
  it("renders the shared header, content and footer", () => {
    render(
      <PublicShell>
        <section>Contenido principal</section>
      </PublicShell>,
    );

    expect(screen.getByText("Header publico")).toBeInTheDocument();
    expect(screen.getByText("Contenido principal")).toBeInTheDocument();
    expect(screen.getByText("Footer publico")).toBeInTheDocument();
  });
});
