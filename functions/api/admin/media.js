// XUYI shared R2 image library, adapted from Demalong's protected admin media.
import {authorizeAdminRequest} from "../../_shared/admin-security.js";
import {checkedImage} from "../../_shared/media-image.js";
const KINDS=new Set(["product","page","shared"]);
const PREFIX="site-media/";
const MAX_BYTES=1024*1024*1024;
const reply=(data,status=200)=>Response.json(data,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function guard(c){
 if(!c.env.ADMIN_TOKEN)return reply({error:"Admin unavailable"},503);
 if(!(await authorizeAdminRequest(c.request,c.env)))return reply({error:"Unauthorized"},401);
 if(!c.env.XUYI_ASSETS)return reply({error:"XUYI_ASSETS missing"},503);
 return null;
}
async function usage(bucket){
 let cursor,bytes=0,objects=0;
 do{
  const r=await bucket.list({prefix:PREFIX,limit:1000,...(cursor?{cursor}:{})});
  for(const object of r.objects||[]){bytes+=Number(object.size||0);objects++}
  cursor=r.truncated?r.cursor||undefined:undefined;
  if(r.truncated&&!cursor)throw Error("Unpageable R2 inventory");
 }while(cursor);
 return {usageBytes:bytes,usageObjects:objects,limitBytes:MAX_BYTES};
}
export async function onRequestGet(c){
 const denied=await guard(c);if(denied)return denied;
 const u=new URL(c.request.url);
 const kind=u.searchParams.get("kind")||"product";
 if(!KINDS.has(kind))return reply({error:"Unsupported media category"},400);
 const cursor=u.searchParams.get("cursor")||undefined;
 if(cursor&&(cursor.length>1024||!/^[a-zA-Z0-9_=-]+$/.test(cursor)))return reply({error:"Invalid cursor"},400);
 try{
  const [page,stats]=await Promise.all([
   c.env.XUYI_ASSETS.list({prefix:PREFIX+kind+"/",limit:80,...(cursor?{cursor}:{})}),
   usage(c.env.XUYI_ASSETS)
  ]);
  return reply({kind,...stats,items:(page.objects||[]).map(o=>({
   path:"/media/"+kind+"/"+o.key.split("/").pop(),size:o.size,uploadedAt:o.uploaded?.toISOString?.()||"",
   etag:o.etag||""
  })),cursor:page.truncated?page.cursor||"":""});
 }catch{return reply({error:"R2 inventory unavailable"},503)}
}
export async function onRequestPost(c){
 const denied=await guard(c);if(denied)return denied;
 if(Number(c.request.headers.get("content-length")||0)>7*1024*1024)return reply({error:"Image too large"},413);
 let form;try{form=await c.request.formData()}catch{return reply({error:"Invalid form-data"},400)}
 const kind=String(form.get("kind")||"product");
 if(!KINDS.has(kind))return reply({error:"Unsupported media category"},400);
 let media;try{media=await checkedImage(form.get("image"))}
 catch(err){return reply({error:String(err?.message||err)},400)}
 let stats;try{stats=await usage(c.env.XUYI_ASSETS)}
 catch{return reply({error:"Cannot verify R2 storage quota"},503)}
 if(stats.usageBytes+media.buffer.byteLength>MAX_BYTES)return reply({error:"R2 media quota reached",...stats},413);
 const name=crypto.randomUUID().replaceAll("-","")+"."+media.extension;
 const key=PREFIX+kind+"/"+name;
 await c.env.XUYI_ASSETS.put(key,media.buffer,{
  httpMetadata:{contentType:media.type},
  customMetadata:{source:"xuyi-admin-media",originalName:String(form.get("image")?.name||"").slice(0,180)}
 });
 return reply({saved:true,kind,path:"/media/"+kind+"/"+name,
  usageBytes:stats.usageBytes+media.buffer.byteLength,limitBytes:MAX_BYTES},201);
}
export async function onRequestDelete(c){
 const denied=await guard(c);if(denied)return denied;
 const url=new URL(c.request.url);
 const kind=url.searchParams.get("kind")||"";
 const filename=url.searchParams.get("filename")||"";
 if(!KINDS.has(kind)||!/^[a-f0-9]{32}\.(?:jpg|png|webp)$/.test(filename))
  return reply({error:"Invalid image key"},400);
 const key=PREFIX+kind+"/"+filename;
 const publicPath="/media/"+kind+"/"+filename;
 // Preserve assets already linked in approved D1 product / page content.
 if(c.env.XUYI_DB){
  const db=c.env.XUYI_DB;
  for(const sql of [
   "SELECT model FROM xuyi_product_content WHERE publication_status='published' AND instr(content_json,?)>0 LIMIT 1",
   "SELECT route FROM xuyi_page_content WHERE publication_status='published' AND instr(main_html,?)>0 LIMIT 1"
  ]){
   try{if(await db.prepare(sql).bind(publicPath).first())return reply({error:"Image is in use by published content"},409)}
   catch{return reply({error:"Cannot confirm image is unused"},503)}
  }
 }
 const stored=await c.env.XUYI_ASSETS.head(key);
 if(!stored)return reply({error:"Image not found"},404);
 await c.env.XUYI_ASSETS.delete(key);
 return reply({deleted:true,path:publicPath});
}