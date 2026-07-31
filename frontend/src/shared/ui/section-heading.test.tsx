import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SectionHeading } from "@/shared/ui/section-heading";

describe("SectionHeading", () => {
  it("renders eyebrow, title and description", () => {
    render(
      <SectionHeading
        eyebrow="Explora"
        title="Titulo principal"
        description="Descripcion de apoyo"
      />,
    );

    expect(screen.getByText("Explora")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Titulo principal" })).toBeVisible();
    expect(screen.getByText("Descripcion de apoyo")).toBeInTheDocument();
  });
});
