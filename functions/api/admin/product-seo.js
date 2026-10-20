// Unified, owner-editable SEO title/description records in the existing D1
// CMS. Each product × locale is an independent authoritative row.
import {authorizeAdminRequest} from "../../_shared/admin-security.js";
import {MANAGED_MODELS} from "../../_shared/xuyi-routes.js";
import {bumpPublishRevision} from "../../_shared/site-settings.js";
import {ensureProductSeo,canonicalProductSlug,normalizeProductSeo,upsertProductSeo} from "../../_shared/product-seo.js";

const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function ready(c){
 if(!c.env.ADMIN_TOKEN)return {error:respond({error:"Admin not configured"},503)};
 if(!(await authorizeAdminRequest(c.request,c.env)))return {error:respond({error:"Unauthorized"},401)};
 if(!c.env.XUYI_DB)return {error:respond({error:"XUYI_DB unavailable"},503)};
 const db=c.env.XUYI_DB;await ensureProductSeo(db);return {db};
}
async function hasProduct(db,slug){
 if([...MANAGED_MODELS].some(model=>canonicalProductSlug(model)===slug))return true;
 const product=await db.prepare("SELECT content_json,publication_status FROM xuyi_product_content WHERE model=?")
   .bind(slug).first();
 try{return product?.publication_status==="published"&&JSON.parse(product.content_json)?.newProduct===true}
 catch{return false}
}
export async function onRequestGet(c){
 const {db,error}=await ready(c);if(error)return error;
 const rows=(await db.prepare("SELECT slug,locale,seo_title,meta_description,updated_at FROM xuyi_product_seo ORDER BY slug,locale LIMIT 2000").all()).results||[];
 return respond({models:[...new Set([...MANAGED_MODELS].map(canonicalProductSlug))].sort(),
  items:rows.map(r=>({slug:r.slug,locale:r.locale,seoTitle:r.seo_title,
    metaDescription:r.meta_description,updatedAt:r.updated_at}))});
}
export async function onRequestPost(c){
 const {db,error}=await ready(c);if(error)return error;
 let input;try{input=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
 if(input?.action!=="save")return respond({error:"Unknown action"},400);
 let value;try{value=normalizeProductSeo(input)}catch(e){return respond({error:e.message},400)}
 if(!await hasProduct(db,value.slug))return respond({error:"产品型号不属于已发布的 XUYI 目录"},400);
 await upsertProductSeo(db,{slug:value.slug,locale:value.locale,seoTitle:value.title,metaDescription:value.description});
 const revision=await bumpPublishRevision(db);
 return respond({saved:true,slug:value.slug,locale:value.locale,...revision});
}
