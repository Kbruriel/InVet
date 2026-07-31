import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PublicHeader } from "@/features/public-landing/components/public-header";

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

describe("PublicHeader", () => {
  it("renders the brand and public navigation links", () => {
    render(<PublicHeader />);

    expect(screen.getByText("InVet")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Clinicas" })).toHaveAttribute(
      "href",
      "/clinicas",
    );
    expect(screen.getByRole("link", { name: "Registrarse" })).toHaveAttribute(
      "href",
      "/registrarse",
    );
  });
});
