"""Source-build media curation that never resets a CMS-edited image.

Legacy image substitutions are permitted only while the exact, previously
reviewed original is still in the intended element. If the editor replaces
the image, the source build preserves it rather than refusing publication.
"""
import re


def replace_if_original(markup, prefix, original, approved, context):
    """Return (updated_html, replaced_bool).

    prefix is an exact HTML prefix ending immediately before the src value.
    Keep the surrounding tag/alt verbatim, changing only original image URLs.
    """
    pattern=re.compile(re.escape(prefix)+r'(?P<src>[^"]+)"')
    matches=list(pattern.finditer(markup))
    if not matches:
        # An owner may remove or restructure this section entirely.
        return markup,False
    originals=[m for m in matches if m.group("src")==original]
    if len(originals)>1:
        raise ValueError("Multiple identical original images in reviewed slot: "+context)
    if not originals:
        # Includes a previously applied image or a future CMS replacement.
        return markup,False
    match=originals[0]
    lo,hi=match.span("src")
    return markup[:lo]+approved+markup[hi:],True