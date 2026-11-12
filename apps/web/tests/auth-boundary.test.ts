import { readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import { expect, it } from "vitest";
import ts from "typescript";
import { m9ServerFile } from "./m9-server-boundary";

it("never exempts arbitrary or future server files from the M8 boundary", () => {
  expect(m9ServerFile(resolve("src/server/auth"),"handlers.ts")).toBe(true);
  for (const name of ["future.ts","handlers.tsx","rooms.ts"])
    expect(m9ServerFile(resolve("src/server/auth"),name)).toBe(false);
  expect(m9ServerFile(resolve("src/features/marketing"),"handlers.ts")).toBe(false);
  expect(m9ServerFile(resolve("src/app/health/ready"),"route.ts")).toBe(true);
  expect(m9ServerFile(resolve("src/app/health/ready"),"future.ts")).toBe(false);
  expect(m9ServerFile(resolve("src/app/health/future"),"route.ts")).toBe(false);
});
it("keeps server authority out of every presentation import and the Core", () => {
  for (const entry of readdirSync("src",{recursive:true,withFileTypes:true})) {
    if (!entry.isFile() || !/\.tsx?$/.test(entry.name)) continue;
    const file = resolve(entry.parentPath,entry.name), code = readFileSync(file,"utf8");
    expect(code).not.toMatch(/from ["'].*(?:engines|krypt-node|secretflow|openfhe|web3)/);
    if (m9ServerFile(entry.parentPath,entry.name)) {
      if (file.includes("server")) expect(code).toContain('import "server-only"');
      continue;
    }
    const parsed = ts.createSourceFile(file,code,ts.ScriptTarget.Latest,true);
    for (const statement of parsed.statements) {
      if (!ts.isImportDeclaration(statement) || !ts.isStringLiteral(statement.moduleSpecifier)) continue;
      const source = statement.moduleSpecifier.text;
      const target = source.startsWith("@/") ? resolve("src",source.slice(2)) : resolve(entry.parentPath,source);
      expect(target.startsWith(resolve("src/server")+"\\") || target.startsWith(resolve("src/server")+"/"),file).toBe(false);
    }
    expect(code,file).not.toMatch(/\bimport\s*\(\s*["'](?:@\/server|[^"']*server\/auth)/);
  }
});
