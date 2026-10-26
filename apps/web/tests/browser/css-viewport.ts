import { expect, type Page } from "@playwright/test";

/** Windows WebKit applies the host display scale to Playwright viewport requests.
 * Normalize the test's CSS-pixel contract and assert the real layout dimensions.
 * No application styles, browser security flags or assertions are bypassed.
 */
export async function setCssViewport(page: Page, size: { width: number; height: number }) {
  const windowsWebKit = process.platform === "win32" && page.context().browser()?.browserType().name() === "webkit";
  const scale = windowsWebKit ? await page.evaluate(() => devicePixelRatio) : 1;
  await page.setViewportSize({ width: Math.round(size.width * scale), height: Math.round(size.height * scale) });
  // A blank mobile document has the browser's 980px legacy viewport until the
  // application supplies its viewport meta tag. Verify real application pages.
  if (page.url() === "about:blank") return;
  await expect.poll(() => page.evaluate(() => innerWidth)).toBe(size.width);
  await expect.poll(() => page.evaluate(() => innerHeight)).toBe(size.height);
}
