import {serveModelOverflow} from "./_shared/model-overflow.js";

// SECURITY: Pages can retain historic deployment assets long after a project
// update. These three exact source paths must never fall through to static
// serving; the remaining public routes retain their existing behavior.
const RETIRED_SOURCE_PATHS=new Set([
  "/build.py",
  "/site_renderer.py",
  "/data/products.json"
]);
export async function onRequest(context){
  if(RETIRED_SOURCE_PATHS.has(new URL(context.request.url).pathname))
    return new Response("Gone\n",{status:410,headers:{
      "cache-control":"no-store",
      "x-robots-tag":"noindex,nofollow,noarchive",
      "x-content-type-options":"nosniff",
      "content-type":"text/plain; charset=utf-8"
    }});
  return serveModelOverflow(context);
}
