// Build-time public-content snapshot (XUYI D1 truth model, XUYI data).
// Requires a verified XUYI build/admin token. Never exposes submissions, secrets
// or other private tables; responses are no-store and not indexable.
import { authorizedBuildRequest } from "../_shared/build-auth.js";

const json=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function list(db,sql){
  try{return (await db.prepare(sql).all()).results||[]}catch(error){
    // Tables are initialized by their respective admin modules on first save.
    if (/no such table/i.test(String(error?.message||error)))return [];
    throw error;
  }
}
export async function onRequestGet(context){
  if(!(await authorizedBuildRequest(context.request,context.env)))return json({error:"Unauthorized"},401);
  const db=context.env.XUYI_DB;
  if(!db)return json({error:"XUYI_DB binding missing"},503);
  try{
    const [state,pages,navigation,redirects,products,translations,pageBodies,mediaAlts,productReviews,productSeo,blogPosts]=await Promise.all([
      list(db,"SELECT key,value FROM site_state WHERE key IN ('brand_config','contact_config','language_config','admin_security_config','publish_revision','home_banner_config')"),
      list(db,"SELECT route,label,seo_title,meta_description,robots,sitemap_enabled FROM site_pages ORDER BY route"),
      list(db,"SELECT id,parent_id,label,url,sort_order,new_window FROM site_navigation WHERE enabled=1 ORDER BY sort_order,id"),
      list(db,"SELECT source_path,target_path,status_code FROM site_redirects WHERE enabled=1 ORDER BY source_path"),
      list(db,"SELECT model,content_json,publication_status FROM xuyi_product_content WHERE publication_status='published' ORDER BY model"),
      list(db,"SELECT resource_id,locale,translated_json FROM xuyi_translation_overrides ORDER BY locale,resource_id"),
      list(db,"SELECT route,main_html FROM xuyi_page_content WHERE publication_status='published' ORDER BY route"),
      list(db,"SELECT path,alt_json FROM xuyi_media_alt ORDER BY path LIMIT 12000"),
      list(db,"SELECT id,model,rating,author,review_date,content,status FROM xuyi_product_reviews WHERE status='published' ORDER BY model,review_date DESC,id"),
      list(db,"SELECT slug,locale,seo_title,meta_description FROM xuyi_product_seo ORDER BY slug,locale"),
      list(db,"SELECT slug,status,content_json,updated_at,published_at FROM xuyi_blog_posts WHERE status='published' ORDER BY slug")
    ]);
    const config=Object.fromEntries(state.map(r=>[r.key,r.value]));
    const security=config.admin_security_config?JSON.parse(config.admin_security_config):{};
    const adminPath=security.adminPath||"admin";
    if(typeof adminPath!=="string"||!/^[a-z0-9][a-z0-9-]{2,47}$/.test(adminPath))
      throw new Error("Invalid XUYI admin route");
    const onlyRoutes=pages.filter(r=>(r.route==="/"||/^\/(?:[a-z0-9_-]+\/)+$/.test(r.route))&&r.route.length<=300);
    const onlyProducts=products.filter(r=>/^[a-zA-Z0-9_\-\u4e00-\u9fff]{1,80}$/.test(r.model));
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
      site:"xuyi-drinkware-site",schemaVersion:1,
      adminPath,
      publishRevision:Number(config.publish_revision||0),
      brand:config.brand_config?JSON.parse(config.brand_config):null,
      contacts:config.contact_config?JSON.parse(config.contact_config):null,
      languages:config.language_config?JSON.parse(config.language_config):null,
      pages:onlyRoutes,navigation,redirects,
      banners:config.home_banner_config?JSON.parse(config.home_banner_config):null,
      pageBodies:pageBodies.filter(r=>typeof r.route==="string"&&typeof r.main_html==="string")
        .map(r=>({route:r.route,mainHtml:r.main_html})),
      products:onlyProducts.map(r=>({model:r.model,content:JSON.parse(r.content_json)})),
      blogPosts:onlyBlogPosts,
      productSeo:productSeo.filter(r=>/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(r.slug)
        && ["en","es","pt","ru","tr"].includes(r.locale)
        && typeof r.seo_title==="string"&&r.seo_title.length<=90
        && typeof r.meta_description==="string"&&r.meta_description.length<=240)
        .map(r=>({slug:r.slug,locale:r.locale,seoTitle:r.seo_title,
          metaDescription:r.meta_description})),
      productReviews:productReviews
        .filter(r=>/^[a-zA-Z0-9_\-\u4e00-\u9fff]{1,80}$/.test(r.model)
          && Number.isInteger(r.rating)&&r.rating>=1&&r.rating<=5
          && typeof r.author==="string"&&r.author.length>=2&&r.author.length<100
          && /^\d{4}-\d{2}-\d{2}$/.test(r.review_date)
          && typeof r.content==="string"&&r.content.length>=12)
        .map(r=>({id:r.id,model:r.model,rating:r.rating,author:r.author,
          reviewDate:r.review_date,content:r.content,status:"published"})),
      mediaAlts:mediaAlts.filter(r=>/^\/media\/(?:product|page|shared|ppt|excel|group|capability|gallery|blog)\/[a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|webp)$/.test(r.path))
        .map(r=>({path:r.path,translations:JSON.parse(r.alt_json)})),
      translations:translations.map(r=>({resourceId:r.resource_id,locale:r.locale,content:JSON.parse(r.translated_json)}))
    });
  }catch(error){return json({error:"XUYI build snapshot unavailable"},503)}
}
