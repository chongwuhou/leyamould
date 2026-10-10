// Human-reviewed homepage carousel controls, stored in XUYI's existing D1 site_state.
import {authorizedBuildRequest} from "../../_shared/build-auth.js";
import {authorizeAdminRequest} from "../../_shared/admin-security.js";
import {bumpPublishRevision} from "../../_shared/site-settings.js";
import {normalizeBanners} from "../../_shared/home-banners.js";
const json=(v,status=200)=>Response.json(v,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function auth(c){
 if(!c.env.ADMIN_TOKEN)return json({error:"Admin not configured"},503);
 if(!(await authorizedBuildRequest(c.request,c.env)))return json({error:"Unauthorized"},401);
 if(!c.env.XUYI_DB)return json({error:"XUYI_DB unavailable"},503);
 return null;
}
export async function onRequestGet(c){
 const denied=await auth(c);if(denied)return denied;
 try{
  const row=await c.env.XUYI_DB.prepare("SELECT value,updated_at FROM site_state WHERE key='home_banner_config'").first();
  return json({source:row?"cloudflare-d1":"source-default",config:row?normalizeBanners(JSON.parse(row.value)):null,updatedAt:row?.updated_at||""});
 }catch(err){return json({error:"Unable to read homepage banner configuration"},503)}
}
export async function onRequestPost(c){
 const denied=await auth(c);if(denied)return denied;
 if(!(await authorizeAdminRequest(c.request,c.env)))return json({error:"Only a signed-in administrator can update homepage banners"},401);
 let value;try{value=await c.request.json()}catch{return json({error:"Invalid JSON"},400)}
 let config;try{config=normalizeBanners(value.config)}catch(error){return json({error:String(error.message||error)},400)}
 try{
  const db=c.env.XUYI_DB;
  if(!c.env.XUYI_ASSETS)return json({error:"Cannot validate R2 media without XUYI_ASSETS"},503);
  // R2 objects must actually exist; deployed /assets files are validated by the release gate.
  for(const slide of config.slides){
   if(slide.img.startsWith("/assets/")){
    if(!c.env.ASSETS?.fetch)return json({error:"Cannot verify static Banner images"},503);
    const response=await c.env.ASSETS.fetch(new Request(new URL(slide.img,c.request.url)));
    if(!response.ok)return json({error:"Static image does not exist: "+slide.img},409);
    continue;
   }
   const match=/^\/media\/([a-z]+)\/([a-zA-Z0-9._-]+\.(?:webp|jpg|jpeg|png))$/.exec(slide.img);
   if(!match)continue;
   const kind=match[1],name=match[2];
   const prefixes={product:"site-media/product/",page:"site-media/page/",shared:"site-media/shared/",
    ppt:"catalog-staging/ppt/",excel:"site-preview/excel/",group:"site-preview/group/",
    capability:"site-capabilities/",gallery:"site-gallery/",blog:"site-blog/"};
   if(!Object.hasOwn(prefixes,kind))return json({error:"Unsupported R2 image group"},400);
   const exists=await c.env.XUYI_ASSETS.head(prefixes[kind]+name);
   if(!exists)return json({error:"R2 image not found: "+slide.img},409);
  }
  await db.prepare("INSERT INTO site_state(key,value,updated_at) VALUES('home_banner_config',?,CURRENT_TIMESTAMP) "+
    "ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP").bind(JSON.stringify(config)).run();
  const revision=await bumpPublishRevision(db);
  return json({saved:true,revision,slides:3,publish:"queued"});
 }catch(error){return json({error:"Could not save homepage banner: "+String(error?.message||error)},503)}
}