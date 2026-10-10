// Authenticated in-place R2 picture replacement, including legacy XUYI assets.
// Requires a conscious model/content confirmation; no file path/HTML rewrite.
import {authorizeAdminRequest} from "../../_shared/admin-security.js";
import {checkedImage} from "../../_shared/media-image.js";
import {KINDS,imageKey} from "../../_shared/r2-usage.js";
import {imageDimensions,mimeOfName} from "../../_shared/image-dimensions.js";
const MAX=6*1024*1024;
const HISTORY_ROOT="site-image-versions/";
const response=(obj,status=200)=>Response.json(obj,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function guard(c){
 if(!c.env.ADMIN_TOKEN)return response({error:"Admin unavailable"},503);
 if(!(await authorizeAdminRequest(c.request,c.env)))return response({error:"Unauthorized"},401);
 if(!c.env.XUYI_ASSETS)return response({error:"XUYI_ASSETS missing"},503);
 return null;
}
const reference=c=>{
 const url=new URL(c.request.url);
 const kind=url.searchParams.get("kind")||"";
 const filename=url.searchParams.get("filename")||"";
 const key=imageKey(kind,filename);
 // Includes validated legacy images, but never overflow/system/backups buckets.
 if(!key||!Object.hasOwn(KINDS,kind))return null;
 return {kind,filename,key,path:"/media/"+kind+"/"+filename};
};
const folder=x=>HISTORY_ROOT+x.kind+"/"+x.filename+"/";
const validVersion=x=>/^\d{13}-[a-f0-9]{32}$/.test(x);
async function previous(bucket,x,old,oldBuffer=null){
 if(old.size>MAX)throw Error("Original image exceeds safe rollback backup size");
 const body=oldBuffer||await old.arrayBuffer();
 if(body.byteLength!==old.size)throw Error("Original R2 image could not be read completely");
 const version=Date.now()+"-"+crypto.randomUUID().replaceAll("-","");
 const contentType=mimeOfName(x.filename);
 const backupKey=folder(x)+version;
 await bucket.put(backupKey,body,{httpMetadata:{contentType},customMetadata:{originalKey:x.key,originalEtag:old.etag||"",originalBytes:String(old.size)}});
 const saved=await bucket.head(backupKey);
 if(!saved||saved.size!==body.byteLength)throw Error("Previous version could not be verified; original unchanged");
 return {version,backupKey,size:body.byteLength,body};
}
async function stored(bucket,x){
 const item=await bucket.get(x.key);
 if(!item)return null;
 if(item.size>MAX)throw Error("Original image too large for safe versioned replacement");
 return item;
}
async function checkEtag(item,expected){
 if(!expected||expected!==item.etag)throw Error("Image was changed since list refresh; reload before replacing");
}
async function quota(bucket,x,newSize,oldSize){
 if(!KINDS[x.kind].editable)return;
 let cursor,bytes=0;
 do{
  const page=await bucket.list({prefix:"site-media/",limit:1000,...(cursor?{cursor}:{})});
  for(const o of page.objects||[])bytes+=Number(o.size||0);
  cursor=page.truncated?page.cursor:undefined;
  if(page.truncated&&!cursor)throw Error("R2 inventory cursor unavailable");
 }while(cursor);
 if(bytes-oldSize+newSize>1024*1024*1024)throw Error("Managed media storage 1GB quota exceeded");
}
async function listHistory(bucket,x){
 const r=await bucket.list({prefix:folder(x),limit:150});
 if(r.truncated)throw Error("Version history limit exceeded; manual review needed");
 return (r.objects||[]).filter(o=>validVersion(o.key.slice(folder(x).length)))
  .sort((a,b)=>b.key.localeCompare(a.key))
  .slice(0,12).map(o=>({version:o.key.slice(folder(x).length),bytes:o.size,
    uploadedAt:o.uploaded?.toISOString?.()||""}));
}
export async function onRequestGet(c){
 const denied=await guard(c);if(denied)return denied;
 const x=reference(c);if(!x)return response({error:"Unsupported R2 image path"},400);
 try{
  const current=await c.env.XUYI_ASSETS.head(x.key);
  if(!current)return response({error:"R2 image not found"},404);
  return response({path:x.path,etag:current.etag,size:current.size,
    versions:await listHistory(c.env.XUYI_ASSETS,x)});
 }catch(error){return response({error:"Cannot read version history: "+String(error.message||error)},503)}
}
export async function onRequestPut(c){
 const denied=await guard(c);if(denied)return denied;
 const x=reference(c);if(!x)return response({error:"Unsupported R2 image path"},400);
 if(Number(c.request.headers.get("content-length")||0)>MAX+1_048_576)
  return response({error:"New image exceeds upload size limit"},413);
 let form;try{form=await c.request.formData()}catch{return response({error:"Invalid image upload"},400)}
 if(form.get("confirm")!=="same-subject")return response({error:"Confirm same product/model and permitted image usage"},400);
 let file;try{file=await checkedImage(form.get("image"))}
 catch(error){return response({error:String(error.message||error)},400)}
 const requiredMime=mimeOfName(x.filename);
 if(file.type!==requiredMime)return response({error:"New image format must match original URL ("+requiredMime+"). Browser can convert to WebP before upload."},400);
 let dimensions;
 try{dimensions=imageDimensions(file.buffer,file.type)}
 catch{return response({error:"Cannot determine new image dimensions"},400)}
 try{
  const bucket=c.env.XUYI_ASSETS;
  const original=await stored(bucket,x);
  if(!original)return response({error:"Original R2 image no longer exists"},404);
  try{await checkEtag(original,String(form.get("etag")||""))}
  catch(error){return response({error:error.message},409)}
  let oldSize,originalBytes;
  try{originalBytes=await original.arrayBuffer();oldSize=imageDimensions(originalBytes,requiredMime)}
  catch{return response({error:"Cannot verify original dimensions; replacement blocked"},409)}
  if(dimensions.width<oldSize.width||dimensions.height<oldSize.height)
   return response({error:"New image resolution is lower than original",oldSize,dimensions},409);
  await quota(bucket,x,file.buffer.byteLength,original.size);
  // Backup and HEAD verification precede any modification to live path.
  const backup=await previous(bucket,x,original,originalBytes);
  await bucket.put(x.key,file.buffer,{httpMetadata:{contentType:file.type},customMetadata:{
    source:"xuyi-admin-replace",backupVersion:backup.version,
    newPixelSize:dimensions.width+"x"+dimensions.height}});
  const written=await bucket.head(x.key);
  if(!written||written.size!==file.buffer.byteLength)
   return response({error:"Replacement write could not be verified; previous version is safe in history",backupVersion:backup.version},503);
  return response({replaced:true,path:x.path,oldSize,newSize:dimensions,
    backupVersion:backup.version,oldBytes:original.size,newBytes:written.size,
    cacheNote:"Unversioned image URLs may remain cached for up to one hour."});
 }catch(error){return response({error:"Replacement failed: "+String(error.message||error)},503)}
}
export async function onRequestPost(c){
 const denied=await guard(c);if(denied)return denied;
 const x=reference(c);if(!x)return response({error:"Unsupported R2 image path"},400);
 let data;try{data=await c.request.json()}catch{return response({error:"Invalid JSON"},400)}
 if(data?.action!=="restore"||!validVersion(data?.version)||data.confirm!=="restore")
  return response({error:"Invalid restore confirmation/version"},400);
 try{
  const bucket=c.env.XUYI_ASSETS;
  const current=await stored(bucket,x);
  if(!current)return response({error:"Image not found"},404);
  try{await checkEtag(current,String(data.etag||""))}
  catch(error){return response({error:error.message},409)}
  const backup=await bucket.get(folder(x)+data.version);
  if(!backup)return response({error:"Selected previous version not found"},404);
  if(backup.size>MAX)return response({error:"Backup exceeds safe restore size"},413);
  const buffer=await backup.arrayBuffer();
  try{imageDimensions(buffer,mimeOfName(x.filename))}
  catch{return response({error:"Backup image invalid; restoration blocked"},409)}
  await quota(bucket,x,buffer.byteLength,current.size);
  // Save the current image as a new version before restoring an older one.
  const undo=await previous(bucket,x,current);
  await bucket.put(x.key,buffer,{httpMetadata:{contentType:mimeOfName(x.filename)},
    customMetadata:{source:"xuyi-admin-restore",restoredFrom:data.version}});
  return response({restored:true,path:x.path,undoVersion:undo.version,
    cacheNote:"Current viewers may see a cached version for up to one hour."});
 }catch(error){return response({error:"Restore failed: "+String(error.message||error)},503)}
}