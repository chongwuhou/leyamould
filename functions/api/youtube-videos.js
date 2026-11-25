import { ensureYoutubeVideos } from "../_shared/youtube-videos.js";

const json = (body, status = 200) => Response.json(body, {
  status,
  headers: { "cache-control": "no-store", "x-robots-tag": "noindex,nofollow,noarchive" }
});

// The public gallery is allowed to fall back to an owner-entered English
// title when a Spanish title has not been supplied yet.  Translate the small
// technical vocabulary at the read boundary so a stale D1 row cannot leak a
// mixed-language card into the Spanish page.  Editors can still replace this
// fallback with a reviewed title from the admin module at any time.
const ES_VIDEO_TERMS = [
  ["automatic beverage bottle cap folding and cutting machine", "máquina automática de plegado y corte de tapas de botellas"],
  ["mineral water bottle cap cutting machine", "máquina de corte de tapas para agua mineral"],
  ["bottle cap folding and cutting machine", "máquina de plegado y corte de tapas"],
  ["automatic combination bottle cap lining machine", "máquina automática combinada de revestimiento de tapas"],
  ["bottle cap assembly machine", "máquina de montaje de tapas"],
  ["cap folding and slitting machine", "máquina de plegado y corte de tapas"],
  ["gasket mounting machine", "máquina de montaje de juntas"],
  ["five gallon", "garrafón de cinco galones"], ["5 gallon", "garrafón de 5 galones"],
  ["bottle cap", "tapa de botella"], ["cap mold", "molde de tapas"], ["cap mould", "molde de tapas"],
  ["mould", "molde"], ["mold", "molde"], ["machine", "máquina"], ["cavity", "cavidad"], ["cavities", "cavidades"],
  ["water", "agua"], ["oil", "aceite"], ["beverage", "bebidas"], ["automatic", "automática"],
  ["folding", "plegado"], ["cutting", "corte"], ["slitting", "corte"], ["trial video", "vídeo de prueba"],
  ["trial", "prueba"], ["assembly", "montaje"], ["lining", "revestimiento"], ["handle", "asa"],
  ["plastic", "plástico"], ["bottle", "botella"], ["cover", "tapa"], ["inner lid", "tapa interior"],
  ["high speed", "alta velocidad"], ["wide mouth", "boca ancha"], ["virus tube", "tubo de virus"],
  ["sampling tube", "tubo de muestreo"], ["edible oil", "aceite comestible"], ["engine oil", "aceite de motor"],
  ["automatic combination", "combinación automática"]
];
const spanishVideoText = (value) => {
  let text = String(value || "").trim();
  for (const [source, target] of ES_VIDEO_TERMS) text = text.replace(new RegExp(source.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi"), target);
  return text.replace(/\s{2,}/g, " ").trim();
};

export async function onRequestGet(context) {
  const db = context.env.LEYA_DB;
  if (!db) return json({ error: "LEYA_DB unavailable" }, 503);
  try {
    await ensureYoutubeVideos(db);
    const locale = new URL(context.request.url).searchParams.get("locale") === "es" ? "es" : "en";
    const rows = (await db.prepare(`SELECT id,video_id,youtube_url,title,title_en,title_es,description,category,thumbnail_url,source,status,published_at,sort_order,created_at,updated_at
      FROM leya_youtube_videos WHERE status='published' ORDER BY sort_order ASC, created_at DESC, id ASC LIMIT 500`).all()).results || [];
    return json({ items: rows.map(row => ({
      id: row.id, videoId: row.video_id, youtubeUrl: row.youtube_url,
      title: (locale === "es" ? spanishVideoText(row.title_es || row.title_en || row.title) : (row.title_en || row.title_es || row.title)),
      titleEn: row.title_en || row.title, titleEs: locale === "es" ? spanishVideoText(row.title_es || row.title_en || row.title) : (row.title_es || ""),
      description: locale === "es" ? spanishVideoText(row.description || "") : row.description, category: row.category || "mould-trial", thumbnailUrl: row.thumbnail_url || ("https://i.ytimg.com/vi/" + row.video_id + "/mqdefault.jpg"), source: row.source || "youtube", status: row.status || "published", publishedAt: row.published_at, sortOrder: row.sort_order,
      createdAt: row.created_at, updatedAt: row.updated_at
    })) });
  } catch (error) {
    return json({ error: "Unable to read YouTube videos" }, 503);
  }
}

