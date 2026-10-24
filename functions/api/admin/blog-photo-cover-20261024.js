import { authorizedReviewedBlogBatchRequest } from "../../_shared/build-auth.js";
import { ensureBlogSchema } from "../../_shared/blog-cms.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";
import { PHOTO_SLUGS,PHOTO_LANGS,changeBlogPostCover,changeLocalizedBlogHero,changeLocalizedIndex } from "../../_shared/blog-photo-cover-guard.js";

const respond=(data,status=200)=>Response.json(data,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
export async function onRequestPost(context){
  if(!(await authorizedReviewedBlogBatchRequest(context.request,context.env)))return respond({error:"Unauthorized"},401);
  const db=context.env.XUYI_DB;
  if(!db)return respond({error:"Database binding unavailable"},503);
  let payload;
  try{payload=await context.request.json();}catch{return respond({error:"Invalid JSON"},400);}
  if(!payload||payload.approvedFivePhotoCovers!==true||Object.keys(payload).length!==1)return respond({error:"Unapproved operation"},400);
  try{
    await ensureBlogSchema(db);
    const posts=(await db.prepare("SELECT slug,status,content_json FROM xuyi_blog_posts WHERE slug IN (?,?,?,?,?)")
      .bind(...PHOTO_SLUGS).all()).results||[];
    if(posts.length!==5||posts.some(row=>row.status!=="published"))return respond({error:"Reviewed published articles incomplete"},409);
    const statements=[],activeSlugs=[];
    for(const row of posts){
      const original=JSON.parse(row.content_json);
      const fixed=changeBlogPostCover(original,row.slug);
      if(fixed===original)continue; // Already corrected or owner-selected different cover
      statements.push(db.prepare("UPDATE xuyi_blog_posts SET content_json=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND content_json=?")
       .bind(JSON.stringify(fixed),row.slug,row.content_json));
      activeSlugs.push(row.slug);
    }
    const resources=["page:/blog/",...PHOTO_SLUGS.map(s=>"page:/blog/"+s+"/")];
    const tr=(await db.prepare("SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides WHERE resource_id IN (?,?,?,?,?,?) AND locale IN (?,?,?,?)")
      .bind(...resources,...PHOTO_LANGS).all()).results||[];
    if(tr.length!==24)return respond({error:"Expected 20 localized article bodies and four index bodies"},409);
    let heroRows=0,indexRows=0;
    for(const row of tr){
      const content=JSON.parse(row.translated_json);
      if(typeof content.mainHtml!=="string")return respond({error:"Invalid localized content"},409);
      const original=content.mainHtml;
      let next=original;
      if(row.resource_id==="page:/blog/"){
        next=changeLocalizedIndex(original,activeSlugs);
        if(next!==original)indexRows++;
      }else{
        const slug=row.resource_id.slice("page:/blog/".length).replace(/\/$/,"");
        if(activeSlugs.includes(slug)){
          next=changeLocalizedBlogHero(original,slug);
          if(next!==original)heroRows++;
        }
      }
      if(next!==original){
        statements.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=? WHERE resource_id=? AND locale=? AND translated_json=?")
          .bind(JSON.stringify({...content,mainHtml:next}),"2026-10-24",row.resource_id,row.locale,row.translated_json));
      }
    }
    if(!statements.length)return respond({success:true,alreadyApplied:true,updatedSlugs:[],heroRows:0,indexRows:0});
    const results=await db.batch(statements);
    if(results.some(r=>Number(r?.meta?.changes||0)!==1))return respond({error:"Concurrent CMS edit; inspect exact D1 state"},409);
    const revision=await bumpPublishRevision(db);
    return respond({success:true,updatedSlugs:activeSlugs,heroRows,indexRows,publishRevision:revision.revision});
  }catch(e){
    return respond({error:"Photo cover update refused: "+String(e?.message||"Unknown").slice(0,175)},409);
  }
}
