// Build-time public-content snapshot for LEYA MOULD's D1 truth model.
// Requires a verified LEYA build/admin token. Never exposes submissions, secrets
// or other private tables; responses are no-store and not indexable.
import { authorizedBuildRequest } from "../_shared/build-auth.js";
import { defaultLanguageConfig, normalizeLanguageConfig, publicLanguages } from "../_shared/site-settings.js";
import { MOULD_MODELS, MOULD_ROUTES, mouldModelFromRoute } from "../_shared/mould-routes.js";

const json=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function list(db,sql){
  try{return (await db.prepare(sql).all()).results||[]}catch(error){
    // Tables are initialized by their respective admin modules on first save.
    if (/no such table/i.test(String(error?.message||error)))return [];
    throw error;
  }
}
function parseJson(value,fallback){
  try{return value?JSON.parse(value):fallback}catch{return fallback}
}
export async function onRequestGet(context){
  if(!(await authorizedBuildRequest(context.request,context.env)))return json({error:"Unauthorized"},401);
  const db=context.env.LEYA_DB;
  if(!db)return json({error:"LEYA_DB binding missing"},503);
  try{
    const [state,pages,navigation,redirects,products,translations,pageBodies,mediaAlts,productReviews,productSeo,blogPosts,youtubeVideos,modelReferences]=await Promise.all([
      list(db,"SELECT key,value FROM site_state WHERE key IN ('brand_config','contact_config','language_config','admin_security_config','publish_revision','home_banner_config','common_copy','page_copy')"),
      list(db,"SELECT route,label,seo_title,meta_description,robots,sitemap_enabled FROM site_pages ORDER BY route"),
      list(db,"SELECT id,parent_id,label,url,sort_order,new_window FROM site_navigation WHERE enabled=1 ORDER BY sort_order,id"),
      list(db,"SELECT source_path,target_path,status_code FROM site_redirects WHERE enabled=1 ORDER BY source_path"),
      list(db,"SELECT model,content_json,publication_status FROM xuyi_product_content WHERE publication_status='published' ORDER BY model"),
      list(db,"SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides ORDER BY locale,resource_id"),
      list(db,"SELECT route,main_html FROM xuyi_page_content WHERE publication_status='published' ORDER BY route"),
      list(db,"SELECT path,alt_json FROM xuyi_media_alt ORDER BY path LIMIT 12000"),
      list(db,"SELECT id,model,rating,author,review_date,content,status FROM xuyi_product_reviews WHERE status='published' ORDER BY model,review_date DESC,id"),
      list(db,"SELECT slug,locale,seo_title,meta_description,updated_at FROM xuyi_product_seo ORDER BY slug,locale"),
      // Keep the build snapshot in the same deterministic order as the live
      // English Blog route. Localized static indexes are rendered from this
      // D1 order so every language presents the same article sequence.
      list(db,"SELECT slug,status,content_json,updated_at,published_at FROM xuyi_blog_posts WHERE status='published' ORDER BY COALESCE(published_at,updated_at) DESC,slug ASC"),
      list(db,"SELECT id,video_id,youtube_url,title,title_en,title_es,description,published_at,sort_order,updated_at FROM leya_youtube_videos ORDER BY sort_order ASC,created_at DESC,id ASC LIMIT 500"),
      // Model references are reviewed catalogue records. Only formally
      // published rows enter the immutable build snapshot.
      list(db,"SELECT slug,family,title,alt,source_url,source_image,image_path,description,translations_json,publication_status,sort_order,updated_at FROM leya_model_references WHERE publication_status='published' ORDER BY family,sort_order,slug LIMIT 2000")
    ]);
      const config=Object.fromEntries(state.map(r=>[r.key,r.value]));
      const languageConfig=normalizeLanguageConfig(parseJson(config.language_config,defaultLanguageConfig()));
     const publicLocaleCodes=new Set(publicLanguages(languageConfig).map(item=>item.code));
     const security=parseJson(config.admin_security_config,{});
    const adminPath=security.adminPath||"admin";
    if(typeof adminPath!=="string"||!/^[a-z0-9][a-z0-9-]{2,47}$/.test(adminPath))
      throw new Error("Invalid LEYA admin route");
    const onlyRoutes=pages.filter(r=>MOULD_ROUTES.has(String(r.route||""))&&r.route.length<=300);
    const onlyNavigation=navigation.filter(r=>MOULD_ROUTES.has(String(r.url||"")));
    const onlyProducts=products.filter(r=>MOULD_MODELS.has(String(r.model||"")));
    const onlyBlogPosts=blogPosts.flatMap(r=>{
      if(typeof r.slug!=="string"||!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(r.slug)
         ||r.status!=="published"||typeof r.content_json!=="string"||r.content_json.length>100000)return [];
      try{
        const post=JSON.parse(r.content_json);
        if(!post||typeof post!=="object"||Array.isArray(post))return [];
        return [{...post,slug:r.slug,status:"published",updated_at:r.updated_at||"",published_at:r.published_at||""}];
      }catch{return [];}
    });
    return json({
      site:"leyamould",schemaVersion:1,
      adminPath,
      publishRevision:Number(config.publish_revision||0),
       brand:parseJson(config.brand_config,null),
       contacts:parseJson(config.contact_config,null),
       languages:languageConfig,
       pages:onlyRoutes,navigation:onlyNavigation,redirects,
       banners:parseJson(config.home_banner_config,null),
       commonCopy:parseJson(config.common_copy,null),
       pageCopy:parseJson(config.page_copy,null),
      pageBodies:pageBodies.filter(r=>MOULD_ROUTES.has(String(r.route||""))&&typeof r.main_html==="string")
        .map(r=>({route:r.route,mainHtml:r.main_html})),
       products:onlyProducts.map(r=>({model:r.model,content:parseJson(r.content_json,{})})),
      blogPosts:onlyBlogPosts,
       productSeo:productSeo.filter(r=>MOULD_MODELS.has(String(r.slug||""))
         && publicLocaleCodes.has(r.locale)
        && typeof r.seo_title==="string"&&r.seo_title.length<=90
        && typeof r.meta_description==="string"&&r.meta_description.length<=240)
        .map(r=>({slug:r.slug,locale:r.locale,seoTitle:r.seo_title,
          metaDescription:r.meta_description,updatedAt:r.updated_at})),
       productReviews:productReviews
         .filter(r=>MOULD_MODELS.has(String(r.model||""))
          && Number.isInteger(r.rating)&&r.rating>=1&&r.rating<=5
          && typeof r.author==="string"&&r.author.length>=2&&r.author.length<100
          && /^\d{4}-\d{2}-\d{2}$/.test(r.review_date)
          && typeof r.content==="string"&&r.content.length>=12)
        .map(r=>({id:r.id,model:r.model,rating:r.rating,author:r.author,
          reviewDate:r.review_date,content:r.content,status:"published"})),
       mediaAlts:mediaAlts.filter(r=>/^\/media\/(?:product|page|shared|ppt|excel|group|capability|gallery|blog)\/[a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|webp)$/.test(r.path))
         .map(r=>({path:r.path,translations:parseJson(r.alt_json,{})})),
       translations:translations.filter(r=>{
         const resource=String(r.resource_id||"");
         if(!resource.startsWith("page:"))return false;
         return MOULD_ROUTES.has(resource.slice(5));
       }).map(r=>({resourceId:r.resource_id,locale:r.locale,content:parseJson(r.translated_json,{})})),
       youtubeVideos:youtubeVideos.filter(r=>/^[A-Za-z0-9_-]{11}$/.test(String(r.video_id||"")))
        .map(r=>({id:r.id,videoId:r.video_id,youtubeUrl:r.youtube_url,title:r.title||"",titleEn:r.title_en||r.title||"",titleEs:r.title_es||"",description:r.description||"",publishedAt:r.published_at||"",sortOrder:Number(r.sort_order||0),updatedAt:r.updated_at||""}))
      ,modelReferences:modelReferences.filter(r=>
          r.publication_status==="published"
          && /^[a-z0-9][a-z0-9-]{1,139}$/.test(String(r.slug||""))
          && typeof r.family==="string"&&r.family.length<=100
          && typeof r.title==="string"&&r.title.length>=2&&r.title.length<=180
          && typeof r.alt==="string"&&r.alt.length>=2&&r.alt.length<=180
          && /^\/media\/[a-z]+\/[a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|webp)$/.test(String(r.image_path||""))
        ).map(r=>({slug:r.slug,family:r.family,title:r.title,alt:r.alt,
          sourceUrl:r.source_url||"",sourceImage:r.source_image||"",image:r.image_path,
          description:r.description||"",translations:parseJson(r.translations_json,{}),
          sortOrder:Number(r.sort_order||0),updatedAt:r.updated_at||""}))
    });
  }catch(error){return json({error:"LEYA build snapshot unavailable"},503)}
}


