"""Source-stage Turkish terminology correction with D1 field ownership.

Known wrongly-translated 'spor şapkalar' is not a product feature: this means
sports hats, whereas the article discusses bottle caps (şişe kapakları).
Only fields matching the exact previously reviewed D1 source are rewritten.
A later CMS edit or new locale passes through unchanged, without dist edits.
"""
from hashlib import sha256
import json
from pathlib import Path

_RULES=json.loads((Path(__file__).resolve().parent/"data/turkish-bottle-cap-review.json").read_text(encoding="utf8"))

def reviewed_turkish_bottle_caps(route,locale,fields):
    if locale!=_RULES["locale"] or route not in _RULES["originalFields"]:
        return fields
    updated=None
    for field,source_sha in _RULES["originalFields"][route].items():
        value=fields.get(field)
        if not isinstance(value,str) or sha256(value.encode("utf8")).hexdigest()!=source_sha:
            continue
        if _RULES["legacy"] not in value:
            raise ValueError("Reviewed D1 translation fingerprint missing old Turkish phrase: "+route)
        if updated is None:updated=fields.copy()
        updated[field]=value.replace(_RULES["legacy"],_RULES["corrected"])
    return updated if updated is not None else fields
