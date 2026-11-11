import {render,screen,waitFor} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {afterEach,expect,it,vi} from "vitest";
import {CollaborationPanel} from "../src/features/rooms/collaboration-panel";
vi.mock("server-only",()=>({}));
import {proxyPath} from "../src/server/auth/security";
const a="019a0000-0000-7000-8000-000000000010",b="019a0000-0000-7000-8000-000000000011",r="019a0000-0000-7000-8000-000000000012",i="019a0000-0000-7000-8000-000000000013";
const invitation={id:i,roomId:r,ownerOrganizationId:a,targetOrganizationId:b,status:"PENDING",version:1};
function reply(data:unknown,status=200){return new Response(JSON.stringify({data}),{status,headers:{"X-CSRF-Token":"bound","Content-Type":"application/json"}});}
afterEach(()=>vi.unstubAllGlobals());
it("allowlists only the implemented collaboration methods",()=>{
 expect(proxyPath(["rooms",r,"invitations"],"POST")).not.toBeNull();
 expect(proxyPath(["rooms",r,"participants"],"GET")).not.toBeNull();
 expect(proxyPath(["organizations",b,"room-invitations",i],"PATCH")).not.toBeNull();
 for(const [path,method] of [[["rooms",r,"invitations"],"GET"],[["rooms",r,"participants"],"POST"],[["organizations",b,"room-invitations",i],"DELETE"]] as const)expect(proxyPath([...path],method)).toBeNull();
});
it("accepts with actual version and CSRF, then renders accepted state",async()=>{
 let status="PENDING";
 const fetcher=vi.fn(async(url:string,init?:RequestInit)=>{
  if(init?.method==="PATCH"){status="ACCEPTED";return reply({...invitation,status,version:2});}
  return reply(url.endsWith("/me")?{organizations:[{id:b,displayName:"B"}],memberships:[{organizationId:b,role:"ORG_ADMIN",status:"ACTIVE"}]}:{items:[{...invitation,status}],next_cursor:null});
 });vi.stubGlobal("fetch",fetcher);render(<CollaborationPanel/>);
 expect(screen.getByText("Loading")).toBeInTheDocument();
 await userEvent.click(await screen.findByRole("button",{name:"Accept"}));
 await screen.findByRole("button",{name:"Leave Room"});
 const request=fetcher.mock.calls.find(([,init])=>init?.method==="PATCH")![1]!;
 expect(request.headers).toMatchObject({"If-Match":'"1"',"X-CSRF-Token":"bound"});
 expect(JSON.parse(request.body as string)).toEqual({roomId:r,action:"accept"});
 expect(screen.getByRole("link",{name:"Open shared Room"})).toHaveAttribute("href",`/app/rooms/${r}`);
});
it("clears records on refusal without rendering server secrets",async()=>{
 vi.stubGlobal("fetch",vi.fn(async()=>reply({private:"never-render"},403)));
 render(<CollaborationPanel/>);
 await waitFor(()=>expect(screen.getByText("Access unavailable or request failed")).toBeInTheDocument());
 expect(screen.queryByText("never-render")).not.toBeInTheDocument();
 expect(screen.queryByRole("button",{name:"Accept"})).not.toBeInTheDocument();
});
