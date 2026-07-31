import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HeroSection } from "@/features/public-landing/components/hero-section";

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: React.ComponentPropsWithoutRef<"a"> & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("@/features/public-landing/components/category-chips", () => ({
  CategoryChips: () => <div>Categorias</div>,
}));

vi.mock("@/features/public-landing/components/hero-bento-visual", () => ({
  HeroBentoVisual: () => <div>Visual principal</div>,
}));

vi.mock("@/features/public-landing/components/public-search-bar", () => ({
  PublicSearchBar: () => <div>Buscador publico</div>,
}));

describe("HeroSection", () => {
  it("renders the landing headline and primary CTAs", () => {
    render(<HeroSection />);

    expect(screen.getByText("Base tecnica FE-001")).toBeInTheDocument();
    expect(screen.getByText("Buscador publico")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Registrar clinica" })).toHaveAttribute(
      "href",
      "/registrar-clinica",
    );
    expect(screen.getByText("Visual principal")).toBeInTheDocument();
  });
});
