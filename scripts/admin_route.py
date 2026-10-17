"""XUYI build-only admin route sanitizer. Never stores credentials."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
ROUTES=json.loads((ROOT/"data/route-manifest.json").read_text(encoding="utf8"))
RESERVED={str(r["path"]).strip("/").split("/")[0] for r in ROUTES if str(r.get("path","")).strip("/")}
RESERVED.update({"api","assets","media","blog","admin","es","pt","ru","tr","de","fr","ar","zh","id"})
def admin_path(value):
    path=value if value is not None else "admin"
    if not isinstance(path,str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,47}",path):
        raise ValueError("Invalid XUYI admin route")
    if path!="admin" and path in RESERVED:
        raise ValueError("Admin route collides with a public URL")
    return path
