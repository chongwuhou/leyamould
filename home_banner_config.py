"""XUYI homepage 3-slide shared D1 config and reviewed language payload."""
import json,re
from urllib.parse import urlsplit
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DEFAULT=json.loads((ROOT/"assets/home-banner-defaults.json").read_text(encoding="utf8"))
from locale_registry import approved_locales
FIELDS=("title","highlight","description","alt","cta")
def verified(config,state=None):
 if not isinstance(config,dict) or not isinstance(config.get("slides"),list) or len(config["slides"])!=3:
  raise ValueError("XUYI homepage requires three banner slides")
 for slide in config["slides"]:
  if not isinstance(slide,dict):raise ValueError("Invalid banner slide")
  image=str(slide.get("img",""))
  link=str(slide.get("link",""))
  if not re.fullmatch(r"/(?:assets/[A-Za-z0-9/_-]+\.(?:jpg|jpeg|webp|png)|media/(?:product|page|shared|ppt|excel|group|gallery|capability|blog)/[A-Za-z0-9._-]+\.(?:jpg|jpeg|webp|png))",image):
   raise ValueError("Invalid homepage banner image")
  unsafe=any(char.isspace() or char in (chr(60),chr(62),chr(34),chr(39),chr(92)) for char in link)
  parsed=urlsplit(link)
  local=bool(re.fullmatch(r"/[A-Za-z0-9_/?#=%&.+~-]*",link)) and not link.startswith("//")
  external=parsed.scheme=="https" and bool(parsed.hostname) and parsed.username is None and parsed.password is None
  if unsafe or not (local or external):
   raise ValueError("Invalid homepage banner destination")
  for loc in [lang["code"] for lang in approved_locales(state or {})]:
   texts=slide if loc=="en" else (slide.get("translations") or {}).get(loc)
   if not isinstance(texts,dict):raise ValueError("Missing reviewed "+loc+" banner text")
   for field in FIELDS:
    val=texts.get(field)
    if not isinstance(val,str) or not val.strip() or "<" in val or ">" in val or "\n" in val:
     raise ValueError("Unsafe homepage banner text "+loc+"/"+field)
 return config
def config_for(state):
 conf=state.get("banners")
 return verified(conf if conf is not None else DEFAULT,state)
def for_locale(state,locale="en",published_routes=None):
 config=config_for(state)
 rows=[]
 prefixes={lang["code"]:lang["pathPrefix"] for lang in approved_locales(state)}
 if locale not in prefixes:raise ValueError("Unpublished banner locale: "+locale)
 for slide in config["slides"]:
  words=slide if locale=="en" else slide["translations"][locale]
  link=slide["link"]
  if locale!="en" and published_routes is not None and link.startswith("/") and not link.startswith("//"):
   from urllib.parse import urlsplit
   parsed=urlsplit(link)
   if parsed.path in published_routes:
    link="/"+prefixes[locale]+link
  rows.append({**{key:words[key] for key in FIELDS},
   "img":slide["img"],"link":link})
 return rows
def tag(state,locale="en",published_routes=None):
 rows=for_locale(state,locale,published_routes)
 return '<script type="application/json" id="xuyi-home-banners">'+json.dumps(rows,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")+'</script>'
