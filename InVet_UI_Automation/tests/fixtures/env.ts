export type AutomationEnv = {
  frontendBaseUrl: string;
  apiBaseUrl: string;
  loginUiEnabled: boolean;
  loginApiEnabled: boolean;
  loginPath: string;
  loginApiPath: string;
  loginEmail: string;
  loginPassword: string;
  clinicEmail: string;
  clinicPassword: string;
  vetEmail: string;
  vetPassword: string;
  adminEmail: string;
  adminPassword: string;
};

function readBoolean(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined) {
    return fallback;
  }

  return value.toLowerCase() === "true";
}

function normalizeApiBaseUrl(value: string): string {
  const trimmed = value.replace(/\/+$/, "");
  const withoutApiV1 = trimmed.replace(/\/api\/v1$/, "");
  return withoutApiV1.replace(/^http:\/\/127\.0\.0\.1:8000$/, "http://localhost:8000");
}

export function readAutomationEnv(): AutomationEnv {
  return {
    frontendBaseUrl: process.env.FRONTEND_BASE_URL || "http://localhost:3000",
    apiBaseUrl: normalizeApiBaseUrl(process.env.API_BASE_URL || "http://localhost:8000"),
    loginUiEnabled: readBoolean(process.env.LOGIN_UI_ENABLED, true),
    loginApiEnabled: readBoolean(process.env.LOGIN_API_ENABLED, true),
    loginPath: process.env.LOGIN_PATH || "/login",
    loginApiPath: process.env.LOGIN_API_PATH || "/api/v1/auth/login",
    loginEmail: process.env.LOGIN_EMAIL || "qa@example.com",
    loginPassword: process.env.LOGIN_PASSWORD || "secret123",
    clinicEmail: process.env.CLINIC_EMAIL || "clinic@example.com",
    clinicPassword: process.env.CLINIC_PASSWORD || "secret123",
    vetEmail: process.env.VET_EMAIL || "vet@example.com",
    vetPassword: process.env.VET_PASSWORD || "secret123",
    adminEmail: process.env.ADMIN_EMAIL || "admin@example.com",
    adminPassword: process.env.ADMIN_PASSWORD || "secret123",
  };
}
