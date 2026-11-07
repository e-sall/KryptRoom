import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests-identity", fullyParallel: false, workers: 1, retries: 0,
  timeout: 300000, expect: {timeout: 15000},
  use: {baseURL: "http://127.0.0.1:3004", actionTimeout: 15000, navigationTimeout: 15000,
    trace: "off", screenshot: "off", video: "off",
    launchOptions: {args: process.env.KR_TEST_TLS_SPKI ?
      [`--ignore-certificate-errors-spki-list=${process.env.KR_TEST_TLS_SPKI}`] : []}},
  reporter: [["line"]],
});
