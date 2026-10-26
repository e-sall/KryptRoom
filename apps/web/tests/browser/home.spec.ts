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

test("review F01: showcase title clears the floating navbar with the complete desktop frame", async ({ page }, info) => {
  const desktop = (info.project.use.viewport?.width ?? 1440) >= 1200;
  for (const [width,height] of desktop ? [[1440,900],[1366,768]] : [[info.project.use.viewport!.width,info.project.use.viewport!.height]]) {
    await setCssViewport(page,{width,height}); await page.emulateMedia({reducedMotion:"reduce"}); await page.goto("/");
    await page.locator(".home-showcase").evaluate(e => scrollTo(0,scrollY+e.getBoundingClientRect().top-document.querySelector(".marketing-navbar")!.getBoundingClientRect().bottom-16));
    const rects = await page.locator(".marketing-navbar, .showcase-heading, #showcase-title, .showcase-window").evaluateAll(es => es.map(e => e.getBoundingClientRect().toJSON()));
    const [nav,heading,title,frame] = rects;
    expect(heading.top).toBeGreaterThanOrEqual(nav.bottom + 15);
    expect(title.top).toBeGreaterThanOrEqual(nav.bottom + 15);
    expect(title.bottom).toBeLessThan(frame.top);
    expect(title.left).toBeGreaterThanOrEqual(0); expect(title.right).toBeLessThanOrEqual(width);
    if (desktop) expect(frame.bottom).toBeLessThanOrEqual(height);
    await page.screenshot({path:info.outputPath(`review-heading-${width}.png`)});
  }
});

test("review F02: automatic storytelling progressively reveals inputs, operation and exact lineage", async ({page}) => {
  await page.clock.install(); await page.goto("/");
  const show = page.locator(".home-showcase"); await show.scrollIntoViewIfNeeded(); await expect(show).toHaveAttribute("data-running","true");
  const initial = await show.locator(".showcase-stage").boundingBox();
  for(let scene=0;scene<7;scene++) {
    await expect(show).toHaveAttribute("data-scene",String(scene+1));
    const inputs=show.locator(".showcase-protected-inputs"), operation=show.locator(".showcase-operation"), lineage=show.locator(".showcase-lineage");
    if(scene>=1) await expect(inputs).toBeVisible(); else await expect(inputs).toBeHidden();
    if(scene>=2) await expect(operation).toBeVisible(); else await expect(operation).toBeHidden();
    if(scene>=3) await expect(lineage).toBeVisible(); else await expect(lineage).toBeHidden();
    if(scene>=3) {
      expect(await show.locator(".showcase-state small").allTextContents()).toEqual(["Parents: None","Parents: S1","Parents: S1","Parents: S2 · S3"]);
      await expect(show.locator(".showcase-state")).toHaveCount(4);
    }
    if(scene===4) await expect(show.locator(".showcase-story-note")).toContainText("not a grant or a disclosed value");
    if(scene===5) await expect(show.locator(".showcase-story-note")).toContainText("No proof or chain record");
    if(scene===6) await expect(show.locator(".showcase-story-note")).toContainText("existing synthetic Supply Chain states");
    expect((await show.locator(".showcase-stage").boundingBox())!.height).toBe(initial!.height);
    await page.clock.runFor(6100);
  }
});

test("review F03: narrow ordered state cards have readable noncolliding labels", async ({page}) => {
  await page.emulateMedia({reducedMotion:"reduce"});
  for(const width of [320,375,390]) {
    await setCssViewport(page,{width,height:844}); await page.goto("/");
    const show=page.locator(".home-showcase"); await show.locator(".showcase-scenes button").nth(6).click();
    const labels=await show.locator(".showcase-state > span, .showcase-state strong > span, .showcase-state small, .showcase-context dt, .showcase-context dd").evaluateAll(es=>es.map(e=>({font:parseFloat(getComputedStyle(e).fontSize),rect:e.getBoundingClientRect().toJSON(),parent:e.parentElement!.getBoundingClientRect().toJSON(),overflow:e.scrollWidth>e.clientWidth+1})));
    for(const label of labels) {expect(label.font).toBeGreaterThanOrEqual(12);expect(label.rect.left).toBeGreaterThanOrEqual(label.parent.left);expect(label.rect.right).toBeLessThanOrEqual(label.parent.right+1);expect(label.overflow).toBe(false);}
    for(const state of await show.locator(".showcase-state").all()) {
      // Explicit line boxes also cover hidden monospace metrics before the
      // first screenshot/font resolution on Linux, without relaxing stability.
      expect(await state.locator("strong, strong > span").evaluateAll(es=>es.map(e=>getComputedStyle(e).lineHeight))).toEqual(["20px","20px"]);
      const lines=await state.locator(":scope > span, :scope > strong, :scope > small").evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));
      for(let i=1;i<lines.length;i++) expect(lines[i].top).toBeGreaterThanOrEqual(lines[i-1].bottom);
    }
    const cards=await show.locator(".showcase-state").evaluateAll(es=>es.map(e=>e.getBoundingClientRect().toJSON()));
    for(let i=1;i<cards.length;i++) expect(cards[i].top).toBeGreaterThan(cards[i-1].bottom);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=Math.ceil(visualViewport?.width??innerWidth))).toBe(true);
  }
});

test("review F04: original portrait uses local responsive optimization without layout shift", async ({page}) => {
  let release!:()=>void; const gate=new Promise<void>(resolve=>{release=resolve;});
  await page.route("**/_next/image?**",async route=>{await gate;await route.continue();});
  const response=page.waitForResponse(r=>r.url().includes("/_next/image?"));
  await page.goto("/",{waitUntil:"domcontentloaded"});
  const portrait=page.getByAltText("Elimane Sall, founder of KryptRoom"); await portrait.scrollIntoViewIfNeeded();
  const before=await portrait.boundingBox(); release(); const delivered=await response;
  expect(delivered.status()).toBe(200); expect(delivered.headers()["content-type"]).toMatch(/^image\//);
  expect((await delivered.body()).length).toBeLessThan(300000);
  await portrait.evaluate(async e=>{await (e as HTMLImageElement).decode();});
  const url=new URL(await portrait.evaluate(e=>(e as HTMLImageElement).currentSrc));
  expect(url.pathname).toBe("/_next/image");expect(url.searchParams.get("url")).toBe("/images/elimane-sall.jpeg");
  expect(Number(url.searchParams.get("w"))).toBeLessThanOrEqual(1080);
  await expect(portrait).toHaveAttribute("srcset",/640w/);await expect(portrait).toHaveAttribute("width","3367");await expect(portrait).toHaveAttribute("height","3958");
  const after=await portrait.boundingBox();expect(after!.width).toBe(before!.width);expect(after!.height).toBe(before!.height);
  expect(await portrait.evaluate(e=>({fit:getComputedStyle(e).objectFit,position:getComputedStyle(e).objectPosition}))).toEqual({fit:"cover",position:"50% 35%"});
});
