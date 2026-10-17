import { clean, emailRe, ensureFormSchema, isInquiryFormReady, sendSubmissionNotification } from "../_shared/forms.js";
import { defaultContactConfig, loadSiteSetting, normalizeContactConfig, selectExternalContact } from "../_shared/site-settings.js";

function response(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "cache-control": "no-store",
      "x-robots-tag": "noindex, nofollow, noarchive"
    }
  });
}

function normalizePayload(payload) {
  const fields = payload?.fields && typeof payload.fields === "object" ? payload.fields : {};
  const pick = (...names) => {
    for (const name of names) {
      const value = payload?.[name] ?? fields?.[name];
      if (value != null && String(value).trim()) return String(value);
    }
    return "";
  };
  return {
    source: clean(pick("source", "formSource") || "website-form", 120),
    pageUrl: clean(pick("pageUrl", "page_url"), 1500),
    locale: clean(pick("locale") || "en", 16).toLowerCase(),
    region: clean(pick("region", "country", "market"), 120).toLowerCase(),
    name: clean(pick("name", "author"), 200),
    email: clean(pick("email"), 320).toLowerCase(),
    phone: clean(pick("phone", "whatsapp", "tel", "telephone"), 120),
    company: clean(pick("company", "organization"), 300),
    brand: clean(pick("brand"), 200),
    reference: clean(pick("reference", "model", "part", "part_number", "partNo"), 300),
    requirements: clean(pick("requirements", "message", "comment"), 10000),
    equipment: clean(pick("equipment", "application"), 2000),
    honeypot: clean(pick("website", "homepage", "url"), 500),
    consent: payload?.consent === true || fields?.consent === true,
    fields
  };
}

export async function onRequestPost(context) {
  const db = context.env.XUYI_DB;
  if (!db) return response({ error: "Form storage is unavailable" }, 503);
  const contentLength = Number(context.request.headers.get("content-length") || 0);
  if (contentLength > 65536) return response({ error: "Form payload is too large" }, 413);
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid form payload" }, 400); }
  const data = normalizePayload(payload);
  if (data.honeypot) return response({ ok: true, saved: false });
  if (!data.consent) return response({ error: "Please accept the privacy policy" }, 400);
  if (data.email && !emailRe.test(data.email)) return response({ error: "Please enter a valid email address" }, 400);
  if (!data.email && !data.phone) return response({ error: "Please provide an email or phone number" }, 400);
  if (!data.reference && !data.requirements && !data.equipment) return response({ error: "Please describe the bottle model or order requirements" }, 400);
  if (!(await isInquiryFormReady(db, context.env))) {
    return response({ error: "Online enquiries are temporarily unavailable. Please contact us by email or WhatsApp." }, 503);
  }
  await ensureFormSchema(db);

  const ip = clean(context.request.headers.get("cf-connecting-ip"), 100);
  const userAgent = clean(context.request.headers.get("user-agent"), 800);
  if (ip) {
    const recent = await db.prepare(`SELECT COUNT(*) AS c FROM form_submissions
      WHERE ip=? AND created_at >= datetime('now','-10 minutes')`).bind(ip).first();
    if (Number(recent?.c || 0) >= 8) return response({ error: "Too many submissions. Please try again later." }, 429);
  }
  if (ip && (data.email || data.reference)) {
    const duplicate = await db.prepare(`SELECT id FROM form_submissions
      WHERE ip=? AND email=? AND reference=? AND created_at >= datetime('now','-2 minutes')
      ORDER BY created_at DESC LIMIT 1`).bind(ip, data.email, data.reference).first();
    if (duplicate?.id) return response({ ok: true, saved: true, id: duplicate.id, duplicate: true });
  }

  const id = "inq_" + Date.now().toString(36) + "_" + crypto.randomUUID().replace(/-/g, "").slice(0, 12);
  const safeFields = { privacy_consent: "accepted" };
  for (const [key, value] of Object.entries(data.fields || {})) {
    if (Object.keys(safeFields).length >= 40) break;
    if (!/^[A-Za-z0-9_.-]{1,80}$/.test(key)) continue;
    if (["website", "homepage", "url"].includes(key)) continue;
    safeFields[key] = clean(value, 2000);
  }
  const pageUrl = data.pageUrl || context.request.headers.get("referer") || "";
  const brandStored = { config: {} };
  const contactStored = await loadSiteSetting(db, "contact_config", defaultContactConfig(brandStored?.config || {}));
  const contactConfig = normalizeContactConfig(contactStored.value, brandStored?.config || {});
  const assignedContact = selectExternalContact(contactConfig, { locale: data.locale, region: data.region });
  await db.prepare(`INSERT INTO form_submissions
    (id,source,page_url,locale,region,name,email,phone,company,brand,reference,requirements,equipment,fields_json,ip,user_agent,
     assigned_contact_id,assigned_contact_name,assigned_contact_email,smtp_status)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pending')`)
    .bind(
      id, data.source, clean(pageUrl, 1500), data.locale || "en", data.region, data.name, data.email, data.phone,
      data.company, data.brand, data.reference, data.requirements, data.equipment,
      JSON.stringify(safeFields), ip, userAgent,
      assignedContact?.id || "", assignedContact?.name || "", assignedContact?.email || ""
    ).run();

  const submission = {
    id, created_at: new Date().toISOString(), source: data.source, page_url: clean(pageUrl, 1500),
    locale: data.locale, region: data.region, name: data.name, email: data.email, phone: data.phone, company: data.company,
    brand: data.brand, reference: data.reference, requirements: data.requirements, equipment: data.equipment,
    assigned_contact_id: assignedContact?.id || "",
    assigned_contact_name: assignedContact?.name || "",
    assigned_contact_email: assignedContact?.email || ""
  };
  const task = sendSubmissionNotification(db, context.env, submission).catch(() => null);
  if (context.waitUntil) context.waitUntil(task); else await task;
  return response({ ok: true, saved: true, id, notification: "queued", assignedContactId: assignedContact?.id || "" }, 201);
}
