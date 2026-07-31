import { describe, expect, it } from "vitest";
import type { ClinicCardModel } from "@/entities/clinic/model";

describe("ClinicCardModel", () => {
  it("describes the FE-001 clinic card contract", () => {
    const clinic: ClinicCardModel = {
      slug: "demo",
      name: "InVet Demo",
      city: "Ciudad de Mexico",
      category: "Veterinaria",
      services: ["Consulta general"],
      badge: "Base tecnica",
      responseTime: "Responde en 10 min",
    };

    expect(clinic.slug).toBe("demo");
    expect(clinic.services).toContain("Consulta general");
  });
});
