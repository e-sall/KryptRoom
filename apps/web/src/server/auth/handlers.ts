import "server-only";
import { NextRequest, NextResponse } from "next/server";
import { randomUUID } from "node:crypto";
import * as oidc from "openid-client";
import { createRemoteJWKSet, jwtVerify } from "jose";
import type { PoolClient } from "pg";
import { config, provider } from "./config";
import { csrfValid, digest, equal, opaque, proxyPath, returnPath, seal, unseal } from "./security";

function output(data: unknown, status = 200) {
  const correlation = randomUUID();
  return NextResponse.json({data, correlation_id: correlation}, {
    status, headers: {"Cache-Control": "private, no-store", "Referrer-Policy": "no-referrer",
      "X-Correlation-ID":correlation},
  });
}
function denied(status = 401) {
  const correlation = randomUUID();
  return NextResponse.json({error: {code: status === 403 ? "permission_denied" : "request_rejected",
    message: "Request could not be completed"}, correlation_id: correlation}, {
    status, headers: {"Cache-Control": "private, no-store", "X-Correlation-ID":correlation},
  });
}
export async function guarded(fn: () => Promise<NextResponse>) {
  try { return await fn(); } catch { return denied(503); }
}
function cookie(response: NextResponse, name: string, value: string, seconds: number) {
  response.cookies.set(name, value, {secure: config().secure, httpOnly: true,
    sameSite: "lax", path: "/", maxAge: seconds});
}
function redirect(url: URL | string) {
  const response = NextResponse.redirect(url, 303);
  response.headers.set("Cache-Control", "private, no-store");
  response.headers.set("Referrer-Policy", "no-referrer");
  return response;
}
async function body(request: NextRequest, max = 16384): Promise<string> {
  if (Number(request.headers.get("content-length") || 0) > max) throw new Error("Body too large");
  const reader = request.body?.getReader();
  if (!reader) return "";
  const chunks: Uint8Array[] = []; let length = 0;
  try {
    for (;;) {
      const item = await reader.read(); if (item.done) break;
      length += item.value.length;
      if (length > max) throw new Error("Body too large");
      chunks.push(item.value);
    }
    return Buffer.concat(chunks).toString("utf8");
  } finally { await reader.cancel(); }
}
export async function login(request: NextRequest) {
  const c = config(), p = await provider();
  const state = opaque(), nonce = opaque(), verifier = oidc.randomPKCECodeVerifier(), browser = opaque();
  const stateHash = digest(c.hashKey, state);
  const payload = JSON.stringify({state, nonce, verifier, returnPath: returnPath(request.nextUrl.searchParams.get("returnTo"))});
  await c.pool.query("INSERT INTO bff_auth.oidc_transactions(state_hash,browser_hash,encrypted_payload,expires_at) VALUES($1,$2,$3,now()+interval '5 minutes')",
    [stateHash, digest(c.hashKey, browser), seal(c.encryptKey, c.keyId, `oidc:${stateHash}`, payload)]);
  const url = oidc.buildAuthorizationUrl(p, {redirect_uri: c.site + "/auth/callback",
    response_type: "code", scope: "openid profile email", state, nonce,
    code_challenge: await oidc.calculatePKCECodeChallenge(verifier), code_challenge_method: "S256"});
  const response = redirect(url);
  cookie(response, c.transactionCookie, browser, 300);
  return response;
}
export async function callback(request: NextRequest) {
  const c = config(), state = request.nextUrl.searchParams.get("state"), browser = request.cookies.get(c.transactionCookie)?.value;
  if (!state || !browser || !/^[A-Za-z0-9_-]{43}$/.test(state) || !/^[A-Za-z0-9_-]{43}$/.test(browser)) return denied();
  const stateHash = digest(c.hashKey, state);
  // Consume before network access; replay or partial provider failure requires a new login.
  const record = await c.pool.query("DELETE FROM bff_auth.oidc_transactions WHERE state_hash=$1 AND browser_hash=$2 AND expires_at>now() RETURNING encrypted_payload",
    [stateHash, digest(c.hashKey, browser)]);
  if (record.rowCount !== 1) return denied();
  const transaction = JSON.parse(unseal(c.encryptKey, c.keyId, `oidc:${stateHash}`, record.rows[0].encrypted_payload));
  if (!equal(transaction.state, state)) return denied();
  const p = await provider();
  // Construct callback from fixed site, never forwarded Host/proxy headers.
  const url = new URL(c.site + "/auth/callback" + request.nextUrl.search);
  let tokens: Awaited<ReturnType<typeof oidc.authorizationCodeGrant>>;
  try {
    tokens = await oidc.authorizationCodeGrant(p, url, {expectedState: state,
      expectedNonce: transaction.nonce, pkceCodeVerifier: transaction.verifier, idTokenExpected: true});
  } catch (error) {
    if (error instanceof oidc.ClientError || error instanceof oidc.AuthorizationResponseError ||
        (error instanceof oidc.ResponseBodyError && ["invalid_grant","invalid_request"].includes(error.error)))
      return denied();
    throw error;
  }
  const claims = tokens.claims();
  if (!claims?.sub || !tokens.access_token) return denied();
  const identity = await fetch(c.api + "/api/v1/auth/complete", {method: "POST",
    headers: {Authorization: `Bearer ${tokens.access_token}`}, cache: "no-store", redirect: "error",
    signal: AbortSignal.timeout(5000)});
  if (!identity.ok) return denied(identity.status === 403 ? 403 : 401);
  const user = await identity.json();
  if (typeof user.data?.id !== "string") return denied();
  const sid = opaque(), idHash = digest(c.hashKey, sid), db = await c.pool.connect();
  try {
    await db.query("BEGIN");
    const old = request.cookies.get(c.cookie)?.value;
    if (old) await db.query("UPDATE bff_auth.sessions SET revoked_at=now(),version=version+1 WHERE id_hash=$1", [digest(c.hashKey, old)]);
    await db.query(`INSERT INTO bff_auth.sessions(id_hash,user_id,issuer,subject,provider_sid,
      encrypted_access_token,encrypted_refresh_token,token_expires_at,created_at,last_seen_at,
      idle_expires_at,absolute_expires_at,encryption_key_id,version)
      VALUES($1,$2,$3,$4,$5,$6,$7,now()+($8*interval '1 second'),now(),now(),
      now()+interval '30 minutes',now()+interval '8 hours',$9,1)`, [idHash, user.data.id,
      c.issuer, claims.sub, claims.sid || null,
      seal(c.encryptKey,c.keyId,`access:${idHash}`,tokens.access_token),
      tokens.refresh_token ? seal(c.encryptKey,c.keyId,`refresh:${idHash}`,tokens.refresh_token) : null,
      tokens.expires_in || 300, c.keyId]);
    await db.query("COMMIT");
  } catch { await db.query("ROLLBACK"); throw new Error("Session creation failed"); }
  finally { db.release(); }
  const response = redirect(new URL(returnPath(transaction.returnPath), c.site));
  cookie(response, c.cookie, sid, 28800); cookie(response, c.transactionCookie, "", 0);
  return response;
}
type Session = { idHash: string; token: string; csrf: string; };
async function session(request: NextRequest, db: PoolClient): Promise<Session | null> {
  const c = config(), sid = request.cookies.get(c.cookie)?.value;
  if (!sid || !/^[A-Za-z0-9_-]{43}$/.test(sid)) return null;
  const idHash = digest(c.hashKey, sid);
  const result = await db.query(`SELECT *, idle_expires_at>now() AND absolute_expires_at>now() AS alive
    FROM bff_auth.sessions WHERE id_hash=$1 FOR UPDATE`, [idHash]);
  if (result.rowCount !== 1) return null;
  const row = result.rows[0];
  if (row.revoked_at || !row.alive || row.issuer !== c.issuer) {
    await db.query("UPDATE bff_auth.sessions SET revoked_at=coalesce(revoked_at,now()) WHERE id_hash=$1", [idHash]); return null;
  }
  let token: string;
  try {
    token = unseal(c.encryptKey, c.keyId, `access:${idHash}`, row.encrypted_access_token);
    if (row.token_expires_at.getTime() < Date.now() + 15000) {
      if (!row.encrypted_refresh_token) throw new Error("Refresh unavailable");
      const refresh = unseal(c.encryptKey,c.keyId,`refresh:${idHash}`,row.encrypted_refresh_token);
      const tokens = await oidc.refreshTokenGrant(await provider(), refresh);
      token = tokens.access_token;
      await db.query(`UPDATE bff_auth.sessions SET encrypted_access_token=$2,
        encrypted_refresh_token=$3,token_expires_at=now()+($4*interval '1 second'),version=version+1
        WHERE id_hash=$1`, [idHash, seal(c.encryptKey,c.keyId,`access:${idHash}`,token),
        seal(c.encryptKey,c.keyId,`refresh:${idHash}`,tokens.refresh_token || refresh), tokens.expires_in || 300]);
    }
  } catch {
    await db.query("UPDATE bff_auth.sessions SET revoked_at=now(),version=version+1 WHERE id_hash=$1", [idHash]);
    return null;
  }
  await db.query(`UPDATE bff_auth.sessions SET last_seen_at=now(),
    idle_expires_at=least(absolute_expires_at,now()+interval '30 minutes') WHERE id_hash=$1`, [idHash]);
  return {idHash, token, csrf: digest(c.hashKey, "csrf:" + sid)};
}
async function authenticated(request: NextRequest, action: (s: Session, db: PoolClient) => Promise<NextResponse>) {
  const db = await config().pool.connect();
  try {
    await db.query("BEGIN");
    const s = await session(request, db);
    const response = s ? await action(s, db) : denied();
    await db.query("COMMIT"); return response;
  } catch { await db.query("ROLLBACK"); throw new Error("Authenticated request failed"); }
  finally { db.release(); }
}
export async function proxy(request: NextRequest, path: string[]) {
  const route = proxyPath(path, request.method);
  if (!route) return denied(404);
  return authenticated(request, async (s, db) => {
    const c = config(), write = request.method !== "GET";
    if (write && !csrfValid(request.headers,c.site,s.csrf)) return denied(403);
    const query = new URLSearchParams();
    for (const [key,value] of request.nextUrl.searchParams) {
      if (request.method !== "GET" || !["limit","cursor"].includes(key) || query.has(key) ||
          value.length > 512) return denied(400);
      query.set(key,value);
    }
    const headers: Record<string,string> = {Authorization: `Bearer ${s.token}`, Accept: "application/json"};
    if (write) {
      headers["Content-Type"] = "application/json";
      for (const name of ["if-match","idempotency-key"]) {
        const value = request.headers.get(name); if (value) headers[name] = value;
      }
    }
    const upstream = await fetch(c.api + route + (query.size ? "?"+query : ""), {method: request.method,
      headers, body: write ? await body(request) : undefined, redirect: "error", cache: "no-store",
      signal: AbortSignal.timeout(5000)});
    if (upstream.status === 401) await db.query("UPDATE bff_auth.sessions SET revoked_at=now() WHERE id_hash=$1",[s.idHash]);
    const data = await upstream.json();
    const response = NextResponse.json(data,{status: upstream.status,headers:{"Cache-Control":"private, no-store"}});
    if (typeof data.correlation_id === "string") response.headers.set("X-Correlation-ID",data.correlation_id);
    const etag = upstream.headers.get("etag"); if (etag) response.headers.set("ETag",etag);
    if (!write) response.headers.set("X-CSRF-Token",s.csrf);
    return response;
  });
}
export async function logout(request: NextRequest) {
  return authenticated(request, async (s, db) => {
    const c = config();
    if (!csrfValid(request.headers,c.site,s.csrf)) return denied(403);
    await db.query("UPDATE bff_auth.sessions SET revoked_at=now(),version=version+1 WHERE id_hash=$1",[s.idHash]);
    let destination: string | null = null;
    try { destination = oidc.buildEndSessionUrl(await provider(), {client_id:"kryptroom-web-bff",
      post_logout_redirect_uri:c.site+"/"}).href; } catch { /* Local revocation remains effective. */ }
    const response = output({loggedOut:true,providerLogout:destination});
    cookie(response,c.cookie,"",0); return response;
  });
}
let logoutKeys: ReturnType<typeof createRemoteJWKSet> | undefined;
export async function backchannel(request: NextRequest) {
  if (request.headers.get("content-type")?.split(";")[0] !== "application/x-www-form-urlencoded") return denied(400);
  const raw = new URLSearchParams(await body(request)).get("logout_token");
  if (!raw || raw.length > 16384) return denied(400);
  const c = config(), p = await provider(), uri = p.serverMetadata().jwks_uri;
  if (!uri?.startsWith(c.issuer + "/")) return denied(400);
  logoutKeys ??= createRemoteJWKSet(new URL(uri),{timeoutDuration:3000});
  let payload;
  try {
    ({payload} = await jwtVerify(raw,logoutKeys,{issuer:c.issuer,audience:"kryptroom-web-bff",
      algorithms:["RS256"],clockTolerance:30,maxTokenAge:300,requiredClaims:["iat","jti","events"]}));
  } catch { return denied(400); }
  const events = payload.events as Record<string,unknown> | undefined;
  if (typeof payload.jti !== "string" || !payload.jti || payload.jti.length > 255 || "nonce" in payload ||
      (!payload.sid && !payload.sub) || !events ||
      (payload.sid !== undefined && (typeof payload.sid !== "string" || !payload.sid || payload.sid.length > 255)) ||
      (payload.sub !== undefined && (typeof payload.sub !== "string" || !payload.sub || payload.sub.length > 255)) ||
      JSON.stringify(events["http://schemas.openid.net/event/backchannel-logout"]) !== "{}") return denied(400);
  const db = await c.pool.connect();
  try {
    await db.query("BEGIN");
    const inserted = await db.query(`INSERT INTO bff_auth.logout_replays(issuer,jti,expires_at)
      VALUES($1,$2,now()+interval '10 minutes') ON CONFLICT DO NOTHING RETURNING jti`,[c.issuer,payload.jti]);
    if (inserted.rowCount !== 1) { await db.query("ROLLBACK"); return denied(400); }
    await db.query(`UPDATE bff_auth.sessions SET revoked_at=now(),version=version+1
      WHERE issuer=$1 AND ${payload.sid ? "provider_sid" : "subject"}=$2`,[c.issuer,payload.sid || payload.sub]);
    await db.query("COMMIT"); return output({accepted:true});
  } catch { await db.query("ROLLBACK"); throw new Error("Logout processing failed"); }
  finally { db.release(); }
}
