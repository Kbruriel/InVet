import { describe, expect, it } from "vitest";
import * as landing from "@/features/public-landing";

describe("public-landing index", () => {
  it("re-exports the FE-001 public sections", () => {
    expect(typeof landing.HeroSection).toBe("function");
    expect(typeof landing.HowItWorksSection).toBe("function");
    expect(typeof landing.ProfessionalCtaSection).toBe("function");
  });
});
