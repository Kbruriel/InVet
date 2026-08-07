import { test } from "@playwright/test";

import { readAutomationEnv } from "../../fixtures/env";
import { annotateTraceability, attachGherkinScenario } from "../../helpers/traceability";
import { LoginPage } from "../../pages/login.page";

const env = readAutomationEnv();

test.describe("login ui", () => {
  test.skip(
    !env.loginUiEnabled,
    "LOGIN_UI_ENABLED=false or the frontend login route is not ready yet.",
  );

  test(
    "@smoke @regression US-002-01 CA-01 login form is visible",
    async ({ page }, testInfo) => {
      annotateTraceability(testInfo, {
        slice: "002",
        userStory: "US-002-01",
        criteria: ["CA-01"],
      });
      await attachGherkinScenario(testInfo, {
        feature: "Autenticacion de usuarios",
        scenario: "Visualizacion del formulario de inicio de sesion",
        given: ["el frontend de InVet esta disponible en la ruta de login"],
        when: ["la persona visitante abre la pantalla de inicio de sesion"],
        then: ["el formulario de acceso se muestra completo y listo para capturar credenciales"],
        and: ["la evidencia del test queda trazada al slice US-002-01 / CA-01"],
      });

      const loginPage = new LoginPage(page);
      await loginPage.goto(env.loginPath);
      await loginPage.expectFormVisible();
    },
  );
});
