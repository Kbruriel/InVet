import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProfessionalCtaSection } from "@/features/public-landing/components/professional-cta-section";

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

describe("ProfessionalCtaSection", () => {
  it("links to clinic registration with the shared CTA", () => {
    render(<ProfessionalCtaSection />);

    expect(screen.getByText("CTA inicial")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Solicitar alta de clinica" })).toHaveAttribute(
      "href",
      "/registrar-clinica",
    );
  });
});
