#!/usr/bin/env python3
"""Turkish bottle caps cannot be mistranslated as sports hats.

Run against source snapshot and all five published locales; D1 edits win.
"""
from pathlib import Path
import sys,json,hashlib,html,re
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from turkish_bottle_cap_source import reviewed_turkish_bottle_caps,_RULES
DIST=ROOT/"dist"
snapshot=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
translations={(v["resourceId"][5:],v["locale"]):v["content"] for v in snapshot["translations"] if v.get("resourceId","").startswith("page:")}
old=_RULES["legacy"]
correct=_RULES["corrected"]
checked=0
for route,checks in _RULES["originalFields"].items():
    d1=translations[(route,"tr")]
    fixed=reviewed_turkish_bottle_caps(route,"tr",d1)
    assert fixed is not d1,route
    assert reviewed_turkish_bottle_caps(route,"tr",fixed) is fixed,(route,"idempotence")
    for key,hash_value in checks.items():
        original=d1[key]
        assert hashlib.sha256(original.encode("utf8")).hexdigest()==hash_value,route
        assert fixed[key]==original.replace(old,correct)
        assert old not in fixed[key]
        assert old in original
        # CMS replaces its own content; the source transform must preserve
        # exactly the editor's new text and other previously edited fields.
        updated=dict(d1,**{key:original.replace(old,"Yönetici tarafından gözden geçirilmiş şişe kapakları.")})
        assert reviewed_turkish_bottle_caps(route,"tr",updated)[key]==updated[key]
        assert reviewed_turkish_bottle_caps(route,"es",d1)==d1
        checked+=1
    relative=route.lstrip("/")+"index.html"
    text=(DIST/"tr"/relative).read_text(encoding="utf8")
    assert "spor şapkalar" not in text and "spor şapka" not in text,route
    assert correct in html.unescape(text),route
    assert text.count(correct)>=sum(d1[k].count(old) for k in checks),route
    if route=="/blog/tritan-vs-pp-petg-pc/":
        head=text.split("</head>",1)[0]
        assert '<meta name="description" content="'+html.escape(correct,quote=True)+'">' in head
        assert '<meta property="og:description" content="'+html.escape(correct,quote=True)+'">' in head
        for graph in re.findall(r'<script type="application/ld\\+json">(.*?)</script>',head,re.S):
            obj=json.loads(graph)
            for item in obj.get("@graph",[]):
                if item.get("@type")=="BlogPosting":
                    assert item.get("description")==correct
for file in (DIST/"tr").rglob("index.html"):
    contents=file.read_text(encoding="utf8").lower()
    assert "spor şapkalar" not in contents,(file,"sports hats mistranslation")
# Unrelated locales and a future translated page remain unchanged.
for language in ("en","es","pt","ru"):
    for route in _RULES["originalFields"]:
        original=(DIST/("" if language=="en" else language)/route.lstrip("/")/"index.html")
        assert original.is_file(),original
        assert correct not in original.read_text(encoding="utf8"),(language,route)
assert reviewed_turkish_bottle_caps("/blog/a-new-article/","tr",{"description":old})=={"description":old}
print("XUYI_TURKISH_BOTTLE_CAP_TERMINOLOGY_PASSED",len(_RULES["originalFields"]),"routes",checked,"D1 fields")