import { NextRequest } from "next/server";
import { guarded, proxy } from "@/server/auth/handlers";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
type Context = {params: Promise<{path: string[]}>};
async function handle(request: NextRequest, context: Context) {
  return guarded(async () => proxy(request, (await context.params).path));
}
export { handle as GET, handle as POST, handle as PATCH, handle as DELETE };
