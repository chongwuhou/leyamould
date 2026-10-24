"""Source-only quality guard for five B2B article cover photographs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
manifest=json.loads((ROOT/"data/blog-photo-cover-map-20261024.json").read_text("utf8"))
entries=manifest["photos"]
assert len(entries)==5
assert len({p["slug"] for p in entries})==5
assert len({p["cover"] for p in entries})==5
all_posts=[]
for path in ["blog-guides.json","blog-guides-20261020.json","blog-guides-20261021.json","blog-guides-20261022.json","blog-guides-20261023.json","blog-guides-20261024.json"]:
    all_posts.extend(json.loads((ROOT/"data"/path).read_text("utf8")))
lookup={p["slug"]:p for p in all_posts}
assert len(lookup)==len(all_posts)
cover_overrides=json.loads((ROOT/"data/blog-cover-overrides.json").read_text("utf8"))
for p in entries:
    assert lookup[p["slug"]]["cover"]==p["cover"],p["slug"]
    f=ROOT/p["cover"].lstrip("/")
    b=f.read_bytes()
    assert len(b)>30000 and b[:4]==b"RIFF" and b[8:12]==b"WEBP",(p["slug"],len(b))
all_covers=[cover_overrides.get(p["slug"],p["cover"]) for p in all_posts]
assert len(set(all_covers))==len(all_covers),"No duplicate source blog cover images"
print("XUYI_FIVE_BLOG_PHOTO_SOURCE_EXISTENCE_UNIQUENESS_WEBP_PASS")
