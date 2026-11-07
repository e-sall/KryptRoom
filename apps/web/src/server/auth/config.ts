import "server-only";
import { lstatSync, readFileSync } from "node:fs";
import { Pool } from "pg";
import * as oidc from "openid-client";

function secret(name: string): string {
  const file = process.env[name];
  if (!file) throw new Error("BFF credential unavailable");
  const info = lstatSync(file);
  if (!info.isFile() || info.isSymbolicLink() || info.nlink !== 1 ||
      (process.platform !== "win32" && ((info.mode & 0o777) !== 0o400 || info.uid !== process.getuid?.())))
    throw new Error("Invalid BFF credential metadata");
  const value = readFileSync(file, "utf8");
  if (!/^[A-Za-z0-9_-]{24,128}$/.test(value)) throw new Error("Invalid BFF credential");
  return value;
}
function origin(name: string, local: boolean): string {
  const value = process.env[name];
  if (!value) throw new Error("BFF endpoint unavailable");
  const url = new URL(value);
  if (url.username || url.password || url.search || url.hash || url.pathname !== "/" ||
      (url.protocol !== "https:" && !(local && url.protocol === "http:" &&
       ["127.0.0.1", "localhost"].includes(url.hostname)))) throw new Error("Invalid BFF endpoint");
  return url.origin;
}
function key(name: string): Buffer {
  const value = secret(name), bytes = Buffer.from(value, "base64url");
  if (bytes.length !== 32 || bytes.toString("base64url") !== value) throw new Error("Invalid BFF key");
  return bytes;
}
let cached: ReturnType<typeof configure> | undefined;
function configure() {
  const local = process.env.KR_BFF_PROFILE === "local";
  const site = origin("KR_BFF_ORIGIN", local), api = origin("KR_API_ORIGIN", local);
  const issuer = new URL(process.env.KR_OIDC_ISSUER || "");
  if (issuer.protocol !== "https:" || issuer.username || issuer.password || issuer.search || issuer.hash)
    throw new Error("Invalid trusted issuer");
  const encryptKey = key("KR_BFF_ENCRYPTION_KEY_FILE"), hashKey = key("KR_BFF_HASH_KEY_FILE");
  if (encryptKey.equals(hashKey)) throw new Error("Separate BFF keys required");
  const keyId = process.env.KR_BFF_KEY_ID || "local-v1";
  if (!/^[A-Za-z0-9_-]{1,48}$/.test(keyId)) throw new Error("Invalid key identifier");
  const pool = new Pool({host: process.env.KR_BFF_DB_HOST || "127.0.0.1",
    port: Number(process.env.KR_BFF_DB_PORT || "5432"), database: "kryptroom",
    user: "kryptroom_bff", password: secret("KR_BFF_DB_PASSWORD_FILE"),
    ssl: local ? false : {rejectUnauthorized: true}, max: 5, connectionTimeoutMillis: 2000,
    statement_timeout: 5000, application_name: "kryptroom-bff"});
  pool.on("error", () => { /* Drop failed idle connections; requests fail closed, no driver detail logged. */ });
  return { local, site, api, issuer: issuer.href.replace(/\/$/, ""), encryptKey, hashKey, keyId,
    cookie: local && site.startsWith("http:") ? "kr_dev_sid" : "__Host-kr_sid",
    transactionCookie: local && site.startsWith("http:") ? "kr_dev_oidc" : "__Host-kr_oidc",
    secure: site.startsWith("https:"), clientSecret: secret("KR_OIDC_BFF_SECRET_FILE"),
    pool,
  };
}
export function config() { return cached ??= configure(); }
let discovered: Promise<oidc.Configuration> | undefined;
export function provider(): Promise<oidc.Configuration> {
  if (!discovered) {
    const c = config();
    discovered = oidc.discovery(new URL(c.issuer), "kryptroom-web-bff", {
      id_token_signed_response_alg: "RS256",
      token_endpoint_auth_method: "client_secret_basic",
    }, oidc.ClientSecretBasic(c.clientSecret), {timeout: 3, execute: [oidc.enableNonRepudiationChecks]})
      .then(p => {
        if (p.serverMetadata().issuer !== c.issuer) throw new Error("Issuer mismatch");
        for (const name of ["authorization_endpoint", "token_endpoint", "jwks_uri", "end_session_endpoint"] as const) {
          const endpoint = p.serverMetadata()[name];
          if (typeof endpoint !== "string" || !endpoint.startsWith(c.issuer + "/"))
            throw new Error("Untrusted identity endpoint");
        }
        return p;
      }).catch(() => { discovered = undefined; throw new Error("Identity provider unavailable"); });
  }
  return discovered;
}
