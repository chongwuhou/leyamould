"""Make content-hashed display WebPs from authoritative images without editing R2."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, UnidentifiedImageError
import hashlib
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "_local_ops" / "responsive-stage"
MANIFEST = ROOT / "_local_ops" / "responsive-image-manifest.json"
ORIGIN = "https://xuyibottles.com"
MEDIA = re.compile(r"/media/(?:excel|ppt|gallery|product|page|shared|blog|group|capability)/[a-zA-Z0-9._-]+\.(?:webp|jpg|png)")


def candidates(snapshot):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from responsive_image_render import LEGACY_REPLACED_SOURCES
    found = set()
    for base in (ROOT / "data", ROOT / "templates" / "site"):
        for p in base.rglob("*"):
            if p.suffix in (".json", ".html"):
                found.update(MEDIA.findall(p.read_text(encoding="utf8")))
    for p in list(ROOT.glob("*.py")) + [ROOT / "scripts" / "render_locales.py"]:
        found.update(MEDIA.findall(p.read_text(encoding="utf8")))
    if snapshot.is_file():
        found.update(MEDIA.findall(snapshot.read_text(encoding="utf8")))
    found.update(f"/media/excel/row-{n:03d}.webp" for n in range(3, 79))
    found.update(f"/media/ppt/slide-{n:03d}.webp" for n in list(range(5, 78)) + list(range(91, 97)))
    for p in (ROOT / "assets").rglob("*"):
        if p.is_file() and p.suffix.lower() in (".webp", ".png", ".jpg", ".jpeg"):
            if "catalog" not in p.relative_to(ROOT / "assets").parts:
                found.add("/" + p.relative_to(ROOT).as_posix())
    return sorted(found - LEGACY_REPLACED_SOURCES)


def source_bytes(src):
    if src.startswith("/assets/"):
        p = ROOT / src.lstrip("/")
        return p.read_bytes() if p.is_file() and p.stat().st_size >= 180 * 1024 else None
    if not MEDIA.fullmatch(src):
        return None
    try:
        with urlopen(Request(ORIGIN + src, method="HEAD", headers={"User-Agent": "XUYI-Image-Build"}), timeout=12) as r:
            size = int(r.headers.get("Content-Length") or 0)
        if 0 < size < 180 * 1024 or size > 12 * 1024 * 1024:
            return None
        with urlopen(Request(ORIGIN + src, headers={"User-Agent": "XUYI-Image-Build"}), timeout=25) as r:
            body = r.read(12 * 1024 * 1024 + 1)
        return body if 180 * 1024 <= len(body) <= 12 * 1024 * 1024 else None
    except (OSError, ValueError):
        return None


def prepare_one(src):
    data = source_bytes(src)
    if not data:
        return src, None
    try:
        with Image.open(BytesIO(data)) as im:
            im.load()
            width, height = im.size
            if width * height > 65_000_000 or width < 720:
                return src, None
            image = im.convert("RGBA" if "A" in im.getbands() else "RGB")
            digest = hashlib.sha256(data).hexdigest()[:28]
            variants = []
            for w in (480, 960, 1600):
                if w >= width:
                    continue
                filename = f"{digest}-{w}.webp"
                target = STAGE / filename
                # This filename is derived from the source content hash.
                # Reuse unchanged local derivatives on repeat clean builds,
                # but always inspect the current original to detect CMS edits.
                if target.is_file() and target.stat().st_size < 0.90 * len(data):
                    variants.append({"w": w, "url": f"/assets/responsive/{filename}"})
                    continue
                thumb = image.resize((w, max(1, round(height * w / width))), Image.Resampling.LANCZOS)
                output = BytesIO()
                thumb.save(output, "WEBP", quality=87, method=4)
                encoded = output.getvalue()
                if len(encoded) >= 0.90 * len(data):
                    continue
                if not target.is_file():
                    target.write_bytes(encoded)
                variants.append({"w": w, "url": f"/assets/responsive/{filename}"})
            return src, {"width": width, "height": height, "variants": variants} if variants else None
    except (OSError, ValueError, UnidentifiedImageError):
        return src, None


def prepare(snapshot):
    # Stage persists only inside the ignored local build workspace; no source
    # asset is mutated. Build artifacts still receive only current variants.
    STAGE.mkdir(parents=True, exist_ok=True)
    if MANIFEST.exists():
        MANIFEST.unlink()
    result = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(prepare_one, src) for src in candidates(snapshot)]
        for future in as_completed(futures):
            src, item = future.result()
            if item:
                result[src] = item
    active = {v["url"].rsplit("/", 1)[-1] for item in result.values()
              for v in item["variants"]}
    for file in STAGE.glob("*.webp"):
        if file.name not in active:
            file.unlink()
    MANIFEST.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True), encoding="utf8")
    outfiles = list(STAGE.glob("*.webp"))
    print("XUYI_RESPONSIVE_PREPARED", len(result), "sources", len(outfiles), "variants",
          round(sum(p.stat().st_size for p in outfiles) / 1048576, 2), "MiB")
    return MANIFEST, STAGE


if __name__ == "__main__":
    prepare(ROOT / "_local_ops" / "build-snapshot.json")
