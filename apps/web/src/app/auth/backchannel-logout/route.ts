import { NextRequest } from "next/server";
import { guarded, backchannel } from "@/server/auth/handlers";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function POST(request: NextRequest) {
  return guarded(() => backchannel(request));
}
