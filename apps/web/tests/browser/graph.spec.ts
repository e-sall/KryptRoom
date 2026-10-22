import { test, expect, type Page, type TestInfo } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
const url = "/preview/rooms/supply-chain/workspace";
async function capture(page: Page, info: TestInfo, name: string) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  await page.screenshot({ path: info.outputPath(name + ".png"), fullPage: true });
  if (info.project.name === "mobile")
    await page.screenshot({ path: info.outputPath(name + "-viewport.png") });
}
test("P04 modes, multi-parent edges, tabs and scoped Room navigation", async ({ page }, info) => {
  await page.goto("/preview/rooms/supply-chain");
  await page.locator("main").getByRole("link", { name: "Open Workspace" }).click();
  await expect(page).toHaveURL(url);
  await expect(page.getByRole("button", { name: "Classic", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".graph-node")).toHaveCount(4);
  await expect(page.locator('[data-edge="S2-S4"]')).toHaveAttribute("data-parent-index", "0");
  await expect(page.locator('[data-edge="S3-S4"]')).toHaveAttribute("data-parent-index", "1");
  await capture(page, info, "classic-selected");
  await page.getByRole("button", { name: "State S2: Private Join" }).click();
  await expect(page.getByRole("button", { name: "State S2: Private Join" })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "Detailed", exact: true }).click();
  await capture(page, info, "detailed");
  if (info.project.name === "mobile") await page.getByRole("button", { name: "Workspace details", exact: true }).click();
  const inspector = info.project.name === "mobile" ? page.getByRole("dialog", { name: "Workspace details" }) : page.getByLabel("Context inspector");
  await expect(inspector.getByRole("heading", { name: "Private Join", exact: true })).toBeVisible();
  await inspector.getByRole("tab", { name: "Inputs" }).click();
  await inspector.getByRole("button", { name: "Inspect parent S1" }).click();
  await expect(inspector.getByRole("heading", { name: "Initial State" })).toBeVisible();
  await inspector.getByRole("tab", { name: "Outputs" }).click();
  await expect(inspector).toContainText("No example artifact references.");
  await inspector.getByRole("tab", { name: "Metadata" }).click();
  await expect(inspector).toContainText("Unavailable · no digest fabricated");
  await inspector.getByRole("tab", { name: "Metadata" }).press("Home");
  await expect(inspector.getByRole("tab", { name: "Overview" })).toBeFocused();
  await expect(inspector.getByRole("tab", { name: "Overview" })).toHaveAttribute("aria-selected", "true");
  if (info.project.name === "mobile") {
    await capture(page, info, "bottom-sheet");
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press("Tab");
      expect(await inspector.evaluate((n) => n.contains(document.activeElement))).toBe(true);
    }
    await page.keyboard.press("Escape");
    await expect(page.getByRole("button", { name: "Workspace details", exact: true })).toBeFocused();
  }
  await page.getByRole("button", { name: "Focus", exact: true }).click();
  await expect(page.locator(".graph-node.subdued")).toHaveCount(1);
  await capture(page, info, "focus");
  await page.getByRole("button", { name: "Return to full view" }).click();
  await expect(page.getByRole("button", { name: "Detailed", exact: true })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("link", { name: "Back to Room details" }).click();
  await expect(page).toHaveURL("/preview/rooms/supply-chain");
});
test("viewport pan zoom fit keyboard and long DAG navigation", async ({ page }, info) => {
  await page.goto(url);
  const canvas = page.getByRole("region", { name: "State graph canvas" });
  const plane = page.getByTestId("graph-plane");
  await page.getByRole("button", { name: "Fit View", exact: true }).click();
  const initial = await plane.evaluate((n) => getComputedStyle(n).transform);
  await page.getByRole("button", { name: "Zoom in", exact: true }).click();
  await expect.poll(() => plane.evaluate((n) => getComputedStyle(n).transform)).not.toBe(initial);
  await page.getByRole("button", { name: "Fit View", exact: true }).click();
  await expect.poll(() => plane.evaluate((n) => getComputedStyle(n).transform)).toBe(initial);
  await canvas.scrollIntoViewIfNeeded();
  const box = (await canvas.boundingBox())!;
  await page.mouse.move(box.x + 15, box.y + 15);
  await page.mouse.down();
  await page.mouse.move(box.x + 65, box.y + 65, { steps: 5 });
  await page.mouse.up();
  await expect.poll(() => plane.evaluate((n) => getComputedStyle(n).transform)).not.toBe(initial);
  if (info.project.name === "mobile") {
    const beforeTouch = await plane.evaluate((n) => getComputedStyle(n).transform);
    const session = await page.context().newCDPSession(page);
    await session.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: box.x + 15, y: box.y + 15 }] });
    await session.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: box.x + 55, y: box.y + 45 }] });
    await session.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await expect.poll(() => plane.evaluate((n) => getComputedStyle(n).transform)).not.toBe(beforeTouch);
    await session.detach();
  }
  await canvas.focus(); await page.keyboard.press("f");
  await expect.poll(() => plane.evaluate((n) => getComputedStyle(n).transform)).toBe(initial);
  const node = page.getByRole("button", { name: "State S1: Initial State" });
  await node.focus(); await page.keyboard.press("ArrowRight");
  await expect(page.getByRole("button", { name: "State S2: Private Join" })).toBeFocused();
  await page.keyboard.press("End");
  await expect(page.getByRole("button", { name: "State S4: Private Analytics" })).toHaveAttribute("aria-pressed", "true");
  await page.keyboard.press("Escape");
  await expect(canvas).toBeFocused();
  await expect(page.locator('.graph-node[aria-pressed="true"]')).toHaveCount(0);
  await page.getByText("Graph display examples", { exact: true }).click();
  await page.getByLabel("Long DAG · 24 synthetic states").check();
  await expect(page.locator(".graph-node")).toHaveCount(24);
  await page.getByText("Ordered state list · accessible navigation", { exact: true }).click();
  await page.getByRole("button", { name: "L24 · Example state 24", exact: true }).click();
  await expect(page.getByRole("button", { name: "State L24: Example state 24", exact: true })).toBeInViewport();
  await expect(page.getByRole("button", { name: "State L24: Example state 24", exact: true })).toBeFocused();
  await capture(page, info, "long-dag");
});
test("P11 system states, 320px, reduced motion and disconnected runtime", async ({ page }, info) => {
  const failures: string[] = [], requests: string[] = [], errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("request", (request) => {
    if (request.method() !== "GET") failures.push(request.method() + " " + request.url());
    if (!request.url().startsWith("http://127.0.0.1:3000/")) requests.push(request.url());
    if (/\/api\/|rpc|groth16|sepolia/i.test(request.url())) failures.push(request.url());
  });
  await page.goto(url);
  await page.getByText("Graph display examples", { exact: true }).click();
  for (const state of ["empty", "loading", "blocked", "error", "unavailable"]) {
    await page.getByRole("button", { name: state, exact: true }).click();
    if (state === "blocked") {
      await expect(page.locator(".graph-node")).toHaveCount(4);
    } else await expect(page.locator(".graph-node")).toHaveCount(0);
    await capture(page, info, state);
  }
  await page.getByRole("button", { name: "normal", exact: true }).click();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 320, height: 740 });
  await page.getByRole("button", { name: "Detailed", exact: true }).click();
  await capture(page, info, "narrow-320");
  expect(await page.locator(".graph-node").first().evaluate((n) => getComputedStyle(n).transitionDuration)).toMatch(/^0s/);
  await page.getByRole("button", { name: "Workspace details", exact: true }).click();
  await page.getByRole("dialog").getByRole("tab", { name: "Metadata" }).click();
  await expect(page.getByRole("dialog")).toContainText("StateCommitment");
  await capture(page, info, "narrow-sheet");
  await page.keyboard.press("Escape");
  await page.goto("/app/graph");
  await expect(page.locator(".graph-node")).toHaveCount(0);
  await expect(page.locator("main")).toContainText("Unavailable");
  expect(errors).toEqual([]); expect(failures).toEqual([]); expect(requests).toEqual([]);
});
