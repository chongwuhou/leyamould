// D1-managed, reviewed English page bodies for XUYI static pages.
// Reuses the Demalong admin auth/revision pattern; does not touch Blog or catalog sources.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";
import { MANAGED_ROUTES } from "../../_shared/xuyi-routes.js";

const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const clean=(value,limit)=>String(value??"").trim().slice(0,limit);
const allowedRoute=(route)=>MANAGED_ROUTES.has(route)
  && (route==="/"||!/^\/(?:products|collections|blog|contact)(?:\/|$)/.test(route))
  && !["/privacy-policy/","/request-sample/"].includes(route);

async function ensure(db){
  await db.prepare(`CREATE TABLE IF NOT EXISTS xuyi_page_content(
    route TEXT PRIMARY KEY,
    main_html TEXT NOT NULL DEFAULT '',
    publication_status TEXT NOT NULL DEFAULT 'draft'
      CHECK(publication_status IN ('draft','published')),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`).run();
}
async function deny(c){
  if(!c.env.ADMIN_TOKEN)return respond({error:"Admin not configured"},503);
  if(!(await authorizedBuildRequest(c.request,c.env)))return respond({error:"Unauthorized"},401);
  if(!c.env.XUYI_DB)return respond({error:"XUYI_DB missing"},503);
  return null;
}
export async function onRequestGet(c){
  const denied=await deny(c);if(denied)return denied;
  const db=c.env.XUYI_DB;await ensure(db);
  const rows=(await db.prepare(
    "SELECT route,main_html,publication_status,updated_at FROM xuyi_page_content ORDER BY route LIMIT 200"
  ).all()).results||[];
  return respond({editableRoutes:[...MANAGED_ROUTES].filter(allowedRoute).sort(),
    items:rows.map(r=>({route:r.route,mainHtml:r.main_html,status:r.publication_status,updatedAt:r.updated_at}))});
}
export async function onRequestPost(c){
  const denied=await deny(c);if(denied)return denied;
  let payload;try{payload=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
  if(payload?.action!=="save_page")return respond({error:"Unknown action"},400);
  const route=clean(payload.route,250);
  const mainHtml=clean(payload.mainHtml,180000);
  const status=payload.status==="published"?"published":"draft";
  if(!allowedRoute(route))return respond({error:"Route is not an editable XUYI page"},400);
  if(mainHtml.length<100||!/<(?:section|article|div|h1)\b/i.test(mainHtml))
    return respond({error:"Complete page-body HTML is required"},400);
  if(/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i.test(mainHtml))
    return respond({error:"Unsafe HTML in edited page body"},400);
  const db=c.env.XUYI_DB;await ensure(db);
  await db.prepare(`INSERT INTO xuyi_page_content(route,main_html,publication_status,updated_at)
    VALUES(?,?,?,CURRENT_TIMESTAMP)
    ON CONFLICT(route) DO UPDATE SET
    main_html=excluded.main_html,publication_status=excluded.publication_status,
    updated_at=CURRENT_TIMESTAMP`)
    .bind(route,mainHtml,status).run();
  const revision=await bumpPublishRevision(db);
  return respond({saved:true,route,status,...revision});
}
