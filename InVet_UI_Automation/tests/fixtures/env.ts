export type AutomationEnv = {
  frontendBaseUrl: string;
  apiBaseUrl: string;
  loginUiEnabled: boolean;
  loginApiEnabled: boolean;
  loginPath: string;
  loginApiPath: string;
  loginEmail: string;
  loginPassword: string;
};

function readBoolean(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined) {
    return fallback;
  }

  return value.toLowerCase() === "true";
}

export function readAutomationEnv(): AutomationEnv {
  return {
    frontendBaseUrl: process.env.FRONTEND_BASE_URL || "http://127.0.0.1:3000",
    apiBaseUrl: process.env.API_BASE_URL || "http://127.0.0.1:8000",
    loginUiEnabled: readBoolean(process.env.LOGIN_UI_ENABLED, true),
    loginApiEnabled: readBoolean(process.env.LOGIN_API_ENABLED, true),
    loginPath: process.env.LOGIN_PATH || "/login",
    loginApiPath: process.env.LOGIN_API_PATH || "/api/v1/auth/login",
    loginEmail: process.env.LOGIN_EMAIL || "qa@example.com",
    loginPassword: process.env.LOGIN_PASSWORD || "secret123",
  };
}
