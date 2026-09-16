#!/usr/bin/env python3
"""Build and download a broad, reproducible CC0 RAW camera corpus."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "RAW"
MANIFEST_PATH = RAW_DIR / "manifest.json"
REPOSITORY_URL = "https://raw.pixls.us/json/getrepository.php?set=all"

BRAND_NAMES = {
    "apple": "Apple",
    "asus": "ASUS",
    "bq": "BQ",
    "canon": "Canon",
    "fujifilm": "Fujifilm",
    "gitup": "Gitup",
    "google": "Google",
    "gopro": "GoPro",
    "hasselblad": "Hasselblad",
    "huawei": "Huawei",
    "kandao": "KanDao",
    "leica": "Leica",
    "minolta": "Minolta",
    "motorola": "Motorola",
    "nikon": "Nikon",
    "olympus": "Olympus",
    "om system": "OM System",
    "oneplus": "OnePlus",
    "panasonic": "Panasonic",
    "parrot": "Parrot",
    "pentax": "Pentax",
    "phase one": "Phase One",
    "raspberrypi": "Raspberry Pi",
    "ricoh": "Ricoh",
    "samsung": "Samsung",
    "sigma": "Sigma",
    "sony": "Sony",
    "xiaomi": "Xiaomi",
    "xiaoyi": "Xiaoyi",
}

LINK_RE = re.compile(r"href='(?P<url>[^']+)'[^>]*>(?P<name>[^<]+)</a>")
CHECKSUM_RE = re.compile(r"sha256 Checksum'>(?P<sha>[0-9a-f]{64})</span>")
SIZE_RE = re.compile(r"\((?P<size>[0-9.]+)(?P<unit>[KMGT]B)\)")
INVALID_PATH_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def canonical_brand(value: str) -> str:
    cleaned = value.strip()
    return BRAND_NAMES.get(cleaned.casefold(), cleaned)


def safe_component(value: str) -> str:
    cleaned = INVALID_PATH_RE.sub("_", html.unescape(value)).strip().rstrip(".")
    return cleaned or "Unknown"


def parse_size(value: str, unit: str) -> int:
    multiplier = {"KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}[unit]
    return round(float(value) * multiplier)


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for row in payload.get("data", []):
        if len(row) < 8 or "publicdomain/zero" not in row[5]:
            continue
        if str(row[0]).strip().casefold() == "adobe dng converter":
            continue
        link = LINK_RE.search(row[7])
        checksum = CHECKSUM_RE.search(row[7])
        size = SIZE_RE.search(row[7])
        if not link or not checksum or not size:
            continue
        brand = canonical_brand(str(row[0]))
        camera = safe_component(str(row[1]))
        filename = safe_component(link.group("name"))
        sample = {
                "brand": brand,
                "camera": camera,
                "filename": filename,
                "url": html.unescape(link.group("url")),
                "license": "CC0-1.0",
                "source_sha256": checksum.group("sha"),
                "source_size_bytes": parse_size(size.group("size"), size.group("unit")),
                "format": Path(filename).suffix.lstrip(".").upper(),
                "capture_mode": str(row[2]).strip(),
                "source_make": str(row[0]).strip(),
                "source_model": str(row[1]).strip(),
                "expected_make": str(row[0]).strip(),
                "expected_model": str(row[1]).strip(),
            }
        if brand == "Fujifilm":
            sample["generate_test_profiles"] = False
        candidates.append(sample)
    return candidates


def select_one_per_model(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for sample in candidates:
        key = (sample["brand"].casefold(), sample["camera"].casefold())
        current = selected.get(key)
        if current is None or sample["source_size_bytes"] < current["source_size_bytes"]:
            selected[key] = sample
    return sorted(selected.values(), key=lambda item: (item["brand"].casefold(), item["camera"].casefold()))


def load_inventory(path: Path | None) -> dict[str, Any]:
    if path:
        return json.loads(path.read_text(encoding="utf-8"))
    request = urllib.request.Request(REPOSITORY_URL, headers={"User-Agent": "LR-Profile-Unlocker/0.2"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def load_manifest() -> dict[str, Any]:
    if MANIFEST_PATH.is_file():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"schema_version": 2, "source": "https://raw.pixls.us/", "samples": []}


def merge_manifest(selected: list[dict[str, Any]]) -> dict[str, Any]:
    manifest = load_manifest()
    samples = list(manifest.get("samples", []))
    existing_models = {
        (canonical_brand(str(item["brand"])).casefold(), str(item["camera"]).casefold())
        for item in samples
    }
    for sample in selected:
        key = (sample["brand"].casefold(), sample["camera"].casefold())
        if key not in existing_models:
            samples.append(sample)
            existing_models.add(key)
    samples.sort(key=lambda item: (str(item["brand"]).casefold(), str(item["camera"]).casefold(), str(item["filename"])))
    manifest.update(
        {
            "schema_version": 2,
            "source": "https://raw.pixls.us/",
            "selection": "One smallest CC0 sample per camera model, plus explicitly retained observation samples.",
            "samples": samples,
        }
    )
    temporary = MANIFEST_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(MANIFEST_PATH)
    return manifest


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quoted_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, urllib.parse.quote(parts.path, safe="/%"), parts.query, parts.fragment)
    )


def download(sample: dict[str, Any]) -> tuple[str, str, int]:
    relative = Path(str(sample["brand"])) / str(sample["camera"]) / str(sample["filename"])
    destination = RAW_DIR / relative
    expected = str(sample.get("source_sha256", ""))
    if destination.is_file() and (not expected or sha256(destination) == expected):
        return "existing", str(relative), destination.stat().st_size

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    url = quoted_url(str(sample["url"]))
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            offset = partial.stat().st_size if partial.is_file() else 0
            headers = {"User-Agent": "LR-Profile-Unlocker/0.2"}
            if offset:
                headers["Range"] = f"bytes={offset}-"
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=120) as response:
                append = offset > 0 and response.status == 206
                with partial.open("ab" if append else "wb") as stream:
                    shutil.copyfileobj(response, stream, length=1024 * 1024)
            if expected and sha256(partial) != expected:
                partial.unlink(missing_ok=True)
                raise ValueError("SHA-256 mismatch")
            partial.replace(destination)
            return "downloaded", str(relative), destination.stat().st_size
        except (OSError, urllib.error.URLError, ValueError) as error:
            last_error = error
            time.sleep(2**attempt)
    return "failed", f"{relative}: {last_error}", 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, help="Use a previously downloaded repository JSON file")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--brand", action="append", help="Limit synchronization to one or more brands")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()

    selected = select_one_per_model(source_rows(load_inventory(args.inventory)))
    if args.brand:
        brands = {canonical_brand(item).casefold() for item in args.brand}
        selected = [item for item in selected if item["brand"].casefold() in brands]
    manifest = merge_manifest(selected)
    selected_keys = {(item["brand"].casefold(), item["camera"].casefold()) for item in selected}
    queue = [
        item for item in manifest["samples"]
        if (canonical_brand(str(item["brand"])).casefold(), str(item["camera"]).casefold()) in selected_keys
    ]
    planned_bytes = sum(int(item.get("source_size_bytes", 0)) for item in queue)
    print(f"Planned: {len(queue)} files, approximately {planned_bytes / 1024**3:.2f} GiB", flush=True)
    if args.plan_only:
        return 0

    counts = {"downloaded": 0, "existing": 0, "failed": 0}
    total_bytes = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(download, sample): sample for sample in queue}
        for index, future in enumerate(as_completed(futures), start=1):
            status, detail, size = future.result()
            counts[status] += 1
            total_bytes += size
            print(
                f"[{index}/{len(queue)}] {status.upper():10} {detail} "
                f"({total_bytes / 1024**3:.2f} GiB checked)",
                flush=True,
            )

    print(json.dumps(counts, ensure_ascii=False), flush=True)
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
