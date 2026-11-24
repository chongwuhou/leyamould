// LEYA system tables: explicit schema versioning and immutable content audit.
//
// Business content remains in the existing D1 tables for compatibility with
// the water-cup backend contract. These two tables are LEYA-owned and provide
// the missing operational layer: a schema checkpoint and a small append-only
// audit trail for owner edits and publish requests.

export const LEYA_SCHEMA_VERSION = 1;

const SCHEMA_SQL = [
  `CREATE TABLE IF NOT EXISTS leya_schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`,
  `CREATE TABLE IF NOT EXISTS leya_content_audit (
    id TEXT PRIMARY KEY,
    actor TEXT NOT NULL DEFAULT 'system',
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    before_hash TEXT NOT NULL DEFAULT '',
    after_hash TEXT NOT NULL DEFAULT '',
    publish_revision INTEGER,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`,
  `CREATE INDEX IF NOT EXISTS idx_leya_content_audit_created
    ON leya_content_audit(created_at DESC, id DESC)`,
  `CREATE INDEX IF NOT EXISTS idx_leya_content_audit_resource
    ON leya_content_audit(resource_type, resource_id, created_at DESC)`,
  `CREATE TABLE IF NOT EXISTS site_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`
];

const schemaReady = new WeakSet();

export async function ensureLeyaSystemSchema(db) {
  if (!db) throw new Error("LEYA_DB binding missing");
  // A D1 isolate may be reused for several requests, but must not rely on
  // process lifetime for correctness. The idempotent DDL is safe on cold start.
  if (!schemaReady.has(db)) {
    for (const sql of SCHEMA_SQL) await db.prepare(sql).run();
    await db.prepare(
      `INSERT INTO leya_schema_migrations(version,name)
       VALUES(?,?) ON CONFLICT(version) DO NOTHING`
    ).bind(LEYA_SCHEMA_VERSION, "leya-system-audit-v1").run();
    schemaReady.add(db);
  }
  return { version: LEYA_SCHEMA_VERSION };
}

function clean(value, max = 1600) {
  return String(value ?? "").replace(/\0/g, "").trim().slice(0, max);
}

function safeJson(value) {
  try {
    return JSON.stringify(value && typeof value === "object" ? value : {});
  } catch {
    return "{}";
  }
}

export async function recordContentAudit(db, {
  actor = "system",
  action = "update",
  resourceType = "site",
  resourceId = "",
  beforeHash = "",
  afterHash = "",
  publishRevision = null,
  metadata = {}
} = {}) {
  await ensureLeyaSystemSchema(db);
  const id = `audit_${Date.now().toString(36)}_${crypto.randomUUID().replaceAll("-", "").slice(0, 16)}`;
  await db.prepare(
    `INSERT INTO leya_content_audit
      (id,actor,action,resource_type,resource_id,before_hash,after_hash,publish_revision,metadata_json)
     VALUES(?,?,?,?,?,?,?,?,?)`
  ).bind(
    id,
    clean(actor, 120) || "system",
    clean(action, 80) || "update",
    clean(resourceType, 120) || "site",
    clean(resourceId, 300),
    clean(beforeHash, 128),
    clean(afterHash, 128),
    publishRevision === null || publishRevision === undefined ? null : Number(publishRevision),
    safeJson(metadata)
  ).run();
  return id;
}

export { clean as cleanAuditValue };

