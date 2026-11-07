import {
  applyTranslationOverride,
  ensureTranslationSchema,
  languageAndTranslationSettings,
  machineTranslatePayload,
  queueBlogTranslationJobs,
  queueModelTranslationJobs
} from "../../_shared/translation.js";
import { authorizedBuildRequest } from "../../_shared/build-auth.js";

const clean = (value, max = 12000) => String(value ?? "").replace(/\0/g, "").trim().slice(0, max);

function response(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store", "x-robots-tag": "noindex, nofollow, noarchive" } });
}

async function loadJob(db, id) {
  return db.prepare("SELECT * FROM translation_jobs WHERE id=?").bind(id).first();
}

export async function onRequestGet(context) {
  if (!(await authorizedBuildRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401);
  const db = context.env.XUYI_DB;
  if (!db) return response({ error: "XUYI_DB binding missing" }, 503);
  await ensureTranslationSchema(db);
  const url = new URL(context.request.url);
  const limit = Math.min(300, Math.max(10, Number(url.searchParams.get("limit")) || 100));
  const status = clean(url.searchParams.get("status"), 30);
  const query = status
    ? db.prepare("SELECT * FROM translation_jobs WHERE status=? ORDER BY updated_at DESC LIMIT ?").bind(status, limit)
    : db.prepare("SELECT * FROM translation_jobs ORDER BY updated_at DESC LIMIT ?").bind(limit);
  const jobs = await query.all();
  const settings = await languageAndTranslationSettings(db);
  return response({
    settings: settings.translation,
    languages: settings.languages,
    secretStatus: {
      googleCloudTranslation: Boolean(clean(context.env.GOOGLE_TRANSLATE_API_KEY)),
      deepl: Boolean(clean(context.env.DEEPL_API_KEY)),
      openaiCompatible: Boolean(clean(context.env.TRANSLATION_API_KEY))
    },
    jobs: (jobs.results || []).map((row) => ({
      ...row,
      source: (() => { try { return JSON.parse(row.source_json || "{}"); } catch { return {}; } })(),
      translated: (() => { try { return JSON.parse(row.translated_json || "{}"); } catch { return {}; } })()
    }))
  });
}

export async function onRequestPost(context) {
  if (!(await authorizedBuildRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401);
  const db = context.env.XUYI_DB;
  if (!db) return response({ error: "XUYI_DB binding missing" }, 503);
  await ensureTranslationSchema(db);
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid JSON" }, 400); }
  try {
    const action = clean(payload.action, 40);
    if (action === "enqueue_model") {
      return response(await queueModelTranslationJobs(db, clean(payload.modelId, 200), { force: Boolean(payload.force) }));
    }
    if (action === "enqueue_blog") {
      return response(await queueBlogTranslationJobs(db, clean(payload.slug, 140), { force: Boolean(payload.force) }));
    }
    if (action === "save_job") {
      const job = await loadJob(db, clean(payload.id, 100));
      if (!job) return response({ error: "Translation job not found" }, 404);
      const translated = payload.translated && typeof payload.translated === "object" ? payload.translated : {};
      await db.prepare("UPDATE translation_jobs SET translated_json=?,status='review',error_message='',updated_at=CURRENT_TIMESTAMP WHERE id=?")
        .bind(JSON.stringify(translated), job.id).run();
      return response({ saved: true, id: job.id, status: "review" });
    }
    if (action === "run_job") {
      const job = await loadJob(db, clean(payload.id, 100));
      if (!job) return response({ error: "Translation job not found" }, 404);
      const { translation } = await languageAndTranslationSettings(db);
      await db.prepare("UPDATE translation_jobs SET status='translating',provider=?,error_message='',updated_at=CURRENT_TIMESTAMP WHERE id=?")
        .bind(translation.provider, job.id).run();
      try {
        const source = JSON.parse(job.source_json || "{}");
        const translated = await machineTranslatePayload(source, job.source_locale, job.target_locale, translation, context.env);
        if (translation.requireHumanReview) {
          await db.prepare("UPDATE translation_jobs SET translated_json=?,status='review',provider=?,updated_at=CURRENT_TIMESTAMP WHERE id=?")
            .bind(JSON.stringify(translated), translation.provider, job.id).run();
          return response({ translated: true, id: job.id, status: "review", payload: translated });
        }
        const revision = await applyTranslationOverride(db, { ...job, provider: translation.provider }, translated);
        return response({ translated: true, approved: true, id: job.id, ...revision });
      } catch (error) {
        await db.prepare("UPDATE translation_jobs SET status='error',error_message=?,updated_at=CURRENT_TIMESTAMP WHERE id=?")
          .bind(clean(error?.message || error, 2000), job.id).run();
        throw error;
      }
    }
    if (action === "approve_job") {
      const job = await loadJob(db, clean(payload.id, 100));
      if (!job) return response({ error: "Translation job not found" }, 404);
      const translated = payload.translated && typeof payload.translated === "object"
        ? payload.translated
        : JSON.parse(job.translated_json || "{}");
      if (!translated || typeof translated !== "object") throw new Error("Translated payload is empty");
      const revision = await applyTranslationOverride(db, job, translated);
      return response({ approved: true, id: job.id, ...revision });
    }
    if (action === "requeue_job") {
      const id = clean(payload.id, 100);
      await db.prepare("UPDATE translation_jobs SET status='queued',error_message='',updated_at=CURRENT_TIMESTAMP WHERE id=?").bind(id).run();
      return response({ saved: true, id, status: "queued" });
    }
    return response({ error: "Unknown action" }, 400);
  } catch (error) {
    return response({ error: clean(error?.message || error, 2000) }, 400);
  }
}
