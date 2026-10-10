// XUYI R2 media manager: safe inventory, live references and fail-closed delete.
import {authorizeAdminRequest} from "../../_shared/admin-security.js";
import {checkedImage} from "../../_shared/media-image.js";
import {KINDS,readUsageIndex,findMediaUsage,imageKey} from "../../_shared/r2-usage.js";
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
 if(!Object.hasOwn(KINDS,kind))return reply({error:"Unsupported media category"},400);
 const selected=u.searchParams.get("filename")||"";
 if(selected){
  const key=imageKey(kind,selected);
  if(!key)return reply({error:"Invalid filename"},400);
  try{
   const index=await readUsageIndex(c.env,c.request.url);
   return reply({kind,filename:selected,path:"/media/"+kind+"/"+selected,
    canDelete:!!KINDS[kind].editable,
    ...await findMediaUsage(c.env,"/media/"+kind+"/"+selected,index)});
  }catch{return reply({error:"Cannot verify deployed pages and all D1 references",usageStatus:"unknown"},503)}
 }
 const cursor=u.searchParams.get("cursor")||undefined;
 if(cursor&&(cursor.length>1024||!/^[a-zA-Z0-9_=-]+$/.test(cursor)))return reply({error:"Invalid cursor"},400);
 try{
  const [page,stats]=await Promise.all([
   c.env.XUYI_ASSETS.list({prefix:KINDS[kind].prefix,limit:80,...(cursor?{cursor}:{})}),
   usage(c.env.XUYI_ASSETS)
  ]);
  let index=null;try{index=await readUsageIndex(c.env,c.request.url)}catch{}
  const items=(page.objects||[]).map(o=>{
   const filename=o.key.split("/").pop();
   const path="/media/"+kind+"/"+filename;
   const refs=index?.references?.[path]||[];
   return {path,key:o.key,size:o.size,uploadedAt:o.uploaded?.toISOString?.()||"",
     etag:o.etag||"",usageStatus:refs.length?"used":index?"needs-check":"unknown",
     referenceCount:refs.length,references:refs.slice(0,4),canDelete:!!KINDS[kind].editable};
  });
  return reply({kind,readOnly:!KINDS[kind].editable,referenceIndexReady:!!index,
    ...stats,items,cursor:page.truncated?page.cursor||"":""});
 }catch{return reply({error:"R2 inventory unavailable"},503)}
}
export async function onRequestPost(c){
 const denied=await guard(c);if(denied)return denied;
 if(Number(c.request.headers.get("content-length")||0)>7*1024*1024)return reply({error:"Image too large"},413);
 let form;try{form=await c.request.formData()}catch{return reply({error:"Invalid form-data"},400)}
 const kind=String(form.get("kind")||"product");
 if(!Object.hasOwn(KINDS,kind)||!KINDS[kind].editable)return reply({error:"Upload only supports managed media groups"},400);
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
 const key=imageKey(kind,filename);
 if(!key||!Object.hasOwn(KINDS,kind)||!KINDS[kind].editable)return reply({error:"Deleting legacy catalog and system files is forbidden"},403);
 const path="/media/"+kind+"/"+filename;
 let usage;
 try{
  const index=await readUsageIndex(c.env,c.request.url);
  usage=await findMediaUsage(c.env,path,index);
 }catch{return reply({error:"Cannot verify deployed-page and D1 usages; deletion blocked"},503)}
 if(usage.used)return reply({error:"Image is in use; remove all references before deletion",...usage},409);
 const stored=await c.env.XUYI_ASSETS.head(key);
 if(!stored)return reply({error:"Image not found"},404);
 await c.env.XUYI_ASSETS.delete(key);
 return reply({deleted:true,path,usageStatus:"unused"});
}
