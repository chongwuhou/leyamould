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
function walkStrings(value, path = [], out = []) {
  if (typeof value === "string") {
    const text = value.trim();
    if (text && !/^https?:\/\//i.test(text) && !/^[A-Z0-9][A-Z0-9._\/-]{4,}$/i.test(text)) out.push({ path, text });
    return out;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => walkStrings(item, [...path, index], out));
    return out;
  }
  if (value && typeof value === "object") {
    for (const [key, item] of Object.entries(value)) {
      if (key === "geoEntities") continue;
      walkStrings(item, [...path, key], out);
    }
  }
  return out;
}

function setPath(root, path, value) {
  let cursor = root;
  for (let i = 0; i < path.length - 1; i++) cursor = cursor[path[i]];
  cursor[path[path.length - 1]] = value;
}

async function googleTranslate(texts, source, target, apiKey, format = "text") {
  const response = await fetch("https://translation.googleapis.com/language/translate/v2?key=" + encodeURIComponent(apiKey), {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ q: texts, source, target, format: format === "html" ? "html" : "text" })
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.error?.message || "Google Translation HTTP " + response.status);
  return (data?.data?.translations || []).map((item) => String(item.translatedText || ""));
}

async function deeplTranslate(texts, source, target, apiKey, endpoint) {
  const body = new URLSearchParams();
  for (const text of texts) body.append("text", text);
  body.set("source_lang", source.split("-")[0].toUpperCase());
  body.set("target_lang", target.split("-")[0].toUpperCase());
  const response = await fetch(endpoint || "https://api-free.deepl.com/v2/translate", {
    method: "POST",
    headers: { authorization: "DeepL-Auth-Key " + apiKey, "content-type": "application/x-www-form-urlencoded" },
    body
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.message || "DeepL HTTP " + response.status);
  return (data?.translations || []).map((item) => String(item.text || ""));
}

async function openAiCompatibleTranslate(payload, source, target, apiKey, endpoint, model) {
  if (!endpoint) throw new Error("OpenAI-compatible translation endpoint is not configured");
  if (!model) throw new Error("OpenAI-compatible translation model is not configured");
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { authorization: "Bearer " + apiKey, "content-type": "application/json" },
    body: JSON.stringify({
      model,
      temperature: 0.1,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: "Translate the JSON content from " + source + " to " + target + ". Preserve JSON keys, URLs, part numbers, brand names, measurements and technical facts. Return only one JSON object with the same structure." },
        { role: "user", content: JSON.stringify(payload) }
      ]
    })
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.error?.message || "Translation provider HTTP " + response.status);
  const content = data?.choices?.[0]?.message?.content || "";
  try { return JSON.parse(content); }
  catch { throw new Error("OpenAI-compatible provider did not return valid JSON"); }
}

export async function machineTranslatePayload(payload, source, target, config, env) {
  if (config.provider === "manual") throw new Error("Translation provider is manual");
  if (config.provider === "openai-compatible") {
    const key = clean(env.TRANSLATION_API_KEY, 4000);
    if (!key) throw new Error("TRANSLATION_API_KEY Pages Secret is not configured");
    return openAiCompatibleTranslate(payload, source, target, key, config.endpoint, config.model);
  }
  const cloned = JSON.parse(JSON.stringify(payload));
  const parts = walkStrings(cloned);
  if (!parts.length) return cloned;
  const texts = parts.map((item) => item.text);
  let translated;
  if (config.provider === "google-cloud-translation") {
    const key = clean(env.GOOGLE_TRANSLATE_API_KEY, 4000);
    if (!key) throw new Error("GOOGLE_TRANSLATE_API_KEY Pages Secret is not configured");
    const format = parts.some((item) => item.path[item.path.length - 1] === "mainHtml") ? "html" : "text";
    translated = await googleTranslate(texts, source, target, key, format);
  } else if (config.provider === "deepl") {
    const key = clean(env.DEEPL_API_KEY, 4000);
    if (!key) throw new Error("DEEPL_API_KEY Pages Secret is not configured");
    translated = await deeplTranslate(texts, source, target, key, config.endpoint);
  } else {
    throw new Error("Unsupported translation provider");
  }
  if (translated.length !== parts.length) throw new Error("Translation provider returned an unexpected item count");
  translated.forEach((text, index) => setPath(cloned, parts[index].path, text));
  return cloned;
}

export async function applyTranslationOverride(db, job, translatedPayload) {
  await ensureTranslationSchema(db);
  const payload = translatedPayload && typeof translatedPayload === "object" ? translatedPayload : {};
  const resourceId = String(job?.resource_id || "");
  const isBlog = job?.resource_type === "blog" || /^page:\/blog\/[a-z0-9][a-z0-9-]{1,119}\/$/.test(resourceId);
  let blogIndexJson = "";
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
    let index;try{index=JSON.parse(indexRow.translated_json)}catch{throw new Error("Target language Blog index JSON is invalid");}
    const slug=match[1],translatedCard=String(payload.indexCardHtml||"").trim(),fallbackCard=blogCard({...sourcePost,slug,title,description}),card=translatedCard||fallbackCard;
    const count=(value,needle)=>String(value).split(needle).length-1;
    if(!card.startsWith('<article class="news-card">')||!card.endsWith("</article>")||blocked.test(card)||count(card,'href="/blog/'+slug+'/"')!==3)throw new Error("Approved Blog translation card is invalid");
    const cardRe=/<article class="news-card">[\s\S]*?<\/article>/g,linkRe=new RegExp('href="/(?:[a-z]{2}/)?blog/'+slug+'/"');
    const current=String(index.mainHtml||""),cards=[...current.matchAll(cardRe)],matched=cards.filter(item=>linkRe.test(item[0]));
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
  const statements=[db.prepare("INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at) VALUES (?,?,?,?) ON CONFLICT(resource_id,locale) DO UPDATE SET translated_json=excluded.translated_json,reviewed_at=excluded.reviewed_at").bind(job.resource_id,job.target_locale,JSON.stringify(payload),reviewedAt)];
  if(blogIndexJson)statements.push(db.prepare("INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at) VALUES ('page:/blog/',?,?,?) ON CONFLICT(resource_id,locale) DO UPDATE SET translated_json=excluded.translated_json,reviewed_at=excluded.reviewed_at").bind(job.target_locale,blogIndexJson,reviewedAt));
  statements.push(db.prepare("UPDATE translation_jobs SET translated_json=?,status='approved',reviewed_at=?,updated_at=CURRENT_TIMESTAMP,error_message='' WHERE id=?").bind(JSON.stringify(payload),reviewedAt,job.id));
  await db.batch(statements);
  return bumpPublishRevision(db);
}
export async function autoTranslateQueuedModelJobs(db, modelId, env, limit = 12) {
  await ensureTranslationSchema(db);
  const { translation } = await languageAndTranslationSettings(db);
  if (!translation.autoTranslate || translation.provider === "manual") {
    return { attempted: 0, completed: 0, review: 0, errors: 0, skipped: true };
  }
  const rows = await db.prepare(`SELECT * FROM translation_jobs
    WHERE resource_type='product' AND resource_id=? AND status='queued'
    ORDER BY target_locale LIMIT ?`).bind(modelId, Math.max(1, Math.min(30, Number(limit) || 12))).all();
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

export { languageAndTranslationSettings, json };
