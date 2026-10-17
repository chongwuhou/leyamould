import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { clean, ensureFormSchema, loadSmtpSettings, sendSubmissionNotification } from "../../_shared/forms.js";

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
  const db = context.env.XUYI_DB;
  const url = new URL(context.request.url);
  const id = clean(url.searchParams.get("id"), 100);
  if (id) {
    const row = await db.prepare("SELECT * FROM form_submissions WHERE id=?").bind(id).first();
    if (!row) return response({ error: "Submission not found" }, 404);
    return response({ submission: row });
  }
  const status = clean(url.searchParams.get("status"), 20);
  const q = clean(url.searchParams.get("q"), 200);
  const limit = Math.min(200, Math.max(1, Number(url.searchParams.get("limit") || 100)));
  const where = [];
  const bindings = [];
  if (["new", "read", "replied", "spam"].includes(status)) { where.push("status=?"); bindings.push(status); }
  if (q) {
    where.push("(name LIKE ? OR email LIKE ? OR company LIKE ? OR brand LIKE ? OR reference LIKE ? OR requirements LIKE ?)");
    const like = "%" + q.replace(/[%_]/g, "") + "%";
    bindings.push(like, like, like, like, like, like);
  }
  const sql = `SELECT id,created_at,updated_at,status,source,page_url,locale,name,email,phone,company,brand,reference,
    substr(requirements,1,260) AS requirements,smtp_status,smtp_error,smtp_sent_at
    FROM form_submissions ${where.length ? "WHERE " + where.join(" AND ") : ""}
    ORDER BY created_at DESC LIMIT ?`;
  const result = await db.prepare(sql).bind(...bindings, limit).all();
  const stats = await db.prepare(`SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN status='new' THEN 1 ELSE 0 END) AS new_count,
    SUM(CASE WHEN status='read' THEN 1 ELSE 0 END) AS read_count,
    SUM(CASE WHEN status='replied' THEN 1 ELSE 0 END) AS replied_count,
    SUM(CASE WHEN status='spam' THEN 1 ELSE 0 END) AS spam_count
    FROM form_submissions`).first();
  return response({ submissions: result.results || [], stats: stats || {} });
}

export async function onRequestPost(context) {
  const denied = await guard(context);
  if (denied) return denied;
  let payload;
  try { payload = await context.request.json(); }
  catch { return response({ error: "Invalid JSON" }, 400); }
  const id = clean(payload.id, 100);
  if (!id) return response({ error: "Submission id is required" }, 400);
  if (payload.action === "set_status") {
    const status = clean(payload.status, 20);
    if (!["new", "read", "replied", "spam"].includes(status)) return response({ error: "Invalid status" }, 400);
    const result = await context.env.XUYI_DB.prepare(
      "UPDATE form_submissions SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?"
    ).bind(status, id).run();
    return response({ saved: true, status, changes: result.meta?.changes || 0 });
  }
  if (payload.action === "retry_notification") {
    const db = context.env.XUYI_DB;
    const row = await db.prepare("SELECT * FROM form_submissions WHERE id=?").bind(id).first();
    if (!row) return response({ error: "Inquiry not found" }, 404);
    if (row.status === "spam") return response({ error: "Spam enquiries cannot trigger notifications" }, 400);
    if (row.smtp_status === "sent") return response({ error: "This enquiry has already been emailed" }, 409);
    const settings = await loadSmtpSettings(db, context.env);
    if (!settings.enabled || !settings.host || !settings.fromEmail ||
        (!settings.toEmails && !row.assigned_contact_email)) {
      return response({ error: "SMTP is not ready. Enable and configure it before retrying." }, 409);
    }
    // Only one admin request may claim an unsent enquiry. Never resend an
    // already accepted email or deliver anything classed as spam.
    const claimed = await db.prepare(
      "UPDATE form_submissions SET smtp_status='sending',updated_at=CURRENT_TIMESTAMP " +
      "WHERE id=? AND smtp_status IN ('pending','disabled','failed')"
    ).bind(id).run();
    if (Number(claimed.meta?.changes || 0) !== 1) {
      return response({ error: "Another notification attempt is in progress" }, 409);
    }
    try {
      const result = await sendSubmissionNotification(db, context.env, row);
      if (!result.sent) return response({ error: "SMTP delivery was not completed" }, 502);
      return response({ sent: true, id, recipients: result.recipients });
    } catch {
      // The helper records the failure privately in D1. Do not expose SMTP
      // credentials, email content, or raw server diagnostics here.
      return response({ error: "Email delivery failed. Check the SMTP status in the inquiry." }, 502);
    }
  }
  return response({ error: "Unknown action" }, 400);
}

export async function onRequestDelete(context) {
  const denied = await guard(context);
  if (denied) return denied;
  const id = clean(new URL(context.request.url).searchParams.get("id"), 100);
  if (!id) return response({ error: "Submission id is required" }, 400);
  const result = await context.env.XUYI_DB.prepare("DELETE FROM form_submissions WHERE id=?").bind(id).run();
  return response({ deleted: true, changes: result.meta?.changes || 0 });
}
