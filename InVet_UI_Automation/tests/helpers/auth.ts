import { expect, type Page } from "@playwright/test";

import { readAutomationEnv } from "../fixtures/env";

const env = readAutomationEnv();

export async function authenticateAs(page: Page, email: string, password: string) {
  const loginUrl = `${env.apiBaseUrl}${env.loginApiPath}`;
  const response = await page.request.post(loginUrl, {
    data: { email, password },
  });

  expect(response.status()).toBe(200);

  const payload = (await response.json()) as { access_token: string; refresh_token: string };
  await page.addInitScript(
    ({ accessToken, refreshToken }) => {
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("refresh_token", refreshToken);
    },
    {
      accessToken: payload.access_token,
      refreshToken: payload.refresh_token,
    },
  );
}

export async function authenticateAdmin(page: Page) {
  await authenticateAs(page, env.adminEmail, env.adminPassword);
}
