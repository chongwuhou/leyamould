#!/usr/bin/env python3
"""Augment only the ephemeral build snapshot for the one-time endpoint bootstrap deploy.

This does not write to D1. The reviewed payload is published to the real CMS only
after this deployment installs /api/admin/blog-batch in production.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SNAPSHOT=ROOT/"_local_ops"/"build-snapshot.json"
PAYLOAD=ROOT/"_local_ops"/"blog-batch-20261019"/"payload.json"
TAIL="</div></div></section>"
SLUGS=(
 "can-you-put-hot-water-in-plastic-water-bottle",
 "are-plastic-water-bottles-dishwasher-safe",
 "why-does-reusable-water-bottle-smell-bad",
)
LOCALES=("es","pt","ru","tr")

def main():
 if not SNAPSHOT.is_file() or not PAYLOAD.is_file():
  raise SystemExit("Bootstrap needs a fresh build snapshot and reviewed Blog payload.")
 snapshot=json.loads(SNAPSHOT.read_text(encoding="utf8"))
 payload=json.loads(PAYLOAD.read_text(encoding="utf8"))
 rows=snapshot.get("translations")
 if not isinstance(rows,list):
  raise SystemExit("Build snapshot has no translations array.")
 by_key={(row.get("resourceId"),row.get("locale")):row for row in rows}
 for item in payload.get("translations",[]):
  resource="page:"+item["route"]
  key=(resource,item["locale"])
  expected={"title":item["title"],"description":item["description"],"mainHtml":item["mainHtml"]}
  existing=by_key.get(key)
  if existing is None:
   existing={"resourceId":resource,"locale":item["locale"],"content":expected,"reviewedAt":"2026-10-19"}
   rows.append(existing)
   by_key[key]=existing
  elif existing.get("content")!=expected:
   raise SystemExit("Existing owner translation differs; refusing to overwrite "+resource+" "+item["locale"])
 for locale in LOCALES:
  row=by_key.get(("page:/blog/",locale))
  if not row:
   raise SystemExit("Build snapshot is missing the localized Blog index: "+locale)
  content=row.get("content") or {}
  body=str(content.get("mainHtml") or "")
  if not body.endswith(TAIL):
   raise SystemExit("Localized Blog index has an unexpected ending; refusing bootstrap edit: "+locale)
  for item in payload.get("indexCards",[]):
   if item.get("locale")!=locale:continue
   slug=item.get("slug","")
   href="/blog/"+slug+"/"
   if href not in body:
    body=body[:-len(TAIL)]+item["html"]+TAIL
   else:
    cards=[part.split("</article>",1)[0] for part in body.split('<article class="news-card">')[1:]]
    matches=[card for card in cards if href in card]
    if len(matches)!=1 or matches[0].count('href="'+href+'"')!=3:
     raise SystemExit("Existing localized Blog card is ambiguous; refusing bootstrap edit: "+locale+" "+slug)
  content["mainHtml"]=body
  row["content"]=content
 for slug in SLUGS:
  for locale in LOCALES:
   row=by_key.get(("page:/blog/"+slug+"/",locale))
   if not row or len(str(row.get("content",{}).get("mainHtml","")))<5000:
    raise SystemExit("Bootstrap translation validation failed: "+slug+" "+locale)
 SNAPSHOT.write_text(json.dumps(snapshot,ensure_ascii=False,separators=(",",":")),encoding="utf8")
 print("XUYI_BOOTSTRAP_SNAPSHOT_READY",len(payload["translations"]),"reviewed translations",len(payload["indexCards"]),"index cards; D1 unchanged")

if __name__=="__main__":main()
