// YouTube link catalogue for the LEYA MOULD video gallery.
// The public page uses direct thumbnail/embed URLs; it never calls the YouTube Data API.
export const VIDEO_SEED = [
  { videoId: "elkadaPoBHc", title: "Video of 5 gallon cap trial mold", description: "", publishedAt: "2021-10-07T00:57:36Z" },
  { videoId: "wMPqPOKdnf4", title: "8cavity flip top cap mold with cold runner", description: "", publishedAt: "2021-10-07T00:58:46Z" },
  { videoId: "E0M3IwYBsGw", title: "16cavity cap mold with slitting machine and cold runner", description: "", publishedAt: "2021-10-07T00:59:24Z" },
  { videoId: "y1NrJ4GUOO4", title: "28mm high speed cap mould", description: "", publishedAt: "2021-10-07T00:59:54Z" },
  { videoId: "YLNnJWATMB4", title: "28 drops plastic cover (24 cavity)", description: "", publishedAt: "2021-10-09T07:30:01Z" },
  { videoId: "t-I5OczexGc", title: "32-cavity cap mold", description: "", publishedAt: "2021-10-09T07:32:51Z" },
  { videoId: "1VO69jVYxgY", title: "32-cavity bottle cap injection molding (hot runner)", description: "", publishedAt: "2021-10-12T03:05:54Z" },
  { videoId: "03FybMF9qCE", title: "48-cavity cap mold", description: "", publishedAt: "2021-10-12T03:06:30Z" },
  { videoId: "LpWp3_8S2c0", title: "48 cavity cap mold", description: "", publishedAt: "2021-10-13T10:20:32Z" },
  { videoId: "eJCq4OYiR68", title: "48mm cap mold", description: "", publishedAt: "2021-10-13T10:21:23Z" },
  { videoId: "2AnfOabyI10", title: "cap molds flip top cap mould", description: "", publishedAt: "2021-10-13T10:22:15Z" },
  { videoId: "5AaCsTX7W2s", title: "Bottle Cap Mould-Oil Cap Trial Video", description: "", publishedAt: "2021-10-19T00:36:22Z" }
];

export const YOUTUBE_TABLE_SQL = `CREATE TABLE IF NOT EXISTS leya_youtube_videos (
  id TEXT PRIMARY KEY,
  video_id TEXT NOT NULL UNIQUE,
  youtube_url TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT 'LEYA MOULD video',
  description TEXT NOT NULL DEFAULT '',
  published_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)`;

export async function ensureYoutubeVideos(db) {
  await db.prepare(YOUTUBE_TABLE_SQL).run();
  await db.prepare("CREATE INDEX IF NOT EXISTS idx_leya_youtube_videos_order ON leya_youtube_videos(sort_order,created_at DESC)").run();
  await db.prepare("CREATE TABLE IF NOT EXISTS leya_youtube_video_meta (key TEXT PRIMARY KEY,value TEXT NOT NULL DEFAULT '')").run();
  const seeded = await db.prepare("SELECT value FROM leya_youtube_video_meta WHERE key='seeded'").first();
  if (seeded?.value === "1") return;
  for (let i = 0; i < VIDEO_SEED.length; i += 1) {
    const item = VIDEO_SEED[i];
    await db.prepare(`INSERT OR IGNORE INTO leya_youtube_videos
      (id,video_id,youtube_url,title,description,published_at,sort_order)
      VALUES(?,?,?,?,?,?,?)`)
      .bind("seed-" + item.videoId, item.videoId, "https://www.youtube.com/watch?v=" + item.videoId,
        item.title, item.description || "", item.publishedAt, i)
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

