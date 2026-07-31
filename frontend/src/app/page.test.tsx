import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import HomePage from "@/app/page";
import ClinicsPage from "@/app/clinicas/page";
import SignInPage from "@/app/iniciar-sesion/page";
import RegisterClinicPage from "@/app/registrar-clinica/page";
import RegisterPage from "@/app/registrarse/page";

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

vi.mock("@/shared/layout/public-shell", () => ({
  PublicShell: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="public-shell">{children}</div>
  ),
}));

vi.mock("@/features/public-landing", () => ({
  HeroSection: () => <section>Hero FE-001</section>,
  HowItWorksSection: () => <section>Como funciona FE-001</section>,
  ProfessionalCtaSection: () => <section>CTA FE-001</section>,
}));

vi.mock("@/features/public-landing/components/clinic-card", () => ({
  ClinicCard: ({ clinic }: { clinic: { name: string } }) => <article>{clinic.name}</article>,
}));

describe("FE-001 pages", () => {
  it("renders the home page shell", () => {
    render(<HomePage />);

    expect(screen.getByTestId("public-shell")).toBeInTheDocument();
    expect(screen.getByText("Hero FE-001")).toBeInTheDocument();
    expect(screen.getByText("CTA FE-001")).toBeInTheDocument();
  });

  it("renders the clinics explorer with filtered results", async () => {
    const page = await ClinicsPage({
      searchParams: Promise.resolve({ query: "Monterrey", category: "Urgencias" }),
    });

    render(page);

    expect(screen.getByText("Resultados: 1")).toBeInTheDocument();
    expect(screen.getByText("InVet Monterrey 24h")).toBeInTheDocument();
  });

  it("renders the empty state when no clinics match the filters", async () => {
    const page = await ClinicsPage({
      searchParams: Promise.resolve({ query: "desconocido" }),
    });

    render(page);

    expect(
      screen.getByText("No encontramos coincidencias todavia"),
    ).toBeInTheDocument();
  });

  it("renders the sign-in placeholder route", () => {
    render(<SignInPage />);

    expect(
      screen.getByText("Inicio de sesion preparado para slices posteriores"),
    ).toBeInTheDocument();
  });

  it("renders the clinic registration placeholder route", () => {
    render(<RegisterClinicPage />);

    expect(screen.getByText("Onboarding de clinicas en preparacion")).toBeInTheDocument();
  });

  it("renders the registration placeholder route", () => {
    render(<RegisterPage />);

    expect(screen.getByText("Registro base listo para crecer")).toBeInTheDocument();
  });
});
