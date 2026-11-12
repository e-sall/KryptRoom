import { relative, resolve } from "node:path";

const files = new Set([
  "server/auth/security.ts", "server/auth/config.ts", "server/auth/handlers.ts",
  "app/auth/login/route.ts", "app/auth/callback/route.ts", "app/auth/logout/route.ts",
  "app/auth/backchannel-logout/route.ts", "app/bff/api/v1/[...path]/route.ts",
  "app/health/ready/route.ts", // PR5 server-only operational readiness, not presentation I/O.
]);
export function m9ServerFile(parent: string, name: string): boolean {
  return files.has(relative(resolve("src"),resolve(parent,name)).replaceAll("\\","/"));
}
