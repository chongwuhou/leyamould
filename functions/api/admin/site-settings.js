import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import {
  bumpPublishRevision,
  defaultContactConfig,
  defaultLanguageConfig,
  defaultTranslationConfig,
  loadSiteSetting,
  normalizeContactConfig,
  normalizeLanguageConfig,
  normalizeTranslationConfig,
  saveSiteSetting
} from "../../_shared/site-settings.js";

const clean = (value) => String(value ?? "").trim();

function response(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "cache-control": "no-store",
      "x-robots-tag": "noindex, nofollow, noarchive"
    }
  });
}

async function currentSettings(db, env) {
  const brand = { config: {} };
  const languageRaw = await loadSiteSetting(db, "language_config", defaultLanguageConfig());
  const languages = normalizeLanguageConfig(languageRaw.value);
  const contactRaw = await loadSiteSetting(db, "contact_config", defaultContactConfig(brand?.config || {}));
  const contacts = normalizeContactConfig(contactRaw.value, brand?.config || {});
  const translationRaw = await loadSiteSetting(db, "translation_config", defaultTranslationConfig());
  const translation = normalizeTranslationConfig(translationRaw.value, languages);
  return {
    languages,
    contacts,
    translation,
    updatedAt: {
      languages: languageRaw.updatedAt,
      contacts: contactRaw.updatedAt,
      translation: translationRaw.updatedAt
    },
    translationSecrets: {
      googleCloudTranslation: Boolean(clean(env.GOOGLE_TRANSLATE_API_KEY)),
      deepl: Boolean(clean(env.DEEPL_API_KEY)),
      openaiCompatible: Boolean(clean(env.TRANSLATION_API_KEY))
    }
  };
}

export async function onRequestGet(context) {
  if (!clean(context.env.ADMIN_TOKEN)) return response({ error: "ADMIN_TOKEN is not configured" }, 503);
  if (!(await authorizedBuildRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401);
  const db = context.env.LEYA_DB;
  if (!db) return response({ error: "LEYA_DB binding missing" }, 503);
  try {
    return response(await currentSettings(db, context.env));
  } catch (error) {
    return response({ error: clean(error?.message || error) }, 400);
  }
}

export async function onRequestPost(context) {
  if (!clean(context.env.ADMIN_TOKEN)) return response({ error: "ADMIN_TOKEN is not configured" }, 503);
  if (!(await authorizedBuildRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401);
  const db = context.env.LEYA_DB;
  if (!db) return response({ error: "LEYA_DB binding missing" }, 503);
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid JSON" }, 400); }
  try {
    const brand = { config: {} };
    const current = await currentSettings(db, context.env);
    const action = clean(payload.action);
    if (action === "save_languages") {
      const languages = normalizeLanguageConfig(payload.config);
      // The current root URL and CMS source are English. Changing them needs
      // a separate canonical/redirect migration, not a language checkbox.
      if(languages.defaultLocale!=="en"||languages.sourceLocale!=="en")
        throw new Error("LEYA default/source language is English. Changing it requires a separate SEO URL migration.");
      const enabled = languages.languages.filter((item) => item.enabled && item.publishReady);
      if (!enabled.length) throw new Error("At least one enabled publish-ready language is required");
      await saveSiteSetting(db, "language_config", languages);
      const translation = normalizeTranslationConfig({ ...current.translation, sourceLocale: languages.sourceLocale }, languages);
      await saveSiteSetting(db, "translation_config", translation);
      const revision = await bumpPublishRevision(db);
      return response({ saved: true, config: languages, ...revision });
    }
    if (action === "save_contacts") {
      const contacts = normalizeContactConfig(payload.config, brand?.config || {});
      await saveSiteSetting(db, "contact_config", contacts);
      const revision = await bumpPublishRevision(db);
      return response({ saved: true, config: contacts, ...revision });
    }
    if (action === "save_translation") {
      const translation = normalizeTranslationConfig(payload.config, current.languages);
      await saveSiteSetting(db, "translation_config", translation);
      return response({ saved: true, config: translation });
    }
    return response({ error: "Unknown action" }, 400);
  } catch (error) {
    return response({ error: clean(error?.message || error) }, 400);
  }
}
