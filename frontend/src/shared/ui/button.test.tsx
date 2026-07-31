import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Button, buttonClassName } from "@/shared/ui/button";

describe("buttonClassName", () => {
  it("returns styles for variant and size", () => {
    expect(buttonClassName({ variant: "secondary", size: "lg" })).toContain(
      "ring-1",
    );
    expect(buttonClassName({ variant: "secondary", size: "lg" })).toContain(
      "min-h-12",
    );
  });
});

describe("Button", () => {
  it("renders a button with a safe default type", () => {
    render(<Button>Continuar</Button>);

    const button = screen.getByRole("button", { name: "Continuar" });

    expect(button).toHaveAttribute("type", "button");
    expect(button.className).toContain("rounded-full");
  });
});
