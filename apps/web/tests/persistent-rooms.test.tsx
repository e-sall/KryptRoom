import { render,screen,waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach,describe,expect,it,vi } from "vitest";
import { PersistentRooms } from "../src/features/rooms/persistent-rooms";
import {readFileSync} from "node:fs";
vi.mock("server-only",()=>({}));
import { proxyPath } from "../src/server/auth/security";
const oid="019a0000-0000-7000-8000-000000000010",rid="019a0000-0000-7000-8000-000000000011";
const room={id:rid,organizationId:oid,displayName:"Persisted lab",description:"Metadata",status:"DRAFT",headStateId:null,version:1};
const me={organizations:[{id:oid,displayName:"Lab A"}],memberships:[{organizationId:oid,role:"ORG_OWNER",status:"ACTIVE"}]};
function reply(data:unknown,status=200){return new Response(JSON.stringify({data}),{status,headers:{"Content-Type":"application/json","ETag":'"1"',"X-CSRF-Token":"session-bound"}});}
afterEach(()=>vi.unstubAllGlobals());
describe("Persistent Rooms boundary",()=>{
 it("permits one same-origin BFF transport and no client credential storage",()=>{
  const source=readFileSync("src/features/rooms/persistent-rooms.tsx","utf8");
  expect(source.match(/\bfetch\s*\(/g)).toHaveLength(1);
  expect(source).toContain('const root="/bff/api/v1"');
  expect(source).toContain('fetch(root+path');
  expect(source).not.toMatch(/https?:|Authorization|localStorage|sessionStorage|document\.cookie/);
 });
 it("allows only implemented Rooms routes and methods",()=>{
  expect(proxyPath(["organizations",oid,"rooms"],"POST")).toBe(`/api/v1/organizations/${oid}/rooms`);
  expect(proxyPath(["rooms",rid],"PATCH")).toBe(`/api/v1/rooms/${rid}`);
  for(const [path,method] of [[["rooms",rid],"DELETE"],[["rooms"],"POST"],[["rooms",rid,"reveal"],"POST"],[["organizations",oid,"rooms","extra"],"GET"]] as const)
   expect(proxyPath([...path],method)).toBeNull();
 });
 it("loads actual response records without synthetic states",async()=>{
  vi.stubGlobal("fetch",vi.fn(async(url:string)=>reply(url.endsWith("/me")?me:{items:[room],next_cursor:null})));
  render(<PersistentRooms/>);
  expect(screen.getByText("Loading Rooms")).toBeInTheDocument();
  expect(await screen.findByRole("link",{name:"Persisted lab"})).toHaveAttribute("href",`/app/rooms/${rid}`);
  expect(screen.queryByText("S1")).not.toBeInTheDocument();
 });
 it("shows empty and sign-in states",async()=>{
  vi.stubGlobal("fetch",vi.fn(async(url:string)=>reply(url.endsWith("/me")?me:{items:[],next_cursor:null})));
  const view=render(<PersistentRooms/>);expect(await screen.findByText("No Rooms yet")).toBeInTheDocument();view.unmount();
  vi.stubGlobal("fetch",vi.fn(async()=>reply(null,401)));
  render(<PersistentRooms/>);expect(await screen.findByRole("link",{name:"Sign in"})).toBeInTheDocument();
 });
 it("creates using CSRF and idempotency, never a browser bearer token",async()=>{
  const fetcher=vi.fn(async(_url:string,init?:RequestInit)=>reply(init?.method==="POST"?room:me));vi.stubGlobal("fetch",fetcher);
  render(<PersistentRooms create/>);const user=userEvent.setup();
  await user.type(await screen.findByLabelText("Room name"),"Persisted lab");
  await user.click(screen.getByRole("button",{name:"Create Room"}));
  await screen.findByRole("status");
  const request=fetcher.mock.calls.find(([,init])=>init?.method==="POST")![1]!;
  expect(request.headers).toMatchObject({"X-CSRF-Token":"session-bound","Idempotency-Key":expect.any(String)});
  expect(request.headers).not.toHaveProperty("Authorization");
 });
 it("sends actual ETag and does not auto-overwrite a conflict",async()=>{
  const fetcher=vi.fn(async(url:string,init?:RequestInit)=>init?.method==="PATCH"?reply(null,412):reply(url.endsWith("/me")?me:room));vi.stubGlobal("fetch",fetcher);
  render(<PersistentRooms roomId={rid}/>);const user=userEvent.setup();
  await user.clear(await screen.findByLabelText("Room name"));await user.type(screen.getByLabelText("Room name"),"Draft edit");
  await user.click(screen.getByRole("button",{name:"Save changes"}));
  await screen.findByText("Changes could not be saved");
  expect(screen.getByLabelText("Room name")).toHaveValue("Draft edit");
  expect(screen.getByRole("button",{name:"Save changes"})).toBeDisabled();
  expect(fetcher.mock.calls.find(([,init])=>init?.method==="PATCH")![1]!.headers).toMatchObject({"If-Match":'"1"'});
 });
 it.each([403,404,503])("renders generic failure %s without response details",async(status)=>{
  vi.stubGlobal("fetch",vi.fn(async(url:string)=>url.endsWith("/me")?reply(me):reply({secret:"must-not-render"},status)));
  render(<PersistentRooms roomId={rid}/>);
  await waitFor(()=>expect(screen.queryByText("Loading Rooms")).not.toBeInTheDocument());
  expect(screen.queryByDisplayValue("Persisted lab")).not.toBeInTheDocument();
  expect(screen.queryByText("must-not-render")).not.toBeInTheDocument();
 });
 it("removes the previously visible record after a revoked mutation is refused",async()=>{
  vi.stubGlobal("fetch",vi.fn(async(url:string,init?:RequestInit)=>init?.method==="PATCH"?reply(null,404):reply(url.endsWith("/me")?me:room)));
  render(<PersistentRooms roomId={rid}/>);
  await screen.findByDisplayValue("Persisted lab");
  await userEvent.click(screen.getByRole("button",{name:"Save changes"}));
  await screen.findByText("Access unavailable");
  expect(screen.queryByDisplayValue("Persisted lab")).not.toBeInTheDocument();
 });
 it("defaults a member to read-only",async()=>{
  vi.stubGlobal("fetch",vi.fn(async(url:string)=>reply(url.endsWith("/me")?{...me,memberships:[{...me.memberships[0],role:"ORG_MEMBER"}]}:room)));
  render(<PersistentRooms roomId={rid}/>);
  await screen.findByDisplayValue("Persisted lab");
  expect(screen.getByRole("button",{name:"Save changes"})).toBeDisabled();
 });
});
