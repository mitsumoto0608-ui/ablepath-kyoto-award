import { defineConfig, devices } from "@playwright/test";
const port = process.env.ABLEPATH_E2E_PORT ?? "4173";
const fixturePort = process.env.ABLEPATH_E2E_FIXTURE_PORT ?? "4175";

export default defineConfig({
  testDir: "tests",
  testMatch: "*.spec.mjs",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  retries: 0,
  reporter: [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]],
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    reducedMotion: "reduce",
  },
  webServer: [
    {
      command: `npm run build && npm run preview -- --port ${port}`,
      url: `http://127.0.0.1:${port}`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: `npx vite --host 127.0.0.1 --port ${fixturePort}`,
      url: `http://127.0.0.1:${fixturePort}/tests/fixtures/verified-cesium.html`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
  projects: [
    { name: "desktop-chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-chromium", use: { ...devices["Pixel 7"] } },
  ],
  outputDir: "test-results",
});
