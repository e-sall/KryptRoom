import { readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import { expect, it } from "vitest";

it("preserves the approved palette and responsive/motion contracts", () => {
  const tokens = readFileSync("src/styles/tokens.css", "utf8");
  const expected = {
    background: "10100F",
    surface: "191918",
    elevated: "242422",
    border: "343432",
    "text-primary": "F1F0EB",
    "text-secondary": "A9A9A2",
    blue: "7CAAD5",
    "blue-muted": "334B60",
    action: "EDECE6",
    success: "84B89A",
    warning: "DBB477",
  };
  for (const [name, value] of Object.entries(expected))
    expect(tokens).toMatch(new RegExp(`--kr-${name}:\\s*#${value}`, "i"));
  const css = readFileSync("src/app/globals.css", "utf8");
  expect(css).toContain("prefers-reduced-motion: reduce");
  expect(css).toContain(":focus-visible");
  expect(css).toContain("min-width: 768px");
  expect(css).toContain("max-width: 1199px");
  expect(css).toContain("max-width: 767px");
});

it("keeps PR1 free of application I/O and stored participant data", () => {
  const files = readdirSync("src", {
    recursive: true,
    withFileTypes: true,
  }).filter((entry) => entry.isFile() && /\.(tsx?|css)$/.test(entry.name));
  for (const entry of files) {
    const source = readFileSync(resolve(entry.parentPath, entry.name), "utf8");
    expect(source, entry.name).not.toMatch(
      /\b(fetch\s*\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage|indexedDB|document\.cookie|dangerouslySetInnerHTML)\b/,
    );
  }
});
