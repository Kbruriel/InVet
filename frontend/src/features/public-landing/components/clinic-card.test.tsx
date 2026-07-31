import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClinicCard } from "@/features/public-landing/components/clinic-card";

describe("ClinicCard", () => {
  it("renders the clinic summary and services", () => {
    render(
      <ClinicCard
        clinic={{
          slug: "norte",
          name: "InVet Norte",
          city: "Ciudad de Mexico",
          category: "Veterinaria",
          services: ["Consulta general", "Vacunacion"],
          badge: "Agenda guiada",
          responseTime: "Responde en 10 min",
        }}
      />,
    );

    expect(screen.getByText("InVet Norte")).toBeInTheDocument();
    expect(screen.getByText("Agenda guiada")).toBeInTheDocument();
    expect(screen.getByText("Vacunacion")).toBeInTheDocument();
  });
});
