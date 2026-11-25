"""Remove the duplicate Python video seed after exporting the D1 bootstrap data."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "mould_build.py"
text = path.read_text(encoding="utf-8")
start = text.index("VIDEO_SEED = [")
end = text.index("\ndef video_card", start)
replacement = 'VIDEO_SEED = json.loads((ROOT / "data/leya-youtube-seed.json").read_text(encoding="utf-8"))\n'
path.write_text(text[:start] + replacement + text[end + 1 :], encoding="utf-8")
