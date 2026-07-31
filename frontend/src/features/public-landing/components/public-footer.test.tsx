import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PublicFooter } from "@/features/public-landing/components/public-footer";

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

describe("PublicFooter", () => {
  it("renders the footer links for the FE-001 shell", () => {
    render(<PublicFooter />);

    expect(screen.getByText("Base tecnica y design system inicial para el flujo de producto.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Registrar clinica" })).toHaveAttribute(
      "href",
      "/registrar-clinica",
    );
  });
});
