// Build-time public-content snapshot for LEYA MOULD's D1 truth model.
// Requires a verified LEYA build/admin token. Never exposes submissions, secrets
// or other private tables; responses are no-store and not indexable.
import { authorizedBuildRequest } from "../_shared/build-auth.js";
import { defaultLanguageConfig, normalizeLanguageConfig, publicLanguages } from "../_shared/site-settings.js";
import { MOULD_MODELS, MOULD_ROUTES, isMouldModel, isMouldProductRoute, isMouldRoute, mouldModelFromRoute } from "../_shared/mould-routes.js";

const BLOG_DETAIL_ROUTE_RE=/^\/blog\/[a-z0-9]+(?:-[a-z0-9]+)*\/$/;
const NEWS_DETAIL_ROUTE_RE=/^\/news\/[A-Za-z0-9][A-Za-z0-9_-]*\.html$/;
function managedPageRoute(route){
  const value=String(route||"");
  const registered=MOULD_ROUTES.has(value);
  return registered||isMouldRoute(value)||BLOG_DETAIL_ROUTE_RE.test(value)||NEWS_DETAIL_ROUTE_RE.test(value);
}
function pageContentType(route){
  const value=String(route||"");
  if(/^\/product\//.test(value))return "product";
  if(BLOG_DETAIL_ROUTE_RE.test(value))return "blog";
  if(NEWS_DETAIL_ROUTE_RE.test(value)||value==="/news/")return "news";
  if(value==="/video/")return "video";
  if(value==="/Bottle-Cap-Machine/Bottle-Cap-Machine.html"||value.startsWith("/capabilities/"))return "capability";
  return "page";
}

const json=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function list(db,sql){
  try{return (await db.prepare(sql).all()).results||[]}catch(error){
    // Tables are initialized by their respective admin modules on first save.
    if (/no such table/i.test(String(error?.message||error)))return [];
    throw error;
  }
}
async function tableColumns(db,table){
  try{
    const rows=(await db.prepare("PRAGMA table_info("+table+")").all()).results||[];
    return new Set(rows.map(row=>String(row.name||"")));
  }catch(error){
    if(/no such table/i.test(String(error?.message||error)))return new Set();
    throw error;
  }
}
const optionalColumn=(columns,name,fallback)=>columns.has(name)?name:(fallback+" AS "+name);
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
  // rows seeded before the SEO table existed may still carry reviewed
  // localized title/description fields in xuyi_product_content; expose those
  // D1-owned fields as effective SEO rows. No repository catalogue fallback is
  // allowed in the production snapshot.
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
  return [...byKey.values()].sort((a,b)=>a.slug.localeCompare(b.slug)||a.locale.localeCompare(b.locale));
}
export async function onRequestGet(context){
  if(!(await authorizedBuildRequest(context.request,context.env)))return json({error:"Unauthorized"},401);
  const db=context.env.LEYA_DB;
  if(!db)return json({error:"LEYA_DB binding missing"},503);
  try{
    // Schema discovery is read-only.  Older D1 tables may not yet contain a
    // newly added optional column; the snapshot must still read safely rather
    // than migrating the database from a GET request.
    const [navigationColumns,reviewColumns,videoColumns,modelReferenceColumns]=await Promise.all([
      tableColumns(db,"site_navigation"),tableColumns(db,"xuyi_product_reviews"),
      tableColumns(db,"leya_youtube_videos"),tableColumns(db,"leya_model_references")
    ]);
    const navigationTranslations=optionalColumn(navigationColumns,"translations_json","'{}'");
    const reviewSourceUrl=optionalColumn(reviewColumns,"source_url","''");
    const reviewSourceVerifiedAt=optionalColumn(reviewColumns,"source_verified_at","''");
    const videoSource=optionalColumn(videoColumns,"source","'youtube'");
    const modelPdfUrl=optionalColumn(modelReferenceColumns,"pdf_url","''");
    const modelPdfSha=optionalColumn(modelReferenceColumns,"pdf_sha256","''");
    const modelPdfPages=optionalColumn(modelReferenceColumns,"pdf_pages","0");
    const [state,pages,navigation,redirects,products,translations,pageBodies,mediaAlts,productReviews,productSeo,blogPosts,youtubeVideos,modelReferences,allModelReferences]=await Promise.all([
      list(db,"SELECT key,value FROM site_state WHERE key IN ('brand_config','contact_config','language_config','admin_security_config','publish_revision','home_banner_config','common_copy','page_copy')"),
      list(db,"SELECT route,label,seo_title,meta_description,robots,sitemap_enabled FROM site_pages ORDER BY route"),
      list(db,"SELECT id,parent_id,label,url,sort_order,new_window,"+navigationTranslations+" FROM site_navigation WHERE enabled=1 ORDER BY sort_order,id"),
      list(db,"SELECT source_path,target_path,status_code FROM site_redirects WHERE enabled=1 ORDER BY source_path"),
      list(db,"SELECT model,content_json,publication_status FROM xuyi_product_content WHERE publication_status='published' ORDER BY model"),
      list(db,"SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides ORDER BY locale,resource_id"),
      list(db,"SELECT route,main_html FROM xuyi_page_content WHERE publication_status='published' ORDER BY route"),
      list(db,"SELECT path,alt_json FROM xuyi_media_alt ORDER BY path LIMIT 12000"),
      list(db,"SELECT id,model,rating,author,review_date,content,"+reviewSourceUrl+","+reviewSourceVerifiedAt+",status FROM xuyi_product_reviews WHERE status='published' ORDER BY model,review_date DESC,id"),
      list(db,"SELECT slug,locale,seo_title,meta_description,updated_at FROM xuyi_product_seo ORDER BY slug,locale"),
      // Keep the build snapshot in the same deterministic order as the live
      // English Blog route. Localized static indexes are rendered from this
      // D1 order so every language presents the same article sequence.
      list(db,"SELECT slug,status,content_json,updated_at,published_at FROM xuyi_blog_posts WHERE status='published' ORDER BY COALESCE(published_at,updated_at) DESC,slug ASC"),
      list(db,"SELECT id,video_id,youtube_url,title,title_en,title_es,description,category,thumbnail_url,"+videoSource+",status,published_at,sort_order,updated_at FROM leya_youtube_videos WHERE status='published' ORDER BY sort_order ASC,created_at DESC,id ASC LIMIT 500"),
      // Model references are reviewed catalogue records. Only formally
      // published rows enter the immutable build snapshot.
      list(db,"SELECT slug,family,title,alt,source_url,source_image,image_path,description,translations_json,"+modelPdfUrl+","+modelPdfSha+","+modelPdfPages+",publication_status,sort_order,reviewed_at,updated_at FROM leya_model_references WHERE publication_status='published' ORDER BY family,sort_order,slug LIMIT 2000"),
      list(db,"SELECT slug,publication_status,source_url,source_image,image_path,reviewed_at FROM leya_model_references ORDER BY family,sort_order,slug LIMIT 2000")
    ]);
      const config=Object.fromEntries(state.map(r=>[r.key,r.value]));
      const languageConfig=normalizeLanguageConfig(parseJson(config.language_config,defaultLanguageConfig()));
     const publicLocaleCodes=new Set(publicLanguages(languageConfig).map(item=>item.code));
     const security=parseJson(config.admin_security_config,{});
    const adminPath=security.adminPath||"admin";
    if(typeof adminPath!=="string"||!/^[a-z0-9][a-z0-9-]{2,47}$/.test(adminPath))
      throw new Error("Invalid LEYA admin route");
    const onlyNavigation=navigation.filter(r=>managedPageRoute(r.url));
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
    // Build a complete D1-owned route registry.  Static page rows remain
    // authoritative; published product and Blog rows are promoted into the
    // same registry so a newly approved route cannot disappear merely because
    // an older site_pages migration has not yet materialized its row.
    const pageRegistry=new Map();
    for(const row of pages){
      const route=String(row.route||"");
      if(!managedPageRoute(route)||route.length>300)continue;
      pageRegistry.set(route,{...row,contentType:pageContentType(route),contentKey:route,source:"site_pages"});
    }
    for(const row of onlyProducts){
      const content=parseJson(row.content_json,{});
      const route=String(content.route||"/product/"+row.model+".html");
      if(!isMouldProductRoute(route))continue;
      const title=String(content.seoTitle||content.title||content.name||row.model).trim();
      const description=String(content.seoDescription||content.description||content.short||"").trim();
      if(!pageRegistry.has(route))pageRegistry.set(route,{route,label:title,seo_title:title,meta_description:description,robots:"noindex,nofollow",sitemap_enabled:0,contentType:"product",contentKey:row.model,source:"product_content"});
    }
    for(const post of onlyBlogPosts){
      const route="/blog/"+String(post.slug||"")+"/";
      if(!BLOG_DETAIL_ROUTE_RE.test(route))continue;
      if(!pageRegistry.has(route))pageRegistry.set(route,{route,label:String(post.title||post.slug||"").trim(),seo_title:String(post.title||"").trim(),meta_description:String(post.description||"").trim(),robots:"noindex,nofollow",sitemap_enabled:0,contentType:"blog",contentKey:String(post.slug||""),source:"blog_posts"});
    }
    const onlyRoutes=[...pageRegistry.values()].sort((a,b)=>String(a.route).localeCompare(String(b.route)));
    const productByRoute=new Map(onlyProducts.map(row=>{
      const content=parseJson(row.content_json,{});
      return [String(content.route||"/product/"+row.model+".html"),{model:row.model,content}];
    }));
    const blogByRoute=new Map(onlyBlogPosts.map(post=>["/blog/"+String(post.slug||"")+"/",post]));
    const pageCopy= parseJson(config.page_copy,{});
    const pageFields=onlyRoutes.map(row=>{
      const route=String(row.route||"");
      const type=String(row.contentType||pageContentType(route));
      let fields={};
      if(type==="product")fields=productByRoute.get(route)?.content||{};
      else if(type==="blog")fields=blogByRoute.get(route)||{};
      else{
        for(const locale of publicLocaleCodes){
          const localized=pageCopy&&typeof pageCopy==="object"&&pageCopy[locale]&&typeof pageCopy[locale]==="object"?pageCopy[locale]:{};
          if(localized[route]&&typeof localized[route]==="object")fields[locale]=localized[route];
        }
      }
      return {route,contentType:type,contentKey:String(row.contentKey||route),seoTitle:String(row.seo_title||""),metaDescription:String(row.meta_description||""),fields};
    });
    const effectiveProductSeo=effectiveProductSeoRows(productSeo,onlyProducts,publicLocaleCodes,languageConfig.sourceLocale);
    const modelReferenceAudit={total:allModelReferences.length,
      published:allModelReferences.filter(row=>row.publication_status==="published").length,
      draft:allModelReferences.filter(row=>row.publication_status!=="published").length,
      publishedIssues:allModelReferences.filter(row=>row.publication_status==="published").map(row=>{
        const issues=[];
        if(!/^https:\/\//i.test(String(row.source_url||"")))issues.push("source_url");
        if(!/^https:\/\//i.test(String(row.source_image||"")))issues.push("source_image");
        if(!/^\/media\/[a-z]+\/[a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|webp)$/i.test(String(row.image_path||"")))issues.push("r2_image");
        return issues.length?{slug:row.slug,issues}:null;
      }).filter(Boolean)};
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
       modelReferenceAudit,
       pageRegistry:onlyRoutes,
       pageFields,
       pageBodies:pageBodies.filter(r=>managedPageRoute(r.route)&&typeof r.main_html==="string")
        .map(r=>({route:r.route,mainHtml:r.main_html})),
       products:onlyProducts.map(r=>{
         const content=parseJson(r.content_json,{});
         const structured=content&&typeof content.structured==="object"&&!Array.isArray(content.structured)
           ?content.structured
           :(content&&typeof content.category==="object"&&!Array.isArray(content.category)?content.category:{});
         return {model:r.model,route:String(content.route||"/product/"+r.model+".html"),content,structured,contentSchemaVersion:1};
       }),
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
          && typeof r.content==="string"&&r.content.length>=12
          && /^https:\/\//i.test(String(r.source_url||""))
          && String(r.source_verified_at||"").trim())
        .map(r=>({id:r.id,model:r.model,rating:r.rating,author:r.author,
          reviewDate:r.review_date,content:r.content,sourceUrl:r.source_url,status:"published"})),
       mediaAlts:mediaAlts.filter(r=>/^\/media\/(?:product|page|shared|ppt|excel|group|capability|gallery|blog)\/[a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|webp)$/.test(r.path))
         .map(r=>({path:r.path,translations:parseJson(r.alt_json,{})})),
       translations:translations.filter(r=>{
         const resource=String(r.resource_id||"");
         if(!resource.startsWith("page:"))return false;
         const route=resource.slice(5);
         // Canonical page translation snapshot includes dynamic routes.
         // Translation rows remain a read-only production build input.
         // The production chain consumes this snapshot without D1 writes.
         // Page overrides are D1-managed for every generated page, including
         // dynamic news and product detail routes. Keep only canonical paths.
         return route==="/"||/^\/[A-Za-z0-9][A-Za-z0-9/_-]*(?:\.html)?$/.test(route);
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
          reviewedAt:r.reviewed_at||"",sortOrder:Number(r.sort_order||0),updatedAt:r.updated_at||""}))
    });
  }catch(error){return json({error:"LEYA build snapshot unavailable"},503)}
}



