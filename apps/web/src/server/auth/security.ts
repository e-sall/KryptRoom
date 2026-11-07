import "server-only";
import { createCipheriv, createDecipheriv, createHmac, randomBytes, timingSafeEqual } from "node:crypto";

export function opaque(): string { return randomBytes(32).toString("base64url"); }
export function digest(key: Buffer, value: string): string {
  return createHmac("sha256", key).update(value).digest("hex");
}
export function equal(a: string, b: string): boolean {
  const x = Buffer.from(a), y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}
export function seal(key: Buffer, keyId: string, purpose: string, value: string): string {
  const nonce = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", key, nonce);
  cipher.setAAD(Buffer.from(`${keyId}:${purpose}`));
  const body = Buffer.concat([cipher.update(value, "utf8"), cipher.final()]);
  return [keyId, nonce.toString("base64url"), body.toString("base64url"),
    cipher.getAuthTag().toString("base64url")].join(".");
}
export function unseal(key: Buffer, keyId: string, purpose: string, value: string): string {
  const parts = value.split(".");
  if (parts.length !== 4 || parts[0] !== keyId) throw new Error("Invalid protected record");
  const nonce = Buffer.from(parts[1], "base64url"), tag = Buffer.from(parts[3], "base64url");
  if (nonce.length !== 12 || tag.length !== 16) throw new Error("Invalid protected record");
  const cipher = createDecipheriv("aes-256-gcm", key, nonce);
  cipher.setAAD(Buffer.from(`${keyId}:${purpose}`)); cipher.setAuthTag(tag);
  return Buffer.concat([cipher.update(Buffer.from(parts[2], "base64url")), cipher.final()]).toString("utf8");
}
export function returnPath(value: string | null): string {
  if (!value || !value.startsWith("/") || value.startsWith("//") || /[\\\r\n\x00]/.test(value))
    return "/bff/api/v1/me";
  try {
    const decoded = decodeURIComponent(value);
    if (decoded.startsWith("//") || /[\\\r\n\x00]/.test(decoded)) return "/bff/api/v1/me";
  } catch { return "/bff/api/v1/me"; }
  // Only internal navigations; never interpret a browser-supplied authority.
  const parsed = new URL(value, "https://local.invalid");
  return parsed.origin === "https://local.invalid" ? parsed.pathname + parsed.search : "/bff/api/v1/me";
}
export function proxyPath(path: string[], method: string): string | null {
  const id = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}";
  const route = path.join("/");
  const allowed: Record<string, RegExp[]> = {
    GET: [/^me(?:\/registrations)?$/, /^organizations$/, new RegExp(`^organizations/${id}(?:/members)?$`)],
    POST: [/^organizations$/],
    PATCH: [new RegExp(`^organizations/${id}(?:/members/${id})?$`)],
    DELETE: [new RegExp(`^organizations/${id}/members/${id}$`)],
  };
  return path.every(p => !p.includes("/") && !p.includes("%")) &&
    allowed[method]?.some(rule => rule.test(route)) ? `/api/v1/${route}` : null;
}
export function csrfValid(headers: Headers, origin: string, expected: string): boolean {
  return headers.get("origin") === origin && equal(headers.get("x-csrf-token") || "", expected) &&
    ["same-origin", "none"].includes(headers.get("sec-fetch-site") || "") &&
    headers.get("content-type")?.split(";")[0].trim() === "application/json";
}
