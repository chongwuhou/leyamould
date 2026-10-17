"""Move the reviewed homepage intro wide-photo choice to upstream rendering.

No produced HTML mutation. The exact source slot is changed only if it still
has the original factory-reviewed small marketing image; later CMS selections
are authoritative.
"""
import re
OLD="/assets/curated-hd/outdoor-lifestyle.webp"
NEW="/assets/hero/sports-bottles-wide-20261013.webp"
def reviewed_home_intro_photo(body):
    pattern=r'(<div class="kreat-intro__media"><img\b[^>]*\bsrc=")'+re.escape(OLD)+r'(")'
    return re.sub(pattern,lambda m:m.group(1)+NEW+m.group(2),body,count=1)
