// Reviewed full-page HTML translations, stored in XUYI's existing translation
// override table. Translation drafts must be reviewed before publication.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";
import { MANAGED_ROUTES } from "../../_shared/xuyi-routes.js";
const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const clean=(v,n)=>String(v??"").trim().slice(0,n);
async function requireAdmin(c){
  if(!c.env.ADMIN_TOKEN)return respond({error:"Admin not configured"},503);
  if(!(await authorizedBuildRequest(c.request,c.env)))return respond({error:"Unauthorized"},401);
  if(!c.env.XUYI_DB)return respond({error:"XUYI_DB missing"},503);
  return null;
}
export async function onRequestGet(c){
  const denied=await requireAdmin(c);if(denied)return denied;
  const rows=(await c.env.XUYI_DB.prepare(
    "SELECT resource_id,locale,translated_json,reviewed_at FROM xuyi_translation_overrides WHERE resource_id LIKE 'page:%' ORDER BY locale,resource_id LIMIT 600"
  ).all()).results||[];
  return respond({items:rows.map(x=>({route:x.resource_id.slice(5),locale:x.locale,
    content:JSON.parse(x.translated_json),reviewedAt:x.reviewed_at}))});
}
export async function onRequestPost(c){
  const denied=await requireAdmin(c);if(denied)return denied;
  let p;try{p=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
  const route=clean(p.route,250),locale=clean(p.locale,12).toLowerCase();
  const title=clean(p.title,180),description=clean(p.description,450),html=clean(p.mainHtml,250000);
  if(!(route==="/"||/^\/(?:[a-z0-9_-]+\/)+$/.test(route)))
    return respond({error:"Invalid XUYI route"},400);
  if(!["es","pt","ru","tr"].includes(locale))return respond({error:"Unsupported locale"},400);
  if(!title||!description||html.length<120||!/<(?:section|article|div|h1)\b/i.test(html))
    return respond({error:"Full translated title, description and main HTML required"},400);
  if(/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i.test(html))
    return respond({error:"Unsafe HTML in translated content"},400);
  const db=c.env.XUYI_DB;
  if(!MANAGED_ROUTES.has(route))return respond({error:"Unknown managed XUYI page"},400);
  await db.prepare(`INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at)
     VALUES(?,?,?,CURRENT_TIMESTAMP)
     ON CONFLICT(resource_id,locale) DO UPDATE SET translated_json=excluded.translated_json,reviewed_at=CURRENT_TIMESTAMP`)
    .bind("page:"+route,locale,JSON.stringify({title,description,mainHtml:html})).run();
  const revision=await bumpPublishRevision(db);
  return respond({saved:true,reviewed:true,route,locale,...revision});
}