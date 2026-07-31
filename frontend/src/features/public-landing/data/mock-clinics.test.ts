import { describe, expect, it } from "vitest";
import { mockClinics } from "@/features/public-landing/data/mock-clinics";

describe("mockClinics", () => {
  it("provides seeded clinics for the FE-001 explorer", () => {
    expect(mockClinics).toHaveLength(3);
    expect(mockClinics.map((clinic) => clinic.slug)).toEqual([
      "vet-norte",
      "estetica-santa-fe",
      "urgencias-monterrey",
    ]);
  });
});
