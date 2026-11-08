import { blogCard, blogHtml, listBlogPosts, sortLocalizedBlogIndexByD1Order } from "./blog-cms.js";
import {
  bumpPublishRevision,
  defaultLanguageConfig,
  defaultTranslationConfig,
  loadSiteSetting,
  normalizeLanguageConfig,
  normalizeTranslationConfig
} from "./site-settings.js";

const clean = (value, max = 12000) => String(value ?? "").replace(/\0/g, "").trim().slice(0, max);
const json = (value, fallback) => {
  try { return typeof value === "string" ? JSON.parse(value || JSON.stringify(fallback)) : (value ?? fallback); }
  catch { return fallback; }
};

export const TRANSLATION_SCHEMA = [
  `CREATE TABLE IF NOT EXISTS xuyi_translation_sources (
    resource_id TEXT PRIMARY KEY, resource_type TEXT NOT NULL DEFAULT 'product',
    source_locale TEXT NOT NULL DEFAULT 'en', source_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`,
  `CREATE TABLE IF NOT EXISTS xuyi_translation_overrides (
    resource_id TEXT NOT NULL, locale TEXT NOT NULL,
    translated_json TEXT NOT NULL DEFAULT '{}',
    reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(resource_id,locale)
  )`,
    `CREATE TABLE IF NOT EXISTS translation_jobs (
    id TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL DEFAULT 'product',
    resource_id TEXT NOT NULL,
    source_locale TEXT NOT NULL,
    target_locale TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    source_json TEXT NOT NULL DEFAULT '{}',
    translated_json TEXT NOT NULL DEFAULT '{}',
    provider TEXT NOT NULL DEFAULT 'manual',
    status TEXT NOT NULL DEFAULT 'queued'
      CHECK (status IN ('queued','translating','review','approved','error','stale')),
    error_message TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TEXT,
    UNIQUE(resource_type, resource_id, source_locale, target_locale)
  )`,
  `CREATE INDEX IF NOT EXISTS idx_translation_jobs_status ON translation_jobs(status, updated_at DESC)`,
  `CREATE INDEX IF NOT EXISTS idx_translation_jobs_resource ON translation_jobs(resource_type, resource_id)`
];

export async function ensureTranslationSchema(db) {
  for (const sql of TRANSLATION_SCHEMA) await db.prepare(sql).run();
}

async function sha256(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function languageAndTranslationSettings(db) {
  const languageRaw = await loadSiteSetting(db, "language_config", defaultLanguageConfig());
  const languages = normalizeLanguageConfig(languageRaw.value);
  const translationRaw = await loadSiteSetting(db, "translation_config", defaultTranslationConfig());
  const translation = normalizeTranslationConfig(translationRaw.value, languages);
  return { languages, translation };
}

export async function readModelLocalePayload(db, id, locale) {
  await ensureTranslationSchema(db);
  const override = await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id=? AND locale=?").bind(id,locale).first();
  if (override) return json(override.translated_json,{});
  const source = await db.prepare("SELECT source_json FROM xuyi_translation_sources WHERE resource_id=?").bind(id).first();
  return source ? json(source.source_json,{}) : null;
}
export async function queueModelTranslationJobs(db, modelId, { force = false } = {}) {
  await ensureTranslationSchema(db);
  const model = await db.prepare("SELECT resource_id,source_json FROM xuyi_translation_sources WHERE resource_id=?").bind(modelId).first();
  if (!model) throw new Error("XUYI product source not found in D1. Import product sources first.");
  const { languages, translation } = await languageAndTranslationSettings(db);
  if (!translation.autoQueue && !force) return { queued: 0, skipped: true };
  const sourceLocale = translation.sourceLocale;
  const sourcePayload = json(model.source_json,{});
  const sourceJson = JSON.stringify(sourcePayload);
  const sourceHash = await sha256(sourceJson);
  let queued = 0;
  for (const target of languages.languages.filter(item => item.enabled && item.code !== sourceLocale)) {
    const id = "tr_" + (await sha256("product|" + modelId + "|" + sourceLocale + "|" + target.code)).slice(0, 24);
    const existing = await db.prepare("SELECT source_hash,status FROM translation_jobs WHERE id=?").bind(id).first();
    if (existing?.source_hash === sourceHash && !force) continue;
    await db.prepare(`INSERT INTO translation_jobs
      (id,resource_type,resource_id,source_locale,target_locale,source_hash,source_json,translated_json,provider,status,error_message,updated_at)
      VALUES (?,'product',?,?,?,?,?,'{}',?,'queued','',CURRENT_TIMESTAMP)
      ON CONFLICT(id) DO UPDATE SET source_hash=excluded.source_hash,source_json=excluded.source_json,
      translated_json='{}',provider=excluded.provider,status='queued',error_message='',updated_at=CURRENT_TIMESTAMP,reviewed_at=NULL`)
      .bind(id,modelId,sourceLocale,target.code,sourceHash,sourceJson,translation.provider).run();
    queued++;
  }
  return { queued,sourceLocale,model:sourcePayload?.localization?.name||modelId };
}

export async function queueBlogTranslationJobs(db, slug, { force = false } = {}) {
  await ensureTranslationSchema(db);
  const blogSlug = clean(slug, 140).toLowerCase();
  if (!/^[a-z0-9](?:[a-z0-9-]{1,118}[a-z0-9])?$/.test(blogSlug)) throw new Error("Invalid Blog slug");
  const row = await db.prepare("SELECT status,content_json FROM xuyi_blog_posts WHERE slug=?").bind(blogSlug).first();
  if (!row) throw new Error("Blog article not found in D1");
  if (row.status !== "published") throw new Error("Only a published Blog article can enter the translation workflow");
  let post; try { post = JSON.parse(row.content_json || "{}"); } catch { throw new Error("Blog source JSON is invalid"); }
  const resourceId = "page:/blog/" + blogSlug + "/";
  const sourcePayload = { title: String(post.title || ""), description: String(post.description || ""), mainHtml: blogHtml({ ...post, slug: blogSlug }), indexCardHtml: blogCard({ ...post, slug: blogSlug }) };
  if (sourcePayload.title.length < 12 || sourcePayload.description.length < 25 || sourcePayload.mainHtml.length < 1000) {
    throw new Error("Published Blog source is incomplete");
  }
  const { languages, translation } = await languageAndTranslationSettings(db);
  if (!translation.autoQueue && !force) return { queued: 0, skipped: true };
  const sourceLocale = translation.sourceLocale;
  const sourceJson = JSON.stringify(sourcePayload);
  const sourceHash = await sha256(sourceJson);
  let queued = 0;
  for (const target of languages.languages.filter(item => item.enabled && item.code !== sourceLocale)) {
    const id = "tr_" + (await sha256("blog|" + resourceId + "|" + sourceLocale + "|" + target.code)).slice(0, 24);
    const existing = await db.prepare("SELECT source_hash FROM translation_jobs WHERE id=?").bind(id).first();
    if (existing?.source_hash === sourceHash && !force) continue;
    await db.prepare("INSERT INTO translation_jobs (id,resource_type,resource_id,source_locale,target_locale,source_hash,source_json,translated_json,provider,status,error_message,updated_at) VALUES (?,'blog',?,?,?,?,?,'{}',?,'queued','',CURRENT_TIMESTAMP) ON CONFLICT(id) DO UPDATE SET source_hash=excluded.source_hash,source_json=excluded.source_json,translated_json='{}',provider=excluded.provider,status='queued',error_message='',updated_at=CURRENT_TIMESTAMP,reviewed_at=NULL")
      .bind(id,resourceId,sourceLocale,target.code,sourceHash,sourceJson,translation.provider).run();
    queued++;
  }
  return { queued, sourceLocale, slug: blogSlug };
}
export async function machineTranslatePayload() {
  throw new Error("外部自动翻译接口已按项目费用规则关闭；请由人工或当前 AI 会话生成草稿后粘贴到翻译任务，再审核入库");
}

export async function applyTranslationOverride(db, job, translatedPayload) {
  await ensureTranslationSchema(db);
  const payload = translatedPayload && typeof translatedPayload === "object" ? translatedPayload : {};
  const resourceId = String(job?.resource_id || "");
  const isBlog = job?.resource_type === "blog" || /^page:\/blog\/[a-z0-9][a-z0-9-]{1,119}\/$/.test(resourceId);
  let blogIndexJson = "", blogIndexOriginalJson = "";
  if (isBlog) {
    const title = String(payload.title || "").trim();
    const description = String(payload.description || "").trim();
    const mainHtml = String(payload.mainHtml || "");
    const blocked = /<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i;
    if (title.length < 12 || description.length < 25 || mainHtml.length < 1000 || mainHtml.length > 250000 || blocked.test(mainHtml)) {
      throw new Error("Approved Blog translation is incomplete or contains unsafe HTML");
    }
    const match=/^page:\/blog\/([a-z0-9][a-z0-9-]{1,119})\/$/.exec(resourceId);
    if (!match) throw new Error("Invalid Blog translation resource");
    const sourceRow=await db.prepare("SELECT content_json FROM xuyi_blog_posts WHERE slug=? AND status='published'").bind(match[1]).first();
    let sourcePost;try{sourcePost=JSON.parse(sourceRow?.content_json||"")}catch{throw new Error("Published D1 Blog source JSON is invalid");}
    const indexRow=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id='page:/blog/' AND locale=?").bind(job.target_locale).first();
    if(!indexRow?.translated_json)throw new Error("Target language Blog index is not initialized");
    blogIndexOriginalJson=indexRow.translated_json;
    let index;try{index=JSON.parse(indexRow.translated_json)}catch{throw new Error("Target language Blog index JSON is invalid");}
    const slug=match[1],translatedCard=String(payload.indexCardHtml||"").trim(),fallbackCard=blogCard({...sourcePost,slug,title,description}),card=translatedCard||fallbackCard;
    const count=(value,needle)=>String(value).split(needle).length-1;
    if(!card.startsWith('<article class="news-card">')||!card.endsWith("</article>")||blocked.test(card)||count(card,'href="/blog/'+slug+'/"')!==3)throw new Error("Approved Blog translation card is invalid");
    const cardRe=/<article class="news-card">[\s\S]*?<\/article>/g;
    const current=String(index.mainHtml||""),cards=[...current.matchAll(cardRe)],matched=cards.filter(item=>[...item[0].matchAll(/href="([^"]+)"/g)].some(match=>{
      const parts=String(match[1]||"").split("?")[0].split("/").filter(Boolean);
      return ((parts.length===2&&parts[0]==="blog")||(parts.length===3&&parts[1]==="blog"))&&parts[parts.length-1]===slug;
    }));
    if(matched.length>1)throw new Error("Target language Blog index contains duplicate cards");
    let nextIndex=current;
    if(matched.length===1){
      const oldCard=matched[0][0];
      const updatedCard=translatedCard?card:oldCard.replace(/(<h3><a[^>]*>)[\s\S]*?(<\/a><\/h3>)/i,"$1"+title.replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))+"$2").replace(/(<p>)[\s\S]*?(<\/p>)/i,"$1"+description.replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))+"$2");
      nextIndex=current.replace(oldCard,updatedCard);
    }else{
      const tail="</div></div></section>";
      if(!current.endsWith(tail))throw new Error("Target language Blog index has an unexpected structure");
      nextIndex=current.slice(0,-tail.length)+card+tail;
    }
    const d1Order=(await listBlogPosts(db,"published")).map(post=>post.slug);
    if(!d1Order.includes(slug))throw new Error("Published D1 Blog order does not contain this article");
    let ordered;try{ordered=sortLocalizedBlogIndexByD1Order(nextIndex,d1Order)}catch(error){throw new Error("Target language Blog index failed D1 order validation: "+String(error.message||error));}
    blogIndexJson=JSON.stringify({...index,mainHtml:ordered});
  } else if (!payload.localization || !String(payload.localization.name||"").trim()) {
    throw new Error("Approved XUYI translation requires localization.name");
  }
  const reviewedAt = new Date().toISOString();
  let blogIndexStatementIndex=-1;
  const statements=[db.prepare("INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at) VALUES (?,?,?,?) ON CONFLICT(resource_id,locale) DO UPDATE SET translated_json=excluded.translated_json,reviewed_at=excluded.reviewed_at").bind(job.resource_id,job.target_locale,JSON.stringify(payload),reviewedAt)];
  if(blogIndexJson){
    statements.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=? WHERE resource_id='page:/blog/' AND locale=? AND translated_json=?").bind(blogIndexJson,reviewedAt,job.target_locale,blogIndexOriginalJson));
    blogIndexStatementIndex=statements.length-1;
  }
  statements.push(db.prepare("UPDATE translation_jobs SET translated_json=?,status='approved',reviewed_at=?,updated_at=CURRENT_TIMESTAMP,error_message='' WHERE id=?").bind(JSON.stringify(payload),reviewedAt,job.id));
  const results=await db.batch(statements);
  if(blogIndexStatementIndex>=0&&Number(results[blogIndexStatementIndex]?.meta?.changes||0)!==1)
    throw new Error("Target language Blog index changed during translation approval; no overwrite was applied");
  return bumpPublishRevision(db);
}
async function processQueuedTranslationJobs(db, resourceType, resourceId, env, limit = 12) {
  await ensureTranslationSchema(db);
  const { translation } = await languageAndTranslationSettings(db);
  if (!translation.autoTranslate || translation.provider === "manual") {
    return { attempted: 0, completed: 0, review: 0, errors: 0, skipped: true };
  }
  const rows = await db.prepare("SELECT * FROM translation_jobs WHERE resource_type=? AND resource_id=? AND status='queued' ORDER BY target_locale LIMIT ?")
    .bind(resourceType, resourceId, Math.max(1, Math.min(30, Number(limit) || 12))).all();
  let completed = 0, review = 0, errors = 0;
  for (const job of rows.results || []) {
    await db.prepare("UPDATE translation_jobs SET status='translating',provider=?,error_message='',updated_at=CURRENT_TIMESTAMP WHERE id=?")
      .bind(translation.provider, job.id).run();
    try {
      const source = JSON.parse(job.source_json || "{}");
      const translated = await machineTranslatePayload(source, job.source_locale, job.target_locale, translation, env);
      if (translation.requireHumanReview) {
        await db.prepare("UPDATE translation_jobs SET translated_json=?,status='review',provider=?,updated_at=CURRENT_TIMESTAMP WHERE id=?")
          .bind(JSON.stringify(translated), translation.provider, job.id).run();
        review++;
      } else {
        await applyTranslationOverride(db, job, translated);
        completed++;
      }
    } catch (error) {
      errors++;
      await db.prepare("UPDATE translation_jobs SET status='error',error_message=?,updated_at=CURRENT_TIMESTAMP WHERE id=?")
        .bind(clean(error?.message || error, 2000), job.id).run();
    }
  }
  return { attempted: (rows.results || []).length, completed, review, errors, skipped: false };
}

export async function autoTranslateQueuedModelJobs(db, modelId, env, limit = 12) {
  return processQueuedTranslationJobs(db, "product", modelId, env, limit);
}

export async function autoTranslateQueuedBlogJobs(db, slug, env, limit = 12) {
  const blogSlug = clean(slug, 140).toLowerCase();
  if (!/^[a-z0-9](?:[a-z0-9-]{1,118}[a-z0-9])?$/.test(blogSlug)) throw new Error("Invalid Blog slug");
  return processQueuedTranslationJobs(db, "blog", "page:/blog/" + blogSlug + "/", env, limit);
}

export { languageAndTranslationSettings, json };
