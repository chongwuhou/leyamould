// YouTube link catalogue for the LEYA MOULD video gallery.
// The public page uses direct thumbnail/embed URLs; it never calls the YouTube Data API.
import VIDEO_SEED_DATA from "../../data/leya-youtube-seed.json";

export const VIDEO_SEED = Array.isArray(VIDEO_SEED_DATA) ? VIDEO_SEED_DATA : [];

export const YOUTUBE_TABLE_SQL = `CREATE TABLE IF NOT EXISTS leya_youtube_videos (
  id TEXT PRIMARY KEY,
  video_id TEXT NOT NULL UNIQUE,
  youtube_url TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT 'LEYA MOULD video',
  title_en TEXT NOT NULL DEFAULT '',
  title_es TEXT NOT NULL DEFAULT '',
  description TEXT NOT NULL DEFAULT '',
  category TEXT NOT NULL DEFAULT 'mould-trial',
  thumbnail_url TEXT NOT NULL DEFAULT '',
  source TEXT NOT NULL DEFAULT 'youtube',
  status TEXT NOT NULL DEFAULT 'published',
  published_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)`;

export async function ensureYoutubeVideos(db) {
  await db.prepare(YOUTUBE_TABLE_SQL).run();
  for (const sql of [
    "ALTER TABLE leya_youtube_videos ADD COLUMN title_en TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE leya_youtube_videos ADD COLUMN title_es TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE leya_youtube_videos ADD COLUMN category TEXT NOT NULL DEFAULT 'mould-trial'",
    "ALTER TABLE leya_youtube_videos ADD COLUMN thumbnail_url TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE leya_youtube_videos ADD COLUMN source TEXT NOT NULL DEFAULT 'youtube'",
    "ALTER TABLE leya_youtube_videos ADD COLUMN status TEXT NOT NULL DEFAULT 'published'"
  ]) { try { await db.prepare(sql).run(); } catch {} }
  await db.prepare("UPDATE leya_youtube_videos SET title_en=title WHERE title_en='' OR title_en IS NULL").run();
  await db.prepare("UPDATE leya_youtube_videos SET thumbnail_url='https://i.ytimg.com/vi/'||video_id||'/mqdefault.jpg' WHERE thumbnail_url='' OR thumbnail_url IS NULL").run();
  await db.prepare("UPDATE leya_youtube_videos SET source='youtube' WHERE source='' OR source IS NULL").run();
  await db.prepare("UPDATE leya_youtube_videos SET status='published' WHERE status='' OR status IS NULL").run();
  for (const item of VIDEO_SEED) {
    await db.prepare("UPDATE leya_youtube_videos SET title_en=?,title_es=? WHERE video_id=? AND (title_es='' OR title_es IS NULL)")
      .bind(item.titleEn, item.titleEs || "", item.videoId).run();
  }
  await db.prepare("CREATE INDEX IF NOT EXISTS idx_leya_youtube_videos_order ON leya_youtube_videos(sort_order,created_at DESC)").run();
  await db.prepare("CREATE TABLE IF NOT EXISTS leya_youtube_video_meta (key TEXT PRIMARY KEY,value TEXT NOT NULL DEFAULT '')").run();
  // Version the catalogue seed so an existing installation can receive newly
  // discovered target-site videos without re-seeding on every request.
  const seeded = await db.prepare("SELECT value FROM leya_youtube_video_meta WHERE key='seeded'").first();
  if (seeded?.value === "2") return;
  for (let i = 0; i < VIDEO_SEED.length; i += 1) {
    const item = VIDEO_SEED[i];
    await db.prepare(`INSERT OR IGNORE INTO leya_youtube_videos
      (id,video_id,youtube_url,title,title_en,title_es,description,category,thumbnail_url,source,status,published_at,sort_order)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)`)
      .bind("seed-" + item.videoId, item.videoId, "https://www.youtube.com/watch?v=" + item.videoId,
        item.titleEn, item.titleEn, item.titleEs || "", item.description || "", "mould-trial",
        "https://i.ytimg.com/vi/" + item.videoId + "/mqdefault.jpg", "youtube", "published", item.publishedAt, i)
      .run();
  }
  await db.prepare("INSERT INTO leya_youtube_video_meta(key,value) VALUES('seeded','2') ON CONFLICT(key) DO UPDATE SET value='2'").run();
}

export function extractYoutubeId(value) {
  const raw = String(value || "").trim();
  if (!raw || raw.length > 500) return "";
  let url;
  try { url = new URL(raw); } catch { return ""; }
  const host = url.hostname.toLowerCase().replace(/^www\./, "");
  let id = "";
  if (host === "youtu.be") id = url.pathname.split("/").filter(Boolean)[0] || "";
  else if (host === "youtube.com" || host === "m.youtube.com" || host === "music.youtube.com") {
    if (url.pathname === "/watch") id = url.searchParams.get("v") || "";
    else if (/^\/(?:embed|shorts|live)\//.test(url.pathname)) id = url.pathname.split("/")[2] || "";
  }
  return /^[A-Za-z0-9_-]{11}$/.test(id) ? id : "";
}

export function normalizeYoutubeUrl(value) {
  const id = extractYoutubeId(value);
  return id ? { id, url: "https://www.youtube.com/watch?v=" + id } : null;
}

