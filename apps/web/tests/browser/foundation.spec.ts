import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { modules } from "../../src/lib/navigation";
import { readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";

test("canonical thin logo across public, workspace and specimen surfaces", async ({
  page,
}, testInfo) => {
  for (const route of ["/", "/app/rooms", "/design-system"]) {
    await page.goto(route);
    const logos = page.locator(".k-logo:visible");
    expect(await logos.count()).toBeGreaterThan(0);
    for (const logo of await logos.all()) {
      await expect(logo).toHaveAttribute("viewBox", "0 0 22 30");
      expect(
        await logo
          .locator("path")
          .evaluateAll((paths) =>
            paths.map((path) => getComputedStyle(path).fill),
          ),
      ).toEqual([
        "rgb(241, 240, 235)",
        "rgb(166, 167, 161)",
        "rgb(115, 117, 111)",
      ]);
      expect(
        await logo.evaluate((node) => {
          const box = (node as SVGSVGElement).getBBox();
          return (
            box.x >= 0 &&
            box.y >= 0 &&
            box.x + box.width <= 22 &&
            box.y + box.height <= 30
          );
        }),
      ).toBe(true);
    }
    await logos
      .first()
      .screenshot({
        path: testInfo.outputPath(
          `logo-${route === "/" ? "marketing" : route === "/app/rooms" ? "workspace" : "specimen"}.png`,
        ),
      });
  }
  // Production file traces must not ship the temporarily excepted lint chain.
  const traces = readdirSync(".next", {
    recursive: true,
    withFileTypes: true,
  }).filter((entry) => entry.isFile() && entry.name.endsWith(".nft.json"));
  expect(traces.length).toBeGreaterThan(0);
  for (const trace of traces) {
    const { files } = JSON.parse(
      readFileSync(resolve(trace.parentPath, trace.name), "utf8"),
    );
    for (const file of files as string[])
      expect(file.replaceAll("\\", "/")).not.toMatch(
        /node_modules\/(braces|micromatch|fast-glob|eslint|eslint-config-next|@next\/eslint-plugin-next)\//,
      );
  }
});

test("responsive shell, honest state and runtime boundary", async ({
  page,
}, testInfo) => {
  const errors: string[] = [];
  const external: string[] = [];
  const mutations: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (!request.url().startsWith("http://127.0.0.1:3000"))
      external.push(request.url());
    if (request.method() !== "GET") mutations.push(request.method());
  });
  const response = await page.goto("/app/rooms");
  expect(response?.headers()["x-frame-options"]).toBe("DENY");
  await expect(
    page.getByRole("heading", { level: 1, name: "Rooms" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Create Room" }),
  ).toBeDisabled();
  const mobile = testInfo.project.name === "mobile";
  await expect(page.getByLabel("Workspace sidebar")).toBeVisible({
    visible: !mobile,
  });
  await expect(page.getByLabel("Context inspector")).toBeVisible({
    visible: !mobile,
  });
  await expect(
    page.getByRole("navigation", { name: "Mobile navigation" }),
  ).toBeVisible({ visible: mobile });
  if (!mobile) {
    const sidebar = await page.getByLabel("Workspace sidebar").boundingBox();
    expect(sidebar?.width).toBe(testInfo.project.name === "tablet" ? 76 : 208);
    const content = await page.locator("main").boundingBox();
    const inspector = await page.getByLabel("Context inspector").boundingBox();
    if (testInfo.project.name === "tablet")
      expect(inspector!.y).toBeGreaterThan(content!.y + content!.height);
    else expect(inspector!.x).toBeGreaterThan(content!.x + content!.width - 1);
  }
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await page.screenshot({
    path: testInfo.outputPath("rooms.png"),
    fullPage: true,
  });
  expect(await page.context().cookies()).toEqual([]);
  expect(
    await page.evaluate(() => [localStorage.length, sessionStorage.length]),
  ).toEqual([0, 0]);
  expect(errors).toEqual([]);
  expect(external).toEqual([]);
  expect(mutations).toEqual([]);
});

test("every module is navigable and labelled unavailable", async ({
  page,
}, testInfo) => {
  await page.goto("/app/rooms");
  for (const item of modules) {
    if (testInfo.project.name === "mobile") {
      await page.getByRole("button", { name: "More navigation" }).click();
      await page
        .getByRole("navigation", { name: "All modules" })
        .getByRole("link", { name: item.label, exact: true })
        .click();
    } else
      await page
        .getByRole("navigation", { name: "Workspace navigation" })
        .getByRole("link", { name: item.label, exact: true })
        .click();
    await expect(page).toHaveURL(`/app/${item.id}`);
    await expect(
      page.getByRole("heading", { level: 1, name: item.title }),
    ).toBeVisible();
    await expect(page.locator(".section-bar")).toContainText("Unavailable");
    await expect(page.locator(".breadcrumbs [aria-current=page]")).toHaveText(
      item.label,
    );
  }
});

test("keyboard focus, modal containment, Escape and reduced motion", async ({
  page,
}) => {
  await page.goto("/design-system");
  await page.keyboard.press("Tab");
  expect(await page.locator(":focus-visible").count()).toBe(1);
  expect(
    await page
      .locator(":focus-visible")
      .evaluate((node) => getComputedStyle(node).outlineStyle),
  ).toBe("solid");
  const trigger = page.getByRole("button", { name: "Open example dialog" });
  await trigger.click();
  const dialog = page.getByRole("dialog", { name: "Example dialog" });
  await expect(dialog).toBeVisible();
  for (let index = 0; index < 8; index++) {
    await page.keyboard.press("Tab");
    expect(
      await dialog.evaluate((node) => node.contains(document.activeElement)),
    ).toBe(true);
  }
  await page.keyboard.press("Shift+Tab");
  expect(
    await dialog.evaluate((node) => node.contains(document.activeElement)),
  ).toBe(true);
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(trigger).toBeFocused();
  await page.getByRole("button", { name: "Show error example" }).click();
  await expect(page.locator("main").getByRole("alert")).toContainText(
    "Unable to load this example",
  );
  await expect(
    page.getByRole("button", { name: "Loading example", exact: true }),
  ).toBeDisabled();
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(
    await page
      .locator(".spinner")
      .first()
      .evaluate((node) => getComputedStyle(node).animationName),
  ).toBe("none");
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
});

test("mobile inspector sheet closes and restores focus", async ({
  page,
}, testInfo) => {
  test.skip(
    testInfo.project.name !== "mobile",
    "Bottom sheet is the mobile layout only",
  );
  await page.goto("/app/rooms");
  const trigger = page.getByRole("button", {
    name: "Workspace details",
    exact: true,
  });
  await trigger.click();
  const dialog = page.getByRole("dialog", { name: "Workspace details" });
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText("No room selected");
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: testInfo.outputPath("inspector-sheet.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "Close workspace details" }).click();
  await expect(trigger).toBeFocused();
});

test("P01 hero, marketing routes and missing route", async ({
  page,
}, testInfo) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Compute together. Reveal nothing.",
  );
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: testInfo.outputPath("marketing.png"),
    fullPage: true,
  });
  await page.getByRole("link", { name: "Security", exact: true }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Security");
  await expect(page.getByText("Unavailable", { exact: true })).toBeVisible();
  const response = await page.goto("/app/not-a-module");
  expect(response?.status()).toBe(404);
});

test("narrow viewport and skip link", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await page.goto("/app/rooms");
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to content" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});
