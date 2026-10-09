import { connect } from "cloudflare:sockets";

const encoder = new TextEncoder();
const decoder = new TextDecoder();
const clean = (value, max = 4000) => String(value ?? "").replace(/\0/g, "").trim().slice(0, max);
const headerSafe = (value, max = 300) => clean(value, max).replace(/[\r\n]+/g, " ");
const emailRe = /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/;

export const FORM_SCHEMA = [
  `CREATE TABLE IF NOT EXISTS form_submissions (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new','read','replied','spam')),
    source TEXT NOT NULL DEFAULT '',
    page_url TEXT NOT NULL DEFAULT '',
    locale TEXT NOT NULL DEFAULT 'en',
    name TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    company TEXT NOT NULL DEFAULT '',
    brand TEXT NOT NULL DEFAULT '',
    reference TEXT NOT NULL DEFAULT '',
    requirements TEXT NOT NULL DEFAULT '',
    equipment TEXT NOT NULL DEFAULT '',
    fields_json TEXT NOT NULL DEFAULT '{}',
    ip TEXT NOT NULL DEFAULT '',
    user_agent TEXT NOT NULL DEFAULT '',
    smtp_status TEXT NOT NULL DEFAULT 'pending',
    smtp_error TEXT NOT NULL DEFAULT '',
    smtp_sent_at TEXT
  )`,
  "CREATE INDEX IF NOT EXISTS idx_form_submissions_created ON form_submissions(created_at DESC)",
  "CREATE INDEX IF NOT EXISTS idx_form_submissions_status ON form_submissions(status, created_at DESC)",
  "CREATE INDEX IF NOT EXISTS idx_form_submissions_email ON form_submissions(email)",
  "CREATE INDEX IF NOT EXISTS idx_form_submissions_ip ON form_submissions(ip, created_at DESC)",
  `CREATE TABLE IF NOT EXISTS form_smtp_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    enabled INTEGER NOT NULL DEFAULT 0 CHECK (enabled IN (0,1)),
    host TEXT NOT NULL DEFAULT '',
    port INTEGER NOT NULL DEFAULT 465,
    security TEXT NOT NULL DEFAULT 'ssl' CHECK (security IN ('ssl','starttls','none')),
    username TEXT NOT NULL DEFAULT '',
    password_ciphertext TEXT NOT NULL DEFAULT '',
    from_name TEXT NOT NULL DEFAULT '',
    from_email TEXT NOT NULL DEFAULT '',
    to_emails TEXT NOT NULL DEFAULT '',
    reply_to_mode TEXT NOT NULL DEFAULT 'visitor' CHECK (reply_to_mode IN ('visitor','from')),
    subject_template TEXT NOT NULL DEFAULT 'Website inquiry: {{reference}} {{name}}',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`
];

export async function ensureFormSchema(db) {
  for (const sql of FORM_SCHEMA) await db.prepare(sql).run();
  const columns = await db.prepare("PRAGMA table_info(form_submissions)").all();
  const existing = new Set((columns.results || []).map((row) => row.name));
  const additions = [
    ["region", "TEXT NOT NULL DEFAULT ''"],
    ["assigned_contact_id", "TEXT NOT NULL DEFAULT ''"],
    ["assigned_contact_name", "TEXT NOT NULL DEFAULT ''"],
    ["assigned_contact_email", "TEXT NOT NULL DEFAULT ''"]
  ];
  for (const [name, definition] of additions) {
    if (!existing.has(name)) await db.prepare("ALTER TABLE form_submissions ADD COLUMN " + name + " " + definition).run();
  }
  await db.prepare(`INSERT INTO form_smtp_settings(id) VALUES(1) ON CONFLICT(id) DO NOTHING`).run();
}

function bytesToBase64(bytes) {
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  return btoa(binary);
}

function base64ToBytes(value) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

async function settingsKey(env) {
  const secret = clean(env.FORM_SETTINGS_KEY, 1000);
  if (!secret) throw new Error("FORM_SETTINGS_KEY is not configured");
  const digest = await crypto.subtle.digest("SHA-256", encoder.encode(secret));
  return crypto.subtle.importKey("raw", digest, "AES-GCM", false, ["encrypt", "decrypt"]);
}

export async function encryptSetting(value, env) {
  if (!value) return "";
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await settingsKey(env);
  const cipher = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, encoder.encode(value)));
  const packed = new Uint8Array(iv.length + cipher.length);
  packed.set(iv, 0);
  packed.set(cipher, iv.length);
  return bytesToBase64(packed);
}

export async function decryptSetting(value, env) {
  if (!value) return "";
  const packed = base64ToBytes(value);
  if (packed.length < 29) throw new Error("Stored SMTP password is invalid");
  const key = await settingsKey(env);
  const plain = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: packed.subarray(0, 12) },
    key,
    packed.subarray(12)
  );
  return decoder.decode(plain);
}

export async function loadSmtpSettings(db, env, includePassword = false) {
  await ensureFormSchema(db);
  const brandStored = { config: { email: { defaultFromName: "XUYI Bottles" } } };
  const brandDefaultFromName = brandStored?.config?.email?.defaultFromName || "Website";
  const row = await db.prepare("SELECT * FROM form_smtp_settings WHERE id=1").first();
  const settings = {
    enabled: Boolean(row?.enabled),
    host: clean(row?.host, 255),
    port: Number(row?.port || 465),
    security: clean(row?.security, 20) || "ssl",
    username: clean(row?.username, 255),
    passwordConfigured: Boolean(row?.password_ciphertext),
    fromName: clean(row?.from_name, 160) || brandDefaultFromName,
    fromEmail: clean(row?.from_email, 320),
    toEmails: clean(row?.to_emails, 2000),
    replyToMode: clean(row?.reply_to_mode, 20) || "visitor",
    subjectTemplate: clean(row?.subject_template, 500) || "Website inquiry: {{reference}} {{name}}",
    updatedAt: row?.updated_at || ""
  };
  if (includePassword && row?.password_ciphertext) settings.password = await decryptSetting(row.password_ciphertext, env);
  return settings;
}

export function validateSmtpSettings(input, existing = {}) {
  const enabled = Boolean(input.enabled);
  const host = clean(input.host, 255);
  const port = Number(input.port || 465);
  const security = clean(input.security, 20) || "ssl";
  const username = clean(input.username, 255);
  const fromName = headerSafe(input.fromName || existing.fromName || "Website", 160);
  const fromEmail = clean(input.fromEmail, 320);
  const toEmails = clean(input.toEmails, 2000);
  const replyToMode = clean(input.replyToMode || "visitor", 20);
  const subjectTemplate = headerSafe(input.subjectTemplate || "Website inquiry: {{reference}} {{name}}", 500);
  if (host && !/^[A-Za-z0-9.-]+$/.test(host)) throw new Error("SMTP host is invalid");
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error("SMTP port is invalid");
  if (port === 25) throw new Error("Cloudflare Workers cannot connect to SMTP port 25; use 465 or 587");
  if (!["ssl", "starttls", "none"].includes(security)) throw new Error("SMTP security must be ssl, starttls or none");
  if (!["visitor", "from"].includes(replyToMode)) throw new Error("Reply-To mode is invalid");
  const recipients = parseEmails(toEmails);
  if (fromEmail && !emailRe.test(fromEmail)) throw new Error("From email is invalid");
  if (enabled) {
    if (!host) throw new Error("SMTP host is required");
    if (!fromEmail) throw new Error("From email is required");
    if (!recipients.length) throw new Error("At least one notification recipient is required");
    if (username && !clean(input.password) && !existing.passwordConfigured) throw new Error("SMTP password is required");
  }
  return { enabled, host, port, security, username, fromName, fromEmail, toEmails, replyToMode, subjectTemplate };
}

export function parseEmails(value) {
  return String(value || "").split(/[;,\s]+/).map((x) => x.trim()).filter((x) => emailRe.test(x)).slice(0, 20);
}

function withTimeout(promise, ms, label) {
  let timer;
  return Promise.race([
    promise,
    new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(label + " timeout")), ms); })
  ]).finally(() => clearTimeout(timer));
}

class SmtpChannel {
  constructor(socket) {
    this.socket = socket;
    this.reader = socket.readable.getReader();
    this.writer = socket.writable.getWriter();
    this.buffer = "";
  }
  release() {
    try { this.reader.releaseLock(); } catch {}
    try { this.writer.releaseLock(); } catch {}
  }
  async sendRaw(text) {
    await withTimeout(this.writer.write(encoder.encode(text)), 12000, "SMTP write");
  }
  async response() {
    const lines = [];
    for (;;) {
      let idx;
      while ((idx = this.buffer.indexOf("\r\n")) >= 0) {
        const line = this.buffer.slice(0, idx);
        this.buffer = this.buffer.slice(idx + 2);
        lines.push(line);
        if (/^\d{3} /.test(line)) {
          return { code: Number(line.slice(0, 3)), text: lines.join("\n") };
        }
      }
      const chunk = await withTimeout(this.reader.read(), 12000, "SMTP read");
      if (chunk.done) throw new Error("SMTP connection closed");
      this.buffer += decoder.decode(chunk.value, { stream: true });
      if (this.buffer.length > 65536) throw new Error("SMTP response too large");
    }
  }
  async command(line, expected) {
    await this.sendRaw(line + "\r\n");
    const result = await this.response();
    if (!expected.includes(result.code)) throw new Error("SMTP " + result.code + ": " + result.text.slice(-800));
    return result;
  }
}

function b64Utf8(value) {
  return bytesToBase64(encoder.encode(String(value ?? "")));
}

function encodeSubject(value) {
  const subject = headerSafe(value, 500);
  return /^[\x20-\x7E]*$/.test(subject) ? subject : "=?UTF-8?B?" + b64Utf8(subject) + "?=";
}

function fillTemplate(template, submission) {
  const values = {
    reference: submission.reference || "",
    brand: submission.brand || "",
    name: submission.name || "",
    email: submission.email || "",
    page: submission.page_url || submission.pageUrl || ""
  };
  return headerSafe(String(template || "").replace(/\{\{(reference|brand|name|email|page)\}\}/g, (_, key) => values[key]), 500);
}

function notificationBody(submission) {
  return [
    "New website inquiry",
    "",
    "ID: " + clean(submission.id, 100),
    "Time: " + clean(submission.created_at || new Date().toISOString(), 100),
    "Name: " + clean(submission.name, 500),
    "Email: " + clean(submission.email, 500),
    "Phone / WhatsApp: " + clean(submission.phone, 500),
    "Company: " + clean(submission.company, 500),
    "Brand: " + clean(submission.brand, 500),
    "Reference: " + clean(submission.reference, 500),
    "Equipment / application: " + clean(submission.equipment, 1500),
    "",
    "Requirements:",
    clean(submission.requirements, 8000),
    "",
    "Page: " + clean(submission.page_url || submission.pageUrl, 1500),
    "Locale: " + clean(submission.locale, 30),
    "Region: " + clean(submission.region, 120),
    "Assigned contact: " + clean(submission.assigned_contact_name, 300) +
      (submission.assigned_contact_email ? " <" + clean(submission.assigned_contact_email, 320) + ">" : ""),
    "Source: " + clean(submission.source, 200)
  ].join("\r\n");
}

export async function sendSmtp(settings, submission) {
  if (!settings.enabled) return { sent: false, disabled: true };
  const recipients = [...new Set([
    ...parseEmails(settings.toEmails),
    ...(emailRe.test(clean(submission.assigned_contact_email, 320)) ? [clean(submission.assigned_contact_email, 320)] : [])
  ])].slice(0, 20);
  if (!recipients.length) throw new Error("No valid SMTP recipients configured");
  if (settings.port === 25) throw new Error("SMTP port 25 is blocked by Cloudflare Workers");

  let socket = connect(
    { hostname: settings.host, port: settings.port },
    { secureTransport: settings.security === "ssl" ? "on" : settings.security === "starttls" ? "starttls" : "off", allowHalfOpen: true }
  );
  await withTimeout(socket.opened, 12000, "SMTP connect");
  let channel = new SmtpChannel(socket);
  try {
    const greeting = await channel.response();
    if (greeting.code !== 220) throw new Error("SMTP greeting rejected: " + greeting.text);
    const ehloDomain = (settings.fromEmail.split("@")[1] || "localhost").replace(/[^A-Za-z0-9.-]/g, "") || "localhost";
    let ehlo = await channel.command("EHLO " + ehloDomain, [250]);

    if (settings.security === "starttls") {
      await channel.command("STARTTLS", [220]);
      channel.release();
      socket = socket.startTls();
      await withTimeout(socket.opened, 12000, "SMTP TLS");
      channel = new SmtpChannel(socket);
      ehlo = await channel.command("EHLO " + ehloDomain, [250]);
    }

    if (settings.username) {
      const password = settings.password || "";
      const caps = ehlo.text.toUpperCase();
      if (caps.includes("AUTH PLAIN")) {
        await channel.command("AUTH PLAIN " + b64Utf8("\0" + settings.username + "\0" + password), [235]);
      } else if (caps.includes("AUTH LOGIN")) {
        await channel.command("AUTH LOGIN", [334]);
        await channel.command(b64Utf8(settings.username), [334]);
        await channel.command(b64Utf8(password), [235]);
      } else {
        throw new Error("SMTP server did not advertise AUTH PLAIN or LOGIN");
      }
    }

    const from = settings.fromEmail;
    await channel.command("MAIL FROM:<" + from + ">", [250]);
    for (const recipient of recipients) await channel.command("RCPT TO:<" + recipient + ">", [250, 251]);
    await channel.command("DATA", [354]);

    const subject = fillTemplate(settings.subjectTemplate, submission) || "Website inquiry";
    const replyTo = settings.replyToMode === "visitor" && emailRe.test(clean(submission.email, 320))
      ? clean(submission.email, 320)
      : settings.fromEmail;
    const domain = settings.fromEmail.split("@")[1] || ehloDomain;
    const headers = [
      "Date: " + new Date().toUTCString(),
      "Message-ID: <" + crypto.randomUUID() + "@" + domain + ">",
      "From: " + headerSafe(settings.fromName) + " <" + settings.fromEmail + ">",
      "To: " + recipients.join(", "),
      "Reply-To: " + replyTo,
      "Subject: " + encodeSubject(subject),
      "MIME-Version: 1.0",
      "Content-Type: text/plain; charset=UTF-8",
      "Content-Transfer-Encoding: 8bit"
    ].join("\r\n");
    const body = notificationBody(submission).replace(/(^|\r\n)\./g, "$1..");
    await channel.sendRaw(headers + "\r\n\r\n" + body + "\r\n.\r\n");
    const accepted = await channel.response();
    if (accepted.code !== 250) throw new Error("SMTP message rejected: " + accepted.text);
    try { await channel.command("QUIT", [221]); } catch {}
    return { sent: true, recipients: recipients.length };
  } finally {
    try { channel.release(); } catch {}
    try { await socket.close(); } catch {}
  }
}

export async function sendSubmissionNotification(db, env, submission) {
  try {
    const settings = await loadSmtpSettings(db, env, true);
    if (!settings.enabled) {
      await db.prepare("UPDATE form_submissions SET smtp_status='disabled',updated_at=CURRENT_TIMESTAMP WHERE id=?").bind(submission.id).run();
      return { disabled: true };
    }
    const result = await sendSmtp(settings, submission);
    await db.prepare(`UPDATE form_submissions SET smtp_status='sent',smtp_error='',smtp_sent_at=CURRENT_TIMESTAMP,updated_at=CURRENT_TIMESTAMP WHERE id=?`).bind(submission.id).run();
    return result;
  } catch (error) {
    const message = clean(error?.message || error, 2000);
    await db.prepare(`UPDATE form_submissions SET smtp_status='failed',smtp_error=?,updated_at=CURRENT_TIMESTAMP WHERE id=?`).bind(message, submission.id).run();
    throw error;
  }
}

export { clean, emailRe };