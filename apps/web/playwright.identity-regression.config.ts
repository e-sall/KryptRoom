import { defineConfig } from "@playwright/test";
import baseline from "./playwright.config";

// Run the unchanged M8 assertions against the separately started local image.
export default defineConfig({
  ...baseline,
  webServer: undefined,
  reporter: [["line"]],
  outputDir: "/run/browser-tmp/m8-results",
});
