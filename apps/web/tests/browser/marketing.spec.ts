import { test, expect, type Page, type TestInfo } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
const names = ["Organizations", "Protected Inputs", "Private Computation", "State Creation", "Authorized Result", "Proof & Provenance", "Explore the State"];
const problems = new WeakMap<Page, string[]>();
test.beforeEach(async ({ page }) => {
  const errors: string[] = []; problems.set(page, errors);
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.method() !== "GET" || !request.url().startsWith("http://127.0.0.1:3000/") || /\/api\/|rpc|groth16|sepolia/i.test(request.url())) errors.push(request.method() + " " + request.url());
  });
  page.on("websocket", (socket) => errors.push(socket.url()));
});
test.afterEach(async ({ page }) => {
  expect(problems.get(page)).toEqual([]);
  expect(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie])).toEqual([0, 0, ""]);
});
async function capture(page: Page, info: TestInfo, name: string) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: info.outputPath(name + ".png"), fullPage: true });
}
test("P01 hero, honest booking and four P02 steps", async ({ page }, info) => {
  test.setTimeout(90_000); await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Compute together. Reveal nothing.");
  await capture(page, info, "home");
  await page.locator(".hero").screenshot({ path: info.outputPath("hero.png") });
  const steps = page.getByRole("list", { name: "Four collaboration steps" });
  for (const name of ["Create Room", "Invite Participants", "Connect Data", "Run Computation"]) {
    const button = steps.getByRole("button", { name: new RegExp(name) });
    await button.click(); await expect(button).toHaveAttribute("aria-current", "step");
    await expect(page.locator(".how-visual figcaption strong")).toHaveText(name);
  }
  // Capture document coordinates without scrolling the sticky header over the section.
  await page.evaluate(() => { window.scrollTo(0, 0); });
  const story = await page.locator("#how-it-works").boundingBox();
  if (!story) throw new Error("Missing P02 section");
  await page.screenshot({ path: info.outputPath("how-it-works.png"), fullPage: true, clip: story });
  if (info.project.name === "desktop") {
    for (const index of [0, 3, 1]) {
      await steps.locator("li").nth(index).evaluate((element) => window.scrollTo(0, scrollY + element.getBoundingClientRect().top - innerHeight * .42));
      await expect(steps.getByRole("button").nth(index)).toHaveAttribute("aria-current", "step");
    }
  }
  await page.getByRole("link", { name: "Explore Product", exact: true }).click(); await expect(page).toHaveURL("/demo");
  await page.goto("/book-demo"); await expect(page.getByText("Unavailable", { exact: true })).toBeVisible();
  await expect(page.locator("form,input,iframe")).toHaveCount(0); await capture(page, info, "booking-unavailable");
});
test("P05 seven scenes, bounds, context and reproducible reset", async ({ page }, info) => {
  test.setTimeout(150_000); await page.goto("/demo");
  const scenes = page.getByRole("navigation", { name: "Demo scenes" });
  const context = page.getByLabel("Demo context");
  await expect(scenes.getByRole("button", { name: /State Creation/ })).toHaveAttribute("aria-current", "step");
  await page.getByRole("button", { name: "Restart demo" }).click(); await expect(page.getByRole("button", { name: "Previous", exact: true })).toBeDisabled();
  for (const [index, name] of names.entries()) {
    await expect(context.getByRole("heading", { name, exact: true })).toBeVisible();
    await expect(scenes.getByRole("button").nth(index)).toHaveAttribute("aria-current", "step");
    await expect(context.getByText("Not assessed", { exact: true })).toBeVisible();
    await expect(context.getByText("Not anchored", { exact: true })).toBeVisible();
    await expect(page.getByText(/^(Verified|Finalized)$/)).toHaveCount(0);
    await capture(page, info, `demo-scene-${index + 1}`);
    if (index < 6) await page.getByRole("button", { name: "Next", exact: true }).click();
  }
  await expect(page.getByRole("button", { name: "Next", exact: true })).toBeDisabled();
  await page.getByRole("button", { name: "Previous", exact: true }).click();
  await expect(context.getByRole("heading", { name: "Proof & Provenance", exact: true })).toBeVisible();
  await context.getByText("What this scene means").click(); await expect(context).toContainText("B does not establish C or MPC correctness");
  await page.getByRole("button", { name: "Restart demo" }).click();
  await expect(context.getByRole("heading", { name: "Organizations", exact: true })).toBeVisible();
});
test("P05 modes preserve geometry and selection, with real catalog DAG and workspace continuity", async ({ page }, info) => {
  test.setTimeout(90_000); await page.goto("/demo");
  await page.getByRole("button", { name: "Scene 7: Explore the State", exact: true }).click();
  const context = page.getByLabel("Demo context");
  await expect(context.getByText("S2 · S3", { exact: true })).toBeVisible();
  const edges = page.locator(info.project.name === "mobile" ? ".demo-mobile-edges path" : ".demo-desktop-edges path");
  expect(await edges.evaluateAll((elements) => elements.map((element) => [element.getAttribute("data-edge"), element.getAttribute("data-parent-index")]))).toEqual([["S1-S2", "0"], ["S1-S3", "0"], ["S2-S4", "0"], ["S3-S4", "1"]]);
  await page.getByRole("button", { name: "Inspect S2: Private Join" }).click();
  const geometry = () => page.locator(".demo-columns > *").evaluateAll((elements) => elements.map((element) => { const box = element.getBoundingClientRect(); return [box.x, box.width, box.height]; }));
  const before = await geometry();
  for (const mode of ["Presentation", "Explore"]) {
    await page.getByRole("button", { name: mode, exact: true }).click();
    expect(await geometry()).toEqual(before);
    await expect(page.getByRole("button", { name: "Inspect S2: Private Join" })).toHaveAttribute("aria-pressed", "true");
    await expect(context.getByRole("link", { name: "Inspect S2 in workspace" })).toHaveAttribute("href", "/preview/rooms/supply-chain/workspace/S2");
    await capture(page, info, "demo-" + mode.toLowerCase() + "-selected-s2");
  }
  await page.getByRole("button", { name: "Inspect S4: Private Analytics" }).click();
  await context.getByRole("link", { name: "Inspect S4 in workspace" }).click();
  await expect(page).toHaveURL("/preview/rooms/supply-chain/workspace/S4");
  await expect(page.getByRole("button", { name: "State S4: Private Analytics", pressed: true })).toBeVisible();
});
test("P05 keyboard, reduced motion, touch and small mobile", async ({ page }, info) => {
  test.setTimeout(120_000); await page.emulateMedia({ reducedMotion: "reduce" }); await page.setViewportSize({ width: 320, height: 800 }); await page.goto("/demo");
  const scenes = page.getByRole("navigation", { name: "Demo scenes" });
  await scenes.getByRole("button", { name: /State Creation/ }).focus(); await page.keyboard.press("Home");
  await expect(scenes.getByRole("button", { name: /Organizations/ })).toBeFocused();
  await page.keyboard.press("ArrowRight"); await expect(scenes.getByRole("button", { name: /Protected Inputs/ })).toBeFocused();
  expect(await scenes.getByRole("button", { name: /Protected Inputs/ }).evaluate((element) => getComputedStyle(element).outlineStyle)).not.toBe("none");
  await page.keyboard.press("End"); await expect(scenes.getByRole("button", { name: /Explore the State/ })).toBeFocused();
  const mode = page.getByRole("button", { name: "Presentation", exact: true });
  if (info.project.use.hasTouch) await mode.tap(); else await mode.click();
  await expect(mode).toHaveAttribute("aria-pressed", "true"); await capture(page, info, "demo-320-presentation");
  await page.getByRole("button", { name: "Inspect S3: Analytics" }).click();
  await expect(page.getByLabel("Demo context").getByRole("link", { name: "Inspect S3 in workspace" })).toBeVisible();
  await capture(page, info, "demo-320-selected-s3");
  const boxes = await page.locator(".demo-state").evaluateAll((elements) => elements.map((element) => { const b = element.getBoundingClientRect(); return { x: b.x, y: b.y, right: b.right, bottom: b.bottom }; }));
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i], b = boxes[j]; expect(a.right <= b.x || b.right <= a.x || a.bottom <= b.y || b.bottom <= a.y).toBe(true);
  }
  await page.goto("/"); await capture(page, info, "home-320");
});
test("marketing boundaries remain honest and operational routes unavailable", async ({ page }, info) => {
  test.setTimeout(90_000);
  for (const section of ["product", "technology", "security", "developers"]) {
    await page.goto("/" + section); await capture(page, info, "marketing-" + section);
    await expect(page.locator("main")).toContainText(section === "product" ? "Integrated Operational Product" : section === "technology" ? "not threshold FHE" : section === "security" ? "not a production-ready" : "no production Workspace API");
  }
  await page.goto("/app/rooms"); await expect(page.locator("main")).toContainText(/unavailable|not connected/i);
});
