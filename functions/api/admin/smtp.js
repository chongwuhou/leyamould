import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import {
  clean, encryptSetting, ensureFormSchema, loadSmtpSettings, sendSmtp, validateSmtpSettings
} from "../../_shared/forms.js";

function response(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store", "x-robots-tag": "noindex, nofollow, noarchive" } });
}

async function guard(context) {
  if (!context.env.XUYI_DB) return response({ error: "XUYI_DB binding missing" }, 503);
  if (!(await authorizedBuildRequest(context.request, context.env))) return response({ error: "Unauthorized" }, 401);
  await ensureFormSchema(context.env.XUYI_DB);
  return null;
}

export async function onRequestGet(context) {
  const denied = await guard(context);
  if (denied) return denied;
  return response({ settings: await loadSmtpSettings(context.env.XUYI_DB, context.env, false) });
}

export async function onRequestPost(context) {
  const denied = await guard(context);
  if (denied) return denied;
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid JSON" }, 400); }
  const db = context.env.XUYI_DB;
  try {
    if (payload.action === "save") {
      const existing = await loadSmtpSettings(db, context.env, false);
      const settings = validateSmtpSettings(payload.settings || {}, existing);
      const suppliedPassword = clean(payload.settings?.password, 1000);
      let encrypted = null;
      if (suppliedPassword) encrypted = await encryptSetting(suppliedPassword, context.env);
      const passwordSql = encrypted == null ? "" : ",password_ciphertext=?";
      const binds = [
        settings.enabled ? 1 : 0, settings.host, settings.port, settings.security, settings.username,
        settings.fromName, settings.fromEmail, settings.toEmails, settings.replyToMode, settings.subjectTemplate
      ];
      if (encrypted != null) binds.push(encrypted);
      binds.push(1);
      await db.prepare(`UPDATE form_smtp_settings SET
        enabled=?,host=?,port=?,security=?,username=?,from_name=?,from_email=?,to_emails=?,reply_to_mode=?,subject_template=?
        ${passwordSql},smtp_verified_at=NULL,updated_at=CURRENT_TIMESTAMP WHERE id=?`).bind(...binds).run();
      return response({ saved: true, settings: await loadSmtpSettings(db, context.env, false) });
    }
    if (payload.action === "test") {
      const settings = await loadSmtpSettings(db, context.env, true);
      if (!settings.enabled) return response({ error: "Enable and save SMTP before testing" }, 400);
      const result = await sendSmtp(settings, {
        id: "smtp-test-" + Date.now(),
        created_at: new Date().toISOString(),
        source: "admin-smtp-test",
        page_url: "/admin/",
        locale: "en",
        name: "SMTP Test",
        email: settings.fromEmail,
        phone: "",
        company: "XUYI Bottles",
        brand: "XUYI Bottles",
        reference: "SMTP-TEST",
        requirements: "This is an XUYI Bottles SMTP verification message.",
        equipment: ""
      });
      if (!result.sent) return response({ error: "SMTP test did not send a message" }, 502);
      await db.prepare("UPDATE form_smtp_settings SET smtp_verified_at=CURRENT_TIMESTAMP WHERE id=1").run();
      return response({ tested: true, result });
    }
    return response({ error: "Unknown action" }, 400);
  } catch (error) {
    return response({ error: clean(error?.message || error, 2000) }, 400);
  }
}