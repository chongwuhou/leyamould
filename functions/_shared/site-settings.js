const clean = (value, max = 4000) => String(value ?? "").replace(/\0/g, "").trim().slice(0, max);
const emailRe = /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/;
const bcp47Re = /^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$/;
const slugRe = /^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/;
const e164Re = /^\+[1-9]\d{6,15}$/;

const BUILTIN_LANGUAGES = [
  ["en", "English", "English", "", 10],
  ["es", "Spanish", "Español", "es", 20],
  ["pt", "Portuguese", "Português", "pt", 30],
  ["ru", "Russian", "Русский", "ru", 40],
  ["tr", "Turkish", "Türkçe", "tr", 50]
];

export function defaultLanguageConfig() {
  return {
    schemaVersion: 1,
    sourceLocale: "en",
    defaultLocale: "en",
    languages: BUILTIN_LANGUAGES.map(([code, displayName, nativeName, pathPrefix, sortOrder]) => ({
      code,
      displayName,
      nativeName,
      pathPrefix,
      enabled: true,
      publishReady: code === "en",
      sortOrder,
      uiText: {}
    }))
  };
}

function normalizeLocaleCode(value) {
  const code = clean(value, 40).replaceAll("_", "-").toLowerCase();
  if (!bcp47Re.test(code)) throw new Error("Invalid BCP47 language code: " + code);
  return code;
}

export function normalizeLanguageConfig(input) {
  const raw = input && typeof input === "object" ? input : {};
  const source = Array.isArray(raw.languages) && raw.languages.length ? raw.languages : defaultLanguageConfig().languages;
  const seenCodes = new Set();
  const seenPrefixes = new Set();
  const languages = source.slice(0, 30).map((item, index) => {
    const code = normalizeLocaleCode(item?.code);
    if (seenCodes.has(code)) throw new Error("Duplicate language code: " + code);
    seenCodes.add(code);
    let pathPrefix = clean(item?.pathPrefix, 32).toLowerCase().replace(/^\/+|\/+$/g, "");
    if (pathPrefix && !slugRe.test(pathPrefix)) throw new Error("Invalid language URL prefix: " + pathPrefix);
    if (pathPrefix) {
      if (seenPrefixes.has(pathPrefix)) throw new Error("Duplicate language URL prefix: " + pathPrefix);
      seenPrefixes.add(pathPrefix);
    }
    const uiText = item?.uiText && typeof item.uiText === "object" && !Array.isArray(item.uiText) ? item.uiText : {};
    return {
      code,
      displayName: clean(item?.displayName, 120) || code,
      nativeName: clean(item?.nativeName, 120) || clean(item?.displayName, 120) || code,
      pathPrefix,
      enabled: item?.enabled !== false,
      publishReady: item?.publishReady !== false,
      sortOrder: Number.isFinite(Number(item?.sortOrder)) ? Number(item.sortOrder) : (index + 1) * 10,
      uiText
    };
  }).sort((a, b) => a.sortOrder - b.sortOrder || a.code.localeCompare(b.code));
  if (!languages.length) throw new Error("At least one language is required");
  const defaultLocale = normalizeLocaleCode(raw.defaultLocale || "en");
  const sourceLocale = normalizeLocaleCode(raw.sourceLocale || defaultLocale);
  const defaultItem = languages.find((item) => item.code === defaultLocale);
  if (!defaultItem) throw new Error("Default language is not in the language list");
  if (!defaultItem.enabled || !defaultItem.publishReady) throw new Error("Default language must be enabled and publish-ready");
  if (!languages.some((item) => item.code === sourceLocale)) throw new Error("Source language is not in the language list");
  defaultItem.pathPrefix = "";
  for (const item of languages) {
    if (item.code !== defaultLocale && !item.pathPrefix) item.pathPrefix = item.code.toLowerCase();
  }
  return { schemaVersion: 1, sourceLocale, defaultLocale, languages };
}

export function publicLanguages(config) {
  const normalized = normalizeLanguageConfig(config);
  return normalized.languages.filter((item) => item.enabled && item.publishReady);
}

// Runtime consumers must read the enabled/publish-ready language registry from
// D1. Keep the built-in list only as a first-install fallback; it is never the
// authority once language_config exists in site_state.
export async function loadLanguageConfig(db) {
  const raw = await loadSiteSetting(db, "language_config", defaultLanguageConfig());
  return normalizeLanguageConfig(raw.value);
}

export async function publishableLanguageCodes(db, { excludeSource = false } = {}) {
  const config = await loadLanguageConfig(db);
  return publicLanguages(config)
    .filter((item) => !excludeSource || item.code !== config.sourceLocale)
    .map((item) => item.code);
}

export function defaultContactConfig(brandConfig = {}) {
  const contact = brandConfig?.contact || {};
  return {
    schemaVersion: 1,
    contacts: [{
      id: "default-sales",
      name: "Sales Team",
      title: "International Sales",
      email: clean(contact.email, 320) || "Janey@xuyibottles.com",
      phoneDisplay: clean(contact.phoneDisplay, 80),
      phoneE164: clean(contact.phoneE164, 40) || "+8615395897937",
      whatsappUrl: clean(contact.whatsappShortUrl || contact.whatsappUrl, 1000) || "https://wa.me/8615395897937",
      avatarUrl: "",
      locales: [],
      regions: [],
      sortOrder: 10,
      enabled: true,
      isDefault: true
    }]
  };
}

export function normalizeContactConfig(input, brandConfig = {}) {
  const raw = input && typeof input === "object" ? input : {};
  const source = Array.isArray(raw.contacts) && raw.contacts.length ? raw.contacts : defaultContactConfig(brandConfig).contacts;
  const ids = new Set();
  const contacts = source.slice(0, 50).map((item, index) => {
    const id = clean(item?.id, 80).toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^-|-$/g, "");
    if (!id) throw new Error("Contact ID is required");
    if (ids.has(id)) throw new Error("Duplicate contact ID: " + id);
    ids.add(id);
    const email = clean(item?.email, 320);
    if (email && !emailRe.test(email)) throw new Error("Invalid contact email: " + id);
    const phoneE164 = clean(item?.phoneE164, 40);
    if (phoneE164 && !e164Re.test(phoneE164)) throw new Error("Invalid E.164 phone for contact: " + id);
    const whatsappUrl = clean(item?.whatsappUrl, 1000);
    if (whatsappUrl && !/^https:\/\//i.test(whatsappUrl)) throw new Error("WhatsApp URL must use HTTPS: " + id);
    const avatarUrl = clean(item?.avatarUrl, 1000);
    if (avatarUrl && !avatarUrl.startsWith("/") && !/^https:\/\//i.test(avatarUrl)) throw new Error("Avatar must be a site path or HTTPS URL: " + id);
    const locales = [...new Set((Array.isArray(item?.locales) ? item.locales : []).map((x) => normalizeLocaleCode(x)))];
    const regions = [...new Set((Array.isArray(item?.regions) ? item.regions : []).map((x) => clean(x, 80).toLowerCase()).filter(Boolean))];
    return {
      id,
      name: clean(item?.name, 160) || "Sales",
      title: clean(item?.title, 160),
      email,
      phoneDisplay: clean(item?.phoneDisplay, 80),
      phoneE164,
      whatsappUrl,
      avatarUrl,
      locales,
      regions,
      sortOrder: Number.isFinite(Number(item?.sortOrder)) ? Number(item.sortOrder) : (index + 1) * 10,
      enabled: item?.enabled !== false,
      isDefault: Boolean(item?.isDefault)
    };
  }).sort((a, b) => a.sortOrder - b.sortOrder || a.id.localeCompare(b.id));
  const enabled = contacts.filter((item) => item.enabled);
  if (!enabled.length) throw new Error("At least one external contact must be enabled");
  if (!enabled.some((item) => item.isDefault)) enabled[0].isDefault = true;
  let foundDefault = false;
  for (const item of contacts) {
    if (item.enabled && item.isDefault && !foundDefault) foundDefault = true;
    else if (item.isDefault) item.isDefault = false;
  }
  return { schemaVersion: 1, contacts };
}

export function selectExternalContact(config, { locale = "", region = "" } = {}) {
  const normalized = normalizeContactConfig(config);
  const candidates = normalized.contacts.filter((item) => item.enabled);
  const localeKey = clean(locale, 40).toLowerCase();
  const baseLocale = localeKey.split("-")[0];
  const regionKey = clean(region, 80).toLowerCase();
  const score = (item) => {
    let value = item.isDefault ? 1 : 0;
    if (localeKey && item.locales.includes(localeKey)) value += 100;
    else if (baseLocale && item.locales.some((code) => code.split("-")[0] === baseLocale)) value += 70;
    if (regionKey && item.regions.includes(regionKey)) value += 120;
    if (!item.locales.length && !item.regions.length) value += 5;
    return value;
  };
  return [...candidates].sort((a, b) => score(b) - score(a) || a.sortOrder - b.sortOrder)[0] || null;
}

export function defaultTranslationConfig() {
  return {
    schemaVersion: 1,
    provider: "manual",
    sourceLocale: "en",
    autoQueue: true,
    autoTranslate: false,
    model: "",
    endpoint: "",
    requireHumanReview: true
  };
}

export function normalizeTranslationConfig(input, languageConfig = defaultLanguageConfig()) {
  const raw = input && typeof input === "object" ? input : {};
  const languages = normalizeLanguageConfig(languageConfig);
  const provider = clean(raw.provider || "manual", 50).toLowerCase();
  if (!["manual","google-cloud-translation","deepl","openai-compatible"].includes(provider)) {
    throw new Error("Unsupported translation provider");
  }
  const sourceLocale = normalizeLocaleCode(raw.sourceLocale || languages.sourceLocale);
  if (!languages.languages.some((item) => item.code === sourceLocale)) throw new Error("Translation source locale is not configured");
  const endpoint = clean(raw.endpoint, 1000);
  if (endpoint && !/^https:\/\//i.test(endpoint)) throw new Error("Translation endpoint must use HTTPS");
  return {
    schemaVersion: 1,
    provider,
    sourceLocale,
    autoQueue: raw.autoQueue !== false,
    autoTranslate: Boolean(raw.autoTranslate) && provider !== "manual",
    model: clean(raw.model, 160),
    endpoint,
    requireHumanReview: raw.requireHumanReview !== false
  };
}

export async function loadSiteSetting(db, key, fallback) {
  await db.prepare(`CREATE TABLE IF NOT EXISTS site_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`).run();
  const row = await db.prepare("SELECT value,updated_at FROM site_state WHERE key=?").bind(key).first();
  if (!row?.value) return { value: fallback, updatedAt: "" };
  try { return { value: JSON.parse(row.value), updatedAt: row.updated_at || "" }; }
  catch { return { value: fallback, updatedAt: row.updated_at || "" }; }
}

export async function saveSiteSetting(db, key, value) {
  await db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES(?,?,CURRENT_TIMESTAMP)
    ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(key, JSON.stringify(value)).run();
}

export async function bumpPublishRevision(db) {
  const row = await db.prepare("SELECT value FROM site_state WHERE key='publish_revision'").first();
  const revision = Number(row?.value || 0) + 1;
  const now = new Date().toISOString();
  await db.batch([
    db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_revision',?,CURRENT_TIMESTAMP)
      ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(String(revision)),
    db.prepare(`INSERT INTO site_state(key,value,updated_at) VALUES('publish_requested_at',?,CURRENT_TIMESTAMP)
      ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP`).bind(now)
  ]);
  return { revision, requestedAt: now };
}

export { emailRe, bcp47Re, e164Re };

