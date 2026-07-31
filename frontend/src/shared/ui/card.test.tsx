import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Card } from "@/shared/ui/card";

describe("Card", () => {
  it("renders children and merges custom classes", () => {
    render(<Card className="custom-card">Contenido base</Card>);

    const card = screen.getByText("Contenido base");

    expect(card).toBeInTheDocument();
    expect(card.className).toContain("custom-card");
    expect(card.className).toContain("rounded-[28px]");
  });
});
