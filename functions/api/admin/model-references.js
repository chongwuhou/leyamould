// Reviewed mould-model reference catalogue backed by LEYA D1.
//
// These records are intentionally separate from the category/product CMS:
// they describe an imported reference model, not an unverified LEYA claim.
// Draft rows may be prepared before their compressed R2 image is uploaded;
// only R2-backed rows can be published into the build snapshot.
import {authorizeAdminRequest} from "../../_shared/admin-security.js";
import {bumpPublishRevision,loadLanguageConfig,publicLanguages} from "../../_shared/site-settings.js";
import {imageKey} from "../../_shared/r2-usage.js";
import {isMouldModel} from "../../_shared/mould-routes.js";

const respond=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
const clean=(value,max=500)=>String(value??"").trim().slice(0,max);
const MODEL_FAMILIES=new Set([
  "general-cap-mould","mineral-water-closure-cap-molds","five-gallon-water-cap-mould",
  "oil-bottle-cap-mould","flip-top-caps-mould","engine-oil-cap-mould",
  "food-packaging-cap-mould","medical-cap-mould","personal-care-cap-mould",
  "functional-cap-mould","plastic-handle-cap-mould","wine-cap-mould",
  "pet-preform-mould","blow-bottle-mould"
]);
const SLUG=/^[a-z0-9][a-z0-9-]{1,139}$/;
const IMAGE_PATH=/^\/(?:media|assets)\/[a-z0-9/_-]+\.(?:png|jpg|jpeg|webp)$/i;

async function ensure(db){
  await db.prepare(`CREATE TABLE IF NOT EXISTS leya_model_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    family TEXT NOT NULL,
    title TEXT NOT NULL,
    alt TEXT NOT NULL,
    source_url TEXT NOT NULL DEFAULT '',
    source_image TEXT NOT NULL DEFAULT '',
    image_path TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    translations_json TEXT NOT NULL DEFAULT '{}',
    pdf_url TEXT NOT NULL DEFAULT '',
    pdf_sha256 TEXT NOT NULL DEFAULT '',
    pdf_pages INTEGER NOT NULL DEFAULT 0,
    publication_status TEXT NOT NULL DEFAULT 'draft' CHECK(publication_status IN ('draft','published')),
    sort_order INTEGER NOT NULL DEFAULT 0,
    reviewed_at TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`).run();
  const columns=(await db.prepare("PRAGMA table_info(leya_model_references)").all()).results||[];
  if(!columns.some(row=>row.name==="pdf_url"))await db.prepare("ALTER TABLE leya_model_references ADD COLUMN pdf_url TEXT NOT NULL DEFAULT ''").run();
  if(!columns.some(row=>row.name==="pdf_sha256"))await db.prepare("ALTER TABLE leya_model_references ADD COLUMN pdf_sha256 TEXT NOT NULL DEFAULT ''").run();
  if(!columns.some(row=>row.name==="pdf_pages"))await db.prepare("ALTER TABLE leya_model_references ADD COLUMN pdf_pages INTEGER NOT NULL DEFAULT 0").run();
  await db.prepare("CREATE INDEX IF NOT EXISTS idx_leya_model_references_status ON leya_model_references(publication_status,family,sort_order,slug)").run();
}

async function guard(c){
  if(!c.env.ADMIN_TOKEN)return {error:respond({error:"Admin unavailable"},503)};
  if(!(await authorizeAdminRequest(c.request,c.env)))return {error:respond({error:"Unauthorized"},401)};
  if(!c.env.LEYA_DB)return {error:respond({error:"LEYA_DB unavailable"},503)};
  const db=c.env.LEYA_DB;await ensure(db);return {db};
}

function parseTranslations(value,locales){
  let input=value;
  if(typeof input==="string"){
    try{input=JSON.parse(input||"{}")}catch{throw Error("translations must be valid JSON")}
  }
  if(input===undefined||input===null)input={};
  if(!input||typeof input!=="object"||Array.isArray(input))throw Error("translations must be an object");
  const allowed=new Set(locales);
  const output={};
  for(const [locale,raw] of Object.entries(input)){
    if(!allowed.has(locale))throw Error("Translation locale is not publish-ready: "+locale);
    if(!raw||typeof raw!=="object"||Array.isArray(raw))throw Error("Translation content must be an object");
    const item={};
    for(const key of ["title","alt","description"]){
      if(raw[key]!==undefined&&typeof raw[key]!=="string")throw Error("Translation field must be text: "+key);
      const max=key==="description"?2000:180;
      const text=clean(raw[key],max);
      if(text)item[key]=text;
    }
    if(Object.keys(item).length)output[locale]=item;
  }
  return output;
}

async function normalized(input,db){
  const languageConfig=await loadLanguageConfig(db);
  const languages=publicLanguages(languageConfig);
  const localeCodes=languages.map(item=>item.code);
  const slug=clean(input?.slug,140).toLowerCase();
  if(!SLUG.test(slug))throw Error("Invalid model slug");
  const family=clean(input?.family,100).toLowerCase();
  if(!MODEL_FAMILIES.has(family) && !isMouldModel(family))throw Error("Choose a configured mould family");
  const title=clean(input?.title,180);
  const alt=clean(input?.alt||title,180);
  if(title.length<2||alt.length<2)throw Error("English title and ALT are required");
  const sourceUrl=clean(input?.sourceUrl||input?.source_url,500);
  const sourceImage=clean(input?.sourceImage||input?.source_image,500);
  if(sourceUrl&& !/^https:\/\//i.test(sourceUrl))throw Error("Source URL must use HTTPS");
  if(sourceImage&& !/^https:\/\//i.test(sourceImage))throw Error("Source image URL must use HTTPS");
  const imagePath=clean(input?.imagePath||input?.image||input?.image_path,300);
  if(imagePath&&!IMAGE_PATH.test(imagePath))throw Error("Image must be a LEYA /media or checked-in /assets path");
  const description=clean(input?.description,2000);
  const pdfUrl=clean(input?.pdfUrl||input?.pdf_url,500);
  if(pdfUrl && !/^\/media\/|^https:\/\//i.test(pdfUrl))throw Error("PDF must use a LEYA /media path or HTTPS URL");
  const pdfSha256=clean(input?.pdfSha256||input?.pdf_sha256,64).toLowerCase();
  if(pdfSha256 && !/^[a-f0-9]{64}$/.test(pdfSha256))throw Error("PDF SHA-256 must be 64 hexadecimal characters");
  const pdfPages=Number(input?.pdfPages??input?.pdf_pages??0);
  if(!Number.isInteger(pdfPages)||pdfPages<0||pdfPages>9999)throw Error("Invalid PDF page count");
  const status=input?.publicationStatus||input?.status||"draft";
  if(status!=="draft"&&status!=="published")throw Error("Invalid publication status");
  const sortOrder=Number(input?.sortOrder??input?.sort_order??0);
  if(!Number.isInteger(sortOrder)||sortOrder<0||sortOrder>99999)throw Error("Invalid sort order");
  const translations=parseTranslations(input?.translations??input?.translationsJson??input?.translations_json,localeCodes);
  if(pdfUrl && !pdfSha256)throw Error("PDF SHA-256 is required when a PDF is attached");
  if(pdfUrl && pdfPages<1)throw Error("PDF page count is required when a PDF is attached");
  if(status==="published"){
    if(!/^https:\/\//i.test(sourceUrl)||!/^https:\/\//i.test(sourceImage))
      throw Error("Published model references require an HTTPS source URL and source image");
    const sourceLocale=String(languageConfig.sourceLocale||"en").toLowerCase();
    for(const locale of localeCodes){
      if(locale===sourceLocale)continue;
      const localized=translations[locale];
      if(!localized?.title||!localized?.alt)
        throw Error("Published model references require reviewed "+locale+" title and ALT text");
      if(description && !localized.description)
        throw Error("Published model references require reviewed "+locale+" description");
    }
  }
  return {slug,family,title,alt,sourceUrl,sourceImage,imagePath,description,translations,pdfUrl,pdfSha256,pdfPages,status,sortOrder,reviewedAt:clean(input?.reviewedAt||input?.reviewed_at,80)};
}

async function verifyPublishedImage(c,record){
  if(!record.imagePath||!record.imagePath.startsWith("/media/"))throw Error("Published model references require an R2 /media image");
  const match=/^\/media\/([a-z]+)\/([^/?#]+)$/.exec(record.imagePath);
  if(!match||!imageKey(match[1],match[2]))throw Error("Published image is not a valid LEYA R2 object");
  if(!c.env.LEYA_ASSETS)throw Error("LEYA_ASSETS unavailable; cannot verify published image");
  if(!await c.env.LEYA_ASSETS.head(imageKey(match[1],match[2])))throw Error("Published image does not exist in LEYA R2");
}

function output(row){
  return {id:row.id,slug:row.slug,family:row.family,title:row.title,alt:row.alt,
    sourceUrl:row.source_url||"",sourceImage:row.source_image||"",imagePath:row.image_path||"",
    description:row.description||"",translations:parseStored(row.translations_json),pdfUrl:row.pdf_url||"",pdfSha256:row.pdf_sha256||"",pdfPages:Number(row.pdf_pages||0),
    publicationStatus:row.publication_status,sortOrder:Number(row.sort_order||0),
    reviewedAt:row.reviewed_at||"",updatedAt:row.updated_at||""};
}
function parseStored(value){try{const data=JSON.parse(value||"{}");return data&&typeof data==="object"&&!Array.isArray(data)?data:{};}catch{return {}}}

function reviewIssues(row,locales,sourceLocale){
  const issues=[];
  if(!/^https:\/\//i.test(String(row.source_url||"")))issues.push("source_url");
  if(!/^https:\/\//i.test(String(row.source_image||"")))issues.push("source_image");
  if(!String(row.image_path||"").startsWith("/media/"))issues.push("r2_image");
  const translations=parseStored(row.translations_json);
  for(const locale of locales){
    if(locale===sourceLocale)continue;
    const item=translations[locale];
    if(!item?.title||!item?.alt)issues.push(locale+"_title_alt");
    if(String(row.description||"").trim()&&!item?.description)issues.push(locale+"_description");
  }
  if(String(row.pdf_url||"").trim()&&(!/^[a-f0-9]{64}$/i.test(String(row.pdf_sha256||""))||Number(row.pdf_pages||0)<1))issues.push("pdf_metadata");
  return issues;
}

export async function onRequestGet(c){
  const {db,error}=await guard(c);if(error)return error;
  const rows=(await db.prepare("SELECT id,slug,family,title,alt,source_url,source_image,image_path,description,translations_json,pdf_url,pdf_sha256,pdf_pages,publication_status,sort_order,reviewed_at,updated_at FROM leya_model_references ORDER BY family,sort_order,slug LIMIT 2000").all()).results||[];
  return respond({items:rows.map(output),counts:{all:rows.length,draft:rows.filter(row=>row.publication_status==="draft").length,published:rows.filter(row=>row.publication_status==="published").length}});
}

export async function onRequestPost(c){
  const {db,error}=await guard(c);if(error)return error;
  let input;try{input=await c.request.json()}catch{return respond({error:"Invalid JSON"},400)}
  const action=input?.action||"save";
  if(action==="regrade"){
    const languageConfig=await loadLanguageConfig(db);
    const locales=publicLanguages(languageConfig).map(item=>item.code);
    const sourceLocale=String(languageConfig.sourceLocale||"en").toLowerCase();
    const rows=(await db.prepare("SELECT id,slug,source_url,source_image,image_path,description,translations_json,pdf_url,pdf_sha256,pdf_pages,publication_status FROM leya_model_references WHERE publication_status='published' ORDER BY slug LIMIT 2000").all()).results||[];
    const demoted=[],kept=[];
    for(const row of rows){
      const issues=reviewIssues(row,locales,sourceLocale);
      if(!issues.length){
        try{await verifyPublishedImage(c,{imagePath:row.image_path});kept.push(row.slug);continue}catch(error){issues.push("r2_image_missing")}
      }
      await db.prepare("UPDATE leya_model_references SET publication_status='draft',reviewed_at='',updated_at=CURRENT_TIMESTAMP WHERE id=?").bind(row.id).run();
      demoted.push({slug:row.slug,issues});
    }
    const revision=demoted.length?await bumpPublishRevision(db):{};
    return respond({regraded:true,demoted,kept,counts:{demoted:demoted.length,kept:kept.length},...revision});
  }
  if(action==="delete"){
    const slug=clean(input?.slug,140).toLowerCase();
    const row=await db.prepare("SELECT publication_status FROM leya_model_references WHERE slug=?").bind(slug).first();
    if(!row)return respond({error:"Model reference not found"},404);
    if(row.publication_status==="published")return respond({error:"Unpublish the model before deleting it"},409);
    await db.prepare("DELETE FROM leya_model_references WHERE slug=?").bind(slug).run();
    return respond({deleted:true,slug});
  }
  if(action!=="save"&&action!=="bulk_import")return respond({error:"Unknown action"},400);
  const records=action==="bulk_import"?(Array.isArray(input.items)?input.items:[]):[input.item||input];
  if(!records.length||records.length>500)return respond({error:"Provide 1-500 model reference records"},400);
  const createOnly=action==="bulk_import"?input.createOnly!==false:false;
  if(action==="bulk_import"){
    const prepared=[],existing=[],failed=[],seen=new Set();
    for(const raw of records){
      try{
        const value=await normalized(raw,db);
        if(seen.has(value.slug))throw Error("Duplicate slug in import payload");
        seen.add(value.slug);
        const prior=await db.prepare("SELECT id,publication_status FROM leya_model_references WHERE slug=?").bind(value.slug).first();
        if(prior&&createOnly){existing.push(value.slug);continue;}
        if(value.status==="published")await verifyPublishedImage(c,value);
        prepared.push(value);
      }catch(err){failed.push({slug:clean(raw?.slug,140),error:String(err?.message||err)})}
    }
    // Do not partially import a batch.  Review every rejected row first, then
    // execute all upserts as one D1 batch and bump the revision once.
    if(failed.length)return respond({error:"Bulk import aborted; no rows were written",existing,failed},400);
    if(prepared.length){
      const statements=prepared.map(value=>db.prepare(`INSERT INTO leya_model_references
        (slug,family,title,alt,source_url,source_image,image_path,description,translations_json,pdf_url,pdf_sha256,pdf_pages,publication_status,sort_order,reviewed_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
        ON CONFLICT(slug) DO UPDATE SET family=excluded.family,title=excluded.title,alt=excluded.alt,
        source_url=excluded.source_url,source_image=excluded.source_image,image_path=excluded.image_path,
        description=excluded.description,translations_json=excluded.translations_json,pdf_url=excluded.pdf_url,pdf_sha256=excluded.pdf_sha256,pdf_pages=excluded.pdf_pages,
        publication_status=excluded.publication_status,sort_order=excluded.sort_order,
        reviewed_at=excluded.reviewed_at,updated_at=CURRENT_TIMESTAMP`)
        .bind(value.slug,value.family,value.title,value.alt,value.sourceUrl,value.sourceImage,value.imagePath,
          value.description,JSON.stringify(value.translations),value.pdfUrl,value.pdfSha256,value.pdfPages,value.status,value.sortOrder,value.reviewedAt));
      try{await db.batch(statements)}catch(err){return respond({error:"Bulk import failed; database batch was not committed",detail:String(err?.message||err)},503)}
      const revision=await bumpPublishRevision(db);
      return respond({saved:prepared.map(value=>value.slug),existing,failed:[],...revision});
    }
    return respond({saved:[],existing,failed:[]});
  }
  const saved=[],existing=[],failed=[];
  for(const raw of records){
    try{
      const value=await normalized(raw,db);
      const prior=await db.prepare("SELECT id,publication_status FROM leya_model_references WHERE slug=?").bind(value.slug).first();
      if(prior&&createOnly){existing.push(value.slug);continue;}
      if(value.status==="published")await verifyPublishedImage(c,value);
      await db.prepare(`INSERT INTO leya_model_references
        (slug,family,title,alt,source_url,source_image,image_path,description,translations_json,pdf_url,pdf_sha256,pdf_pages,publication_status,sort_order,reviewed_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
        ON CONFLICT(slug) DO UPDATE SET family=excluded.family,title=excluded.title,alt=excluded.alt,
        source_url=excluded.source_url,source_image=excluded.source_image,image_path=excluded.image_path,
        description=excluded.description,translations_json=excluded.translations_json,pdf_url=excluded.pdf_url,pdf_sha256=excluded.pdf_sha256,pdf_pages=excluded.pdf_pages,
        publication_status=excluded.publication_status,sort_order=excluded.sort_order,
        reviewed_at=excluded.reviewed_at,updated_at=CURRENT_TIMESTAMP`)
        .bind(value.slug,value.family,value.title,value.alt,value.sourceUrl,value.sourceImage,value.imagePath,
          value.description,JSON.stringify(value.translations),value.pdfUrl,value.pdfSha256,value.pdfPages,value.status,value.sortOrder,value.reviewedAt).run();
      saved.push(value.slug);
    }catch(err){failed.push({slug:clean(raw?.slug,140),error:String(err?.message||err)})}
  }
  if(failed.length&&action==="save")return respond({error:failed[0].error,failed},400);
  let revision={};
  if(saved.length)revision=await bumpPublishRevision(db);
  return respond({saved,existing,failed,...revision},saved.length?200:400);
}

