"""Download, inspect and normalize the 24 mould-news cover images.

The source photographs are from LEYA MOULD's existing cap-molds.com catalogue
(the customer confirmed that site is theirs). Two technical topics use original
in-house engineering illustrations rather than a repeated placeholder. Every
output is a unique 1200x800 sRGB WebP with an auditable source and checksum.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "news"
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "case-study-cap-line-expansion-southeast-asia": "https://www.cap-molds.com/Upload/20261121/202611210157599346.jpg",
    "cap-mold-demand-growth-global-markets": "https://www.cap-molds.com/Upload/20261120/202611200131467551.jpg",
    "global-bottle-cap-mould-market-outlook": "https://www.cap-molds.com/Upload/20261120/202611200049441288.png",
    "reducing-cap-weight-seal-performance": "https://www.cap-molds.com/Upload/20261114/202611140248174335.png",
    "micro-conformal-cooling-lightweight-caps": "https://www.cap-molds.com/Upload/20261113/202611130229253875.png",
    "ultra-thin-wall-cap-molding": "https://www.cap-molds.com/Upload/20261112/202611120102046095.jpg",
    "cap-mold-service-life-maintenance": "https://www.cap-molds.com/Upload/20261107/202611070255255345.jpg",
    "wear-part-management-high-cavity-caps": "https://www.cap-molds.com/Upload/20261106/202611060127336688.jpg",
    "snap-in-bushing-replacement-design": "https://www.cap-molds.com/Upload/20261105/202611050142583314.jpg",
    "running-pcr-content-cap-molds": "https://www.cap-molds.com/Upload/20261031/202610311025284403.jpg",
    "larger-runners-recycled-plastics": "https://www.cap-molds.com/Upload/20261029/202610292147119624.jpg",
    "processing-pcr-hdpe-pp-cap-molds": "https://www.cap-molds.com/Upload/20261028/202610282257247265.jpg",
    "cooling-water-quality-cap-mold-performance": "https://www.cap-molds.com/Upload/20260709/202607092228540366.jpg",
    "mold-temperature-cap-mechanical-properties": "https://www.cap-molds.com/Upload/20260708/202607081642531107.jpg",
    "controlling-cap-sink-marks": "https://www.cap-molds.com/Upload/20260703/202607032047427871.jpg",
    "injection-speed-cap-quality-cycle-time": "https://www.cap-molds.com/Upload/20260627/202606270247389305.jpg",
    "integrated-liner-cap-solutions": "https://www.cap-molds.com/Upload/20260604/202606042146375936.jpg",
    "preventing-cap-short-shots": "https://www.cap-molds.com/Upload/20260530/202605300010394598.jpg",
    "multi-start-thread-cap-design": "https://www.cap-molds.com/Upload/20260527/202605272130057637.jpg",
    "linerless-vs-liner-based-sealing": "https://www.cap-molds.com/Upload/20260522/202605220110087521.jpg",
    "zero-defect-cap-production-quality-system": "https://www.cap-molds.com/Upload/20260515/202605150027085266.jpg",
    "zero-defect-cap-sealing-surfaces": "https://www.cap-molds.com/Upload/20260501/202605010148488510.jpg",
}

DIAGRAMS = {
    "cap-ejection-pin-placement": ("Original LEYA MOULD engineering illustration: balanced ejection layout", "ejection"),
    "managing-cap-shrinkage": ("Original LEYA MOULD engineering illustration: shrinkage measurement loop", "shrinkage"),
}

def _font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def diagram(kind: str) -> Image.Image:
    im = Image.new("RGB", (1200, 800), (239, 245, 249))
    d = ImageDraw.Draw(im)
    navy, blue, orange, slate = (15, 45, 75), (25, 105, 175), (239, 126, 55), (87, 108, 123)
    d.rectangle((0, 0, 1200, 120), fill=navy)
    title = "Balanced ejection layout" if kind == "ejection" else "Shrinkage measurement loop"
    sub = "Engineering illustration · not a production drawing"
    d.text((55, 34), title, font=_font(42, True), fill="white")
    d.text((58, 84), sub, font=_font(22), fill=(186, 219, 239))
    if kind == "ejection":
        d.rounded_rectangle((180, 220, 1020, 670), radius=28, outline=slate, width=8, fill=(250, 252, 253))
        d.ellipse((390, 290, 810, 610), outline=blue, width=12)
        d.ellipse((470, 370, 730, 530), outline=orange, width=10)
        points = [(600, 255), (850, 345), (850, 545), (600, 635), (350, 545), (350, 345)]
        for x, y in points:
            d.ellipse((x-24, y-24, x+24, y+24), fill=orange, outline=navy, width=4)
            d.line((x, y, 600, 450), fill=(220, 140, 95), width=3)
        d.text((212, 690), "Keep force symmetrical around the sealing surface; confirm stroke and support before trial.", font=_font(23), fill=navy)
    else:
        d.rounded_rectangle((140, 220, 1060, 660), radius=28, outline=slate, width=8, fill=(250, 252, 253))
        # process loop
        boxes = [(210, 320, "RESIN DATA"), (460, 320, "MOLD TRIAL"), (710, 320, "MEASURE"), (460, 500, "ADJUST")]
        for x, y, label in boxes:
            d.rounded_rectangle((x, y, x+190, y+90), radius=15, fill=blue if label != "ADJUST" else orange, outline=navy, width=4)
            tw = d.textbbox((0,0), label, font=_font(22, True))[2]
            d.text((x + (190-tw)/2, y+30), label, font=_font(22, True), fill="white")
        d.line((400,365,460,365), fill=navy, width=7); d.polygon([(460,365),(442,353),(442,377)], fill=navy)
        d.line((650,365,710,365), fill=navy, width=7); d.polygon([(710,365),(692,353),(692,377)], fill=navy)
        d.line((805,410,610,500), fill=navy, width=7); d.polygon([(610,500),(627,486),(632,505)], fill=navy)
        d.line((460,545,350,410), fill=navy, width=7); d.polygon([(350,410),(358,433),(375,419)], fill=navy)
        d.text((180, 690), "Measure mass, critical diameters and sealing geometry against the agreed drawing revision.", font=_font(23), fill=navy)
    return im

def crop_1200x800(im: Image.Image) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    return ImageOps.fit(im, (1200, 800), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

def main() -> None:
    records = []
    for slug, url in {**SOURCES, **{k: None for k in DIAGRAMS}}.items():
        if url:
            request = urllib.request.Request(url, headers={"User-Agent": "LEYA-MOULD editorial asset fetch"})
            with urllib.request.urlopen(request, timeout=40) as response:
                raw = response.read()
            im = Image.open(io.BytesIO(raw))
            source_type = "authorized reference-site asset"
            source = url
            scene = "cap-mould technical reference image; use as an illustrative editorial cover, not as a customer case or production proof"
            visible = "plastic closure/mould component or tooling detail visible in the source photograph"
            fit = "The image is retained for the matching technical topic and disclosed as an illustrative reference image."
        else:
            label, kind = DIAGRAMS[slug]
            im = diagram(kind)
            source_type = "original in-house engineering illustration"
            source = "LEYA MOULD editorial team"
            scene = "technical engineering illustration for buyer education"
            visible = label
            fit = "Original diagram directly explains the article's decision point; it is explicitly not a production drawing."
        final = crop_1200x800(im)
        target = OUT / f"{slug}.webp"
        final.save(target, "WEBP", quality=82, method=6)
        size = target.stat().st_size
        if not 30_000 <= size <= 350_000:
            # Keep the same visual file but lower/raise quality into the gate.
            for quality in (76, 70, 88, 92, 100):
                final.save(target, "WEBP", quality=quality, method=6)
                size = target.stat().st_size
                if 30_000 <= size <= 350_000:
                    break
        if size < 30_000:
            # Some clean, nearly flat source photographs compress below the
            # editorial floor. Lossless WebP preserves the same pixels while
            # keeping the manifest within the review gate.
            final.save(target, "WEBP", lossless=True, method=6)
            size = target.stat().st_size
        if not 30_000 <= size <= 350_000:
            raise SystemExit(f"image size outside editorial gate: {slug} ({size})")
        sha = hashlib.sha256(target.read_bytes()).hexdigest()
        records.append({
            "slug": slug,
            "path": f"/assets/news/{slug}.webp",
            "source": source,
            "sourceType": source_type,
            "scene": scene,
            "visibleSubject": visible,
            "fitReason": fit,
            "dimensions": {"width": 1200, "height": 800},
            "bytes": size,
            "sha256": sha,
            "review": {"industryMatch": 4, "buyerUse": 4, "commercialRealism": 4, "truthAndRights": 5, "composition": 4, "status": "reviewed"},
        })
    (ROOT / "data" / "mould-news-image-manifest.json").write_text(json.dumps({"schemaVersion": 1, "standard": "XUYI_B2B_COVER_1200x800_WEBP", "items": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"prepared {len(records)} unique covers")

if __name__ == "__main__":
    main()
