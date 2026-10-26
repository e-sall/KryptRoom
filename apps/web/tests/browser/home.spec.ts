import { test, expect, type Page, type TestInfo } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { setCssViewport } from "./css-viewport";
const problems = new WeakMap<Page, string[]>();
test.beforeEach(async ({ page }, info) => {
  await setCssViewport(page, info.project.use.viewport ?? { width: 1440, height: 900 });
  const errors: string[] = []; problems.set(page, errors);
  page.on("pageerror", e => errors.push(e.message));
  page.on("request", r => { if (r.method() !== "GET" || !r.url().startsWith("http://127.0.0.1:3000/") || /\/api\/|rpc|groth16|sepolia/i.test(r.url())) errors.push(r.method() + " " + r.url()); });
  page.on("websocket", ws => errors.push(ws.url()));
});
test.afterEach(async ({ page }) => {
  expect(problems.get(page)).toEqual([]);
  expect(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie])).toEqual([0, 0, ""]);
});
test("autoplay advances seven scenes, loops, pauses, resumes and suspends", async ({ page }) => {
  await page.clock.install(); await page.goto("/");
  const showcase = page.getByRole("region", { name: "A shared question. A protected way forward." });
  await showcase.scrollIntoViewIfNeeded(); await expect(showcase).toHaveAttribute("data-running", "true");
  for (let i = 0; i < 7; i++) { await expect(showcase).toHaveAttribute("data-scene", String(i + 1)); await page.clock.runFor(6100); }
  await expect(showcase).toHaveAttribute("data-scene", "1");
  await showcase.getByRole("button", { name: "Pause demo" }).click();
  const paused = await showcase.getAttribute("data-scene"); await page.clock.runFor(15000);
  await expect(showcase).toHaveAttribute("data-scene", paused!);
  await showcase.getByRole("button", { name: "Resume demo" }).click(); await page.clock.runFor(6100);
  await expect(showcase).not.toHaveAttribute("data-scene", paused!);
  await page.getByRole("heading", { name: "Questions & answers" }).scrollIntoViewIfNeeded();
  await expect(showcase).toHaveAttribute("data-running", "false");
  const offscreen = await showcase.getAttribute("data-scene"); await page.clock.runFor(12000); await expect(showcase).toHaveAttribute("data-scene", offscreen!);
  await showcase.scrollIntoViewIfNeeded(); await expect(showcase).toHaveAttribute("data-running", "true");
  // Exercise the real visibility listener with a deterministic hidden-tab event.
  await page.evaluate(() => { Object.defineProperty(document, "visibilityState", { configurable: true, value: "hidden" }); document.dispatchEvent(new Event("visibilitychange")); });
  await expect(showcase).toHaveAttribute("data-running", "false");
  const hidden = await showcase.getAttribute("data-scene"); await page.clock.runFor(12000); await expect(showcase).toHaveAttribute("data-scene", hidden!);
  await page.evaluate(() => { Object.defineProperty(document, "visibilityState", { configurable: true, value: "visible" }); document.dispatchEvent(new Event("visibilitychange")); });
  await expect(showcase).toHaveAttribute("data-running", "true");
  await showcase.getByRole("button", { name: "Replay demo" }).click(); await expect(showcase).toHaveAttribute("data-scene", "1");
  await expect(showcase).toHaveAttribute("data-running", "true");
});

test("showcase framing, stable scenes, section evidence and accessible FAQ", async ({ page }, info: TestInfo) => {
  test.setTimeout(180000); await page.emulateMedia({ reducedMotion: "reduce" });
  const width = info.project.use.viewport?.width ?? 1440;
  const sizes = width >= 1280 ? [[1440,900],[1366,768],[1280,800],[1024,768]] : width >= 768 ? [[834,1112],[768,1024]] : [[390,844],[375,812],[320,800]];
  for (const [w,h] of sizes) {
    await setCssViewport(page, { width: w, height: h }); await page.goto("/");
    expect(await page.evaluate(() => innerWidth)).toBe(w);
    const showcase = page.locator(".home-showcase");
    for (let i = 0; i < 7; i++) {
      await showcase.getByRole("navigation").getByRole("button").nth(i).click();
      const boxes = await showcase.locator(".showcase-window, .showcase-body, .showcase-stage, .showcase-context, .showcase-state").evaluateAll(es => es.map(e => { const r = e.getBoundingClientRect(); return { x:r.x, y:r.y, right:r.right, bottom:r.bottom, w:r.width, h:r.height, scrollH:e.scrollHeight, clientH:e.clientHeight }; }));
      const frame = boxes[0];
      for (const b of boxes.slice(1)) { expect(b.x).toBeGreaterThanOrEqual(frame.x); expect(b.right).toBeLessThanOrEqual(frame.right + 1); expect(b.y).toBeGreaterThanOrEqual(frame.y); expect(b.bottom).toBeLessThanOrEqual(frame.bottom + 1); expect(b.scrollH).toBeLessThanOrEqual(b.clientH + 1); }
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= Math.ceil(visualViewport?.width ?? innerWidth))).toBe(true);
      if (i === 0) await showcase.evaluate(e => { e.dataset.initialHeight = String(e.getBoundingClientRect().height); });
      expect(Math.abs(frame.h - Number(await showcase.locator(".showcase-window").evaluate(e => e.getBoundingClientRect().height)))).toBeLessThan(1);
      const initialHeight = Number(await showcase.getAttribute("data-initial-height"));
      expect(Math.abs((await showcase.boundingBox())!.height - initialHeight)).toBeLessThan(1);
      if ([0,3,6].includes(i)) await showcase.screenshot({ path: info.outputPath(`showcase-${w}-scene-${i + 1}.png`) });
    }
    await page.evaluate(() => scrollTo(0,0)); await page.screenshot({ path: info.outputPath(`home-${w}-viewport.png`) });
  }
  await setCssViewport(page, { width, height: info.project.use.viewport?.height ?? 900 });
  for (const [index, section] of (await page.locator(".home-page > section").all()).entries()) await section.screenshot({ path: info.outputPath(`section-${index + 1}.png`) });
  const faq = page.locator(".home-faq"); await expect(faq.locator("details")).toHaveCount(10);
  for (const summary of await faq.locator("summary").all()) {
    await summary.focus(); await page.keyboard.press("Enter"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve()))); await expect(summary.locator("..")).toHaveAttribute("open", "");
    await page.keyboard.press("Enter"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve()))); await expect(summary.locator("..")).not.toHaveAttribute("open", "");
  }
  await expect(page.locator(".home-page > section:last-child")).toHaveAttribute("aria-labelledby", "faq-title");
  await expect(page.getByAltText("Elimane Sall, founder of KryptRoom")).toBeVisible();
  expect((await new AxeBuilder({ page }).withTags(["wcag2a","wcag2aa","wcag21aa","wcag22aa"]).analyze()).violations).toEqual([]);
});

test("reduced motion and no-JavaScript keep honest static explanations", async ({ page, browser }, info) => {
  await page.clock.install(); await page.emulateMedia({ reducedMotion: "reduce" }); await page.goto("/");
  const showcase = page.locator(".home-showcase"); await showcase.scrollIntoViewIfNeeded();
  await expect(showcase).toHaveAttribute("data-running", "false"); await page.clock.runFor(20000);
  await expect(showcase).toHaveAttribute("data-scene", "1"); await expect(page.getByRole("button", { name: "Pause demo" })).toBeDisabled();
  await showcase.getByRole("navigation").getByRole("button").nth(6).click(); await expect(showcase).toHaveAttribute("data-scene", "7");
  await expect(showcase.getByText("Not assessed", { exact:true })).toBeVisible(); await expect(showcase.getByText("Not anchored", { exact:true })).toBeVisible();
  const context = await browser.newContext({ javaScriptEnabled:false, viewport:info.project.use.viewport }); const staticPage = await context.newPage();
  await setCssViewport(staticPage, info.project.use.viewport ?? { width: 1440, height: 900 }); await staticPage.goto("http://127.0.0.1:3000/"); await expect(staticPage.getByText(/This is a static synthetic collaboration diagram/)).toBeVisible();
  await expect(staticPage.getByRole("link", { name:/Open full demo/ })).toHaveAttribute("href", "/demo");
  await expect(staticPage.locator(".showcase-state")).toHaveCount(8); await context.close();
});
