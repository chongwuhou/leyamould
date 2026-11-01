#!/usr/bin/env python3
"""New English B2B articles receive three related cards without overwriting D1."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from blog_editorial import GUIDES, ensure_related_guides
SLUGS = (
    "homeware-store-reusable-water-bottles-wholesale",
    "tennis-club-team-water-bottles-bulk-buying",
    "functional-training-gym-member-bottles-wholesale",
)
for slug in SLUGS:
    source = '<article class="article"><p>Owner-approved D1 body must remain unchanged.</p><div class="blog-editorial__cta">Existing CTA</div></article>'
    result = ensure_related_guides("/blog/" + slug + "/", source)
    assert "Owner-approved D1 body must remain unchanged." in result
    assert "Existing CTA" in result
    assert result.count('class="blog-related__item"') == 3
    for linked in GUIDES[slug]["related"]:
        assert 'href="/blog/' + linked + '/"' in result
    assert ensure_related_guides("/blog/" + slug + "/", result) == result
    assert ensure_related_guides("/es/blog/" + slug + "/", source) == source
print("XUYI_ENGLISH_B2B_RELATED_GUIDES_PASSED", len(SLUGS), "articles; exact 3 cards; CMS body retained; idempotent")