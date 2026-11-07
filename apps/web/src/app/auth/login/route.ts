import { NextRequest } from "next/server";
import { guarded, login } from "@/server/auth/handlers";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET(request: NextRequest) {
  return guarded(() => login(request));
}
