import { describe, expect, it } from "vitest";
import { routes } from "@/shared/config/routes";

describe("routes", () => {
  it("exposes the public FE-001 routes without placeholders", () => {
    expect(routes).toEqual({
      home: "/",
      clinics: "/clinicas",
      signIn: "/iniciar-sesion",
      register: "/registrarse",
      registerClinic: "/registrar-clinica",
    });
  });
});
