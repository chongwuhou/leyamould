import {authorizedReviewedBlogImageUploadRequest} from "../../_shared/build-auth.js";
import {checkedImage} from "../../_shared/media-image.js";
import manifest from "../../../data/blog-images-reviewed-20261111.json" with {type:"json"};
const json=(v,s=200)=>Response.json(v,{status:s,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const key=item=>"site-blog/"+item.cover.split("/").at(-1);
const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))).map(v=>v.toString(16).padStart(2,"0")).join("");
export async function onRequestPost(context){
 if(!(await authorizedReviewedBlogImageUploadRequest(context.request,context.env)))return json({error:"Unauthorized"},401);
 if(!context.env.XUYI_ASSETS)return json({error:"Missing dedicated R2 binding"},503);
 let form;try{form=await context.request.formData();}catch{return json({error:"Malformed multipart"},400);}
 const item=manifest.images.find(x=>x.slug===String(form.get("slug")||""));
 if(!item)return json({error:"Unreviewed photo slug"},400);
 let media;try{media=await checkedImage(form.get("image"))}catch(e){return json({error:String(e.message||e)},400);}
 if(media.type!=="image/webp")return json({error:"Approved image must be WebP"},400);
 const actual=await sha(media.buffer);
 if(actual!==item.sha256)return json({error:"Edited or mismatched photo SHA-256"},409);
 const k=key(item),old=await context.env.XUYI_ASSETS.head(k);
 if(old&&old.customMetadata?.sha256!==actual)return json({error:"R2 path occupied by different media; no overwrite"},409);
 if(!old)await context.env.XUYI_ASSETS.put(k,media.buffer,{httpMetadata:{contentType:"image/webp"},customMetadata:{sha256:actual,reviewDate:"2026-11-11",source:"editorially-reviewed-context-asset"}});
 return json({saved:true,unchanged:!!old,url:item.cover,sha256:actual});
}