import { test, expect, type Page, type TestInfo } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { setCssViewport } from "./css-viewport";

const room = "/preview/rooms/supply-chain";
const problems = new WeakMap<Page, string[]>();
test.beforeEach(async ({ page }, info) => {
  await setCssViewport(page, info.project.use.viewport ?? { width: 1440, height: 900 });
  const errors: string[] = []; problems.set(page, errors);
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("request", (r) => {
    if (r.method() !== "GET" || !r.url().startsWith("http://127.0.0.1:3000/") || /\/api\/|rpc|groth16|sepolia/i.test(r.url())) errors.push(r.method() + " " + r.url());
  });
  page.on("websocket", (ws) => errors.push(ws.url()));
});
test.afterEach(async ({ page }) => {
  expect(problems.get(page)).toEqual([]);
  expect(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie])).toEqual([0, 0, ""]);
});
async function capture(page: Page, info: TestInfo, name: string) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= Math.ceil(visualViewport?.width ?? innerWidth))).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]).analyze()).violations).toEqual([]);
  await page.screenshot({ path: info.outputPath(name + ".png"), fullPage: !(await page.getByRole("dialog").count()) });
}

test("mobile keyboard focus clears bottom navigation", async ({ page }, info) => {
  await setCssViewport(page, { width: 390, height: 844 }); await page.goto("/preview/rooms");
  await page.getByRole("button", { name: "Cards", exact: true }).click();
  await page.getByRole("button", { name: "List", exact: true }).click();
  await page.getByLabel("Search Rooms").focus();
  for (let i = 0; i < 18; i++) {
    await page.keyboard.press("Tab"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve())));
    const focus = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement;
      if (!el.matches("button,a,input,select,summary") || el.closest(".mobile-bottom-nav")) return null;
      const box = el.getBoundingClientRect();
      return { name: el.getAttribute("aria-label") || el.textContent, top: box.top, bottom: box.bottom,
        nav: document.querySelector(".mobile-bottom-nav")!.getBoundingClientRect().top };
    });
    if (focus) {
      // Keep the failing frame as before evidence when running against the baseline.
      if (focus.bottom > focus.nav) await page.screenshot({ path: info.outputPath("focus-bottom-nav.png") });
      expect(focus.bottom, String(focus.name)).toBeLessThanOrEqual(focus.nav);
      expect(focus.top, String(focus.name)).toBeGreaterThanOrEqual(0);
    }
  }
  await page.getByRole("button", { name: "Expand Research Partnership" }).focus();
  await page.screenshot({ path: info.outputPath("focus-bottom-nav.png") });
});

test("rotation retires modal sheet, preserves state and restores visible focus", async ({ page }, info) => {
  await setCssViewport(page, { width: 390, height: 844 }); await page.goto(room + "/workspace/S4");
  await page.getByRole("button", { name: "Workspace details", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("Private Analytics");
  await setCssViewport(page, { width: 834, height: 1112 });
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.locator("main")).toBeFocused();
  expect(await page.evaluate(() => document.body.style.overflow)).not.toBe("hidden");
  await expect(page.getByLabel("Context inspector")).toContainText("Private Analytics");
  await capture(page, info, "sheet-rotation");
  await setCssViewport(page, { width: 766, height: 700 });
  const trigger = page.getByRole("button", { name: "Workspace details", exact: true });
  await trigger.click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Close workspace details" }).focus();
  await page.keyboard.press("Shift+Tab"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve()))); expect(await dialog.evaluate(e => e.contains(document.activeElement))).toBe(true);
  await page.keyboard.press("Tab"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve()))); await expect(dialog.getByRole("button", { name: "Close workspace details" })).toBeFocused();
  await page.keyboard.press("Escape"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve()))); await expect(trigger).toBeFocused();
  await page.getByRole("button", { name: "More navigation" }).click();
  await setCssViewport(page, { width: 1024, height: 768 });
  await expect(page.getByRole("dialog")).toHaveCount(0); await expect(page.locator("main")).toBeFocused();
  await page.keyboard.press("Tab"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve()))); await expect(page.locator("main")).not.toBeFocused();
});

test("marketing reverse keyboard focus clears sticky header", async ({ page }, info) => {
  await setCssViewport(page, { width: 320, height: 800 }); await page.goto("/");
  await page.locator(".hero").getByRole("link", { name: "See how it works", exact: true }).focus();
  for (let i = 0; i < 30; i++) {
    await page.keyboard.press(i < 15 ? "Tab" : "Shift+Tab"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve())));
    const focus = await page.evaluate(() => {
      const el = document.activeElement!;
      if (!el.matches("a,button,summary") || el.closest("header") || el.matches(".skip-link")) return null;
      const box = el.getBoundingClientRect();
      return { name: el.textContent, top: box.top, bottom: box.bottom, header: document.querySelector(".marketing-navbar")!.getBoundingClientRect().bottom, height: innerHeight };
    });
    if (focus) {
      if (focus.top < focus.header) await page.screenshot({ path: info.outputPath("marketing-focus.png") });
      expect(focus.top, String(focus.name)).toBeGreaterThanOrEqual(focus.header);
      expect(focus.bottom, String(focus.name)).toBeLessThanOrEqual(focus.height);
    }
  }
  await page.screenshot({ path: info.outputPath("marketing-focus.png") });
});

test("complete M8 journey preserves context and changes Room without stale events", async ({ page }, info) => {
  test.setTimeout(90_000);
  await page.goto("/");
  await page.locator(".hero").getByRole("link", { name: "See how it works", exact: true }).click();
  await expect(page).toHaveURL("/#how-it-works");
  await page.getByRole("link", { name: "Interactive demo", exact:true }).click();
  await expect(page).toHaveURL("/demo");
  await page.getByRole("button", { name: "Restart demo" }).click();
  const scenes = page.getByRole("navigation", { name: "Demo scenes" }).getByRole("button");
  for (let i = 0; i < 7; i++) {
    await expect(scenes.nth(i)).toHaveAttribute("aria-current", "step");
    if (i < 6) await page.getByRole("button", { name: "Next", exact: true }).click();
  }
  await page.getByRole("button", { name: "Inspect S4: Private Analytics" }).click();
  await page.getByRole("link", { name: "Inspect S4 in workspace" }).click();
  await expect(page).toHaveURL(room + "/workspace/S4");
  await page.getByRole("button", { name: "State S2: Private Join", exact: true }).click();
  await expect(page.getByRole("link", { name: "Explore Proofs & Provenance" })).toHaveAttribute("href", room + "/proofs/S2");
  await page.getByRole("link", { name: "Explore Computations" }).click();
  await expect(page).toHaveURL(room + "/computations");
  const trail = page.getByRole("navigation", { name: "Room preview journey" });
  await trail.getByRole("link", { name: "Results", exact: true }).click();
  await expect(page).toHaveURL(room + "/results");
  await page.getByRole("navigation", { name: "Result category" }).getByRole("link", { name: /Analytics/ }).click();
  await expect(page).toHaveURL(room + "/results/analytics");
  await trail.getByRole("link", { name: "Proofs & Provenance" }).click();
  await expect(page).toHaveURL(room + "/proofs/S4");
  await page.getByRole("group", { name: "RoomState selection" }).getByRole("button", { name: /^S3/ }).click();
  await trail.getByRole("link", { name: "Activity", exact: true }).click();
  await expect(page).toHaveURL(room + "/activity/S3");
  await page.getByRole("group", { name: "Activity type" }).getByRole("button", { name: "Security", exact: true }).click();
  await expect(page.getByRole("heading", { name: "No matching examples" })).toBeVisible();
  await page.getByText("Change example Room", { exact: true }).click();
  await page.getByRole("navigation", { name: "Example Room selection" }).getByRole("link", { name: "Joint Insights Room" }).click();
  await expect(page).toHaveURL("/preview/rooms/insights/activity");
  await expect(page.getByRole("combobox", { name: "Related state" })).toHaveValue("");
  await expect(page.getByRole("button", { name: "All", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".activity-selection")).not.toContainText("S4");
  await trail.getByRole("link", { name: "Rooms", exact: true }).click();
  await page.getByRole("button", { name: "Expand Research Partnership" }).click();
  await page.locator("main").getByRole("link", { name: "View Room details" }).click();
  await page.locator("main").getByRole("link", { name: "Open Workspace" }).click();
  await expect(page).toHaveURL("/preview/rooms/research/workspace");
  await expect(page.getByRole("heading", { name: "Your graph starts here." })).toBeVisible();
  await expect(page.getByRole("button", { name: /^State S/ })).toHaveCount(0);
  await capture(page, info, "journey-empty-room");
});

test("eight-width responsive matrix, P11 layouts and touch targets", async ({ page }, info) => {
  test.setTimeout(180_000);
  const initial = info.project.use.viewport?.width ?? 1440;
  const widths = initial >= 1280 ? [1440, 1280, 1024] : initial >= 768 ? [834, 768] : [390, 375, 320];
  const routes = ["/", "/demo", "/preview/rooms", "/preview/rooms/new", ...["workspace/S4", "computations", "results/analytics", "proofs/S4", "activity"].map(s => room + "/" + s), "/app/rooms"];
  for (const width of widths) {
    await setCssViewport(page, { width, height: 900 });
    for (const [index, route] of routes.entries()) {
      await page.goto(route, { waitUntil: "networkidle" }); await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
      expect(await page.evaluate(() => innerWidth)).toBe(width);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= Math.ceil(visualViewport?.width ?? innerWidth)), `${route} at ${width}`).toBe(true);
      if (width === widths[0]) await capture(page, info, `matrix-${index}-${width}`);
      const targets = await page.locator(".button, .nav-link, .segmented-control button").evaluateAll(elements =>
        elements.filter(e => e.checkVisibility()).map(e => { const b = e.getBoundingClientRect(); return { name: e.textContent, w: b.width, h: b.height }; }));
      for (const target of targets) { expect(target.w, String(target.name)).toBeGreaterThanOrEqual(24); expect(target.h, String(target.name)).toBeGreaterThanOrEqual(24); }
      if (route.endsWith("workspace/S4")) {
        await expect(page.getByRole("button", { name: "State S4: Private Analytics", pressed: true })).toBeVisible();
        const inspector = page.getByLabel("Context inspector");
        if (width < 768) {
          await expect(inspector).toBeHidden(); await expect(page.getByRole("navigation", { name: "Mobile navigation" })).toBeVisible();
        } else {
          await expect(inspector).toBeVisible();
          const ib = (await inspector.boundingBox())!, mb = (await page.locator("main").boundingBox())!;
          if (width <= 1100) expect(ib.y).toBeGreaterThanOrEqual(mb.y + mb.height - 1);
          else expect(ib.x).toBeGreaterThanOrEqual(mb.x + mb.width - 1);
        }
      }
    }
  }
});

test("system states remove stale results, proof and activity context", async ({ page }, info) => {
  test.setTimeout(120_000);
  for (const [route, stale] of [["results/analytics", ".analytics-chart"], ["proofs/S4", ".provenance-lineage"], ["activity/S4", ".activity-selection"]]) {
    await page.goto(room + "/" + route);
    await page.getByText("Display examples · not service responses", { exact: true }).click();
    for (const state of ["empty", "loading", "blocked", "error", "unavailable"]) {
      await page.getByRole("group", { name: "Display state" }).getByRole("button", { name: state, exact: true }).click();
      await expect(page.locator(stale)).toHaveCount(0);
      await expect(page.getByText(/^(Verified|Finalized)$/)).toHaveCount(0);
      const trail = page.getByRole("navigation", { name: "Room preview journey" });
      await expect(trail.getByRole("link", { name: "Graph Workspace" })).toHaveAttribute("href", room + "/workspace");
      if ((await page.evaluate(() => innerWidth)) < 768) {
        await page.getByRole("button", { name: "Workspace details", exact: true }).click();
        await expect(page.getByRole("dialog")).not.toContainText("S4");
        await page.keyboard.press("Escape"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve())));
      } else await expect(page.getByLabel("Context inspector")).not.toContainText("S4");
      if (route.startsWith("results")) await capture(page, info, "state-" + state);
    }
    await page.getByText("Change example Room", { exact: true }).click();
    await page.getByRole("navigation", { name: "Example Room selection" }).getByRole("link", { name: "Research Partnership" }).click();
    await expect(page).toHaveURL(`/preview/rooms/research/${route.split("/")[0]}`);
    await expect(page.locator(".operation-header")).toContainText("Research Partnership");
    await expect(page.locator(stale)).toHaveCount(0);
  }
});

test("invalid deep links fail closed and keyboard reflow keeps navigation usable", async ({ page }, info) => {
  test.setTimeout(90_000);
  for (const route of ["/unknown", "/preview/rooms/unknown/workspace", room + "/workspace/unknown", room + "/proofs/unknown", room + "/activity/unknown", room + "/results/unknown"]) {
    const response = await page.goto(route, { waitUntil: "networkidle" }); expect(response?.status()).toBe(404);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(page.getByText(/^(Verified|Finalized)$/)).toHaveCount(0);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= Math.ceil(visualViewport?.width ?? innerWidth))).toBe(true);
  }
  // 1280px window at 200% browser zoom has a 640 CSS-pixel layout viewport.
  // This is a reflow simulation, not a claim of browser chrome zoom certification.
  await setCssViewport(page, { width: 640, height: 450 }); await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto(room + "/proofs/S4");
  await page.getByRole("button", { name: "Workspace details", exact: true }).click();
  const dialog = page.getByRole("dialog");
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press("Tab"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve()))); expect(await dialog.evaluate(e => e.contains(document.activeElement))).toBe(true);
  }
  await capture(page, info, "reflow-sheet"); await page.keyboard.press("Escape"); await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve())));
  await setCssViewport(page, { width: 844, height: 390 });
  await expect(page.getByLabel("Context inspector")).toBeVisible();
  await capture(page, info, "landscape");
});

test("rendered local destinations resolve and links never invent external authority", async ({ page }) => {
  test.setTimeout(90_000);
  const destinations = new Set<string>();
  for (const path of ["/", "/demo", "/product", "/technology", "/security", "/developers", "/book-demo", "/preview/rooms", ...["workspace/S4", "computations", "results/analytics", "proofs/S4", "activity/S4"].map(s => room + "/" + s)]) {
    await page.goto(path, { waitUntil: "networkidle" });
    const links = await page.locator("a[href]").evaluateAll(elements => elements.map(e => e.getAttribute("href")!));
    for (const href of links) {
      expect(href).not.toMatch(/^(javascript:|data:)|sepolia|etherscan|basescan/i);
      if (href.startsWith("/") && !href.startsWith("//")) destinations.add(href.split("#")[0]);
    }
  }
  expect(destinations.size).toBeGreaterThan(20);
  for (const path of destinations) {
    const response = await page.request.get(path);
    expect(response.status(), path).toBe(200);
  }
});
