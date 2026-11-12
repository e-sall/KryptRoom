import {beforeEach,expect,it,vi} from "vitest";
vi.mock("server-only",()=>({}));
const {query}=vi.hoisted(()=>({query:vi.fn()}));
vi.mock("../src/server/auth/config",()=>({config:()=>({pool:{query},api:"http://api.test",issuer:"https://idp.test/realms/test"})}));
import {GET as live} from "../src/app/health/live/route";
import {GET as ready} from "../src/app/health/ready/route";
beforeEach(()=>{vi.restoreAllMocks();query.mockReset();query.mockResolvedValue({rows:[{}]});});
it("liveness does not require database or IdP",()=>{expect(live().status).toBe(200);expect(query).not.toHaveBeenCalled();});
it("readiness requires DB, API and exact trusted issuer",async()=>{
 vi.stubGlobal("fetch",vi.fn(async(url:string)=>new Response(JSON.stringify(url.endsWith("/health/ready")?{status:"ready"}:{issuer:"https://idp.test/realms/test"}))));
 expect((await ready()).status).toBe(200);
});
it.each(["database","api","issuer","network"])("fails closed without internal diagnostics: %s",async(failure)=>{
 if(failure==="database")query.mockRejectedValue(new Error("synthetic-secret-do-not-log"));
 vi.stubGlobal("fetch",vi.fn(async(url:string)=>{
  if(failure==="network")throw new Error("synthetic-secret-do-not-log");
  return new Response(JSON.stringify({issuer:failure==="issuer"?"https://foreign.test":"https://idp.test/realms/test"}),{status:failure==="api"&&url.endsWith("/health/ready")?503:200});
 }));
 const response=await ready();expect(response.status).toBe(503);
 expect(await response.text()).toBe('{"status":"unavailable"}');
 expect(response.headers.get("cache-control")).toBe("no-store");
});
