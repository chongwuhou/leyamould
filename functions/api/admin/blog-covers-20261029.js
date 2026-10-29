import {authorizedReviewedBlogCoverRequest} from "../../_shared/build-auth.js";
import {checkedImage} from "../../_shared/media-image.js";
import {bumpPublishRevision} from "../../_shared/site-settings.js";
import manifest from "../../../data/blog-reviewed-cover-r2-20261029.json" with {type:"json"};
const photos=manifest.images,locales=["es","pt","ru","tr"];
const respond=(data,status=200)=>Response.json(data,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow"}});
const tag=s=>'src="'+s+'"',key=p=>"site-blog/"+p.cover.split("/").at(-1);
export function replaceReviewedCover(html,oldPath,newPath){return String(html).split(tag(oldPath)).join(tag(newPath));}
async function digest(buffer){return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",buffer))).map(x=>x.toString(16).padStart(2,"0")).join("");}
export async function onRequestPost(c){
 if(!(await authorizedReviewedBlogCoverRequest(c.request,c.env)))return respond({error:"Unauthorized"},401);
 const mode=new URL(c.request.url).searchParams.get("mode"),db=c.env.XUYI_DB,bucket=c.env.XUYI_ASSETS;
 if(!db||!bucket)return respond({error:"XUYI CMS or R2 unavailable"},503);
 if(mode==="upload"){
  let form;try{form=await c.request.formData()}catch{return respond({error:"Invalid multipart"},400)}
  const photo=photos.find(x=>x.slug===String(form.get("slug")||""));
  if(!photo)return respond({error:"Unknown reviewed article"},400);
  let media;try{media=await checkedImage(form.get("image"))}catch(e){return respond({error:String(e.message||e)},400)}
  if(media.type!=="image/webp")return respond({error:"WebP only"},400);
  const hash=await digest(media.buffer);
  if(hash!==photo.sha256)return respond({error:"Reviewed media hash mismatch"},409);
  const previous=await bucket.head(key(photo));
  if(previous&&previous.customMetadata?.sha256!==hash)return respond({error:"R2 key already contains different media"},409);
  if(!previous)await bucket.put(key(photo),media.buffer,{httpMetadata:{contentType:"image/webp"},customMetadata:{sha256:hash,source:"owner-review-20261029"}});
  return respond({saved:true,path:photo.cover,sha256:hash,unchanged:!!previous});
 }
 if(mode!=="commit")return respond({error:"Unknown mode"},400);
 try{
  for(const photo of photos){
   const obj=await bucket.head(key(photo));
   if(!obj||obj.customMetadata?.sha256!==photo.sha256)return respond({error:"R2 media not verified",slug:photo.slug},409);
  }
  const posts=(await db.prepare("SELECT slug,status,content_json FROM xuyi_blog_posts WHERE slug IN (?,?,?)").bind(...photos.map(x=>x.slug)).all()).results||[];
  const ids=["page:/blog/",...photos.map(x=>"page:/blog/"+x.slug+"/")];
  const translations=(await db.prepare("SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (?,?,?,?) AND locale IN (?,?,?,?)").bind(...ids,...locales).all()).results||[];
  if(posts.length!==3||translations.length!==16)return respond({error:"Incomplete published or localized CMS data"},409);
  const byPost=new Map(posts.map(x=>[x.slug,x])),byLoc=new Map(translations.map(x=>[x.resource_id+"|"+x.locale,x]));
  const stmts=[],changed=[];
  for(const photo of photos){
   const post=byPost.get(photo.slug),current=JSON.parse(post.content_json).cover;
   if(post.status!=="published"||![photo.old,photo.cover].includes(current))return respond({error:"Owner-modified article cover preserved",slug:photo.slug},409);
   if(current===photo.old){
    stmts.push(db.prepare("UPDATE xuyi_blog_posts SET content_json=json_set(content_json,'$.cover',?),updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='published' AND json_extract(content_json,'$.cover')=?").bind(photo.cover,photo.slug,photo.old));
    changed.push("article:"+photo.slug);
   }
   for(const lang of locales){
    const id="page:/blog/"+photo.slug+"/",row=byLoc.get(id+"|"+lang),html=JSON.parse(row.translated_json).mainHtml||"";
    if(!html.includes(tag(photo.old))&&!html.includes(tag(photo.cover)))return respond({error:"Owner-changed translated image preserved",slug:photo.slug,lang},409);
    if(html.includes(tag(photo.old))){
     stmts.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=json_set(translated_json,'$.mainHtml',?),reviewed_at=CURRENT_TIMESTAMP WHERE resource_id=? AND locale=? AND translated_json=?").bind(replaceReviewedCover(html,photo.old,photo.cover),id,lang,row.translated_json));
     changed.push("translation:"+photo.slug+":"+lang);
    }
   }
  }
  for(const lang of locales){
   const row=byLoc.get("page:/blog/|"+lang),oldHtml=JSON.parse(row.translated_json).mainHtml||"";
   let html=oldHtml;
   for(const photo of photos){
    if(!html.includes(tag(photo.old))&&!html.includes(tag(photo.cover)))return respond({error:"Owner-changed index image preserved",slug:photo.slug,lang},409);
    html=replaceReviewedCover(html,photo.old,photo.cover);
   }
   if(html!==oldHtml){
    stmts.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=json_set(translated_json,'$.mainHtml',?),reviewed_at=CURRENT_TIMESTAMP WHERE resource_id='page:/blog/' AND locale=? AND translated_json=?").bind(html,lang,row.translated_json));
    changed.push("index:"+lang);
   }
  }
  if(!stmts.length)return respond({success:true,unchanged:true,changed:0});
  const results=await db.batch(stmts);
  if(results.some(x=>Number(x?.meta?.changes||0)!==1))return respond({error:"CMS concurrent edit, inspect before retry"},409);
  const revision=await bumpPublishRevision(db);
  return respond({success:true,changed:changed.length,publishRevision:revision.revision,updated:changed});
 }catch(e){return respond({error:"Reviewed cover update unavailable: "+String(e?.message||e).slice(0,160)},503)}
}
