import { ensureYoutubeVideos } from "../_shared/youtube-videos.js";

const json = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});

export async function onRequestGet(context) {
  const db = context.env.LEYA_DB;
  if (!db) return json({ error: "LEYA_DB unavailable" }, 503);
  try {
    await ensureYoutubeVideos(db);
    const locale = new URL(context.request.url).searchParams.get("locale") === "es" ? "es" : "en";
    const rows = (await db.prepare(`SELECT id,video_id,youtube_url,title,title_en,title_es,description,published_at,sort_order,created_at,updated_at
      FROM leya_youtube_videos ORDER BY sort_order ASC, created_at DESC, id ASC LIMIT 500`).all()).results || [];
    return json({ items: rows.map(row => ({
      id: row.id, videoId: row.video_id, youtubeUrl: row.youtube_url,
      title: (locale === "es" ? (row.title_es || row.title_en || row.title) : (row.title_en || row.title_es || row.title)),
      titleEn: row.title_en || row.title, titleEs: row.title_es || "",
      description: row.description, publishedAt: row.published_at, sortOrder: row.sort_order,
      createdAt: row.created_at, updatedAt: row.updated_at
    })) });
  } catch (error) {
    return json({ error: "Unable to read YouTube videos" }, 503);
  }
}

