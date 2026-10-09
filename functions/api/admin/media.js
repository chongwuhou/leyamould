// Shared R2 media library for confirmed XUYI product/page artwork.
// Reuses the exact image safety checks of the existing blog upload.
import { authorizeAdminRequest } from "../../_shared/admin-security.js";
import { checkedImage } from "../../_shared/media-image.js";
const KINDS = new Set(["product","page","shared"]);
const response = (data,status=200)=>Response.json(data,{status,headers:{
  "cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function guard(context){
  if(!context.env.ADMIN_TOKEN)return response({error:"Admin not configured"},503);
  if(!(await authorizeAdminRequest(context.request,context.env)))return response({error:"Unauthorized"},401);
  if(!context.env.XUYI_ASSETS)return response({error:"XUYI_ASSETS missing"},503);
  return null;
}
export async function onRequestGet(context){
  const denied=await guard(context);if(denied)return denied;
  const url=new URL(context.request.url);
  const kind=url.searchParams.get("kind")||"product";
  if(!KINDS.has(kind))return response({error:"Unsupported image group"},400);
  const cursor=url.searchParams.get("cursor")||undefined;
  if(cursor && (cursor.length>1024 || !/^[A-Za-z0-9_=-]+$/.test(cursor)))
    return response({error:"Invalid cursor"},400);
  try{
    const result=await context.env.XUYI_ASSETS.list({prefix:"site-media/"+kind+"/",limit:80,...(cursor?{cursor}:{})});
    return response({kind,items:(result.objects||[]).map(row=>({
      path:"/media/"+kind+"/"+row.key.split("/").pop(),
      size:row.size,uploadedAt:row.uploaded?.toISOString?.()||""
    })),cursor:result.truncated?result.cursor||"":""});
  }catch{return response({error:"Media list unavailable"},503)}
}
export async function onRequestPost(context){
  const denied=await guard(context);if(denied)return denied;
  if(Number(context.request.headers.get("content-length")||0)>7*1024*1024)
    return response({error:"Image too large"},413);
  let form;try{form=await context.request.formData()}catch{return response({error:"Invalid form-data"},400)}
  const kind=String(form.get("kind")||"product");
  if(!KINDS.has(kind))return response({error:"Unsupported image group"},400);
  let media;try{media=await checkedImage(form.get("image"))}
  catch(error){return response({error:String(error?.message||error)},400)}
  const filename=crypto.randomUUID().replace(/-/g,"")+"."+media.extension;
  const key="site-media/"+kind+"/"+filename;
  await context.env.XUYI_ASSETS.put(key,media.buffer,{
    httpMetadata:{contentType:media.type},
    customMetadata:{source:"xuyi-admin-media"}
  });
  return response({saved:true,kind,path:"/media/"+kind+"/"+filename},201);
}