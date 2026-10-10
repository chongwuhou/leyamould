"""Cloudflare Pages redirects sourced from XUYI D1, with reserved-path guardrails."""
from __future__ import annotations
import re
from urllib.parse import urlsplit

RESERVED=("/api/","/admin/","/assets/","/media/","/_","/robots.txt","/sitemap.xml","/build-meta.json")
WHITESPACE=re.compile(r"[\x00-\x20\x7f]")
def _path(value):
 if not isinstance(value,str) or not value.startswith("/") or value.startswith("//") or WHITESPACE.search(value):
  return False
 return not any(value.lower().startswith(x) for x in RESERVED)
def _target(value):
 if not isinstance(value,str) or not value or WHITESPACE.search(value):return False
 if value.startswith("/") and not value.startswith("//"):return True
 try:
  parts=urlsplit(value)
  return parts.scheme=="https" and bool(parts.netloc) and not parts.username and not parts.password
 except ValueError:return False
def redirect_lines(rows):
 if not isinstance(rows,list):raise ValueError("XUYI D1 redirects must be an array")
 if len(rows)>500:raise ValueError("Redirect count exceeded")
 seen=set();output=[]
 for row in rows:
  if not isinstance(row,dict):raise ValueError("Malformed D1 redirect")
  src=row.get("source_path");dst=row.get("target_path")
  try:code=int(row.get("status_code",301))
  except (ValueError,TypeError):raise ValueError("Invalid redirect status") from None
  if not _path(src):raise ValueError("Unsafe XUYI redirect source")
  if not _target(dst):raise ValueError("Unsafe XUYI redirect destination")
  if code not in (301,302):raise ValueError("Only 301 and 302 are supported")
  if src==dst:raise ValueError("Self redirect")
  if src in seen:raise ValueError("Duplicate redirect source")
  seen.add(src);output.append(f"{src} {dst} {code}")
 return output