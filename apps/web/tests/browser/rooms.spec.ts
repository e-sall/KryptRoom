import { test, expect, type Page, type TestInfo } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

async function checkView(page: Page, info: TestInfo, name: string) {
  await page.evaluate(() => window.scrollTo(0, 0));
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
    path: info.outputPath(`${name}.png`),
    fullPage: true,
  });
  if (info.project.name === "mobile") {
    await page.screenshot({
      path: info.outputPath(`${name}-viewport.png`),
      fullPage: false,
    });
  }
}
test("P03 list, cards, search, filter, expansion and scoped navigation", async ({
  page,
}, info) => {
  await page.goto("/preview/rooms");
  await expect(
    page.getByRole("button", { name: "List", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  const expand = page.getByRole("button", {
    name: "Expand Supply Chain Collaboration",
  });
  await expand.click();
  await expect(expand).toHaveAttribute("aria-expanded", "true");
  await checkView(page, info, "rooms-list");
  await expand.click();
  await expect(expand).toHaveAttribute("aria-expanded", "false");
  await page.getByLabel("Search Rooms").fill(" research ");
  await expect(page.locator(".room-item")).toHaveCount(1);
  await page.getByLabel("Status", { exact: true }).selectOption("Ready");
  await expect(
    page.getByRole("heading", { name: "No matching example Rooms" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Reset example view" }).click();
  await page.getByRole("button", { name: "Cards", exact: true }).click();
  await page
    .getByRole("button", { name: "Select Research Partnership" })
    .click();
  await expect(
    page.getByRole("button", { name: "Select Research Partnership" }),
  ).toHaveAttribute("aria-pressed", "true");
  await page
    .getByRole("button", { name: "Select Supply Chain Collaboration" })
    .click();
  await checkView(page, info, "rooms-cards");
  if (info.project.name === "mobile") {
    const trigger = page.getByRole("button", {
      name: "Workspace details",
      exact: true,
    });
    await trigger.click();
    const dialog = page.getByRole("dialog", { name: "Workspace details" });
    await expect(dialog).toContainText("Supply Chain Collaboration");
    for (let i = 0; i < 7; i++) {
      await page.keyboard.press("Tab");
      expect(
        await dialog.evaluate((n) => n.contains(document.activeElement)),
      ).toBe(true);
    }
    await page.keyboard.press("Shift+Tab");
    await checkView(page, info, "room-sheet");
    await page.keyboard.press("Escape");
    await expect(trigger).toBeFocused();
    await trigger.click();
    await dialog.getByRole("link", { name: "View Room details" }).click();
  } else
    await page
      .getByLabel("Context inspector")
      .getByRole("link", { name: "View Room details" })
      .click();
  await expect(page).toHaveURL("/preview/rooms/supply-chain");
  await expect(page.locator("main")).toBeFocused();
  await page
    .locator("main")
    .getByRole("link", { name: "Open Workspace", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Graph Workspace is reserved for PR3" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "All example Rooms" }).click();
  await expect(
    page.getByRole("button", { name: "Cards", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await page.reload();
  await expect(
    page.getByRole("button", { name: "List", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
});
test("P06 four steps, validation, ephemeral draft and permanently denied operations", async ({
  page,
}, info) => {
  await page.goto("/preview/rooms/new");
  await checkView(page, info, "setup-identity");
  await page.getByRole("button", { name: "Continue preview" }).click();
  await expect(page.locator("main").getByRole("alert")).toContainText(
    "Room name",
  );
  await expect(page.getByLabel("Room name", { exact: true })).toBeFocused();
  await page
    .getByLabel("Room name", { exact: true })
    .fill("Example collaboration");
  await page
    .getByLabel("Description (optional)")
    .fill("Fictional metadata only");
  await expect(
    page.getByRole("button", { name: "Create Room", exact: true }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Continue preview" }).click();
  await page
    .getByLabel("Organization name (optional)")
    .fill("Example Organization B");
  await page.getByLabel("Invite by organization email").fill("invalid");
  await page.getByRole("button", { name: "Continue preview" }).click();
  await expect(page.locator("main").getByRole("alert")).toContainText(
    "valid example email",
  );
  await page
    .getByLabel("Invite by organization email")
    .fill("partner@example.invalid");
  await expect(
    page.getByRole("button", { name: "Send invitation" }),
  ).toBeDisabled();
  await checkView(page, info, "setup-participants");
  await page.getByRole("button", { name: "Continue preview" }).click();
  await page
    .getByLabel("Opaque example reference (optional)")
    .fill("C:/private.csv");
  await page.getByRole("button", { name: "Continue preview" }).click();
  await expect(page.locator("main").getByRole("alert")).toContainText(
    "example-only reference",
  );
  await page
    .getByLabel("Opaque example reference (optional)")
    .fill("example-source-b");
  await page
    .getByLabel("Owning organization")
    .selectOption("Example Organization B");
  await checkView(page, info, "setup-data");
  await page.getByRole("button", { name: "Continue preview" }).click();
  await page.getByLabel("Output disclosure").selectOption("request-aggregate");
  await page.getByRole("button", { name: "Review example fields" }).click();
  await expect(page.getByText(/Example fields reviewed/)).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Save Room policy" }),
  ).toBeDisabled();
  await checkView(page, info, "setup-policies");
  if (info.project.name === "mobile")
    await page
      .getByRole("button", { name: "Workspace details", exact: true })
      .click();
  await expect(
    page
      .getByRole("button", { name: "Run Computation", exact: true })
      .filter({ visible: true }),
  ).toBeDisabled();
  if (info.project.name === "mobile") await page.keyboard.press("Escape");
  for (let i = 0; i < 3; i++)
    await page.getByRole("button", { name: "Back", exact: true }).click();
  await expect(page.getByLabel("Room name", { exact: true })).toHaveValue(
    "Example collaboration",
  );
  await page.getByRole("link", { name: "All example Rooms" }).click();
  await page.getByRole("link", { name: "Create Room preview" }).click();
  await expect(page.getByLabel("Room name", { exact: true })).toHaveValue(
    "Example collaboration",
  );
  await page.reload();
  await expect(page.getByLabel("Room name", { exact: true })).toHaveValue("");
});
test("system states clear inspector; narrow screens and reduced motion", async ({
  page,
}, info) => {
  await page.goto("/preview/rooms");
  await page.getByText("Preview system states", { exact: true }).click();
  for (const name of ["empty", "loading", "blocked", "error", "unavailable"]) {
    await page.getByRole("button", { name, exact: true }).click();
    await expect(page.locator(".room-item")).toHaveCount(0);
    await expect(page.getByLabel("Context inspector")).not.toContainText(
      "Supply Chain",
    );
  }
  await page.getByRole("button", { name: "loading", exact: true }).click();
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(
    await page
      .locator(".spinner")
      .evaluate((n) => getComputedStyle(n).animationName),
  ).toBe("none");
  await page.getByRole("button", { name: "normal", exact: true }).click();
  await page.setViewportSize({ width: 320, height: 740 });
  await checkView(page, info, "narrow-list");
  await page.getByRole("button", { name: "Cards", exact: true }).click();
  await checkView(page, info, "narrow-cards");
  await page.getByRole("link", { name: "Create Room preview" }).click();
  for (const name of [
    "Room Identity",
    "Participants",
    "Protected Data Connections",
    "Security & Policies",
  ]) {
    await page
      .getByRole("navigation", { name: "Setup steps" })
      .getByRole("button", { name: new RegExp(name) })
      .click();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  }
});
test("preview remains disconnected and never becomes application authority", async ({
  page,
}) => {
  const requests: string[] = [],
    errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (req) => {
    if (
      req.method() !== "GET" ||
      new URL(req.url()).origin !== "http://127.0.0.1:3000"
    )
      requests.push(req.url());
  });
  await page.goto("/app/rooms");
  await expect(page.locator(".room-item")).toHaveCount(0);
  await page
    .getByRole("link", { name: "Explore synthetic Rooms preview" })
    .click();
  await page.getByRole("link", { name: "Create Room preview" }).click();
  await page
    .getByLabel("Room name", { exact: true })
    .fill("Example-only-marker");
  await page.getByRole("button", { name: "Continue preview" }).click();
  await page.getByRole("link", { name: "Exit to application" }).click();
  await expect(page).toHaveURL("/app/rooms");
  await expect(page.locator("body")).not.toContainText("Example-only-marker");
  await expect(
    page.getByRole("button", { name: "Create Room", exact: true }),
  ).toBeDisabled();
  await page.goto("/app/rooms/new");
  await expect(
    page.getByRole("heading", { name: "Room creation service unavailable" }),
  ).toBeVisible();
  expect(await page.context().cookies()).toEqual([]);
  expect(
    await page.evaluate(() => [localStorage.length, sessionStorage.length]),
  ).toEqual([0, 0]);
  expect(requests).toEqual([]);
  expect(errors).toEqual([]);
  expect((await page.goto("/preview/rooms/not-a-fixture"))?.status()).toBe(404);
});
