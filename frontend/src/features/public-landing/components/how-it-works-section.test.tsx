import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HowItWorksSection } from "@/features/public-landing/components/how-it-works-section";

describe("HowItWorksSection", () => {
  it("renders the three onboarding steps of FE-001", () => {
    render(<HowItWorksSection />);

    expect(screen.getByText("Paso 1")).toBeInTheDocument();
    expect(screen.getByText("Explora servicios")).toBeInTheDocument();
    expect(screen.getByText("Escala con confianza")).toBeInTheDocument();
  });
});
