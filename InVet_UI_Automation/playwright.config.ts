import { defineConfig, devices, type ReporterDescription } from "@playwright/test";
import dotenv from "dotenv";

dotenv.config();

const ci = Boolean(process.env.CI);
const frontendBaseUrl = process.env.FRONTEND_BASE_URL || "http://127.0.0.1:3001";
const apiBaseUrl = process.env.API_BASE_URL || "http://127.0.0.1:8000";
const uiLifecycleEvents = new Set([
  "test:e2e",
  "test:e2e:all-browsers",
  "test:smoke",
  "test:regression",
  "test:regression:all-browsers",
  "check:ui",
  "check",
]);
const shouldStartFrontend =
  process.env.PLAYWRIGHT_START_FRONTEND === "true" ||
  uiLifecycleEvents.has(process.env.npm_lifecycle_event || "");

function frontendPort(): string {
  return new URL(frontendBaseUrl).port || "3000";
}

const reporters: ReporterDescription[] = [
  ["list"],
  ["html", { open: "never", outputFolder: "playwright-report" }],
];

if (ci) {
  reporters.push(["junit", { outputFile: "test-results/junit/results.xml" }]);
}

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: ci,
  retries: ci ? 2 : 0,
  workers: ci ? 2 : undefined,
  timeout: 60_000,
  reporter: reporters,
  webServer: shouldStartFrontend
    ? {
        command: `npm run dev -- --hostname 127.0.0.1 --port ${frontendPort()}`,
        cwd: "../frontend",
        url: frontendBaseUrl,
        reuseExistingServer: !ci,
        timeout: 120_000,
      }
    : undefined,
  use: {
    locale: "es-MX",
    timezoneId: "America/Monterrey",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "api",
      testMatch: /api\/.*\.spec\.ts/,
      use: {
        baseURL: apiBaseUrl,
        extraHTTPHeaders: {
          Accept: "application/json",
        },
      },
    },
    {
      name: "chromium",
      testMatch: /e2e\/.*\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        baseURL: frontendBaseUrl,
        locale: "es-MX",
        timezoneId: "America/Monterrey",
      },
    },
    {
      name: "firefox",
      testMatch: /e2e\/.*\.spec\.ts/,
      use: {
        ...devices["Desktop Firefox"],
        baseURL: frontendBaseUrl,
        locale: "es-MX",
        timezoneId: "America/Monterrey",
      },
    },
    {
      name: "webkit",
      testMatch: /e2e\/.*\.spec\.ts/,
      use: {
        ...devices["Desktop Safari"],
        baseURL: frontendBaseUrl,
        locale: "es-MX",
        timezoneId: "America/Monterrey",
      },
    },
    {
      name: "mobile-chromium",
      testMatch: /e2e\/.*\.spec\.ts/,
      use: {
        ...devices["Pixel 7"],
        baseURL: frontendBaseUrl,
        locale: "es-MX",
        timezoneId: "America/Monterrey",
      },
    },
  ],
});
