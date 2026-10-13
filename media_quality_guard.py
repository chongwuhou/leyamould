"""Use a documented, larger XUYI marketing photograph for the homepage.

The 670px PPT slide-037 is not an adequate wide homepage marketing visual.
The replacement is from the user's XUYI gallery (curated-hd-manifest.json),
not an invented product-SKU photograph. Leave all SKU images untouched.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = "/media/ppt/slide-037.webp"
NEW = "/assets/curated-hd/outdoor-lifestyle.webp"
ALT = {
    "en": "Plastic sports water bottles in an outdoor lifestyle scene",
    "es": "Botellas deportivas de plástico en una escena al aire libre",
    "pt": "Garrafas esportivas de plástico em um ambiente ao ar livre",
    "ru": "Пластиковые спортивные бутылки на открытом воздухе",
    "tr": "Açık hava ortamında plastik sporcu su şişeleri",
}


def upgrade_home_visual(markup, locale):
    """Only replace the FIRST obsolete homepage photo, not blog/SKU images."""
    if locale not in ALT:
        raise ValueError("Unreviewed marketing image locale: " + locale)
    if not (ROOT / NEW.lstrip("/")).is_file():
        raise FileNotFoundError("Missing documented 1500px XUYI marketing image")
    pattern = r'<img\b(?=[^>]*\bsrc="' + re.escape(OLD) + r'")[^>]*>'
    def replace(match):
        tag = match.group()
        tag = tag.replace('src="' + OLD + '"', 'src="' + NEW + '"', 1)
        tag, count = re.subn(r'\balt="[^"]*"', 'alt="' + ALT[locale] + '"', tag, count=1)
        if count != 1:
            raise ValueError("Homepage marketing image missing ALT")
        return tag
    updated, count = re.subn(pattern, replace, markup, count=1)
    if count != 1:
        raise ValueError("Expected one original XUYI homepage marketing photo")
    return updated