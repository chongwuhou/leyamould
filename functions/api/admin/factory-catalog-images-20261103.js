import {authorizedReviewedFactoryCatalogImageUploadRequest} from "../../_shared/build-auth.js";
import {checkedImage} from "../../_shared/media-image.js";
import {imageKey} from "../../_shared/r2-usage.js";
import manifest from "../../../data/factory-catalog-manifest-2026-11-03.json";

const json=(value,status=200)=>Response.json(value,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))).map(value=>value.toString(16).padStart(2,"0")).join("");
const byModel=new Map((manifest.models||[]).map(item=>[item.model,item]));

export async function onRequestGet(){return json({error:"Unauthorized"},401);}

export async function onRequestPost(context){
  if(!(await authorizedReviewedFactoryCatalogImageUploadRequest(context.request,context.env)))return json({error:"Unauthorized"},401);
  const env=context.env;
  if(!env.LEYA_ASSETS)return json({error:"LEYA R2 binding unavailable"},503);
  let form;
  try{form=await context.request.formData()}catch{return json({error:"Malformed multipart form"},400);}
  const model=String(form.get("model")||"");
  const expected=byModel.get(model);
  if(!expected)return json({error:"Model is not in the reviewed 58-product manifest"},400);
  if(String(form.get("sourceDocument")||"")!==manifest.sourceDocument||
     String(form.get("sourceSha256")||"")!==manifest.sourceSha256||
     String(form.get("sourcePage")||"")!==String(expected.sourcePage)||
     String(form.get("imageReviewStatus")||"")!=="visually_reviewed_source_crop"){
    return json({error:"Source document, page or image-review status does not match the reviewed manifest"},409);
  }
  const supplied=String(form.get("sha256")||"").toLowerCase();
  if(supplied!==expected.imageSha256)return json({error:"Image SHA-256 does not match the reviewed model manifest"},409);
  let media;
  try{media=await checkedImage(form.get("image"))}catch(error){return json({error:String(error.message||error)},400);}
  if(media.type!=="image/webp")return json({error:"Reviewed product photos must be WebP"},400);
  const actual=await sha(media.buffer);
  if(actual!==expected.imageSha256)return json({error:"Image bytes do not match the reviewed SHA-256"},409);
  const filename=actual.slice(0,32)+".webp";
  const path="/media/product/"+filename;
  const key=imageKey("product",filename);
  if(!key)return json({error:"Invalid deterministic product image key"},400);
  let prior;
  try{prior=await env.LEYA_ASSETS.head(key)}catch{return json({error:"Could not inspect LEYA R2 object"},503);}
  if(prior&&(prior.customMetadata?.sha256!==actual||
      prior.customMetadata?.model!==model||
      prior.customMetadata?.sourceSha256!==manifest.sourceSha256)){
    return json({error:"R2 path is occupied by different media; no overwrite was attempted"},409);
  }
  if(!prior){
    try{
      await env.LEYA_ASSETS.put(key,media.buffer,{
        httpMetadata:{contentType:"image/webp",cacheControl:"public, max-age=31536000, immutable"},
        customMetadata:{
          sha256:actual,model,sourceDocument:manifest.sourceDocument,
          sourceSha256:manifest.sourceSha256,sourcePage:String(expected.sourcePage),
          imageReviewStatus:"visually_reviewed_source_crop",reviewDate:"2026-11-03"
        }
      });
    }catch{return json({error:"R2 upload failed"},503);}
  }
  let stored;
  try{stored=await env.LEYA_ASSETS.head(key)}catch{return json({error:"Could not verify uploaded R2 object"},503);}
  if(!stored||stored.customMetadata?.sha256!==actual||stored.customMetadata?.model!==model||
     Number(stored.size)!==media.buffer.byteLength){
    return json({error:"R2 read-back verification failed"},503);
  }
  return json({saved:true,unchanged:Boolean(prior),model,sha256:actual,url:path,bytes:media.buffer.byteLength});
}

