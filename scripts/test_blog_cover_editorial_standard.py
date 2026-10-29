#!/usr/bin/env python3
"""P0: enforce editorial photo evidence for new XUYI B2B article sources.

Machine checks cannot judge image meaning. Editors MUST visually inspect the
actual image, title, buyer and use case; CI fails if approval evidence is
missing or inconsistent. Owner D1/CMS changes are never overwritten here.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
APPROVALS = DATA / "blog-cover-editorial-approvals.json"
START_DAY = "20261029"
IMAGE_MIN_BYTES = 30_000
IMAGE_MAX_BYTES = 350_000
TOPIC_STOP = {"water", "bottle", "bottles", "wholesale", "bulk", "custom", "branded", "reusable", "procurement", "guide", "source", "how", "should", "buy", "for", "with", "and", "the", "from"}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("XUYI_BLOG_PHOTO_EDITORIAL_REJECTED " + reason)


def guide_sources():
    found = []
    for path in sorted(DATA.glob("blog-guides-20*.json")):
        hit = re.fullmatch(r"blog-guides-(\d{8})(?:-\d+)?\.json", path.name)
        if not hit or hit.group(1) < START_DAY:
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        for post in value if isinstance(value, list) else [value]:
            require(isinstance(post, dict) and post.get("slug") and post.get("title"), "invalid source " + str(path))
            found.append((post, path))
    require(bool(found), "missing 2026-10-29 reference source")
    return found


def visible_topic_words(post, entry):
    anchors = entry.get("topicAnchors")
    require(isinstance(anchors, list) and 2 <= len(anchors) <= 5, post["slug"] + " missing 2-5 specific topic anchors")
    actual = re.sub(r"[^a-z0-9]+", " ", post["slug"] + " " + post["title"].lower())
    evidence = " ".join(str(entry.get(key, "")).lower() for key in ("visualScene", "buyerContext", "articleUse", "sceneMatch"))
    for anchor in anchors:
        require(isinstance(anchor, str) and re.fullmatch("[a-z]{4,22}", anchor) and anchor not in TOPIC_STOP, post["slug"] + " generic topic anchor")
        require(anchor in actual and anchor in evidence, post["slug"] + " topic anchor not evidenced: " + anchor)


def validate_record(post, entry, *, check_file=True):
    slug = post["slug"]
    require(entry.get("slug") == slug and entry.get("articleTitle") == post["title"], slug + " title/slug approval drift")
    require(entry.get("cover") == post.get("cover"), slug + " photo not the reviewed source cover")
    require(re.fullmatch(r"/(?:media/blog|assets/blog)/[a-z0-9-]+\.webp", str(entry.get("cover", ""))) is not None, slug + " non-blog or unversioned cover")
    source = entry.get("source")
    require(isinstance(source, str) and re.fullmatch(r"assets/blog/[a-z0-9-]+\.webp", source) is not None, slug + " requires a versioned source WebP")
    require(entry.get("source", "").split("/")[-1] == entry["cover"].split("/")[-1], slug + " R2/source filename mismatch")
    require(re.fullmatch("[a-f0-9]{64}", str(entry.get("sha256", ""))) is not None, slug + " requires sha256")
    for field, minimum in [("visualScene", 50), ("buyerContext", 20), ("articleUse", 20), ("sceneMatch", 100), ("provenance", 25), ("usageDisclosure", 30)]:
        require(isinstance(entry.get(field), str) and len(entry[field].strip()) >= minimum, slug + " missing substantive visual evidence " + field)
    require(entry.get("productVisibility") in ("clearly-visible", "owner-approved-contextual"), slug + " must verify actual bottle visibility")
    visible_topic_words(post, entry)
    if entry.get("reviewDecision") == "owner-selected-reference-2026-10-29":
        require(post.get("updated") == "2026-10-29" and slug in REFERENCE_SLUGS, slug + " cannot claim reference exemption")
        require(entry.get("visualReview") == "owner-selected-three-covers", slug + " reference provenance changed")
    else:
        require(entry.get("reviewDecision") == "visually-reviewed-approved", slug + " needs real visual editorial approval")
        require(entry.get("visualReview") == "actual-image-and-article-compared", slug + " cannot use metadata/prompt as visual proof")
        require(entry.get("productVisibility") == "clearly-visible", slug + " contextual no-bottle new image needs explicit owner exemption, not AI auto-publish")
    scores = entry.get("scores")
    keys = ("sector", "productUse", "commercialRealism", "truthfulness", "composition")
    require(isinstance(scores, dict) and set(scores) == set(keys), slug + " requires five photo score dimensions")
    require(all(type(scores[k]) is int and 4 <= scores[k] <= 5 for k in keys) and sum(scores.values()) >= 22, slug + " image scores below threshold")
    if not check_file:
        return None
    path = ROOT / source
    require(path.is_file(), slug + " missing actual media " + source)
    data = path.read_bytes()
    require(IMAGE_MIN_BYTES <= len(data) <= IMAGE_MAX_BYTES, slug + " photo outside 30-350 KB")
    digest = hashlib.sha256(data).hexdigest()
    require(digest == entry["sha256"], slug + " image was swapped after review")
    with Image.open(path) as img:
        require(img.format == "WEBP" and img.size == (1200, 800), slug + " cover must be 1200x800 WebP")
        # Perceptual near-duplicate guard, stronger than a file hash alone.
        mono = ImageOps.grayscale(img.convert("RGB")).resize((9, 8))
        pixels = list(mono.getdata())
        bits = 0
        for y in range(8):
            for x in range(8):
                bits = (bits << 1) | (pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return (digest, bits)


REFERENCE_SLUGS = {
    "warehouse-staff-custom-water-bottles-bulk-procurement",
    "airport-rail-station-travel-retail-water-bottles-wholesale",
    "coworking-space-member-welcome-kit-water-bottles-wholesale",
}


def negative_tests(posts, records):
    post = posts[0]
    original = records[post["slug"]]
    cases = [
        ({"articleTitle": "Unrelated warehouse sales copy"}, "title"),
        ({"sceneMatch": "It looks nice."}, "unexplained image"),
        ({"topicAnchors": ["bottle", "wholesale"]}, "generic tag"),
        ({"sha256": "a" * 64, "reviewDecision": "visually-reviewed-approved"}, "forged source review"),
        ({"scores": {**original["scores"], "sector": 2}}, "wrong customer setting"),
        ({"cover": "/assets/products/generic.webp"}, "wrong-category photo"),
        ({"visualReview": "filename-only", "reviewDecision": "visually-reviewed-approved"}, "metadata-only review"),
    ]
    for patch, name in cases:
        entry = {**copy.deepcopy(original), **patch}
        try:
            validate_record(post, entry, check_file=False)
        except ValueError:
            continue
        raise AssertionError("PHOTO_GATE_NEGATIVE_CASE_NOT_BLOCKED " + name)


def main():
    document = json.loads(APPROVALS.read_text(encoding="utf-8"))
    require(document.get("site") == "xuyi-drinkware-site" and document.get("schemaVersion") == 1, "wrong approval authority")
    records = document.get("records")
    require(isinstance(records, list), "missing approved photo records")
    mapping = {}
    for record in records:
        slug = record.get("slug")
        require(isinstance(slug, str) and slug not in mapping, "duplicate approved slug")
        mapping[slug] = record
    inputs = guide_sources()
    source_slugs = set()
    hashes, visual = {}, {}
    for post, path in inputs:
        slug = post["slug"]
        require(slug not in source_slugs, "duplicate new source article " + slug)
        source_slugs.add(slug)
        require(slug in mapping, "no documented real visual review for " + slug + " (" + str(path) + ")")
        digest, fingerprint = validate_record(post, mapping[slug])
        require(digest not in hashes, "reused identical picture in unrelated articles " + slug + " / " + hashes.get(digest, ""))
        for other_slug, other in visual.items():
            require((fingerprint ^ other).bit_count() > 7, "visually near-duplicate cover " + slug + " / " + other_slug)
        hashes[digest] = slug
        visual[slug] = fingerprint
    # Approval records for older/reference posts are retained; unrelated CMS
    # owner edits or added product SKUs do not become fixed-count test failures.
    negative_tests([inputs[0][0]], mapping)
    print("XUYI_BLOG_PHOTO_P0_EDITORIAL_GATE_PASSED", len(source_slugs), "guide sources; source hashes, visual evidence, unique photos, 1200x800 and negative fixtures")


if __name__ == "__main__":
    main()
