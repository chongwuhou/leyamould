"""Move the Cloudflare video bootstrap list to the reviewed JSON registry."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "functions" / "_shared" / "youtube-videos.js"
text = path.read_text(encoding="utf-8")
start = text.index("export const VIDEO_SEED = [")
end = text.index("\n\nexport const YOUTUBE_TABLE_SQL", start)
replacement = 'import VIDEO_SEED_DATA from "../../data/leya-youtube-seed.json";\n\nexport const VIDEO_SEED = Array.isArray(VIDEO_SEED_DATA) ? VIDEO_SEED_DATA : [];'
path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")
