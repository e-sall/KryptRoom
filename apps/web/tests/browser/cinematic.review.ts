import { test, expect, type Page } from "@playwright/test";
import { offsets, duration } from "../../src/features/marketing/cinematic/timeline";

async function open(page: Page) {
  await page.goto("/demo");
  await page.waitForFunction(() => !!window.kryptroomMovieReview);
  await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(() => {
    const target = document.querySelector("#product-walkthrough")!;
    window.scrollTo(0, window.scrollY + target.getBoundingClientRect().top - 90);
  });
}
async function seek(page: Page, time: number) { await page.evaluate(t => window.kryptroomMovieReview!.seek(t), time); }
async function painted(page: Page) {
  return page.evaluate(() => [...document.querySelectorAll('[data-movie-paint] > *')]
    .filter(e => e.getAttribute("display") !== "none" && Number(e.getAttribute("opacity")) > .0001)
    .map(e => ({ tag: e.tagName, text: e.textContent, attrs: [...e.attributes].map(a => [a.name, a.value]).sort() })));
}

test("single SVG, original narrative, deterministic reverse seeks and every seam", async ({ page }) => {
  const errors: string[] = []; page.on("pageerror", e => errors.push(e.message));
  await open(page);
  await expect(page.locator("#product-walkthrough svg")).toHaveCount(1);
  await expect(page.locator("#product-walkthrough button, #product-walkthrough input, #product-walkthrough [tabindex], #product-walkthrough [role=button], #product-walkthrough audio")).toHaveCount(0);
  const surface = await page.locator("#product-walkthrough svg").elementHandle();
  const cursor = await page.locator("[data-movie-cursor]").elementHandle();
  // Authored press targets, including workspace switches and the missing-source adaptation.
  // A single canonical pointer must arrive at each target at the original click time.
  for (const [clip, local, x, y] of [
    [0,2120,80,583],[0,3850,126,477],[1,1900,651,506],
    [1,4540,81,585],[1,5800,127,471],[2,1960,627,500],
    [3,2040,869,501],[4,5320,92,293],[5,1940,957,513],
    [6,5750,97,344],[7,2010,325,490],[8,740,930,511],
    [9,1140,933,510],[9,6380,720,490],[11,2050,362,474],
  ]) {
    await seek(page, offsets[clip] + local);
    const pointer = await cursor!.evaluate(e => ({
      position: (e.getAttribute("transform")!.match(/-?[\d.]+/g) || []).map(Number),
      opacity: Number(e.getAttribute("opacity")),
    }));
    expect(pointer.position[0]).toBeCloseTo(x, 1);
    expect(pointer.position[1]).toBeCloseTo(y, 1);
    expect(pointer.opacity).toBeGreaterThan(.9);
  }
  for (const t of [0, 4000, 14000, 21000, 30000, 38000, 46000, 55000, 64000, 68000, 77000, 84000, 92400]) {
    await seek(page, t); const first = await painted(page);
    await seek(page, duration - t); await seek(page, t);
    expect(await painted(page), `history-independent frame ${t}`).toEqual(first);
    expect(first.length).toBeGreaterThan(60);
  }
  for (const t of offsets.slice(1)) {
    for (const d of [-200, -16, 0, 16, 200]) {
      await seek(page, t + d);
      expect(await surface!.evaluate(e => e === document.querySelector("#product-walkthrough svg"))).toBe(true);
      expect(await cursor!.evaluate(e => e === document.querySelector("[data-movie-cursor]"))).toBe(true);
      expect((await painted(page)).length).toBeGreaterThan(60);
    }
  }
  await seek(page, 55000);
  const gallery = (await painted(page)).map(s => s.text).join(" ");
  expect(gallery).toContain("Ready"); expect(gallery.match(/NOT RUN/g)).toHaveLength(2);
  expect(gallery).not.toContain("Total risk signals");
  await seek(page, 84000);
  const insights = (await painted(page)).map(s => s.text).join(" ");
  expect(insights).toContain("6 / 12"); expect(insights).toContain("4 / 12"); expect(insights).toContain("2 / 12");
  expect(insights).toContain("Prioritize joint mitigation");
  await seek(page, duration);
  const final = (await painted(page)).map(s => s.text).join(" ");
  expect(final.match(/Review action/g)).toHaveLength(3);
  expect(final).toContain("Monitor shared risk");
  expect(errors).toEqual([]);
});

test("09→10 modifies only the right panel; Ask AI types one line; Week 1 click hits its card", async ({ page }) => {
  await open(page);
  const left = async () => (await painted(page)).filter(s => {
    const a = Object.fromEntries(s.attrs); const x = Number(a.x || a.cx || 0);
    return x >= 212 && x < 775;
  });
  await seek(page, 64900); const overview = await left();
  for (const t of [65000, 65640, 65900, 66550, 68200, 69000]) {
    await seek(page, t); expect(await left(), `stationary left dashboard ${t}`).toEqual(overview);
  }
  await seek(page, 68200 + 5499);
  const typed = await page.locator('[data-movie-paint] text').evaluateAll(nodes => nodes.filter(e => e.getAttribute("display") !== "none" && e.textContent?.startsWith("What's driving"))
    .map(e => ({ text: e.textContent, children: e.children.length, rect: e.getBoundingClientRect().toJSON() })));
  expect(typed).toHaveLength(1); expect(typed[0].children).toBe(0);
  expect(typed[0].rect.width).toBeLessThan(700);
  await seek(page, 84800 + 2050);
  await expect(page.locator('[data-movie-cursor]')).toHaveAttribute("transform", /translate\(362(?:\.\d+)? 474(?:\.\d+)?\)/);
});

test("autoplay suspends offscreen and in a hidden tab without catch-up", async ({ page }) => {
  await open(page);
  await page.waitForTimeout(350);
  const a = await page.evaluate(() => window.kryptroomMovieReview!.time());
  await page.waitForTimeout(350);
  expect(await page.evaluate(() => window.kryptroomMovieReview!.time())).toBeGreaterThan(a);
  // The film is now the last /demo section: the page top, rather than its
  // bottom, genuinely takes it outside the viewport.
  await page.evaluate(() => window.scrollTo(0, 0));
  await expect(page.locator('#product-walkthrough')).not.toBeInViewport();
  await page.waitForTimeout(200);
  const b = await page.evaluate(() => window.kryptroomMovieReview!.time());
  await page.waitForTimeout(350);
  expect(await page.evaluate(() => window.kryptroomMovieReview!.time())).toBe(b);
  await page.evaluate(() => {
    const target = document.querySelector("#product-walkthrough")!;
    window.scrollTo(0, window.scrollY + target.getBoundingClientRect().top - 90);
    Object.defineProperty(document, "hidden", { configurable: true, value: true });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await page.waitForTimeout(100);
  const c = await page.evaluate(() => window.kryptroomMovieReview!.time());
  await page.waitForTimeout(350);
  expect(await page.evaluate(() => window.kryptroomMovieReview!.time())).toBe(c);
  await page.evaluate(() => { Reflect.deleteProperty(document, "hidden"); document.dispatchEvent(new Event("visibilitychange")); });
  await page.waitForTimeout(200);
  const resumed = await page.evaluate(() => window.kryptroomMovieReview!.time());
  expect(resumed).toBeGreaterThan(c); expect(resumed - c).toBeLessThan(300);
});
