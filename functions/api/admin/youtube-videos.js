import { authorizeAdminRequest } from "../../_shared/admin-security.js";
import { ensureYoutubeVideos, normalizeYoutubeUrl } from "../../_shared/youtube-videos.js";

const json = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});

async function authorized(context) {
  if (!context.env.ADMIN_TOKEN) return json({ error: "Admin not configured" }, 503);
  if (!(await authorizeAdminRequest(context.request, context.env))) return json({ error: "Unauthorized" }, 401);
  if (!context.env.LEYA_DB) return json({ error: "LEYA_DB unavailable" }, 503);
  return null;
}

async function list(db) {
  await ensureYoutubeVideos(db);
  return (await db.prepare(`SELECT id,video_id,youtube_url,title,title_en,title_es,description,published_at,sort_order,created_at,updated_at
    FROM leya_youtube_videos ORDER BY sort_order ASC, created_at DESC, id ASC LIMIT 500`).all()).results || [];
}

function mapRow(row) {
  return { id: row.id, videoId: row.video_id, youtubeUrl: row.youtube_url, title: row.title,
    titleEn: row.title_en || row.title, titleEs: row.title_es || "",
    description: row.description, publishedAt: row.published_at, sortOrder: row.sort_order,
    createdAt: row.created_at, updatedAt: row.updated_at };
}

export async function onRequestGet(context) {
  const denied = await authorized(context); if (denied) return denied;
  try { return json({ items: (await list(context.env.LEYA_DB)).map(mapRow) }); }
  catch { return json({ error: "Unable to read YouTube videos" }, 503); }
}

export async function onRequestPost(context) {
  const denied = await authorized(context); if (denied) return denied;
  let input; try { input = await context.request.json(); } catch { return json({ error: "Invalid JSON" }, 400); }
  const action = String(input?.action || "save");
  const db = context.env.LEYA_DB;
  try {
    await ensureYoutubeVideos(db);
    if (action === "delete") {
      const id = String(input?.id || "").trim();
      if (!id || id.length > 80) return json({ error: "Invalid video ID" }, 400);
      const result = await db.prepare("DELETE FROM leya_youtube_videos WHERE id=?").bind(id).run();
      if (!result.meta?.changes) return json({ error: "Video not found" }, 404);
      return json({ deleted: true, id });
    }
    if (action !== "save") return json({ error: "Unknown action" }, 400);
    const normalized = normalizeYoutubeUrl(input?.youtubeUrl || input?.url);
    if (!normalized) return json({ error: "请输入有效的 YouTube 视频地址（watch、youtu.be、shorts、live 或 embed）" }, 400);
    const titleEn = String(input?.titleEn || input?.title || "").trim().slice(0, 180);
    const titleEs = String(input?.titleEs || "").trim().slice(0, 180);
    if (!titleEn) return json({ error: "请填写英文标题" }, 400);
    const title = titleEn || titleEs || "LEYA MOULD video";
    const description = String(input?.description || "").trim().slice(0, 500);
    const id = crypto.randomUUID();
    const order = Number.isFinite(Number(input?.sortOrder)) ? Math.max(0, Math.min(9999, Number(input.sortOrder))) : 0;
    const publishedAt = String(input?.publishedAt || "").trim();
    if (publishedAt && !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?$/.test(publishedAt))
      return json({ error: "发布时间格式不正确" }, 400);
    await db.prepare(`INSERT INTO leya_youtube_videos
      (id,video_id,youtube_url,title,title_en,title_es,description,published_at,sort_order)
      VALUES(?,?,?,?,?,?,?,?,?)`).bind(id, normalized.id, normalized.url, title, titleEn, titleEs, description, publishedAt || new Date().toISOString(), order).run();
    return json({ saved: true, item: mapRow(await db.prepare("SELECT id,video_id,youtube_url,title,title_en,title_es,description,published_at,sort_order,created_at,updated_at FROM leya_youtube_videos WHERE id=?").bind(id).first()) });
  } catch (error) {
    if (/UNIQUE|constraint/i.test(String(error?.message || ""))) return json({ error: "这个 YouTube 视频已经存在" }, 409);
    return json({ error: "Unable to save YouTube video" }, 503);
  }
}

