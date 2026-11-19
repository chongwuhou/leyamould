"""Canonical XUYI Blog source registry.

The checked-in catalog is an editorial fallback only. Published content,
translations and SEO remain authoritative in D1/CMS.
"""
import json
from pathlib import Path

SOURCE_NAME = "blog-guides.json"

def load_guides(root):
    data = Path(root) / "data"
    source = data / SOURCE_NAME
    if not source.is_file():
        raise FileNotFoundError(f"Missing canonical Blog source: {source}")
    seen = set()
    posts = []
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
