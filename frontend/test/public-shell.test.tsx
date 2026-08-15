// Mock Next.js navigation hooks used by CategoryChips BEFORE any imports
jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

// Mock CategoryChips to avoid router issues in shell test
jest.mock("@/features/public-landing/components/CategoryChips", () => ({
  CategoryChips: () => <div data-testid="category-chips">Categorias</div>,
}));

import { render, screen } from "@testing-library/react";

import HomePage from "@/app/page";
import { PublicFooter } from "@/features/public-landing/components/PublicFooter";
import { PublicHeader } from "@/features/public-landing/components/PublicHeader";

describe("public shell", () => {
  it("renders the home entry page with hero and CTA", () => {
    render(<HomePage />);

    expect(
      screen.getByText(/encuentra la clinica ideal/i),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /registrar clinica/i })).toHaveAttribute(
      "href",
      "/register",
    );
    expect(screen.getByRole('link', { name: /ver clínicas/i })).toHaveAttribute(
      "href",
      "/clinicas",
    );
  });

  it("renders the public header links", () => {
    render(<PublicHeader />);

    expect(screen.getByRole("link", { name: /InVet, ir al inicio/i })).toHaveAttribute(
      "href",
      "/",
    );
    expect(screen.getByRole("link", { name: /iniciar sesion/i })).toHaveAttribute(
      "href",
      "/login",
    );
    expect(screen.getByRole("link", { name: /registrarse/i })).toHaveAttribute(
      "href",
      "/register",
    );
    expect(screen.getAllByRole("link")).toHaveLength(6);
  });

  it("renders the public footer", () => {
    render(<PublicFooter />);

    expect(
      screen.getByText(/InVet\. Todos los derechos reservados\./i),
    ).toBeInTheDocument();
  });
});
