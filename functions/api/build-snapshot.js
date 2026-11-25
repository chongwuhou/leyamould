// Build-time public-content snapshot for LEYA MOULD's D1 truth model.
// Requires a verified LEYA build/admin token. Never exposes submissions, secrets
// or other private tables; responses are no-store and not indexable.
import { authorizedBuildRequest } from "../_shared/build-auth.js";
import { defaultLanguageConfig, normalizeLanguageConfig, publicLanguages } from "../_shared/site-settings.js";
import { ensureLeyaSystemSchema } from "../_shared/leya-system.js";
import { ensureYoutubeVideos } from "../_shared/youtube-videos.js";
import { MOULD_MODELS, MOULD_ROUTES, isMouldModel, isMouldProductRoute, isMouldRoute, mouldModelFromRoute } from "../_shared/mould-routes.js";
import MOULD_CATALOG from "../../data/mould-catalog.json";

const json=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function list(db,sql){
  try{return (await db.prepare(sql).all()).results||[]}catch(error){
    // Tables are initialized by their respective admin modules on first save.
    if (/no such table/i.test(String(error?.message||error)))return [];
    throw error;
  }
}
async function ensureNavigationSchema(db){
  try{
    const columns=(await db.prepare("PRAGMA table_info(site_navigation)").all()).results||[];
    if(columns.length&&!columns.some(row=>row.name==="translations_json"))
      await db.prepare("ALTER TABLE site_navigation ADD COLUMN translations_json TEXT NOT NULL DEFAULT '{}'").run();
  }catch(error){
    // A clean database may not have navigation yet; the existing list helper
    // will safely return an empty D1 section in that case.
    if(!/no such table/i.test(String(error?.message||error)))throw error;
  }
}
async function ensureModelReferenceSchema(db){
  try{
    const columns=(await db.prepare("PRAGMA table_info(leya_model_references)").all()).results||[];
    if(!columns.length)return;
    for(const [name,type] of [["pdf_url","TEXT"],["pdf_sha256","TEXT"],["pdf_pages","INTEGER"]]){
      if(!columns.some(row=>row.name===name))await db.prepare(`ALTER TABLE leya_model_references ADD COLUMN ${name} ${type} NOT NULL DEFAULT '${type==="INTEGER"?"0":""}'`).run();
    }
  }catch(error){if(!/no such table/i.test(String(error?.message||error)))throw error;}
}
function parseJson(value,fallback){
  try{return value?JSON.parse(value):fallback}catch{return fallback}
}
function validSeoTitle(value){
  const text=String(value??"").trim();
  return text.length>=12&&text.length<=90&&!/[<>]/.test(text)?text:"";
}
function validMetaDescription(value){
  const text=String(value??"").trim();
  return text.length>=30&&text.length<=240&&!/[<>]/.test(text)?text:"";
}
function effectiveProductSeoRows(rows,products,localeCodes,sourceLocale){
  // The dedicated SEO table remains the first owner. Older published product
  // rows seeded before the SEO table existed still carry reviewed localized
  // title/description fields in xuyi_product_content; expose those D1-owned
  // fields as the effective SEO rows so a release never drops their metadata.
  const byKey=new Map();
  for(const row of rows){
    const slug=String(row.slug||"").trim().toLowerCase();
    const locale=String(row.locale||"").trim().toLowerCase();
    const seoTitle=validSeoTitle(row.seo_title);
    const metaDescription=validMetaDescription(row.meta_description);
    if(!isMouldModel(slug)||!localeCodes.has(locale)||!seoTitle||!metaDescription)continue;
    byKey.set(slug+"\u0000"+locale,{slug,locale,seoTitle,metaDescription,updatedAt:row.updated_at||"",source:"xuyi_product_seo"});
  }
  for(const product of products){
    const slug=String(product.model||"").trim().toLowerCase();
    if(!isMouldModel(slug))continue;
    const content=parseJson(product.content_json,{});
    for(const locale of localeCodes){
      const key=slug+"\u0000"+locale;
      if(byKey.has(key))continue;
      const isSource=locale===String(sourceLocale||"en").toLowerCase()||locale==="en";
      const title=validSeoTitle(content[isSource?"seoTitle":"seoTitle"+(locale==="es"?"Es":"")])
        ||validSeoTitle(content[locale==="es"?"titleEs":"title"])
        ||validSeoTitle(content[locale==="es"?"nameEs":"name"]);
      const metaDescription=validMetaDescription(content[isSource?"seoDescription":"seoDescription"+(locale==="es"?"Es":"")])
        ||validMetaDescription(content[locale==="es"?"descriptionEs":"description"])
        ||validMetaDescription(content[locale==="es"?"shortEs":"short"]);
      if(title&&metaDescription)
        byKey.set(key,{slug,locale,seoTitle:title,metaDescription,updatedAt:product.updated_at||"",source:"xuyi_product_content"});
    }
  }
  // The reviewed catalogue is the last deterministic source for a legacy row
  // that predates localized product fields. It is only used when neither D1
  // SEO table nor D1 product content has a value, and never overwrites edits.
  for(const item of (MOULD_CATALOG?.categories||[])){
    const slug=String(item?.slug||"").trim().toLowerCase();
    if(!isMouldModel(slug))continue;
    for(const locale of localeCodes){
      const key=slug+"\u0000"+locale;
      if(byKey.has(key))continue;
      const title=validSeoTitle(locale==="es"?item?.titleEs:item?.title);
      const metaDescription=validMetaDescription(locale==="es"?item?.descriptionEs:item?.description);
      if(title&&metaDescription)byKey.set(key,{slug,locale,seoTitle:title,metaDescription,updatedAt:"",source:"mould-catalog"});
    }
  }
  return [...byKey.values()].sort((a,b)=>a.slug.localeCompare(b.slug)||a.locale.localeCompare(b.locale));
}
export async function onRequestGet(context){
  if(!(await authorizedBuildRequest(context.request,context.env)))return json({error:"Unauthorized"},401);
  const db=context.env.LEYA_DB;
  if(!db)return json({error:"LEYA_DB binding missing"},503);
  try{
    await ensureLeyaSystemSchema(db);
    await ensureNavigationSchema(db);
    await ensureModelReferenceSchema(db);
    // The build snapshot is also the first reader after a fresh deployment.
    // Ensure the video schema/migrations exist before selecting the published
    // rows, so a new column never makes an otherwise valid build fail.
    await ensureYoutubeVideos(db);
    const [state,pages,navigation,redirects,products,translations,pageBodies,mediaAlts,productReviews,productSeo,blogPosts,youtubeVideos,modelReferences]=await Promise.all([
      list(db,"SELECT key,value FROM site_state WHERE key IN ('brand_config','contact_config','language_config','admin_security_config','publish_revision','home_banner_config','common_copy','page_copy')"),
      list(db,"SELECT route,label,seo_title,meta_description,robots,sitemap_enabled FROM site_pages ORDER BY route"),
      list(db,"SELECT id,parent_id,label,url,sort_order,new_window,translations_json FROM site_navigation WHERE enabled=1 ORDER BY sort_order,id"),
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
      list(db,"SELECT id,video_id,youtube_url,title,title_en,title_es,description,category,thumbnail_url,source,status,published_at,sort_order,updated_at FROM leya_youtube_videos WHERE status='published' ORDER BY sort_order ASC,created_at DESC,id ASC LIMIT 500"),
      // Model references are reviewed catalogue records. Only formally
      // published rows enter the immutable build snapshot.
      list(db,"SELECT slug,family,title,alt,source_url,source_image,image_path,description,translations_json,pdf_url,pdf_sha256,pdf_pages,publication_status,sort_order,updated_at FROM leya_model_references WHERE publication_status='published' ORDER BY family,sort_order,slug LIMIT 2000")
    ]);
      const config=Object.fromEntries(state.map(r=>[r.key,r.value]));
      const languageConfig=normalizeLanguageConfig(parseJson(config.language_config,defaultLanguageConfig()));
     const publicLocaleCodes=new Set(publicLanguages(languageConfig).map(item=>item.code));
     const security=parseJson(config.admin_security_config,{});
    const adminPath=security.adminPath||"admin";
    if(typeof adminPath!=="string"||!/^[a-z0-9][a-z0-9-]{2,47}$/.test(adminPath))
      throw new Error("Invalid LEYA admin route");
    const onlyRoutes=pages.filter(r=>(MOULD_ROUTES.has(r.route)||isMouldRoute(r.route))&&r.route.length<=300);
    const onlyNavigation=navigation.filter(r=>isMouldRoute(r.url));
    // Existing categories remain in the static allow-list, while new CMS
    // categories are admitted only when the model and canonical route are safe.
    const onlyProducts=products.filter(r=>{
      const model=String(r.model||"");
      if(!isMouldModel(model)) return false;
      const content=parseJson(r.content_json,{});
      const route=String(content.route||"");
      return MOULD_MODELS.has(model)||isMouldProductRoute(route)||isMouldProductRoute("/product/"+model+".html");
    });
    const onlyBlogPosts=blogPosts.flatMap(r=>{
      if(typeof r.slug!=="string"||!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(r.slug)
         ||r.status!=="published"||typeof r.content_json!=="string"||r.content_json.length>100000)return [];
      try{
        const post=JSON.parse(r.content_json);
        if(!post||typeof post!=="object"||Array.isArray(post))return [];
        return [{...post,slug:r.slug,status:"published",updated_at:r.updated_at||"",published_at:r.published_at||""}];
      }catch{return [];}
    });
    const effectiveProductSeo=effectiveProductSeoRows(productSeo,onlyProducts,publicLocaleCodes,languageConfig.sourceLocale);
    return json({
      site:"leyamould",schemaVersion:1,
      adminPath,
      publishRevision:Number(config.publish_revision||0),
       brand:parseJson(config.brand_config,null),
       contacts:parseJson(config.contact_config,null),
       languages:languageConfig,
       pages:onlyRoutes,navigation:onlyNavigation.map(r=>({...r,translations:parseJson(r.translations_json,{}),translations_json:undefined})),redirects,
       banners:parseJson(config.home_banner_config,null),
       commonCopy:parseJson(config.common_copy,null),
       pageCopy:parseJson(config.page_copy,null),
      pageBodies:pageBodies.filter(r=>isMouldRoute(r.route)&&typeof r.main_html==="string")
        .map(r=>({route:r.route,mainHtml:r.main_html})),
       products:onlyProducts.map(r=>({model:r.model,content:parseJson(r.content_json,{})})),
      blogPosts:onlyBlogPosts,
       // D1 remains the only source: explicit xuyi_product_seo rows win, and
       // legacy product content fields are promoted into the same snapshot
       // contract without inventing copy or touching owner data.
       productSeo:effectiveProductSeo,
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
         return isMouldRoute(resource.slice(5));
       }).map(r=>({resourceId:r.resource_id,locale:r.locale,content:parseJson(r.translated_json,{})})),
       youtubeVideos:youtubeVideos.filter(r=>/^[A-Za-z0-9_-]{11}$/.test(String(r.video_id||""))&&r.status!=="draft")
        .map(r=>({id:r.id,videoId:r.video_id,youtubeUrl:r.youtube_url,title:r.title||"",titleEn:r.title_en||r.title||"",titleEs:r.title_es||"",description:r.description||"",category:r.category||"mould-trial",thumbnailUrl:r.thumbnail_url||("https://i.ytimg.com/vi/"+r.video_id+"/mqdefault.jpg"),source:r.source||"youtube",status:r.status||"published",publishedAt:r.published_at||"",sortOrder:Number(r.sort_order||0),updatedAt:r.updated_at||""}))
      ,modelReferences:modelReferences.filter(r=>
          r.publication_status==="published"
          && /^[a-z0-9][a-z0-9-]{1,139}$/.test(String(r.slug||""))
          && typeof r.family==="string"&&r.family.length<=100
          && typeof r.title==="string"&&r.title.length>=2&&r.title.length<=180
          && typeof r.alt==="string"&&r.alt.length>=2&&r.alt.length<=180
          && /^\/media\/[a-z]+\/[a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|webp)$/.test(String(r.image_path||""))
        ).map(r=>({slug:r.slug,family:r.family,title:r.title,alt:r.alt,
          sourceUrl:r.source_url||"",sourceImage:r.source_image||"",image:r.image_path,
          description:r.description||"",translations:parseJson(r.translations_json,{}),pdfUrl:r.pdf_url||"",pdfSha256:r.pdf_sha256||"",pdfPages:Number(r.pdf_pages||0),
          sortOrder:Number(r.sort_order||0),updatedAt:r.updated_at||""}))
    });
  }catch(error){return json({error:"LEYA build snapshot unavailable"},503)}
}

