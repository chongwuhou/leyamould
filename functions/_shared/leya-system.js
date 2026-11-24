// LEYA system table checkpoint.
//
// Business content remains in the existing D1 tables for compatibility with
// the water-cup backend contract. This helper only makes the shared site state
// table available to the snapshot/build path. Content editing stays as simple
// as the water-cup project: authenticate, save D1, bump the publish revision.

export const LEYA_SCHEMA_VERSION = 1;

const SCHEMA_SQL = [
  `CREATE TABLE IF NOT EXISTS leya_schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`,
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
    ).bind(LEYA_SCHEMA_VERSION, "leya-system-state-v1").run();
    schemaReady.add(db);
  }
  return { version: LEYA_SCHEMA_VERSION };
}



