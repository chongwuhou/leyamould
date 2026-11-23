// D1 CRUD for authentic, SKU-associated testimonials. Existing admin login.
import {authorizeAdminRequest} from "../../_shared/admin-security.js";
import {MANAGED_MODELS} from "../../_shared/mould-routes.js";
import {bumpPublishRevision} from "../../_shared/site-settings.js";
import {ensureProductReviews,normalizeProductReview} from "../../_shared/product-reviews.js";
const json=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
async function authorized(c){
 if(!c.env.ADMIN_TOKEN)return json({error:"Admin not configured"},503);
 if(!(await authorizeAdminRequest(c.request,c.env)))return json({error:"Unauthorized"},401);
 if(!c.env.LEYA_DB)return json({error:"LEYA_DB unavailable"},503);
 return null;
}
async function knownModel(db,model){
 if(MANAGED_MODELS.has(model))return true;
 try{
  const row=await db.prepare("SELECT publication_status,content_json FROM xuyi_product_content WHERE model=?").bind(model).first();
  return row?.publication_status==="published"&&JSON.parse(row.content_json)?.newProduct===true;
 }catch{return false;}
}
export async function onRequestGet(c){
 const denied=await authorized(c);if(denied)return denied;
 const db=c.env.LEYA_DB;await ensureProductReviews(db);
 const [rows,products]=await Promise.all([
  db.prepare("SELECT id,model,rating,author,review_date,content,status,updated_at FROM xuyi_product_reviews ORDER BY updated_at DESC,id LIMIT 2000").all(),
  db.prepare("SELECT model,content_json,publication_status FROM xuyi_product_content WHERE publication_status='published' ORDER BY model").all()
 ]);
 const extra=(products.results||[]).filter(x=>{try{return JSON.parse(x.content_json)?.newProduct===true}catch{return false}}).map(x=>x.model);
 return json({models:[...new Set([...MANAGED_MODELS,...extra])].sort(),
  items:(rows.results||[]).map(r=>({id:r.id,model:r.model,rating:r.rating,author:r.author,reviewDate:r.review_date,content:r.content,status:r.status,updatedAt:r.updated_at}))});
}
export async function onRequestPost(c){
 const denied=await authorized(c);if(denied)return denied;
 let input;try{input=await c.request.json()}catch{return json({error:"Invalid JSON"},400)}
 const db=c.env.LEYA_DB;await ensureProductReviews(db);
 const action=String(input?.action||"");
 if(action==="delete"){
  const id=String(input?.id||"");
  if(!/^[0-9a-f-]{36}$/i.test(id))return json({error:"Invalid review ID"},400);
  const result=await db.prepare("DELETE FROM xuyi_product_reviews WHERE id=?").bind(id).run();
  if(!result.meta?.changes)return json({error:"Review not found"},404);
  const revision=await bumpPublishRevision(db);
  return json({deleted:true,id,...revision});
 }
 if(action!=="save")return json({error:"Unknown action"},400);
 let review;try{review=normalizeProductReview(input)}catch(e){return json({error:String(e.message||e)},400)}
 if(!(await knownModel(db,review.model)))return json({error:"型号必须属于已确认的 LEYA MOULD 模具目录"},400);
 const id=input?.id?String(input.id):crypto.randomUUID();
 if(!/^[0-9a-f-]{36}$/i.test(id))return json({error:"Invalid review ID"},400);
 if(input.id&&!await db.prepare("SELECT id FROM xuyi_product_reviews WHERE id=?").bind(id).first())
   return json({error:"Review not found"},404);
 const sql=[
  "INSERT INTO xuyi_product_reviews",
  "(id,model,rating,author,review_date,content,status,updated_at)",
  "VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)",
  "ON CONFLICT(id) DO UPDATE SET model=excluded.model,rating=excluded.rating,",
  "author=excluded.author,review_date=excluded.review_date,content=excluded.content,",
  "status=excluded.status,updated_at=CURRENT_TIMESTAMP"
 ].join(" ");
 await db.prepare(sql).bind(id,review.model,review.rating,review.author,review.reviewDate,review.content,review.status).run();
 const revision=await bumpPublishRevision(db);
 return json({saved:true,id,model:review.model,status:review.status,...revision});
}

