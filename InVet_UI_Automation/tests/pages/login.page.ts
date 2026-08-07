import { expect, type Page } from "@playwright/test";

export class LoginPage {
  constructor(private readonly page: Page) {}

  async goto(pathname: string): Promise<void> {
    await this.page.goto(pathname);
  }

  async expectFormVisible(): Promise<void> {
    await expect(this.page.getByRole("textbox", { name: /email/i })).toBeVisible();
    await expect(this.page.getByLabel(/password/i)).toBeVisible();
    await expect(
      this.page.getByRole("button", { name: /iniciar|login|entrar/i }),
    ).toBeVisible();
  }
}

