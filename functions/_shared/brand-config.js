const clean = (value, max = 8000) => String(value ?? "").trim().slice(0, max);
const emailRe = /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/;
const httpUrl = (value) => {
  const text = clean(value, 2000);
  if (!text) return "";
  let url;
  try { url = new URL(text); } catch { throw new Error("Invalid URL: " + text); }
  if (url.protocol !== "https:" && url.protocol !== "http:") throw new Error("Only HTTP(S) URLs are allowed");
  return url.toString();
};
const pathOrUrl = (value) => {
  const text = clean(value, 2000);
  if (!text) throw new Error("Logo path is required");
  if (text.startsWith("/")) return text;
  return httpUrl(text);
};
const object = (value) => value && typeof value === "object" && !Array.isArray(value) ? value : {};

export function normalizeBrandConfig(input) {
  const raw = object(input);
  const source = object(raw.source);
  const identity = object(raw.identity);
  const contact = object(raw.contact);
  const logos = object(raw.logos);
  const headerLogo = object(logos.header);
  const footerLogo = object(logos.footer);
  const social = object(raw.social);
  const footer = object(raw.footer);
  const seo = object(raw.seo);
  const home = object(seo.home);
  const email = object(raw.email);

  const legalName = clean(identity.legalName, 240);
  const displayName = clean(identity.displayName, 120);
  const textName = clean(identity.textName, 120) || displayName;
  const upperName = clean(identity.upperName, 120) || textName.toUpperCase();
  const filterBrandName = clean(identity.filterBrandName, 160) || displayName;
  const primaryEmail = clean(contact.email, 320);
  const phoneE164 = clean(contact.phoneE164, 40);
  if (!legalName) throw new Error("brand identity.legalName is required");
  if (!displayName) throw new Error("brand identity.displayName is required");
  if (!primaryEmail || !emailRe.test(primaryEmail)) throw new Error("brand contact.email is invalid");
  if (!/^\+[1-9]\d{6,15}$/.test(phoneE164)) throw new Error("brand contact.phoneE164 must be E.164");

  const normalizedHome = {};
  for (const [locale, value] of Object.entries(home)) {
    const item = object(value);
    normalizedHome[clean(locale, 10)] = {
      title: clean(item.title, 240),
      description: clean(item.description, 600)
    };
  }

  return {
    schemaVersion: 1,
    source: {
      mode: clean(source.mode, 160) || "cloudflare-d1-site_state.brand_config",
      verifiedFromOrigin: clean(source.verifiedFromOrigin, 1000),
      capturedAt: clean(source.capturedAt, 80),
      note: clean(source.note, 1000)
    },
    identity: {
      legalName,
      displayName,
      textName,
      upperName,
      filterBrandName,
      acronym: clean(identity.acronym, 30)
    },
    contact: {
      email: primaryEmail,
      phoneDisplay: clean(contact.phoneDisplay, 80),
      phoneDisplayLegacy: clean(contact.phoneDisplayLegacy, 80),
      phoneE164,
      whatsappUrl: httpUrl(contact.whatsappUrl),
      whatsappShortUrl: httpUrl(contact.whatsappShortUrl),
      address: clean(contact.address, 500)
    },
    logos: {
      header: { src: pathOrUrl(headerLogo.src), alt: clean(headerLogo.alt, 180) || displayName },
      footer: { src: pathOrUrl(footerLogo.src), alt: clean(footerLogo.alt, 180) || displayName }
    },
    social: {
      facebook: social.facebook ? httpUrl(social.facebook) : "",
      instagram: social.instagram ? httpUrl(social.instagram) : "",
      linkedin: social.linkedin ? httpUrl(social.linkedin) : "",
      youtube: social.youtube ? httpUrl(social.youtube) : "",
      x: social.x ? httpUrl(social.x) : ""
    },
    footer: {
      about: clean(footer.about, 4000),
      contactHeading: clean(footer.contactHeading, 120) || "Contact us",
      copyright: clean(footer.copyright, 500)
    },
    seo: { home: normalizedHome },
    email: {
      defaultFromName: clean(email.defaultFromName, 160) || (textName + " Website"),
      defaultFromPlaceholder: clean(email.defaultFromPlaceholder, 320),
      ehloDomain: clean(email.ehloDomain, 253).toLowerCase()
    }
  };
}

export function parseBrandConfig(value) {
  let parsed;
  try { parsed = typeof value === "string" ? JSON.parse(value) : value; }
  catch { throw new Error("Stored brand_config is invalid JSON"); }
  return normalizeBrandConfig(parsed);
}

export async function loadBrandConfigFromD1(db) {
  await db.prepare(`CREATE TABLE IF NOT EXISTS site_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`).run();
  const row = await db.prepare("SELECT value,updated_at FROM site_state WHERE key='brand_config'").first();
  if (!row?.value) return null;
  return { config: parseBrandConfig(row.value), updatedAt: row.updated_at || "" };
}

export function brandPublicPayload(config, updatedAt = "") {
  return {
    source: "cloudflare-d1",
    key: "site_state.brand_config",
    updatedAt,
    config: normalizeBrandConfig(config)
  };
}