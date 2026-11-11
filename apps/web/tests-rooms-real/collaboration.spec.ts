import {test,expect,type Browser} from "@playwright/test";
import {readFileSync} from "node:fs";
import {execFileSync} from "node:child_process";
import {randomUUID} from "node:crypto";

test.use({channel:process.env.KR_ROOMS_BROWSER_CHANNEL||undefined});
test("PR4 real two-organization collaboration, revocation and restart",async({browser})=>{
 const privateDir=process.env.KR_ROOMS_TEST_PRIVATE,operator=process.env.KR_ROOMS_TEST_OPERATOR;
 const runtime=process.env.KR_COLLABORATION_RUNTIME;
 if(!privateDir||!operator||!runtime)throw new Error("Explicit isolated synthetic runtime required");
 const origin="http://127.0.0.1:3004",root=origin+"/bff/api/v1";
 async function login(browser:Browser,user:string){
  const context=await browser.newContext(),page=await context.newPage();
  await page.goto(origin+"/auth/login?returnTo=/app/rooms");
  await page.locator("#username").fill(user);
  await page.locator("#password").fill(readFileSync(`${privateDir}/${user}_password`,"utf8"));
  await page.locator("#kc-login").click();await page.waitForURL("**/app/rooms");
  const me=await context.request.get(root+"/me");expect(me.status()).toBe(200);
  return {context,page,csrf:me.headers()["x-csrf-token"]};
 }
 function headers(csrf:string){return {Origin:origin,"Sec-Fetch-Site":"same-origin","X-CSRF-Token":csrf};}
 const a=await login(browser,"alice"),b=await login(browser,"bob"),c=await login(browser,"charlie");
 const orgs:string[]=[];
 for(const user of [a,b,c]){
  const response=await user.context.request.post(root+"/organizations",{data:{displayName:"Synthetic PR4 "+randomUUID()},headers:{...headers(user.csrf),"Idempotency-Key":randomUUID()}});
  expect(response.status()).toBe(202);const id=(await response.json()).data.id;orgs.push(id);
  execFileSync("wsl",["-d","Ubuntu-24.04","-u","root","--","python3",operator,"approve",id]);
 }
 const [aid,bid,cid]=orgs;
 await a.page.goto(origin+"/app/rooms/new");
 await a.page.getByLabel("Organization",{exact:true}).selectOption(aid);
 await a.page.getByLabel("Room name").fill("Synthetic PR4 collaboration");
 await a.page.getByRole("button",{name:"Create Room",exact:true}).click();
 await a.page.getByRole("link",{name:"Open Room",exact:true}).click();
 await a.page.waitForURL(/\/app\/rooms\/[0-9a-f-]{36}$/);
 const rid=a.page.url().split("/").pop()!;
 async function invite(){
  await a.page.getByLabel("Pre-registered organization ID").fill(bid);
  await a.page.getByRole("button",{name:"Invite organization",exact:true}).click();
  await expect(a.page.getByText(new RegExp(`Room ${rid} · PENDING`))).toBeVisible();
 }
 await invite();
 const pending=await a.context.request.get(root+`/organizations/${aid}/room-invitations`);
 const iid=(await pending.json()).data.items[0].id;
 expect(await c.context.request.get(root+`/rooms/${rid}`).then(r=>r.status())).toBe(404);
 const forged=await c.context.request.patch(root+`/organizations/${cid}/room-invitations/${iid}`,{data:{roomId:rid,action:"accept"},headers:{...headers(c.csrf),"If-Match":'"1"'}});
 expect(forged.status()).toBe(404);
 expect(await b.context.request.post(root+`/rooms/${rid}/invitations`,{data:{organizationId:bid,targetOrganizationId:cid},headers:{...headers(b.csrf),"Idempotency-Key":randomUUID()}}).then(r=>r.status())).toBe(404);
 expect(await b.context.request.patch(root+`/organizations/${bid}/room-invitations/${iid}`,{data:{roomId:rid,action:"accept"},headers:{"If-Match":'"1"'}}).then(r=>r.status())).toBe(403);
 console.log("PASS pending isolation, forged acceptance, unauthorized invitation and CSRF denial");
 await b.page.goto(origin+"/app/rooms/invitations");
 await b.page.getByLabel("Invitation organization").selectOption(bid);
 await b.page.getByRole("button",{name:"Accept",exact:true}).click();
 await b.page.getByRole("link",{name:"Open shared Room",exact:true}).click();
 await expect(b.page.getByLabel("Room name")).toHaveValue("Synthetic PR4 collaboration");
 await expect(b.page.getByRole("button",{name:"Save changes"})).toBeDisabled();
 await expect(b.page.getByText("Partner · read-only metadata",{exact:false})).toBeVisible();
 const shared=await b.context.request.get(root+`/rooms/${rid}`);expect((await shared.json()).data.headStateId).toBeNull();
 expect(await b.context.request.patch(root+`/rooms/${rid}`,{data:{displayName:"Forbidden partner edit"},headers:{...headers(b.csrf),"If-Match":shared.headers().etag}}).then(r=>r.status())).toBe(404);
 await a.page.reload();await expect(a.page.getByText("Partner · read-only metadata",{exact:false})).toBeVisible();
 await b.context.close();const again=await login(browser,"bob");await again.page.goto(origin+`/app/rooms/${rid}`);
 await expect(again.page.getByLabel("Room name")).toHaveValue("Synthetic PR4 collaboration");
 execFileSync("wsl",["-d","Ubuntu-24.04","-u","root","--","python3",runtime,"restart",rid,bid]);
 await expect.poll(async()=>again.context.request.get(root+`/rooms/${rid}`).then(r=>r.status())).toBe(200);
 await again.page.reload();await expect(again.page.getByLabel("Room name")).toHaveValue("Synthetic PR4 collaboration");
 console.log("PASS accepted read-only metadata, reconnect, API restart and direct PostgreSQL persistence");
 await again.page.goto(origin+"/app/rooms/invitations");await again.page.getByLabel("Invitation organization").selectOption(bid);await again.page.getByRole("button",{name:"Leave Room",exact:true}).click();
 await expect(again.page.getByText(new RegExp(`Room ${rid} · LEFT`))).toBeVisible();
 expect(await again.context.request.get(root+`/rooms/${rid}`).then(r=>r.status())).toBe(404);
 await a.page.reload();await invite();await again.page.reload();await again.page.getByLabel("Invitation organization").selectOption(bid);
 await again.page.getByRole("button",{name:"Reject",exact:true}).click();
 await expect(again.page.getByText(new RegExp(`Room ${rid} · REJECTED`))).toBeVisible();
 await a.page.reload();await invite();await again.page.reload();await again.page.getByLabel("Invitation organization").selectOption(bid);
 await again.page.getByRole("button",{name:"Accept",exact:true}).click();
 await expect(again.page.getByRole("button",{name:"Leave Room",exact:true})).toBeVisible();
 await a.page.reload();await a.page.getByRole("button",{name:"Revoke",exact:true}).click();
 await expect(a.page.getByText(new RegExp(`Room ${rid} · REVOKED`))).toBeVisible();
 expect(await again.context.request.get(root+`/rooms/${rid}`).then(r=>r.status())).toBe(404);
 await again.page.goto(origin+`/app/rooms/${rid}`);await expect(again.page.getByText("Access unavailable",{exact:true})).toBeVisible();
 expect(await again.page.locator("body").textContent()).not.toMatch(/access_token|refresh_token|client_secret/);
 console.log("PASS leave, rejection, re-invitation, accepted revocation and subsequent request denial");
 if(process.env.KR_COLLABORATION_SCREENSHOT)await a.page.screenshot({path:process.env.KR_COLLABORATION_SCREENSHOT,fullPage:true});
 await Promise.all([a.context.close(),again.context.close(),c.context.close()]);
});
