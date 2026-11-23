// D1-managed, reviewed English page bodies for LEYA MOULD static pages.
// Uses the shared admin auth/revision pattern; does not touch Blog or catalog sources.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";
import { MOULD_ROUTES } from "../../_shared/mould-routes.js";

const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const clean=(value,limit)=>String(value??"").trim().slice(0,limit);
// Product, blog, and translation data have their own modules.  The page-body
// editor owns only the shared LEYA informational/contact pages.
const EDITABLE_PAGE_ROUTES=new Set([
  "/", "/about/", "/capabilities/", "/capabilities/mould-design/",
  "/capabilities/precision-manufacturing/", "/capabilities/trial-sampling/",
  "/manufacturing/", "/quality-control/", "/request-sample/", "/contact/",
  "/samples/", "/news/", "/news/Bottle-cap-molds.html",
  "/Bottle-Cap-Machine/Bottle-Cap-Machine.html", "/video/", "/faq/",
  "/privacy-policy/"
]);
const allowedRoute=(route,knownRoutes=MOULD_ROUTES)=>knownRoutes.has(route)
  && EDITABLE_PAGE_ROUTES.has(route);

async function configuredRoutes(db){
 try{return ((await db.prepare("SELECT route FROM site_pages ORDER BY route LIMIT 500").all()).results||[])
   .map(row=>String(row.route||"")).filter(Boolean)}catch{return []}
}
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
  if(!c.env.LEYA_DB)return respond({error:"LEYA_DB missing"},503);
  return null;
}
export async function onRequestGet(c){
  const denied=await deny(c);if(denied)return denied;
  const db=c.env.LEYA_DB;await ensure(db);
  const rows=(await db.prepare(
    "SELECT route,main_html,publication_status,updated_at FROM xuyi_page_content ORDER BY route LIMIT 200"
  ).all()).results||[];
  const knownRoutes=new Set([...MANAGED_ROUTES,...await configuredRoutes(db)]);
  return respond({editableRoutes:[...knownRoutes].filter(route=>allowedRoute(route,knownRoutes)).sort(),
    items:rows.map(r=>({route:r.route,mainHtml:r.main_html,status:r.publication_status,updatedAt:r.updated_at}))});
}
export async function onRequestPost(c){
  const denied=await deny(c);if(denied)return denied;
  let payload;try{payload=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
  if(payload?.action!=="save_page")return respond({error:"Unknown action"},400);
  const route=clean(payload.route,250);
  const mainHtml=clean(payload.mainHtml,180000);
  const status=payload.status==="published"?"published":"draft";
  const knownRoutes=new Set([...MANAGED_ROUTES,...await configuredRoutes(c.env.LEYA_DB)]);
  if(!allowedRoute(route,knownRoutes))return respond({error:"Route is not an editable configured page"},400);
  if(mainHtml.length<100||!/<(?:section|article|div|h1)\b/i.test(mainHtml))
    return respond({error:"Complete page-body HTML is required"},400);
  if(/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i.test(mainHtml))
    return respond({error:"Unsafe HTML in edited page body"},400);
  const db=c.env.LEYA_DB;await ensure(db);
  await db.prepare(`INSERT INTO xuyi_page_content(route,main_html,publication_status,updated_at)
    VALUES(?,?,?,CURRENT_TIMESTAMP)
    ON CONFLICT(route) DO UPDATE SET
    main_html=excluded.main_html,publication_status=excluded.publication_status,
    updated_at=CURRENT_TIMESTAMP`)
    .bind(route,mainHtml,status).run();
  const revision=await bumpPublishRevision(db);
  return respond({saved:true,route,status,...revision});
}

