"""Versioned XUYI Blog source registry with automatic new-date discovery.

Source templates/data define default pages; D1/CMS owner edits to article bodies,
translations and SEO remain authoritative at release-build time.
"""
import json
import re
from pathlib import Path

DATED_GUIDE = re.compile(r"blog-guides-20[0-9]{6}(?:-[0-9]+)?\.json\Z")

def load_guides(root):
    data = Path(root) / "data"
    sources = [data / "blog-guides.json"] + [
        p for p in sorted(data.glob("blog-guides-*.json"))
        if DATED_GUIDE.fullmatch(p.name)
    ]
    seen = set()
    posts = []
    for source in sources:
        payload = json.loads(source.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else [payload]
        for post in rows:
            if not isinstance(post, dict) or not all(
                isinstance(post.get(k), str) and post[k].strip()
                for k in ("slug", "title", "description")
            ):
                raise ValueError("Invalid Blog source " + str(source))
            if post["slug"] in seen:
                raise ValueError("Duplicate Blog slug " + post["slug"])
            seen.add(post["slug"])
            posts.append(post)
    return posts