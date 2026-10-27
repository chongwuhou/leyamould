"""D1-owned customer reviews in Product JSON-LD + visible SKU-specific pages.

This is a source-render component (English and localized CMS pages), NOT a
post-processing change to dist. It never manufactures a rating/price or
assigns general company testimonials to specific product models.
"""
from collections import defaultdict
from html import escape
from datetime import date, datetime
from zoneinfo import ZoneInfo
import json
import re

LD_SCRIPT = re.compile(
    r'<script\b(?=[^>]*\btype=["\x27]application/ld\+json["\x27])[^>]*>.*?</script>',
    re.I | re.S
)
TITLES = {
    "en": ("Customer reviews for this model", "Verified by the site editor against customer feedback. Original words are shown."),
    "es": ("Opiniones de clientes sobre este modelo", "Opiniones originales de clientes asociadas a este modelo."),
    "pt": ("Avaliações de clientes deste modelo", "Opiniões originais de clientes sobre este modelo."),
    "ru": ("Отзывы покупателей об этой модели", "Оригинальные отзывы клиентов об этой модели."),
    "tr": ("Bu model hakkında müşteri yorumları", "Bu modele ait müşterilerin özgün yorumları.")
}


def published_reviews(snapshot, model):
    result = []
    seen = set()
    for r in (snapshot or {}).get("productReviews", []):
        if not isinstance(r, dict) or str(r.get("model")) != str(model) or r.get("status") != "published":
            continue
        uid = str(r.get("id", ""))
        if not uid or uid in seen:
            continue
        rating = r.get("rating")
        author = str(r.get("author", "")).strip()
        review_date = str(r.get("reviewDate", ""))
        body = str(r.get("content", "")).strip()
        if type(rating) is not int or not 1 <= rating <= 5 or not 2 <= len(author) < 100 or not 12 <= len(body) <= 3000:
            continue
        try:
            if date.fromisoformat(review_date).isoformat() != review_date:
                continue
        except ValueError:
            continue
        seen.add(uid)
        entry={"id": uid, "rating": rating, "author": author,
               "reviewDate": review_date, "content": body}
        # Only reviews first published after this change carry genuine UTC
        # D1 ledger times. Historic entries retain their exact date-only UI.
        posted_at=str(r.get("publishedAt") or "")
        if posted_at:
            try:
                instant=datetime.fromisoformat(posted_at.replace("Z","+00:00"))
                if instant.tzinfo is not None:
                    beijing=instant.astimezone(ZoneInfo("Asia/Shanghai"))
                    if (beijing.date()>=date(2026,10,28)
                            and beijing.date().isoformat()==review_date):
                        entry["publishedAt"]=beijing.isoformat(timespec="seconds")
                        entry["publishedTimeLabel"]=beijing.strftime("%Y-%m-%d %H:%M (UTC+8)")
            except ValueError:
                pass
        result.append(entry)
    return sorted(result, key=lambda r: (r["reviewDate"], r["id"]), reverse=True)


def schema_properties(reviews):
    if not reviews:
        return {}
    review = [{
        "@type": "Review",
        "author": {"@type": "Person", "name": r["author"]},
        "datePublished": r.get("publishedAt",r["reviewDate"]),
        "reviewBody": r["content"],
        "reviewRating": {"@type": "Rating", "ratingValue": r["rating"], "bestRating": 5, "worstRating": 1}
    } for r in reviews]
    result = {"review": review[0] if len(review) == 1 else review}
    if len(reviews) > 1:
        result["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": round(sum(r["rating"] for r in reviews) / len(reviews), 2),
            "bestRating": 5,
            "worstRating": 1,
            "reviewCount": len(reviews)
        }
    return result


def render_visible(reviews, model, locale):
    if not reviews:
        return ""
    title, note = TITLES.get(locale, TITLES["en"])
    count = len(reviews)
    mean = round(sum(r["rating"] for r in reviews) / count, 2)
    parts = ['<section id="xuyi-customer-reviews" class="section section--soft" data-reviewed-model="' +
             escape(str(model), quote=True) + '"><div class="shell"><div class="section__head"><div>' +
             '<span class="eyebrow">CUSTOMER FEEDBACK</span><h2 class="section__title">' +
             escape(title) + '</h2><p>' + escape(note) + '</p></div></div>' +
             '<p class="product-review__summary"><strong>' + str(mean) +
             '/5 ★</strong> · ' + str(count) + ' customer review' +
             ('s' if count != 1 else '') + '</p><div class="product-reviews__list">']
    for r in reviews:
        score = r["rating"]
        parts.append('<article class="product-review"><div class="product-review__stars" aria-label="' +
                     str(score) + ' out of 5 stars">' + '★' * score + '☆' * (5 - score) +
                     '</div><p class="product-review__text">' +
                     escape(r["content"]).replace("\n", "<br>") + '</p><p class="product-review__meta"><strong>' +
                     escape(r["author"]) + '</strong> · <time datetime="' +
                     escape(r.get("publishedAt",r["reviewDate"]),quote=True) + '">' +
                     escape(r.get("publishedTimeLabel",r["reviewDate"])) + '</time></p></article>')
    return "".join(parts) + "</div></div></section>"


def _enrich_jsonld(markup, model, properties):
    if not properties:
        return markup
    updated = False
    def replace_tag(m):
        nonlocal updated
        if updated:
            return m.group(0)
        tag = m.group(0)
        first = tag.index(">") + 1
        last = tag.lower().rfind("</script>")
        try:
            data = json.loads(tag[first:last])
        except (ValueError, TypeError):
            return tag
        if not isinstance(data, dict):
            return tag
        nodes = data.get("@graph") if isinstance(data.get("@graph"), list) else [data]
        for node in nodes:
            if not isinstance(node, dict) or node.get("@type") != "Product":
                continue
            # Localized page and source product may have differing display
            # titles, but the unique model/SKU remains the same.
            visible_sku = str(node.get("sku", ""))
            # The source renderer describes Chinese-suffix variants in
            # English for search. It is still the same factory model.
            canonical_sku = visible_sku.replace(" (Transparent Variant)", "透明款")
            if canonical_sku != str(model):
                continue
            # Do not overwrite owner-authored structured reviews or prices.
            if "review" in node or "aggregateRating" in node:
                updated = True
                return tag
            node.update(properties)
            updated = True
            encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
            return tag[:first] + encoded + tag[last:]
        return tag
    return LD_SCRIPT.sub(replace_tag, markup)


def at_product_source(markup, model, locale, snapshot):
    reviews = published_reviews(snapshot, model)
    if not reviews:
        return markup
    # User-edited D1 bodies containing this component take precedence and
    # must not get the previous review section inserted a second time.
    if 'id="xuyi-customer-reviews"' in markup:
        return markup
    if "</main>" not in markup:
        return markup
    content = _enrich_jsonld(markup, model, schema_properties(reviews))
    return content.replace("</main>", render_visible(reviews, model, locale) + "</main>", 1)
