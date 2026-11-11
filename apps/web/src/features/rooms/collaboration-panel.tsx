"use client";
import {useEffect,useRef,useState} from "react";
import {Button,ButtonLink,Card,TextField} from "@/components/ui";
import {api} from "./persistent-rooms";
type Invitation={id:string;roomId:string;ownerOrganizationId:string;targetOrganizationId:string;status:string;version:number};
export function CollaborationPanel({roomId,ownerId,canInvite=false}:{roomId?:string;ownerId?:string;canInvite?:boolean}){
 const [org,setOrg]=useState("");const [orgs,setOrgs]=useState<{id:string;displayName:string}[]>([]);
 const [items,setItems]=useState<Invitation[]>([]);const [partners,setPartners]=useState<string[]>([]);
 const [target,setTarget]=useState("");const [csrf,setCsrf]=useState("");const [status,setStatus]=useState("Loading");
 const [revision,setRevision]=useState(0);const [busy,setBusy]=useState(false);const key=useRef<string|null>(null);
 const [cursor,setCursor]=useState<string|null>(null);
 useEffect(()=>{let live=true;void(async()=>{try{
  const me=await api("/me");if(!live)return;setCsrf(me.csrf||"");
  const managed=me.data.organizations.filter((o:{id:string})=>me.data.memberships.some((m:{organizationId:string;status:string;role:string})=>m.organizationId===o.id&&m.status==="ACTIVE"&&["ORG_OWNER","ORG_ADMIN"].includes(m.role)));
  setOrgs(managed);const selected=org||ownerId||managed[0]?.id;
  if(!roomId&&!org&&selected){setOrg(selected);return;}
  if(roomId){const p=await api(`/rooms/${roomId}/participants`);if(!live)return;setPartners([p.data.ownerOrganizationId,...p.data.partnerOrganizationIds]);}
  if((!roomId||canInvite)&&selected){const list=await api(`/organizations/${selected}/room-invitations`);if(!live)return;setItems(list.data.items);setCursor(list.data.next_cursor);}
  setStatus("Ready");
 }catch{if(live){setItems([]);setPartners([]);setStatus("Access unavailable or request failed");}}})();return()=>{live=false;};},[org,roomId,ownerId,canInvite,revision]);
 async function act(invitation?:Invitation,action?:string){if(busy)return;setBusy(true);
  try{key.current??=crypto.randomUUID();const selected=ownerId||org;
   await api(invitation?`/organizations/${selected}/room-invitations/${invitation.id}`:`/rooms/${roomId}/invitations`,{
    method:invitation?"PATCH":"POST",headers:{"Content-Type":"application/json","X-CSRF-Token":csrf,...(invitation?{"If-Match":`"${invitation.version}"`}:{"Idempotency-Key":key.current})},
    body:JSON.stringify(invitation?{roomId:invitation.roomId,action}:{organizationId:selected,targetOrganizationId:target})});
   key.current=null;setStatus("Loading");setRevision(v=>v+1);
  }catch{setStatus("Action refused or conflict. Reload the current invitation before retrying.");}finally{setBusy(false);}}
 async function more(){if(!cursor||busy)return;setBusy(true);try{const list=await api(`/organizations/${ownerId||org}/room-invitations?cursor=${encodeURIComponent(cursor)}`);setItems(old=>[...old,...list.data.items]);setCursor(list.data.next_cursor);}catch{setItems([]);setStatus("Access unavailable or request failed");}finally{setBusy(false);}}
 const visible=items.filter(i=>!roomId||i.roomId===roomId);
 return <Card><h2>{roomId?"Collaboration":"Organization invitations"}</h2><p role="status">{status}</p>
  {!roomId&&<label>Organization<select aria-label="Invitation organization" value={org} disabled={busy} onChange={e=>{setOrg(e.target.value);setItems([]);setStatus("Loading");}}>{orgs.map(o=><option key={o.id} value={o.id}>{o.displayName}</option>)}</select></label>}
  {partners.length>0&&<><h3>Participating organizations</h3>{partners.map((id,index)=><p key={id} style={{overflowWrap:"anywhere"}}>{index===0?"Owner · metadata management":"Partner · read-only metadata"} · {id}</p>)}</>}
  {roomId&&canInvite&&<form onSubmit={e=>{e.preventDefault();void act();}}><TextField id="invite-target" label="Pre-registered organization ID" required value={target} onChange={e=>setTarget(e.target.value)} pattern="[0-9a-fA-F-]{36}"/><Button type="submit" disabled={busy||!csrf}>Invite organization</Button></form>}
  {status==="Ready"&&!visible.length&&<p>No invitations on this page</p>}
  {visible.map(i=><div key={i.id}><p style={{overflowWrap:"anywhere"}}>Room {i.roomId} · {i.status} · {i.targetOrganizationId}</p>
   {i.status==="PENDING"&&i.targetOrganizationId===org&&<><Button disabled={busy} onClick={()=>act(i,"accept")}>Accept</Button><Button disabled={busy} onClick={()=>act(i,"reject")}>Reject</Button></>}
   {i.status==="ACCEPTED"&&i.targetOrganizationId===org&&<Button disabled={busy} onClick={()=>act(i,"leave")}>Leave Room</Button>}
   {["PENDING","ACCEPTED"].includes(i.status)&&(ownerId||org)===i.ownerOrganizationId&&<Button disabled={busy} onClick={()=>act(i,"revoke")}>Revoke</Button>}
   {i.status==="ACCEPTED"&&<ButtonLink href={`/app/rooms/${i.roomId}`}>Open shared Room</ButtonLink>}
  </div>)}{cursor&&<Button onClick={more} disabled={busy}>Load more invitations</Button>}<Button onClick={()=>{setStatus("Loading");setRevision(v=>v+1);}} disabled={busy}>Reload invitations</Button>
  <p>Shared metadata only. No private computation or RoomState is created.</p></Card>;
}
