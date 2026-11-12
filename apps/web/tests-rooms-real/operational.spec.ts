import {test,expect} from "@playwright/test";
import {readFileSync} from "node:fs";
import {execFileSync} from "node:child_process";
test.use({channel:process.env.KR_ROOMS_BROWSER_CHANNEL||undefined});
test("standalone readiness, dependency outage recovery and expired session",async({browser})=>{
 const privateDir=process.env.KR_ROOMS_TEST_PRIVATE,runtime=process.env.KR_COLLABORATION_RUNTIME;
 if(!privateDir||!runtime)throw new Error("Explicit real fixture required");
 const context=await browser.newContext(),page=await context.newPage(),origin="http://127.0.0.1:3004";
 const control=(action:string,uid?:string)=>execFileSync("wsl",["-d","Ubuntu-24.04","-u","root","--","python3",runtime,action,...(uid?[uid]:[])]);
 await expect.poll(async()=>context.request.get(origin+"/health/ready").then(r=>r.status()),{timeout:60000}).toBe(200);
 await page.goto(origin+"/auth/login?returnTo=/app/rooms");
 await page.locator("#username").fill("alice");await page.locator("#password").fill(readFileSync(privateDir+"/alice_password","utf8"));
 await page.locator("#kc-login").click();await page.waitForURL("**/app/rooms");
 const me=await context.request.get(origin+"/bff/api/v1/me");expect(me.status()).toBe(200);const uid=(await me.json()).data.id;
 for(const dependency of ["api","idp"]){
  control("stop-"+dependency);
  try{
   expect(await context.request.get(origin+"/health/live").then(r=>r.status())).toBe(200);
   const unavailable=await context.request.get(origin+"/health/ready");expect(unavailable.status()).toBe(503);
   expect(await unavailable.json()).toEqual({status:"unavailable"});
   expect(await context.request.get(origin+"/bff/api/v1/me").then(r=>r.status())).toBe(503);
  }finally{control("start-"+dependency);}
  await expect.poll(async()=>context.request.get(origin+"/health/ready").then(r=>r.status()),{timeout:60000}).toBe(200);
  expect(await context.request.get(origin+"/bff/api/v1/me").then(r=>r.status())).toBe(200);
 }
 control("expire",uid);
 const expired=await context.request.get(origin+"/bff/api/v1/me");expect(expired.status()).toBe(401);
 expect(await expired.text()).not.toMatch(/encrypted|access_token|refresh_token/);
 console.log("PASS standalone liveness/readiness, API+IdP outages/recovery, real persisted session expiry");
 await context.close();
});
