import { NextRequest } from "next/server";
import { guarded, callback } from "@/server/auth/handlers";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET(request: NextRequest) {
  return guarded(() => callback(request));
}
