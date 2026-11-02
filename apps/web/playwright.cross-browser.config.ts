import { defineConfig } from "@playwright/test";
import baseline from "./playwright.config";

// Optional local QA with the already pinned Playwright engines; CI stays unchanged.
// Windows WebKit is an engine check, not Safari/iOS device certification.
export default defineConfig({
  ...baseline,
  testMatch: ["freeze.spec.ts", "home.spec.ts"],
  outputDir: "test-results/cross-browser",
  reporter: [["list"], ["html", { outputFolder: "playwright-report/cross-browser", open: "never" }]],
  projects: (["firefox", "webkit"] as const).flatMap(browserName => [
    { name: `${browserName}-desktop`, use: { browserName, viewport: { width: 1440, height: 1000 } } },
    { name: `${browserName}-mobile`, use: { browserName, viewport: { width: 390, height: 844 }, hasTouch: true } },
  ]),
});
