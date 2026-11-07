import { test, expect, type Browser, type BrowserContext } from "@playwright/test";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { randomUUID } from "node:crypto";

const site = "http://127.0.0.1:3004";
function password(user: string) {
  if (!["alice","bob","charlie","dora"].includes(user)) throw new Error("Unknown synthetic account");
  return readFileSync("/run/test-users/"+user+"_password","utf8");
}
async function checkpoint(name: "01-enrollment" | "02-restart" | "03-idp-stop" | "04-idp-start" |
  "05-refresh" | "06-refresh-check" | "07-invalid-refresh" | "08-idle-expiry" | "09-absolute-expiry" |
  "10-backchannel-check" | "11-direct-token-before", metadata = {}) {
  if (process.env.KR_TEST_QA_CHANNEL !== "/run/qa") throw new Error("Explicit synthetic QA channel required");
  writeFileSync(`/run/qa/${name}.json`,JSON.stringify(metadata),{mode:0o600,flag:"wx"});
  await expect.poll(() => existsSync(`/run/qa/${name}.ack`),{timeout:90000}).toBe(true);
}
async function authenticated(browser: Browser, user: string, emptyOrganizations = true) {
  const context = await browser.newContext();
  if (user === "alice") await context.addCookies([{name:"kr_dev_sid",value:"A".repeat(43),url:site,httpOnly:true,sameSite:"Lax"}]);
  const page = await context.newPage();
  await page.goto(site+"/auth/login");
  await page.locator("#username").fill(user);
  await page.locator("#password").fill(password(user));
  await page.locator("#kc-login").click();
  await page.waitForURL(site+"/bff/api/v1/me");
  const response = await context.request.get(site+"/bff/api/v1/me");
  expect(response.status()).toBe(200);
  const me = (await response.json()).data;
  if (emptyOrganizations) { expect(me.organizations).toEqual([]); expect(me.memberships).toEqual([]); }
  const cookies = await context.cookies(site);
  const sid = cookies.find(c => c.name === "kr_dev_sid");
  expect(sid?.value).toMatch(/^[A-Za-z0-9_-]{43}$/);
  expect(sid?.value).not.toBe("A".repeat(43));
  expect(sid?.httpOnly).toBe(true); expect(sid?.sameSite).toBe("Lax");
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual([]);
  expect(await page.content()).not.toMatch(/eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/);
  return {context,page,id:me.id as string};
}
async function write(context: BrowserContext, method: string, path: string, data: object = {}, extra = {}) {
  const self = await context.request.get(site+"/bff/api/v1/me");
  return context.request.fetch(site+path,{method,data,headers:{Origin:site,
    "Sec-Fetch-Site":"same-origin","Content-Type":"application/json",
    "X-CSRF-Token":self.headers()["x-csrf-token"],...extra}});
}
test.beforeAll(() => {
  if (process.env.CONTROL_TEST_IDENTITY !== "1" || !process.env.KR_TEST_TLS_SPKI)
    throw new Error("Select real isolated PR2 acceptance explicitly, with a pinned local test certificate");
});

test("real login, controlled tenants, RBAC, revocation, restart and IdP outage", async ({browser}) => {
  const alice = await authenticated(browser,"alice"), bob = await authenticated(browser,"bob");
  const charlie = await authenticated(browser,"charlie"), dora = await authenticated(browser,"dora");
  expect(new Set([alice.id,bob.id,charlie.id,dora.id]).size).toBe(4);
  const key = randomUUID();
  const regA = await write(alice.context,"POST","/bff/api/v1/organizations",{displayName:"Synthetic Org A"},{"Idempotency-Key":key});
  expect(regA.status()).toBe(202);
  const a = (await regA.json()).data; expect(a.status).toBe("PENDING_REVIEW");
  const replay = await write(alice.context,"POST","/bff/api/v1/organizations",{displayName:"Synthetic Org A"},{"Idempotency-Key":key});
  expect(replay.status()).toBe(202); expect((await replay.json()).data).toEqual(a);
  expect((await write(alice.context,"POST","/bff/api/v1/organizations",{displayName:"Changed request"},{"Idempotency-Key":key})).status()).toBe(409);
  expect((await write(alice.context,"POST","/bff/api/v1/organizations",{displayName:"Cross-site"},{"Origin":"https://untrusted.example.test","Idempotency-Key":randomUUID()})).status()).toBe(403);
  expect((await write(alice.context,"POST","/bff/api/v1/organizations",{displayName:"Wrong content type"},{"Content-Type":"text/plain","Idempotency-Key":randomUUID()})).status()).toBe(403);
  expect((await alice.context.request.get(site+"/bff/api/v1/run")).status()).toBe(404);
  const regB = await write(bob.context,"POST","/bff/api/v1/organizations",{displayName:"Synthetic Org B"},{"Idempotency-Key":randomUUID()});
  expect(regB.status()).toBe(202); const b = (await regB.json()).data;
  expect((await alice.context.request.get(site+"/bff/api/v1/organizations/"+a.id)).status()).toBe(404);
  const forged = await write(alice.context,"PATCH","/bff/api/v1/organizations/"+a.id,{status:"ACTIVE"},{"If-Match":'"1"'});
  expect(forged.status()).toBe(422);
  expect((await bob.context.request.get(site+"/bff/api/v1/me/registrations")).status()).toBe(200);
  await checkpoint("01-enrollment",{organizationA:a.id,organizationB:b.id,charlie:charlie.id,dora:dora.id});
  const charlieSelf = (await (await charlie.context.request.get(site+"/bff/api/v1/me")).json()).data;
  expect(charlieSelf.memberships).toHaveLength(1);
  expect(charlieSelf.memberships[0]).toMatchObject({organizationId:a.id,role:"ORG_MEMBER",status:"ACTIVE"});
  expect((await alice.context.request.get(site+"/bff/api/v1/organizations/"+b.id)).status()).toBe(404);
  expect((await bob.context.request.get(site+"/bff/api/v1/organizations/"+a.id)).status()).toBe(404);
  const list = await alice.context.request.get(site+`/bff/api/v1/organizations/${a.id}/members`);
  expect(list.status()).toBe(200); const members = (await list.json()).data.items;
  let cm = members.find((m: {userId:string}) => m.userId === charlie.id);
  const am = members.find((m: {userId:string}) => m.userId === alice.id);
  // QA-PR2-03: exercise role mutations through the real BFF/API, not SQL-only coverage.
  const promoted = await write(alice.context,"PATCH",`/bff/api/v1/organizations/${a.id}/members/${cm.id}`,
    {role:"ORG_ADMIN"},{"If-Match":`"${cm.version}"`});
  expect(promoted.status()).toBe(200); const previousVersion = cm.version;
  cm = (await promoted.json()).data;
  expect(cm).toMatchObject({role:"ORG_ADMIN",status:"ACTIVE",version:previousVersion+1});
  const memberRead = await alice.context.request.get(site+`/bff/api/v1/organizations/${a.id}/members`);
  expect((await memberRead.json()).data.items.find((m: {id:string}) => m.id === cm.id)).toEqual(cm);
  const beforeA = (await (await alice.context.request.get(site+`/bff/api/v1/organizations/${a.id}`)).json()).data;
  const beforeB = (await (await bob.context.request.get(site+`/bff/api/v1/organizations/${b.id}`)).json()).data;
  const beforeMembersA = (await (await alice.context.request.get(site+`/bff/api/v1/organizations/${a.id}/members`)).json()).data;
  const beforeMembersB = (await (await bob.context.request.get(site+`/bff/api/v1/organizations/${b.id}/members`)).json()).data;
  const bm = beforeMembersB.items.find((m: {userId:string}) => m.userId === bob.id);
  const foreignWrites = [
    await write(bob.context,"PATCH",`/bff/api/v1/organizations/${a.id}/members/${cm.id}`,{role:"ORG_OWNER"},{"If-Match":`"${cm.version}"`}),
    await write(bob.context,"DELETE",`/bff/api/v1/organizations/${a.id}/members/${cm.id}`,{},{"If-Match":`"${cm.version}"`}),
    await write(bob.context,"PATCH",`/bff/api/v1/organizations/${a.id}`,{displayName:"Unauthorized foreign A"},{"If-Match":`"${beforeA.version}"`}),
    await write(alice.context,"PATCH",`/bff/api/v1/organizations/${b.id}`,{displayName:"Unauthorized foreign B"},{"If-Match":`"${beforeB.version}"`}),
    await write(alice.context,"PATCH",`/bff/api/v1/organizations/${b.id}/members/${bm.id}`,{role:"ORG_MEMBER"},{"If-Match":`"${bm.version}"`}),
    await write(alice.context,"DELETE",`/bff/api/v1/organizations/${b.id}/members/${bm.id}`,{},{"If-Match":`"${bm.version}"`}),
  ];
  expect(foreignWrites.map(response => response.status())).toEqual([404,404,404,404,404,404]);
  expect((await (await alice.context.request.get(site+`/bff/api/v1/organizations/${a.id}`)).json()).data).toEqual(beforeA);
  expect((await (await bob.context.request.get(site+`/bff/api/v1/organizations/${b.id}`)).json()).data).toEqual(beforeB);
  expect((await (await alice.context.request.get(site+`/bff/api/v1/organizations/${a.id}/members`)).json()).data).toEqual(beforeMembersA);
  expect((await (await bob.context.request.get(site+`/bff/api/v1/organizations/${b.id}/members`)).json()).data).toEqual(beforeMembersB);
  console.log(JSON.stringify({qa:"QA-PR2-03",authorizedRoleChange:promoted.status(),foreignMutationStatuses:foreignWrites.map(r=>r.status()),foreignChangesPersisted:false}));
  expect((await write(charlie.context,"PATCH",`/bff/api/v1/organizations/${a.id}/members/${cm.id}`,{role:"ORG_OWNER"},{"If-Match":'"1"'})).status()).toBe(403);
  const demoted = await write(alice.context,"PATCH",`/bff/api/v1/organizations/${a.id}/members/${cm.id}`,
    {role:"ORG_MEMBER"},{"If-Match":`"${cm.version}"`});
  expect(demoted.status()).toBe(200); cm = (await demoted.json()).data;
  expect(cm.role).toBe("ORG_MEMBER");
  expect((await charlie.context.request.get(site+`/bff/api/v1/organizations/${a.id}`)).status()).toBe(200);
  expect((await alice.context.request.post(site+"/bff/api/v1/organizations",{data:{displayName:"No CSRF"}})).status()).toBe(403);
  expect((await write(alice.context,"DELETE",`/bff/api/v1/organizations/${a.id}/members/${am.id}`,{}, {"If-Match":`"${am.version}"`})).status()).toBe(409);
  expect((await write(dora.context,"DELETE",`/bff/api/v1/organizations/${a.id}/members/${cm.id}`,{}, {"If-Match":`"${cm.version}"`})).status()).toBe(200);
  expect((await charlie.context.request.get(site+`/bff/api/v1/organizations/${a.id}`)).status()).toBe(404);
  await checkpoint("05-refresh",{alice:alice.id,charlie:charlie.id});
  const refreshed = await Promise.all(Array.from({length:6},() => alice.context.request.get(site+"/bff/api/v1/me")));
  expect(refreshed.map(r => r.status())).toEqual([200,200,200,200,200,200]);
  expect((await charlie.context.request.get(site+`/bff/api/v1/organizations/${a.id}`)).status()).toBe(404);
  await checkpoint("06-refresh-check");
  await checkpoint("07-invalid-refresh",{dora:dora.id});
  expect((await dora.context.request.get(site+"/bff/api/v1/me")).status()).toBe(401);
  const idleDora = await authenticated(browser,"dora",false);
  await checkpoint("08-idle-expiry",{dora:dora.id});
  expect((await idleDora.context.request.get(site+"/bff/api/v1/me")).status()).toBe(401);
  const absoluteDora = await authenticated(browser,"dora",false);
  await checkpoint("09-absolute-expiry",{dora:dora.id});
  expect((await absoluteDora.context.request.get(site+"/bff/api/v1/me")).status()).toBe(401);
  await idleDora.context.close(); await absoluteDora.context.close();
  // Persisted identities, sessions and revocation survive all service restarts.
  await checkpoint("02-restart");
  await expect.poll(async () => {
    try { return (await alice.context.request.get(site+"/bff/api/v1/me")).status(); } catch { return 0; }
  },{timeout:90000}).toBe(200);
  expect((await charlie.context.request.get(site+`/bff/api/v1/organizations/${a.id}`)).status()).toBe(404);
  await checkpoint("03-idp-stop");
  expect((await alice.context.request.get(site+`/bff/api/v1/organizations/${a.id}`)).status()).toBe(503);
  expect((await alice.context.request.get("http://127.0.0.1:8001/health/live")).status()).toBe(200);
  expect((await alice.context.request.get("http://127.0.0.1:8001/health/ready")).status()).toBe(200);
  await checkpoint("04-idp-start");
  await expect.poll(async () => (await alice.context.request.get(site+"/bff/api/v1/me")).status(),{timeout:90000}).toBe(200);
  // QA-PR2-01: revoking the initial applicant also denies its actual HTTP access.
  const lateDora = await authenticated(browser,"dora",false);
  const lateMembers = (await (await alice.context.request.get(site+`/bff/api/v1/organizations/${a.id}/members`)).json()).data.items;
  const dm = lateMembers.find((m: {userId:string}) => m.userId === dora.id);
  const secondOwner = await write(alice.context,"PATCH",`/bff/api/v1/organizations/${a.id}/members/${dm.id}`,{role:"ORG_OWNER"},{"If-Match":`"${dm.version}"`});
  expect(secondOwner.status()).toBe(200);
  const revokedApplicant = await write(lateDora.context,"DELETE",`/bff/api/v1/organizations/${a.id}/members/${am.id}`,{},{"If-Match":`"${am.version}"`});
  expect(revokedApplicant.status()).toBe(200);
  expect((await alice.context.request.get(site+`/bff/api/v1/organizations/${a.id}`)).status()).toBe(404);
  expect((await (await alice.context.request.get(site+"/bff/api/v1/organizations")).json()).data.items).toEqual([]);
  expect((await (await alice.context.request.get(site+"/bff/api/v1/me")).json()).data.memberships).toEqual([]);
  await lateDora.context.close();
  const oldCookies = await alice.context.cookies(site);
  expect((await write(alice.context,"POST","/auth/logout")).status()).toBe(200);
  await alice.context.addCookies(oldCookies);
  expect((await alice.context.request.get(site+"/bff/api/v1/me")).status()).toBe(401);
  // Provider-originated signed backchannel logout, distinct from local logout.
  expect((await bob.context.request.post(site+"/auth/backchannel-logout",{form:{logout_token:"forged.invalid.token"}})).status()).toBe(400);
  expect((await bob.context.request.get(site+"/bff/api/v1/me")).status()).toBe(200);
  // Only the trusted controller reads/decrypts Bob's token. No token reaches this browser.
  // It first calls the API directly without a cookie, then reuses the exact token after logout.
  await checkpoint("11-direct-token-before",{bob:bob.id});
  await bob.page.goto("https://127.0.0.1:8444/realms/kryptroom-dev/protocol/openid-connect/logout?client_id=kryptroom-web-bff&post_logout_redirect_uri="+encodeURIComponent(site+"/"));
  await bob.page.locator("#kc-logout").click();
  await checkpoint("10-backchannel-check",{bob:bob.id});
  await expect.poll(async () => (await bob.context.request.get(site+"/bff/api/v1/me")).status()).toBe(401);
  for (const actor of [alice,bob,charlie,dora]) await actor.context.close();
});

for (const attack of ["state","nonce","pkce"] as const) {
  test(`real OIDC rejects altered ${attack} and creates no browser session`, async ({browser}) => {
    const context = await browser.newContext(), page = await context.newPage();
    // Redirect-chain routing does not intercept every browser hop. Obtain the
    // real BFF redirect first, then mutate the actual authorization URL explicitly.
    const initiated = await context.request.get(site+"/auth/login",{maxRedirects:0});
    expect(initiated.status()).toBe(303);
    const authorization = new URL(initiated.headers()["location"]);
    expect(authorization.origin).toBe("https://127.0.0.1:8444");
    const field = attack === "pkce" ? "code_challenge" : attack;
    const replacement = Buffer.alloc(32,2).toString("base64url");
    expect(authorization.searchParams.get(field)).not.toBe(replacement);
    authorization.searchParams.set(field,replacement);
    await page.goto(authorization.href);
    await page.locator("#username").fill("alice"); await page.locator("#password").fill(password("alice"));
    const completion = page.waitForResponse(response => {
      const url = new URL(response.url());
      return url.origin === site && url.pathname === "/auth/callback";
    });
    await page.locator("#kc-login").click();
    expect((await completion).status()).toBe(401);
    expect((await context.cookies(site)).some(c => c.name === "kr_dev_sid")).toBe(false);
    expect((await context.request.get(site+"/bff/api/v1/me")).status()).toBe(401);
    await context.close();
  });
}
