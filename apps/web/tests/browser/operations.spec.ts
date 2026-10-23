import { test, expect, type Page, type TestInfo } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
const room = "/preview/rooms/supply-chain";
async function capture(page: Page, info: TestInfo, name: string) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  // Capture from the page origin so offscreen fixed skip links are not drawn
  // inside a stitched full-page image. Restore the actual journey viewport.
  const scroll = await page.evaluate(() => ({ x: scrollX, y: scrollY }));
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: info.outputPath(name + ".png"), fullPage: true });
  await page.evaluate(({ x, y }) => window.scrollTo(x, y), scroll);
  if (info.project.name === "mobile") await page.screenshot({ path: info.outputPath(name + "-viewport.png") });
}
async function openInspector(page: Page, info: TestInfo) {
  if (info.project.name === "mobile") {
    await page.getByRole("button", { name: "Workspace details", exact: true }).click();
    return page.getByRole("dialog", { name: "Workspace details" });
  }
  return page.getByLabel("Context inspector");
}
const journeyProblems = new WeakMap<Page, string[]>();
test.beforeEach(async ({ page }) => {
  const problems: string[] = [];
  journeyProblems.set(page, problems);
  page.on("pageerror", (e) => problems.push(e.message));
  page.on("request", (r) => {
    if (r.method() !== "GET" || !r.url().startsWith("http://127.0.0.1:3000/") || /\/api\/|rpc|groth16|sepolia/i.test(r.url())) problems.push(r.method() + " " + r.url());
  });
});
test.afterEach(async ({ page }) => {
  // Check every complete journey before the browser fixture closes.
  expect(journeyProblems.get(page)).toEqual([]);
});
test("P08 chart label clearance at 320 390 tablet and desktop", async ({ page }, info) => {
  test.setTimeout(60_000);
  for (const width of [320, 390, 834, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto(room + "/results/analytics");
    await page.evaluate(() => document.fonts.ready);
    const chart = page.getByRole("img", { name: /Illustrative aggregate units/ });
    await expect(chart).toBeVisible();
    await expect(chart.locator("title")).toHaveText("Illustrative aggregate units by cohort");
    await expect(chart.locator("desc")).toContainText("The table view contains exactly these values.");
    const geometry = await chart.evaluate((svg) => {
      const bounds = svg.getBoundingClientRect();
      const texts = [...svg.querySelectorAll("text")].map((text) => {
        const box = text.getBoundingClientRect();
        return { label: text.textContent?.trim(), left: box.left, right: box.right, top: box.top, bottom: box.bottom };
      });
      return { texts, left: bounds.left, right: bounds.right, top: bounds.top, bottom: bounds.bottom };
    });
    const categories = geometry.texts.filter((text) => text.label?.startsWith("Cohort"));
    expect(categories.map((text) => text.label)).toEqual(["Cohort A", "Cohort B", "Cohort C", "Cohort D"]);
    for (let i = 1; i < categories.length; i++) {
      expect(categories[i].left - categories[i - 1].right, `${width}px category clearance`).toBeGreaterThanOrEqual(8);
    }
    // Actual rendered SVG boxes, not text-length estimates: catch collisions
    // between values, categories and axes, plus clipping at the SVG boundary.
    for (const [i, text] of geometry.texts.entries()) {
      expect(text.left).toBeGreaterThanOrEqual(geometry.left);
      expect(text.right).toBeLessThanOrEqual(geometry.right);
      expect(text.top).toBeGreaterThanOrEqual(geometry.top);
      expect(text.bottom).toBeLessThanOrEqual(geometry.bottom);
      for (const other of geometry.texts.slice(i + 1)) {
        expect(text.right <= other.left || other.right <= text.left || text.bottom <= other.top || other.bottom <= text.top,
          `${width}px collision: ${text.label} / ${other.label}`).toBe(true);
      }
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.locator(".analytics-chart").screenshot({ path: info.outputPath(`chart-${width}.png`) });
    const values = await chart.locator("text").filter({ hasText: /^(42|68|55|81)$/ }).allTextContents();
    expect(values).toEqual(["42", "68", "55", "81"]);
    await page.getByRole("tab", { name: "Table", exact: true }).click();
    await expect(page.getByRole("table").getByRole("cell")).toHaveText(values);
    await expect(page.getByRole("table").getByRole("rowheader")).toHaveText(categories.map((text) => text.label!));
  }
});
test("P07 complete Clean workflow and Room Graph integration", async ({ page }, info) => {
  await page.goto("/preview/rooms");
  await page.getByRole("button", { name: "Expand Supply Chain Collaboration" }).click();
  await page.locator("main").getByRole("link", { name: "View Room details" }).click();
  await page.locator("main").getByRole("link", { name: "Open Workspace" }).click();
  await page.getByRole("link", { name: "Explore Computations" }).click();
  await expect(page).toHaveURL(room + "/computations");
  await page.getByRole("checkbox", { name: /S2 · Private Join/ }).check();
  await page.getByRole("checkbox", { name: /S3 · Analytics/ }).check();
  await page.getByRole("checkbox", { name: /S1 · Initial State/ }).uncheck();
  await capture(page, info, "protected-inputs");
  await page.getByRole("button", { name: "Next phase" }).click();
  await expect(page.locator(".workflow-diagram")).toHaveAttribute("data-phase", "1");
  await capture(page, info, "private-operation");
  await page.getByRole("button", { name: "Next phase" }).click();
  await expect(page.locator(".workflow-diagram")).toHaveAttribute("data-phase", "2");
  await capture(page, info, "new-state-review");
  const inspector = await openInspector(page, info);
  await expect(inspector).toContainText("S2 → S3");
  await expect(inspector.getByRole("button", { name: /Run computation/ })).toBeDisabled();
  await expect(inspector.getByRole("button", { name: /Approve/ })).toBeDisabled();
  await expect(inspector.getByRole("button", { name: /Save transition/ })).toBeDisabled();
  await inspector.getByRole("tab", { name: "Review" }).press("Home");
  await expect(inspector.getByRole("tab", { name: "Readiness" })).toBeFocused();
  await expect(inspector).toContainText("No authoritative permission decision");
  await capture(page, info, "readiness-inspector");
  if (info.project.name === "mobile") {
    for (let i = 0; i < 7; i++) { await page.keyboard.press("Tab"); expect(await inspector.evaluate((e) => e.contains(document.activeElement))).toBe(true); }
    await page.keyboard.press("Escape");
    await expect(page.getByRole("button", { name: "Workspace details", exact: true })).toBeFocused();
  }
  await page.getByRole("link", { name: "Explore fixed result example" }).click();
  await expect(page).toHaveURL(room + "/results/join");
  await expect(page.getByRole("article")).toContainText("A state, not a spreadsheet.");
  await page.getByText("Explore result details", { exact: true }).click();
  await page.getByRole("article").getByRole("link", { name: /Inspect S2/ }).click();
  await expect(page).toHaveURL(room + "/workspace/S2");
  await expect(page.getByRole("button", { name: "State S2: Private Join" })).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".graph-node")).toHaveCount(4); // Hypothetical node was not inserted.
});
test("P08 three premium pages and analytics Chart Table parity", async ({ page }, info) => {
  await page.goto(room + "/results");
  await expect(page.getByRole("article")).toContainText("1,248");
  await capture(page, info, "psi-result");
  await page.getByRole("navigation", { name: "Result category" }).getByRole("link", { name: /Private Join/ }).click();
  await expect(page.getByRole("article")).not.toContainText("1,248");
  await expect(page.getByRole("table")).toHaveCount(0);
  await capture(page, info, "join-result");
  await page.getByRole("navigation", { name: "Result category" }).getByRole("link", { name: /Private Analytics/ }).click();
  await expect(page.getByRole("article")).toContainText("The signal, without the rows.");
  await expect(page.getByRole("img", { name: /Illustrative aggregate units/ })).toBeVisible();
  await capture(page, info, "analytics-chart");
  await page.getByRole("tab", { name: "Chart", exact: true }).press("ArrowRight");
  await expect(page.getByRole("tab", { name: "Table", exact: true })).toBeFocused();
  await expect(page.getByRole("table").getByRole("cell")).toHaveText(["42", "68", "55", "81"]);
  await page.getByText("Explore result details", { exact: true }).click();
  await capture(page, info, "analytics-details-table");
  const inspector = await openInspector(page, info);
  await expect(inspector).toContainText("S4 · Private Analytics · synthetic");
  await expect(inspector.getByRole("button", { name: /Reveal result/ })).toBeDisabled();
  await expect(inspector.getByRole("button", { name: /Download result/ })).toBeDisabled();
  await capture(page, info, "result-inspector");
  await inspector.getByRole("link", { name: /Source S3/ }).click();
  await expect(page).toHaveURL(room + "/workspace/S3");
  await expect(page.getByRole("button", { name: "State S3: Analytics" })).toHaveAttribute("aria-pressed", "true");
});
test("P07 keyboard reset operator changes empty Room and no persistence", async ({ page }, info) => {
  await page.goto(room + "/computations");
  await page.getByRole("checkbox", { name: /S1 · Initial State/ }).uncheck();
  await page.getByRole("button", { name: "Next phase" }).click();
  await expect(page.locator("main").getByRole("alert")).toContainText("Select at least one illustrative input");
  await page.getByRole("checkbox", { name: /S4 · Private Analytics/ }).focus(); await page.keyboard.press("Space");
  for (const name of ["PSI Cardinality", "Private Analytics", "Private Join"]) {
    const picker = page.getByRole("group", { name: "Operation example" }).getByRole("button", { name: new RegExp(name) });
    await picker.focus(); await page.keyboard.press("Enter");
    await expect(picker).toHaveAttribute("aria-pressed", "true");
    await page.getByRole("list", { name: "Presentation phases" }).getByRole("button", { name: /New State/ }).click();
    await expect(page.locator(".workflow-diagram")).toHaveAttribute("data-phase", "2");
  }
  await page.getByRole("button", { name: "Previous phase" }).click();
  await page.getByRole("button", { name: "Reset preview" }).click();
  await expect(page.getByRole("checkbox", { name: /S4 · Private Analytics/ })).not.toBeChecked();
  await page.getByRole("checkbox", { name: /S2 · Private Join/ }).check();
  await page.reload();
  await expect(page.getByRole("checkbox", { name: /S2 · Private Join/ })).not.toBeChecked();
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });
  await page.getByText("Change example Room", { exact: true }).click();
  await page.getByRole("navigation", { name: "Example Room selection" }).getByRole("link", { name: "Research Partnership" }).click();
  await expect(page.getByText("No examples in this view")).toBeVisible();
  await page.getByRole("navigation", { name: "Room preview journey" }).getByRole("link", { name: "Results", exact: true }).click();
  await expect(page).toHaveURL("/preview/rooms/research/results");
  await expect(page.getByRole("article")).toHaveCount(0);
  await capture(page, info, "empty-room");
  await page.goto(room + "/results/unknown"); await expect(page.getByRole("heading", { name: /not found/i })).toBeVisible();
});
test("P11 display states 320px reduced motion and real app boundary", async ({ page }, info) => {
  test.setTimeout(90_000);
  for (const screen of ["computations", "results/analytics"]) {
    await page.goto(`${room}/${screen}`);
    await page.getByText("Display examples · not service responses", { exact: true }).click();
    for (const value of ["empty", "loading", "blocked", "error", "unavailable"]) {
      await page.getByRole("button", { name: value, exact: true }).click();
      await expect(page.locator(".workflow-diagram, .result-article")).toHaveCount(0);
      await capture(page, info, `${screen.startsWith("results") ? "result" : "workflow"}-${value}`);
    }
    await page.getByRole("button", { name: "normal", exact: true }).click();
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.setViewportSize({ width: 320, height: 740 });
    if (screen === "computations") {
      await page.getByRole("button", { name: "Next phase" }).click();
      expect(await page.locator(".workflow-connector").first().evaluate((e) => getComputedStyle(e).animationName)).toBe("none");
    }
    await capture(page, info, `${screen.startsWith("results") ? "result" : "workflow"}-320`);
    await page.getByRole("button", { name: "Workspace details", exact: true }).click();
    await capture(page, info, `${screen.startsWith("results") ? "result" : "workflow"}-sheet-320`);
    await page.keyboard.press("Escape");
    await expect(page.getByRole("button", { name: "Workspace details", exact: true })).toBeFocused();
  }
  for (const moduleId of ["computations", "results"]) {
    await page.goto(`/app/${moduleId}`);
    await expect(page.locator("main")).toContainText("Unavailable");
    await expect(page.locator(".workflow-diagram, .result-article")).toHaveCount(0);
    await expect(page.getByText("1,248", { exact: true })).toHaveCount(0);
  }
});
