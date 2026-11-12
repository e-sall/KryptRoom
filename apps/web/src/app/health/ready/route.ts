import {NextResponse} from "next/server";
import {config} from "@/server/auth/config";
export const dynamic="force-dynamic";
export const runtime="nodejs";
export async function GET(){
 try{
  const c=config();await c.pool.query("SELECT 1");
  const [api,idp]=await Promise.all([
   fetch(c.api+"/health/ready",{cache:"no-store",redirect:"error",signal:AbortSignal.timeout(3000)}),
   fetch(c.issuer+"/.well-known/openid-configuration",{cache:"no-store",redirect:"error",signal:AbortSignal.timeout(3000)})]);
  if(api.status!==200||idp.status!==200||(await idp.json()).issuer!==c.issuer)throw new Error("Unavailable");
  return NextResponse.json({status:"ready"},{headers:{"Cache-Control":"no-store"}});
 }catch{return NextResponse.json({status:"unavailable"},{status:503,headers:{"Cache-Control":"no-store"}});}
}
