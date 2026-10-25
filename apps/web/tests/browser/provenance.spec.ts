import { test, expect, type Page, type TestInfo } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
const room = "/preview/rooms/supply-chain";
const roomTrail = (page: Page) => page.getByRole("navigation", { name: "Room preview journey" });
const problems = new WeakMap<Page, string[]>();
test.beforeEach(async ({ page }) => {
  const errors: string[] = [];
  problems.set(page, errors);
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("request", (r) => {
    if (r.method() !== "GET" || !r.url().startsWith("http://127.0.0.1:3000/") || /\/api\/|rpc|groth16|sepolia/i.test(r.url())) errors.push(r.method() + " " + r.url());
  });
  page.on("websocket", (ws) => errors.push("WebSocket " + ws.url()));
});
test.afterEach(async ({ page }) => {
  expect(problems.get(page)).toEqual([]);
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });
  expect(await page.evaluate(() => document.cookie)).toBe("");
});
async function capture(page: Page, info: TestInfo, name: string) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze()).violations).toEqual([]);
  await page.evaluate(() => window.scrollTo(0, 0));
  const sheetOpen = await page.getByRole("dialog").count() > 0;
  await page.screenshot({ path: info.outputPath(name + ".png"), fullPage: !sheetOpen });
}
async function openInspector(page: Page, info: TestInfo) {
  if (info.project.name === "mobile") {
    await page.getByRole("button", { name: "Workspace details", exact: true }).click();
    return page.getByRole("dialog", { name: "Workspace details" });
  }
  return page.getByLabel("Context inspector");
}
async function closeInspector(page: Page, info: TestInfo) {
  if (info.project.name === "mobile") await page.keyboard.press("Escape");
}
test("P09 four stages, all state selections and exact return journey", async ({ page }, info) => {
  test.setTimeout(90_000);
  await page.goto("/preview/rooms");
  await page.getByRole("button", { name: "Expand Supply Chain Collaboration" }).click();
  await page.locator("main").getByRole("link", { name: "View Room details" }).click();
  await page.locator("main").getByRole("link", { name: "Open Workspace" }).click();
  await page.getByRole("link", { name: "Explore Proofs & Provenance" }).click();
  const rail = page.getByRole("navigation", { name: "Provenance stages" });
  for (const stage of ["Lineage", "Evidence", "Verification", "Anchoring"]) {
    await rail.getByRole("button", { name: new RegExp(stage) }).click();
    await expect(page.getByRole("region", { name: stage + " illustration" })).toBeVisible();
    await capture(page, info, "proofs-" + stage.toLowerCase());
  }
  await rail.getByRole("button", { name: /Lineage/ }).click();
  const picker = page.getByRole("group", { name: "RoomState selection" });
  for (const state of ["S1", "S2", "S3", "S4"]) {
    await picker.getByRole("button", { name: new RegExp("^" + state) }).click();
    const inspector = await openInspector(page, info);
    await expect(inspector.getByRole("heading", { name: new RegExp("^" + state + " ·") })).toBeVisible();
    await expect(inspector.getByRole("link", { name: "Open " + state + " in Graph" })).toHaveAttribute("href", room + "/workspace/" + state);
    await expect(inspector.getByRole("button", { name: /Verify proof/ })).toBeDisabled();
    await expect(inspector.getByRole("button", { name: /Anchor state/ })).toBeDisabled();
    await capture(page, info, "proofs-selected-" + state.toLowerCase());
    await closeInspector(page, info);
  }
  const region = page.getByRole("region", { name: "Lineage illustration" });
  await expect(region.locator(".lineage-edges path")).toHaveCount(4);
  await expect(region.getByRole("list", { name: "Ordered parents" }).getByRole("button")).toHaveText(["S2 · Private Join", "S3 · Analytics"]);
  await region.getByRole("list", { name: "Ordered parents" }).getByRole("button", { name: "S2 · Private Join" }).click();
  await region.getByRole("link", { name: "Activity for S2" }).click();
  await expect(page).toHaveURL(room + "/activity/S2");
  await expect(page.getByRole("combobox", { name: "Related state" })).toHaveValue("S2");
  await page.locator("main").getByRole("link", { name: "Open S2 in Graph" }).click();
  await expect(page).toHaveURL(room + "/workspace/S2");
  await expect(page.getByRole("button", { name: "State S2: Private Join", pressed: true })).toBeVisible();
});
test("P09 evidence and progressive conceptual checks never produce a verdict", async ({ page }, info) => {
  await page.goto(room + "/proofs/S3");
  await page.getByRole("navigation", { name: "Provenance stages" }).getByRole("button", { name: /Evidence/ }).click();
  await page.getByRole("group", { name: "Evidence categories" }).getByRole("button", { name: /Proof artifact/ }).click();
  let inspector = await openInspector(page, info);
  await expect(inspector).toContainText("Proof artifact · Cryptographic artifact");
  await expect(inspector).toContainText("No proof artifact is supplied");
  await capture(page, info, "proofs-evidence-inspector");
  await closeInspector(page, info);
  await page.getByRole("navigation", { name: "Provenance stages" }).getByRole("button", { name: /Verification/ }).click();
  for (const check of ["Structural validation", "Document consistency", "Cryptographic proof"]) {
    await page.locator("main").getByRole("button", { name: new RegExp(check) }).click();
    inspector = await openInspector(page, info);
    await expect(inspector).toContainText(check);
    await expect(inspector).toContainText("No verification performed");
    await closeInspector(page, info);
  }
  await expect(page.getByText(/^(Verified|Finalized|Pending)$/)).toHaveCount(0);
  await capture(page, info, "proofs-layer-c-concept");
});
test("P10 timeline, graph, filters, selection and diagnostic inspector", async ({ page }, info) => {
  test.setTimeout(90_000);
  await page.goto(room + "/activity");
  await expect(page.getByRole("tab", { name: "List", exact: true })).toHaveAttribute("aria-selected", "true");
  await expect(page.getByRole("list", { name: "Sample timeline" }).getByRole("button")).toHaveCount(7);
  await capture(page, info, "activity-timeline");
  await page.getByRole("group", { name: "Activity type" }).getByRole("button", { name: "Security", exact: true }).click();
  await expect(page.getByRole("list", { name: "Sample timeline" }).getByRole("button")).toHaveCount(2);
  await page.getByRole("list", { name: "Sample timeline" }).getByRole("button", { name: /Approval requirement/ }).click();
  await capture(page, info, "activity-filter-security");
  const inspector = await openInspector(page, info);
  await expect(inspector.getByRole("heading", { name: "Approval requirement example" })).toBeVisible();
  await inspector.getByRole("tab", { name: "Context" }).click();
  await expect(inspector).toContainText("S2 + S3 → S4");
  await capture(page, info, "activity-context-inspector");
  await inspector.getByRole("tab", { name: "Diagnostic" }).click();
  await expect(inspector).toContainText("No runtime diagnostic");
  await expect(inspector.getByRole("button", { name: /Approve action/ })).toBeDisabled();
  await expect(inspector.getByRole("button", { name: /Download log/ })).toBeDisabled();
  await capture(page, info, "activity-diagnostic");
  await closeInspector(page, info);
  await page.getByRole("tab", { name: "Graph", exact: true }).click();
  await expect(page.getByRole("group", { name: "Related sample events" }).getByRole("button", { name: /Approval requirement/ })).toHaveAttribute("aria-pressed", "true");
  await capture(page, info, "activity-graph");
  await page.getByRole("button", { name: "Select S1 · Initial State" }).click();
  await expect(page.getByRole("heading", { name: "No matching examples" })).toBeVisible();
  await page.getByRole("button", { name: "Clear activity filters" }).click();
  await page.getByRole("button", { name: "Select S3 · Analytics" }).click();
  await page.locator("main").getByRole("link", { name: "Provenance of S3" }).click();
  await expect(page).toHaveURL(room + "/proofs/S3");
  await expect(page.getByRole("group", { name: "RoomState selection" }).getByRole("button", { name: /^S3/ })).toHaveAttribute("aria-pressed", "true");
});
test("P09 P10 keyboard, sheet focus, reduced motion and 320px", async ({ page }, info) => {
  test.setTimeout(90_000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 320, height: 800 });
  await page.goto(room + "/proofs/S4");
  for (const stage of ["Lineage", "Evidence", "Verification", "Anchoring"]) {
    const button = page.getByRole("navigation", { name: "Provenance stages" }).getByRole("button", { name: new RegExp(stage) });
    await button.focus(); await page.keyboard.press("Enter");
    await expect(button).toHaveAttribute("aria-current", "step");
    await capture(page, info, "proofs-320-" + stage.toLowerCase());
  }
  const trigger = page.getByRole("button", { name: "Workspace details", exact: true });
  await trigger.click();
  const sheet = page.getByRole("dialog", { name: "Workspace details" });
  await capture(page, info, "proofs-320-sheet");
  for (let i = 0; i < 10; i++) { await page.keyboard.press("Tab"); expect(await sheet.evaluate((el) => el.contains(document.activeElement))).toBe(true); }
  await page.keyboard.press("Escape"); await expect(trigger).toBeFocused();
  await page.locator("main").getByRole("link", { name: "Activity for S4" }).click();
  await capture(page, info, "activity-320-list");
  const list = page.getByRole("tab", { name: "List", exact: true });
  await list.focus(); await page.keyboard.press("ArrowRight");
  await expect(page.getByRole("tab", { name: "Graph", exact: true })).toBeFocused();
  await capture(page, info, "activity-320-graph");
  await page.getByRole("button", { name: "Workspace details", exact: true }).click();
  await sheet.getByRole("tab", { name: "Overview", exact: true }).focus(); await page.keyboard.press("End");
  await expect(sheet.getByRole("tab", { name: "Diagnostic" })).toBeFocused();
  await capture(page, info, "activity-320-sheet");
  await page.keyboard.press("Escape");
});
test("P09 P10 every system state hides stale metadata and real routes stay unavailable", async ({ page }, info) => {
  test.setTimeout(120_000);
  for (const screen of ["proofs", "activity"]) {
    await page.goto(room + "/" + screen);
    await page.getByText("Display examples · not service responses", { exact: true }).click();
    for (const value of ["empty", "loading", "blocked", "error", "unavailable"]) {
      await page.getByRole("group", { name: "Display state" }).getByRole("button", { name: value, exact: true }).click();
      const inspector = await openInspector(page, info);
      await expect(inspector.getByRole("heading", { name: /No (state|event) selected/ })).toBeVisible();
      await expect(inspector.getByRole("navigation", { name: "Selected state destinations" })).toHaveCount(0);
      await closeInspector(page, info);
      await capture(page, info, screen + "-system-" + value);
    }
    await page.goto("/app/" + screen);
    await expect(page.getByRole("group", { name: "RoomState selection" })).toHaveCount(0);
    await expect(page.getByRole("list", { name: "Sample timeline" })).toHaveCount(0);
    await expect(page.locator("main")).toContainText(/unavailable|not connected/i);
  }
});
test("PR4 results link to the same existing state without expanding the catalog", async ({ page }) => {
  await page.goto(room + "/results/analytics");
  await page.locator("main").getByText("Explore result details", { exact: true }).click();
  await page.locator("main").getByRole("link", { name: "Provenance of S4" }).click();
  await expect(page).toHaveURL(room + "/proofs/S4");
  await expect(page.getByRole("group", { name: "RoomState selection" }).getByRole("button")).toHaveCount(4);
  await page.getByText("Change example Room", { exact: true }).click();
  await page.getByRole("navigation", { name: "Example Room selection" }).getByRole("link", { name: "Research Partnership" }).click();
  await expect(page.getByRole("heading", { name: "No examples in this view" })).toBeVisible();
});

test("RoomTrail preserves Proofs S2 to Activity S2 and Activity S3 to Proofs S3", async ({ page }) => {
  await page.goto(room + "/proofs/S2");
  await roomTrail(page).getByRole("link", { name: "Activity", exact: true }).click();
  await expect(page).toHaveURL(room + "/activity/S2");
  await expect(page.getByRole("combobox", { name: "Related state" })).toHaveValue("S2");
  await expect(page.locator("main").getByRole("link", { name: "Open S2 in Graph" })).toHaveAttribute("href", room + "/workspace/S2");
  await page.getByRole("combobox", { name: "Related state" }).selectOption("S3");
  await roomTrail(page).getByRole("link", { name: "Proofs & Provenance", exact: true }).click();
  await expect(page).toHaveURL(room + "/proofs/S3");
  await expect(page.getByRole("group", { name: "RoomState selection" }).getByRole("button", { name: /^S3/ })).toHaveAttribute("aria-pressed", "true");
});

test("RoomTrail returns both Proofs and Activity S4 to selected Graph S4", async ({ page }) => {
  for (const screen of ["proofs", "activity"]) {
    await page.goto(room + "/" + screen + "/S4");
    await roomTrail(page).getByRole("link", { name: "Graph Workspace", exact: true }).click();
    await expect(page).toHaveURL(room + "/workspace/S4");
    await expect(page.getByRole("button", { name: "State S4: Private Analytics", pressed: true })).toBeVisible();
  }
});

test("RoomTrail empty Activity filter preserves explicit state without inventing an event", async ({ page }, info) => {
  await page.goto(room + "/activity/S1");
  await page.getByRole("group", { name: "Activity type" }).getByRole("button", { name: "Security", exact: true }).click();
  await expect(page.getByRole("heading", { name: "No matching examples" })).toBeVisible();
  await expect(page.getByRole("list", { name: "Sample timeline" }).getByRole("button")).toHaveCount(0);
  const inspector = await openInspector(page, info);
  await expect(inspector.getByRole("heading", { name: "No event selected" })).toBeVisible();
  await expect(inspector.getByRole("navigation", { name: "Selected state destinations" })).toHaveCount(0);
  await closeInspector(page, info);
  await roomTrail(page).getByRole("link", { name: "Proofs & Provenance", exact: true }).click();
  await expect(page).toHaveURL(room + "/proofs/S1");
  await expect(page.getByRole("group", { name: "RoomState selection" }).getByRole("button", { name: /^S1/ })).toHaveAttribute("aria-pressed", "true");
});

test("RoomTrail keeps generic Computations Results and Room changes scoped to existing states", async ({ page }) => {
  await page.goto(room + "/computations");
  await page.getByRole("checkbox", { name: /S2 · Private Join/ }).check();
  for (const [label, path] of [["Graph Workspace", "workspace"], ["Proofs & Provenance", "proofs"], ["Activity", "activity"]]) {
    await expect(roomTrail(page).getByRole("link", { name: label, exact: true })).toHaveAttribute("href", room + "/" + path);
  }
  await roomTrail(page).getByRole("link", { name: "Results", exact: true }).click();
  await expect(page).toHaveURL(room + "/results");
  await expect(roomTrail(page).getByRole("link", { name: "Graph Workspace" })).toHaveAttribute("href", room + "/workspace");
  await page.getByRole("navigation", { name: "Result category" }).getByRole("link", { name: /Private Analytics/ }).click();
  await expect(page).toHaveURL(room + "/results/analytics");
  await expect(roomTrail(page).getByRole("link", { name: "Proofs & Provenance", exact: true })).toHaveAttribute("href", room + "/proofs/S4");
  await roomTrail(page).getByRole("link", { name: "Proofs & Provenance", exact: true }).click();
  await expect(page).toHaveURL(room + "/proofs/S4");
  for (const screen of ["proofs", "activity"]) {
    await page.goto(room + "/" + screen + "/S4");
    await page.getByText("Change example Room", { exact: true }).click();
    await page.getByRole("navigation", { name: "Example Room selection" }).getByRole("link", { name: "Joint Insights Room", exact: true }).click();
    await expect(page).toHaveURL("/preview/rooms/insights/" + screen);
    for (const link of await roomTrail(page).getByRole("link").all()) {
      expect(await link.getAttribute("href")).not.toContain("supply-chain");
      expect(await link.getAttribute("href")).not.toContain("/S4");
    }
    await page.getByText("Change example Room", { exact: true }).click();
    await page.getByRole("navigation", { name: "Example Room selection" }).getByRole("link", { name: "Research Partnership", exact: true }).click();
    await expect(page).toHaveURL("/preview/rooms/research/" + screen);
    await expect(page.getByRole("heading", { name: "No examples in this view" })).toBeVisible();
    await expect(roomTrail(page).getByRole("link", { name: "Graph Workspace" })).toHaveAttribute("href", "/preview/rooms/research/workspace");
  }
});
