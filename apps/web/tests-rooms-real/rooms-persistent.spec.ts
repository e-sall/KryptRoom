import {test,expect,type Browser} from "@playwright/test";
import {readFileSync} from "node:fs";
import {execFileSync} from "node:child_process";
import {randomUUID} from "node:crypto";
test.use({channel:process.env.KR_ROOMS_BROWSER_CHANNEL||undefined});
test("real Rooms UI through session BFF, API, PostgreSQL and Keycloak",async({browser})=>{
 const users=process.env.KR_ROOMS_TEST_PRIVATE;
 const operator=process.env.KR_ROOMS_TEST_OPERATOR;
 if(!users||!operator)throw new Error("Explicit isolated synthetic fixture required");
 async function login(browser:Browser,user:string){
  const context=await browser.newContext();const page=await context.newPage();
  await page.goto("http://127.0.0.1:3004/auth/login?returnTo=/app/rooms");
  await page.locator("#username").fill(user);await page.locator("#password").fill(readFileSync(`${users}/${user}_password`,"utf8"));
  await page.locator("#kc-login").click();await page.waitForURL("**/app/rooms");
  const result=await context.request.get("http://127.0.0.1:3004/bff/api/v1/me");
  expect(result.status()).toBe(200);return {context,page,me:(await result.json()).data,csrf:result.headers()["x-csrf-token"]};
 }
 const alice=await login(browser,"alice"),bob=await login(browser,"bob");
 for(const user of [alice,bob]){
  const response=await user.context.request.post("http://127.0.0.1:3004/bff/api/v1/organizations",{data:{displayName:randomUUID()},headers:{Origin:"http://127.0.0.1:3004","Sec-Fetch-Site":"same-origin","X-CSRF-Token":user.csrf,"Idempotency-Key":randomUUID()}});
  expect(response.status()).toBe(202);const oid=(await response.json()).data.id;
  execFileSync("wsl",["-d","Ubuntu-24.04","-u","root","--","python3",operator,"approve",oid]);
 }
 await alice.page.reload();await expect(alice.page.getByText("No Rooms yet")).toBeVisible();
 await alice.page.getByRole("link",{name:"Create Room",exact:true}).click();
 await alice.page.getByLabel("Room name").fill("Synthetic persisted UI Room");
 await alice.page.getByRole("button",{name:"Create Room",exact:true}).click();
 await expect(alice.page.getByText("Room created.")).toBeVisible();
 await alice.page.getByRole("link",{name:"Open Room"}).click();
 await expect(alice.page.getByLabel("Room name")).toHaveValue("Synthetic persisted UI Room");
 const path=alice.page.url();const rid=path.split("/").pop()!;
 const data=await alice.context.request.get(`http://127.0.0.1:3004/bff/api/v1/rooms/${rid}`);
 const room=(await data.json()).data;expect(room.headStateId).toBeNull();
 expect(await bob.context.request.get(`http://127.0.0.1:3004/bff/api/v1/rooms/${rid}`).then(r=>r.status())).toBe(404);
 const common={Origin:"http://127.0.0.1:3004","Sec-Fetch-Site":"same-origin","X-CSRF-Token":data.headers()["x-csrf-token"],"If-Match":data.headers().etag};
 const denied=await alice.context.request.patch(`http://127.0.0.1:3004/bff/api/v1/rooms/${rid}`,{data:{displayName:"No CSRF"},headers:{"If-Match":common["If-Match"]}});expect(denied.status()).toBe(403);
 const concurrent=await alice.context.request.patch(`http://127.0.0.1:3004/bff/api/v1/rooms/${rid}`,{data:{displayName:"Concurrent update"},headers:common});expect(concurrent.status()).toBe(200);
 await alice.page.getByLabel("Room name").fill("Stale edit");await alice.page.getByRole("button",{name:"Save changes"}).click();
 await expect(alice.page.getByText("Changes could not be saved")).toBeVisible();
 await alice.page.getByRole("button",{name:"Reload",exact:true}).click();await expect(alice.page.getByLabel("Room name")).toHaveValue("Concurrent update");
 await alice.context.close();const again=await login(browser,"alice");await again.page.goto(path);
 await expect(again.page.getByLabel("Room name")).toHaveValue("Concurrent update");
 const member=JSON.parse(execFileSync("wsl",["-d","Ubuntu-24.04","-u","root","--","python3",operator,"revoke-setup",room.organizationId,bob.me.id,again.me.id],{encoding:"utf8"}));
 const current=await bob.context.request.get("http://127.0.0.1:3004/bff/api/v1/me");
 expect((await bob.context.request.delete(`http://127.0.0.1:3004/bff/api/v1/organizations/${room.organizationId}/members/${member.id}`,{headers:{Origin:"http://127.0.0.1:3004","Sec-Fetch-Site":"same-origin","Content-Type":"application/json","X-CSRF-Token":current.headers()["x-csrf-token"],"If-Match":`"${member.version}"`}})).status()).toBe(200);
 await again.page.getByLabel("Room name").fill("Revoked edit");await again.page.getByRole("button",{name:"Save changes"}).click();await expect(again.page.getByText("Access unavailable")).toBeVisible();
 expect(await again.page.locator("body").textContent()).not.toContain("access_token");
 await again.context.close();await bob.context.close();
});
