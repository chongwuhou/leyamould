#!/usr/bin/env python3
"""Owner-gated, create-only publication of the 58 reviewed 2026-11-03 factory models."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_PATH = ROOT / "scripts" / "fixtures" / "factory-catalog-import-2026-11-03.json"
IMAGES_ZIP_PATH = ROOT / "scripts" / "fixtures" / "factory-catalog-images-2026-11-03.zip"
MANIFEST_PATH = ROOT / "data" / "factory-catalog-manifest-2026-11-03.json"
ORIGIN = "https://xuyibottles.com"
EXPECTED_REPOSITORY = "chongwuhou/xuyi-drinkware-site"
EXPECTED_COMMIT = "Publish 58 new XUYI products from factory catalog 2026-11-03"
LANGUAGES = {"en", "es", "pt", "ru", "tr"}


def fail(message: str) -> None:
    raise RuntimeError(message)


def require_owner_gate() -> str:
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if os.environ.get("GITHUB_ACTIONS") != "true":
        fail("This import may run only inside the reviewed GitHub Actions release.")
    if os.environ.get("OWNER_FACTORY_CATALOG_20261103") != "1":
        fail("The owner-approved 58-product release flag is missing.")
    if os.environ.get("GITHUB_REPOSITORY") != EXPECTED_REPOSITORY:
        fail("Unexpected GitHub repository.")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        fail("Factory catalog publication is restricted to main.")
    if os.environ.get("GITHUB_EVENT_NAME") != "push":
        fail("Factory catalog publication requires the explicit main-branch push.")
    if not token:
        fail("CLOUDFLARE_API_TOKEN is unavailable.")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).is_file():
        fail("GitHub push event payload is unavailable.")
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    message = str((event.get("head_commit") or {}).get("message") or "").strip()
    if message != EXPECTED_COMMIT:
        fail("The push commit message does not match the explicit 58-product release gate.")
    return token


def read_sources() -> tuple[dict, dict]:
    bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("site") != "xuyi-drinkware-site" or manifest.get("recordCount") != 58:
        fail("The factory catalog manifest is not the reviewed 58-model manifest.")
    if len(manifest.get("models", [])) != 58 or len(bundle.get("records", [])) != 58:
        fail("Expected exactly 58 factory models.")
    if bundle.get("sourceSha256") != manifest.get("sourceSha256"):
        fail("Source PDF SHA-256 does not match the manifest.")
    if bundle.get("sourceDocument") not in (None, manifest.get("sourceDocument")):
        fail("Source PDF filename does not match the manifest.")
    return bundle, manifest


def prepare_records(bundle: dict, manifest: dict, images: zipfile.ZipFile) -> list[dict]:
    expected = {item["model"]: item for item in manifest["models"]}
    prepared: list[dict] = []
    seen: set[str] = set()
    image_hashes: set[str] = set()

    for record in bundle["records"]:
        model = str(record.get("model") or "").lower()
        spec = expected.get(model)
        if not spec or model in seen:
            fail(f"Unknown or duplicate model in fixture: {model}")
        seen.add(model)

        content = dict(record.get("content") or {})
        if record.get("status") != "published":
            fail(f"Model is not approved for publication: {model}")
        if record.get("imageMime") != "image/webp":
            fail(f"Expected a WebP source image for {model}.")
        if record.get("imageSha256") != spec["imageSha256"]:
            fail(f"Image SHA-256 does not match manifest for {model}.")
        if content.get("factoryModel") != spec["factoryModel"]:
            fail(f"Factory model label does not match manifest for {model}.")
        if content.get("category") != spec["category"]:
            fail(f"Product category does not match manifest for {model}.")
        if str(content.get("sourcePage")) != str(spec["sourcePage"]):
            fail(f"PDF source page does not match manifest for {model}.")
        if content.get("sourceDocument") != manifest["sourceDocument"]:
            fail(f"PDF source filename does not match manifest for {model}.")
        if content.get("sourceSha256") != manifest["sourceSha256"]:
            fail(f"PDF source SHA-256 does not match manifest for {model}.")
        if content.get("sourceImageSha256") != spec["imageSha256"]:
            fail(f"Source image SHA-256 does not match manifest for {model}.")
        if content.get("imageReviewStatus") != "visually_reviewed_source_crop":
            fail(f"Image review status is not approved for {model}.")
        if content.get("qcStatus") not in {"source_read", "needs_confirmation"}:
            fail(f"Unknown source-QC status for {model}.")
        if content.get("newProduct") is not True:
            fail(f"Model is not marked as a new product: {model}")

        raw = images.read(model + ".webp")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != spec["imageSha256"]:
            fail(f"Decoded image bytes failed SHA-256 verification for {model}.")
        if len(raw) < 200 or len(raw) > 6 * 1024 * 1024:
            fail(f"Image size is outside the approved upload range for {model}.")
        if raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
            fail(f"Image is not a valid WebP container for {model}.")
        if digest in image_hashes:
            fail(f"Image bytes are unexpectedly reused by multiple models: {model}")
        image_hashes.add(digest)

        alt = record.get("imageAlt") or {}
        if set(alt) != LANGUAGES or any(not isinstance(alt.get(code), str) or not alt[code].strip() for code in LANGUAGES):
            fail(f"Five non-empty reviewed image ALT languages are required for {model}.")
        if any(len(alt[code]) > 180 for code in LANGUAGES):
            fail(f"Image ALT text is too long for {model}.")

        if content["category"] == "Titanium Vacuum Cups":
            if "pure titanium" in str(content.get("name", "")).lower():
                fail(f"Unqualified titanium-purity claim remains in the title for {model}.")
            if "confirm exact sku" not in str(content.get("material", "")).lower():
                fail(f"Titanium material qualification is missing for {model}.")

        image_path = f"/media/product/{digest[:32]}.webp"
        if content.get("image") not in (None, "", image_path):
            fail(f"Unexpected product image path for {model}.")
        content["image"] = image_path

        prepared.append({
            "model": model,
            "content": content,
            "imageAlt": alt,
            "imageSha256": digest,
            "imageBytes": raw,
            "imagePath": image_path,
            "sourcePage": spec["sourcePage"],
        })

    if seen != set(expected):
        missing = sorted(set(expected) - seen)
        fail("Fixture is missing manifest models: " + ", ".join(missing))
    if len(image_hashes) != 58:
        fail("Expected 58 unique reviewed product images.")
    return prepared


def request_bytes(url: str, token: str | None, method: str = "GET",
                  data: bytes | None = None, content_type: str | None = None,
                  attempts: int = 4) -> bytes:
    headers = {"User-Agent": "XUYI-Reviewed-Factory-Catalog-Import/1.0"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if content_type:
        headers["Content-Type"] = content_type

    for attempt in range(attempts):
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=75) as response:
                if response.status < 200 or response.status >= 300:
                    fail(f"{method} {url} returned HTTP {response.status}.")
                return response.read()
        except urllib.error.HTTPError as error:
            detail = error.read(1200).decode("utf-8", "replace")
            if error.code in {429, 500, 502, 503, 504} and attempt + 1 < attempts:
                time.sleep(2 ** attempt)
                continue
            fail(f"{method} {url} returned HTTP {error.code}: {detail}")
        except urllib.error.URLError as error:
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
                continue
            fail(f"{method} {url} failed: {error}")
    fail(f"{method} {url} exhausted retries.")


def request_json(url: str, token: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    raw = request_bytes(url, token, method, data, "application/json" if data is not None else None)
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        fail(f"{method} {url} returned invalid JSON: {error}")
    if not isinstance(value, dict):
        fail(f"{method} {url} returned an unexpected response.")
    return value


def multipart_body(item: dict, manifest: dict) -> tuple[bytes, str]:
    boundary = "----XUYIFactoryCatalog" + uuid.uuid4().hex
    fields = {
        "model": item["model"],
        "sourceDocument": manifest["sourceDocument"],
        "sourceSha256": manifest["sourceSha256"],
        "sourcePage": str(item["sourcePage"]),
        "imageReviewStatus": item["content"]["imageReviewStatus"],
        "sha256": item["imageSha256"],
    }
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8")
        )
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{item['model']}.webp\"\r\n"
        "Content-Type: image/webp\r\n\r\n".encode("utf-8")
        + item["imageBytes"] + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode("ascii"))
    return b"".join(parts), "multipart/form-data; boundary=" + boundary


def upload_image(item: dict, manifest: dict, token: str) -> dict:
    body, content_type = multipart_body(item, manifest)
    raw = request_bytes(
        ORIGIN + "/api/admin/factory-catalog-images-20261103",
        token, "POST", body, content_type,
    )
    result = json.loads(raw)
    if result.get("saved") is not True or result.get("sha256") != item["imageSha256"]:
        fail(f"R2 upload endpoint did not confirm {item['model']}: {result}")
    return result


def verify_public_image(item: dict) -> str:
    raw = request_bytes(ORIGIN + item["imagePath"], None, "GET")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != item["imageSha256"]:
        fail(f"Public R2 read-back SHA-256 mismatch for {item['model']}.")
    return item["model"]


def snapshot_models(token: str) -> tuple[dict, set[str]]:
    snapshot = request_json(ORIGIN + "/api/build-snapshot", token)
    products = snapshot.get("products")
    if not isinstance(products, list):
        fail("The authenticated D1 build snapshot did not return a product list.")
    models = {str(row.get("model") or "").lower() for row in products if row.get("model")}
    return snapshot, models


def main() -> None:
    token = require_owner_gate()
    bundle, manifest = read_sources()
    with zipfile.ZipFile(IMAGES_ZIP_PATH, "r") as images:
        records = prepare_records(bundle, manifest, images)
    batch_models = {item["model"] for item in records}

    before_snapshot, before_models = snapshot_models(token)
    print(f"Preflight: {len(before_models)} published products; target batch={len(records)}; source={manifest['sourceSha256']}")

    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(upload_image, item, manifest, token): item["model"] for item in records}
        for future in concurrent.futures.as_completed(futures):
            model = futures[future]
            try:
                result = future.result()
                print(f"R2 image ready: {model} ({'existing' if result.get('unchanged') else 'uploaded'})")
            except Exception as error:
                errors.append(f"{model}: {error}")
    if errors:
        fail("Image stage failed; no D1 products were published. Retry is safe. " + " | ".join(errors[:8]))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(verify_public_image, item): item["model"] for item in records}
        verified = set()
        for future in concurrent.futures.as_completed(futures):
            verified.add(future.result())
    if verified != batch_models:
        fail("Public R2 image read-back did not verify all 58 images.")

    commit_records = [{
        "model": item["model"],
        "status": "published",
        "imageSha256": item["imageSha256"],
        "content": item["content"],
        "imageAlt": item["imageAlt"],
    } for item in records]
    result = request_json(
        ORIGIN + "/api/admin/factory-catalog-20261103",
        token, "POST",
        {
            "site": "xuyi-drinkware-site",
            "sourceDocument": manifest["sourceDocument"],
            "sourceSha256": manifest["sourceSha256"],
            "records": commit_records,
        },
    )
    if result.get("saved") is not True or result.get("publishedProducts") != 58:
        fail("D1 create-only batch did not confirm all 58 published products: " + json.dumps(result, ensure_ascii=False))
    if result.get("requested") != 58 or result.get("insertedProducts", 0) + result.get("existingProducts", 0) != 58:
        fail("D1 batch counts are inconsistent: " + json.dumps(result, ensure_ascii=False))

    after_snapshot, after_models = snapshot_models(token)
    if not batch_models.issubset(after_models):
        fail("D1 build snapshot is missing one or more of the 58 published models.")
    if not before_models.issubset(after_models):
        fail("The product snapshot lost an existing published model during import.")
    unexpected = (after_models - before_models) - batch_models
    if unexpected:
        fail("Unexpected non-batch products appeared during this import: " + ", ".join(sorted(unexpected)[:20]))

    print(json.dumps({
        "result": "58-product factory catalog batch committed",
        "requested": 58,
        "insertedProducts": result.get("insertedProducts"),
        "alreadyPublished": result.get("existingProducts"),
        "verifiedPublicImages": len(verified),
        "beforePublishedProducts": len(before_models),
        "afterPublishedProducts": len(after_models),
        "publishRevision": result.get("publishRevision"),
        "sourceSha256": manifest["sourceSha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("FACTORY_CATALOG_IMPORT_FAILED:", error, file=sys.stderr)
        raise