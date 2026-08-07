import { render, screen } from "@testing-library/react";

import HomePage from "@/app/page";
import { PublicFooter } from "@/features/public-landing/components/PublicFooter";
import { PublicHeader } from "@/features/public-landing/components/PublicHeader";

describe("public shell", () => {
  it("renders the home entry page", () => {
    render(<HomePage />);

    expect(
      screen.getByRole("heading", { name: /Bienvenido a InVet/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Iniciar/i })).toHaveAttribute(
      "href",
      "/login",
    );
    expect(screen.getByRole("link", { name: /Explorar/i })).toHaveAttribute(
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
    expect(screen.getAllByRole("link")).toHaveLength(4);
  });

  it("renders the public footer", () => {
    render(<PublicFooter />);

    expect(
      screen.getByText(/InVet\. Todos los derechos reservados\./i),
    ).toBeInTheDocument();
  });
});
