// YouTube link catalogue for the LEYA MOULD video gallery.
// The public page uses direct thumbnail/embed URLs; it never calls the YouTube Data API.
export const VIDEO_SEED = [
  { videoId: "elkadaPoBHc", titleEn: "Video of 5 gallon cap trial mold", titleEs: "Vídeo de prueba del molde de tapa de garrafón", description: "", publishedAt: "2021-10-07T00:57:36Z" },
  { videoId: "wMPqPOKdnf4", titleEn: "8cavity flip top cap mold with cold runner", titleEs: "Molde de tapa abatible de 8 cavidades con colada fría", description: "", publishedAt: "2021-10-07T00:58:46Z" },
  { videoId: "E0M3IwYBsGw", titleEn: "16cavity cap mold with slitting machine and cold runner", titleEs: "Molde de tapas de 16 cavidades con máquina de corte y colada fría", description: "", publishedAt: "2021-10-07T00:59:24Z" },
  { videoId: "y1NrJ4GUOO4", titleEn: "28mm high speed cap mould", titleEs: "Molde de tapas de alta velocidad de 28 mm", description: "", publishedAt: "2021-10-07T00:59:54Z" },
  { videoId: "YLNnJWATMB4", titleEn: "28 drops plastic cover (24 cavity)", titleEs: "Tapa plástica de 28 puntos (24 cavidades)", description: "", publishedAt: "2021-10-09T07:30:01Z" },
  { videoId: "t-I5OczexGc", titleEn: "32-cavity cap mold", titleEs: "Molde de tapas de 32 cavidades", description: "", publishedAt: "2021-10-09T07:32:51Z" },
  { videoId: "1VO69jVYxgY", titleEn: "32-cavity bottle cap injection molding (hot runner)", titleEs: "Inyección de tapas de botella de 32 cavidades (canal caliente)", description: "", publishedAt: "2021-10-12T03:05:54Z" },
  { videoId: "03FybMF9qCE", titleEn: "48-cavity cap mold", titleEs: "Molde de tapas de 48 cavidades", description: "", publishedAt: "2021-10-12T03:06:30Z" },
  { videoId: "LpWp3_8S2c0", titleEn: "48 cavity cap mold", titleEs: "Molde de tapas de 48 cavidades", description: "", publishedAt: "2021-10-13T10:20:32Z" },
  { videoId: "eJCq4OYiR68", titleEn: "48mm cap mold", titleEs: "Molde de tapas de 48 mm", description: "", publishedAt: "2021-10-13T10:21:23Z" },
  { videoId: "2AnfOabyI10", titleEn: "cap molds flip top cap mould", titleEs: "Molde de tapas abatibles", description: "", publishedAt: "2021-10-13T10:22:15Z" },
  { videoId: "5AaCsTX7W2s", titleEn: "Bottle Cap Mould-Oil Cap Trial Video", titleEs: "Vídeo de prueba del molde de tapa para aceite", description: "", publishedAt: "2021-10-19T00:36:22Z" }
];

export const YOUTUBE_TABLE_SQL = `CREATE TABLE IF NOT EXISTS leya_youtube_videos (
  id TEXT PRIMARY KEY,
  video_id TEXT NOT NULL UNIQUE,
  youtube_url TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT 'LEYA MOULD video',
  title_en TEXT NOT NULL DEFAULT '',
  title_es TEXT NOT NULL DEFAULT '',
  description TEXT NOT NULL DEFAULT '',
  published_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)`;

export async function ensureYoutubeVideos(db) {
  await db.prepare(YOUTUBE_TABLE_SQL).run();
  for (const sql of [
    "ALTER TABLE leya_youtube_videos ADD COLUMN title_en TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE leya_youtube_videos ADD COLUMN title_es TEXT NOT NULL DEFAULT ''"
  ]) { try { await db.prepare(sql).run(); } catch {} }
  await db.prepare("UPDATE leya_youtube_videos SET title_en=title WHERE title_en='' OR title_en IS NULL").run();
  for (const item of VIDEO_SEED) {
    await db.prepare("UPDATE leya_youtube_videos SET title_en=?,title_es=? WHERE video_id=? AND (title_es='' OR title_es IS NULL)")
      .bind(item.titleEn, item.titleEs || "", item.videoId).run();
  }
  await db.prepare("CREATE INDEX IF NOT EXISTS idx_leya_youtube_videos_order ON leya_youtube_videos(sort_order,created_at DESC)").run();
  await db.prepare("CREATE TABLE IF NOT EXISTS leya_youtube_video_meta (key TEXT PRIMARY KEY,value TEXT NOT NULL DEFAULT '')").run();
  const seeded = await db.prepare("SELECT value FROM leya_youtube_video_meta WHERE key='seeded'").first();
  if (seeded?.value === "1") return;
  for (let i = 0; i < VIDEO_SEED.length; i += 1) {
    const item = VIDEO_SEED[i];
    await db.prepare(`INSERT OR IGNORE INTO leya_youtube_videos
      (id,video_id,youtube_url,title,title_en,title_es,description,published_at,sort_order)
      VALUES(?,?,?,?,?,?,?,?,?)`)
      .bind("seed-" + item.videoId, item.videoId, "https://www.youtube.com/watch?v=" + item.videoId,
        item.titleEn, item.titleEn, item.titleEs || "", item.description || "", item.publishedAt, i)
      .run();
  }
  await db.prepare("INSERT INTO leya_youtube_video_meta(key,value) VALUES('seeded','1') ON CONFLICT(key) DO UPDATE SET value='1'").run();
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

