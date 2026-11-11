"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Button, ButtonLink, Card, StatusView, TextField } from "@/components/ui";
import { CollaborationPanel } from "./collaboration-panel";

type Room = {id:string;organizationId:string;displayName:string;description:string;status:"DRAFT";headStateId:null;version:number};
type Organization = {id:string;displayName:string};
type Membership = {organizationId:string;role:string;status:string};
type View = "loading"|"ready"|"empty"|"forbidden"|"conflict"|"error"|"login";
const root="/bff/api/v1";
class RequestError extends Error { constructor(readonly status:number){super("Request could not be completed");} }
export async function api(path:string, init:RequestInit={}) {
  const response=await fetch(root+path,{...init,credentials:"same-origin",cache:"no-store",redirect:"error"});
  if(!response.ok) throw new RequestError(response.status);
  return {data:(await response.json()).data,etag:response.headers.get("ETag"),csrf:response.headers.get("X-CSRF-Token")};
}
function failure(error:unknown):View {
  if(error instanceof RequestError){
    if(error.status===401)return "login";
    if([403,404].includes(error.status))return "forbidden";
    if([409,412].includes(error.status))return "conflict";
  }
  return "error";
}
function Notice({state,retry}:{state:View;retry:()=>void}) {
  if(state==="ready")return null;
  const copy:Record<Exclude<View,"ready">,[string,string]>={
    loading:["Loading Rooms","Retrieving your authorized workspace."],
    empty:["No Rooms yet","This organization has no persisted Rooms."],
    forbidden:["Access unavailable","You do not have access to this resource."],
    conflict:["Changes could not be saved","A concurrent update or conflicting request was detected. Reload the latest version before editing again."],
    error:["Unable to complete request","Your changes have not been confirmed. Try again."],
    login:["Sign in to continue","Use your organization account to access persistent Rooms."],
  };
  const [title,description]=copy[state];
  return <StatusView state={state==="loading"?"loading":state==="empty"?"empty":"error"} title={title} description={description}
    action={state==="login"?<ButtonLink href="/auth/login?returnTo=/app/rooms">Sign in</ButtonLink>:state!=="loading"&&state!=="empty"?<Button onClick={retry}>Reload</Button>:undefined}/>;
}
function validRoom(value:Room){
  const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if(!value||!uuid.test(value.id)||!uuid.test(value.organizationId)||typeof value.displayName!=="string"||value.displayName.length>120||typeof value.description!=="string"||value.description.length>1000||!Number.isInteger(value.version)||value.version<1||value.headStateId!==null||value.status!=="DRAFT")throw new Error("Unsupported room response");
  return value;
}

export function PersistentRooms({create=false,roomId}:{create?:boolean;roomId?:string}) {
  const [organizations,setOrganizations]=useState<Organization[]>([]);
  const [memberships,setMemberships]=useState<Membership[]>([]);
  const [organization,setOrganization]=useState("");
  const [state,setState]=useState<View>("loading");
  const [rooms,setRooms]=useState<Room[]>([]),[room,setRoom]=useState<Room|null>(null);
  const [name,setName]=useState(""),[description,setDescription]=useState("");
  const [etag,setEtag]=useState<string|null>(null),[csrf,setCsrf]=useState<string|null>(null);
  const [busy,setBusy]=useState(false),[saved,setSaved]=useState(false);
  const [revision,setRevision]=useState(0),[cursor,setCursor]=useState<string|null>(null);
  const key=useRef<string|null>(null);
  const selected=room?.organizationId||organization;
  const canWrite=memberships.some(m=>m.organizationId===selected&&m.status==="ACTIVE"&&["ORG_OWNER","ORG_ADMIN"].includes(m.role));

  useEffect(()=>{
    let live=true;
    void (async()=>{
      try {
        const me=await api("/me");if(!live)return;
        if(!Array.isArray(me.data?.organizations)||!Array.isArray(me.data?.memberships))throw new Error("Invalid identity response");
        setCsrf(me.csrf);setOrganizations(me.data.organizations);setMemberships(me.data.memberships);
        if(roomId){
          const current=await api("/rooms/"+encodeURIComponent(roomId));if(!live)return;
          const value=validRoom(current.data);setRoom(value);setName(value.displayName);setDescription(value.description);setEtag(current.etag);setCsrf(current.csrf);setState("ready");
        }else{
          const oid=organization||me.data.organizations[0]?.id||"";
          if(!organization&&oid){setOrganization(oid);return;}
          if(!oid){setState("empty");return;}
          if(create){setState("ready");return;}
          const list=await api(`/organizations/${encodeURIComponent(oid)}/rooms`);if(!live)return;
          setRooms(list.data.items.map(validRoom));setCursor(list.data.next_cursor);setCsrf(list.csrf);setState(list.data.items.length?"ready":"empty");
        }
      }catch(error){if(live)setState(failure(error));}
    })();
    return ()=>{live=false;};
  },[organization,roomId,create,revision]);

  async function more(){
    if(!cursor||busy)return;setBusy(true);
    try{const result=await api(`/organizations/${encodeURIComponent(organization)}/rooms?cursor=${encodeURIComponent(cursor)}`);
      setRooms(previous=>[...previous,...result.data.items.map(validRoom)]);setCursor(result.data.next_cursor);
    }catch(error){setRooms([]);setState(failure(error));}finally{setBusy(false);}
  }
  async function submit(event:React.FormEvent){
    event.preventDefault();if(busy||!csrf||!canWrite)return;
    setBusy(true);setSaved(false);
    try{
      const headers:Record<string,string>={"Content-Type":"application/json","X-CSRF-Token":csrf};
      if(create){key.current??=crypto.randomUUID();headers["Idempotency-Key"]=key.current;}
      else {if(!etag)throw new Error("Missing version");headers["If-Match"]=etag;}
      const result=await api(create?`/organizations/${encodeURIComponent(organization)}/rooms`:`/rooms/${encodeURIComponent(roomId!)}`,
        {method:create?"POST":"PATCH",headers,body:JSON.stringify({displayName:name,description})});
      const value=validRoom(result.data);setRoom(value);setEtag(result.etag);setSaved(true);setState("ready");
    }catch(error){const next=failure(error);setState(next);if(next==="login"||next==="forbidden"){setRoom(null);setRooms([]);}}
    finally{setBusy(false);}
  }
  const showForm=(create&&!saved)||!!roomId;
  return <>
    <header className="page-header"><h1>{create?"Create a Room":roomId?"Room details":"Rooms"}</h1><p>Persistent organization workspace · metadata only</p></header>
    <ButtonLink href="/app/rooms/invitations">Organization invitations</ButtonLink>
    {!roomId&&organizations.length>0&&<label className="field">Organization <select aria-label="Organization" style={{maxWidth:"100%",minHeight:44,background:"var(--kr-surface)",color:"var(--kr-text-primary)",border:"1px solid var(--kr-border)",borderRadius:"var(--kr-radius-control)"}} value={organization} disabled={busy} onChange={e=>{setOrganization(e.target.value);setRooms([]);setRoom(null);setCursor(null);setState("loading");key.current=null;}}>
      {organizations.map(o=><option value={o.id} key={o.id}>{o.displayName}</option>)}</select></label>}
    <Notice state={state} retry={()=>{setState("loading");setRoom(null);setRooms([]);setSaved(false);setRevision(r=>r+1);}}/>
    {state!=="loading"&&state!=="login"&&state!=="forbidden"&&<>
      {showForm&&(create?!!organization:!!room)&&<Card><form onSubmit={submit} style={{display:"grid",gap:16}}>
        <TextField id="persistent-room-name" label="Room name" required maxLength={120} value={name} disabled={!canWrite||busy} onChange={e=>{setName(e.target.value);setSaved(false);}}/>
        <TextField id="persistent-room-description" label="Description" maxLength={1000} value={description} disabled={!canWrite||busy} onChange={e=>{setDescription(e.target.value);setSaved(false);}}/>
        <p>No RoomState is associated. Private computations are unavailable.</p>
        {!canWrite&&<p>You have read-only access. An organization owner or administrator can edit Room metadata.</p>}
        <Button type="submit" variant="primary" loading={busy} disabled={!canWrite||!csrf||state==="conflict"||(!create&&!etag)}>{create?"Create Room":"Save changes"}</Button>
      </form></Card>}
      {saved&&room&&<p role="status">{create?"Room created.":"Changes saved."} <Link href={`/app/rooms/${room.id}`}>Open Room</Link></p>}
      {roomId&&room&&state==="ready"&&<CollaborationPanel roomId={roomId} ownerId={room.organizationId} canInvite={canWrite}/>}
      {!create&&!roomId&&rooms.map(value=><Card key={value.id}><h2><Link href={`/app/rooms/${value.id}`}>{value.displayName}</Link></h2><p>{value.description}</p><p>Draft · No RoomState associated</p></Card>)}
      {!create&&!roomId&&cursor&&<Button onClick={more} loading={busy}>Load more</Button>}
      {!create&&!roomId&&canWrite&&<ButtonLink href="/app/rooms/new">Create Room</ButtonLink>}
    </>}
    {(create||roomId)&&<ButtonLink href="/app/rooms">Back to Rooms</ButtonLink>}
  </>;
}
