import {
  defaultContactConfig,
  defaultLanguageConfig,
  loadSiteSetting,
  normalizeContactConfig,
  normalizeLanguageConfig,
  publicLanguages
} from "../_shared/site-settings.js";

export async function onRequestGet(context) {
  const db = context.env.XUYI_DB;
  if (!db) return Response.json({ error: "XUYI_DB binding missing" }, { status: 503 });
  try {
    const brand = { config: {} };
    const languageRaw = await loadSiteSetting(db, "language_config", defaultLanguageConfig());
    const languageConfig = normalizeLanguageConfig(languageRaw.value);
    const contactRaw = await loadSiteSetting(db, "contact_config", defaultContactConfig(brand?.config || {}));
    const contactConfig = normalizeContactConfig(contactRaw.value, brand?.config || {});
    return Response.json({
      source: "cloudflare-d1",
      languages: {
        defaultLocale: languageConfig.defaultLocale,
        sourceLocale: languageConfig.sourceLocale,
        items: publicLanguages(languageConfig).map((item) => ({
          code: item.code,
          displayName: item.displayName,
          nativeName: item.nativeName,
          pathPrefix: item.pathPrefix,
          sortOrder: item.sortOrder
        }))
      },
      contacts: contactConfig.contacts.filter((item) => item.enabled).map((item) => ({
        id: item.id,
        name: item.name,
        title: item.title,
        email: item.email,
        phoneDisplay: item.phoneDisplay,
        phoneE164: item.phoneE164,
        whatsappUrl: item.whatsappUrl,
        avatarUrl: item.avatarUrl,
        locales: item.locales,
        regions: item.regions,
        sortOrder: item.sortOrder,
        isDefault: item.isDefault
      }))
    }, { headers: { "cache-control": "public, max-age=60" } });
  } catch (error) {
    return Response.json({ error: String(error?.message || error) }, { status: 500 });
  }
}