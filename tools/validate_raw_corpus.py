#!/usr/bin/env python3
"""Validate RAW identity and local Adobe base-profile availability."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_DIR / "RAW" / "manifest.json"
REPORT_JSON = PROJECT_DIR / "reports" / "raw-compatibility.json"
REPORT_MD = PROJECT_DIR / "reports" / "raw-compatibility.md"
ADOBE_ROOT = Path("/Library/Application Support/Adobe/CameraRaw/CameraProfiles")

EXIFTOOL_CANDIDATES = (
    Path("/opt/homebrew/bin/exiftool"),
    Path("/usr/local/bin/exiftool"),
    Path("/Applications/Telemetry Overlay.app/Contents/Resources/static/exiftool"),
    Path("/Applications/XnViewMP.app/Contents/Resources/AddOn/exiftool"),
    Path("/Applications/Pixea.app/Contents/Resources/exiftool/exiftool"),
)


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_exiftool() -> Path:
    for candidate in EXIFTOOL_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("ExifTool was not found in any known location")


def read_metadata(exiftool: Path, raw_path: Path) -> dict[str, str]:
    command = [
        str(exiftool),
        "-json",
        "-Make",
        "-Model",
        "-UniqueCameraModel",
        "-FileType",
        str(raw_path),
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)[0]


def find_adobe_standard(model: str) -> Path | None:
    root = ADOBE_ROOT / "Adobe Standard"
    if not root.is_dir():
        return None
    model_key = normalized(model)
    matches = []
    for candidate in root.glob("*.dcp"):
        stem_key = normalized(candidate.stem.replace("Adobe Standard", ""))
        if stem_key == model_key or stem_key.endswith(model_key) or model_key.endswith(stem_key):
            matches.append(candidate)
    if not matches:
        return None
    matches.sort(key=lambda path: (" v2" not in path.stem.casefold(), path.name))
    return matches[0]


def find_camera_matching_dir(model: str) -> Path | None:
    root = ADOBE_ROOT / "Camera"
    if not root.is_dir():
        return None
    model_key = normalized(model)
    matches = []
    for candidate in root.iterdir():
        if not candidate.is_dir():
            continue
        candidate_key = normalized(candidate.name)
        if candidate_key == model_key or candidate_key.endswith(model_key) or model_key.endswith(candidate_key):
            matches.append(candidate)
    return sorted(matches)[0] if matches else None


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    exiftool = find_exiftool()
    results = []

    for sample in manifest["samples"]:
        raw_path = PROJECT_DIR / "RAW" / sample["brand"] / sample["camera"] / sample["filename"]
        result = dict(sample)
        result["path"] = str(raw_path.relative_to(PROJECT_DIR))
        result["downloaded"] = raw_path.is_file()
        if not raw_path.is_file():
            result["status"] = "missing"
            results.append(result)
            continue

        try:
            metadata = read_metadata(exiftool, raw_path)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
            result["status"] = "metadata_error"
            result["error"] = str(error)
            results.append(result)
            continue

        actual_make = metadata.get("Make", "")
        actual_model = metadata.get("UniqueCameraModel") or metadata.get("Model", "")
        adobe_standard = find_adobe_standard(actual_model)
        camera_dir = find_camera_matching_dir(actual_model)
        camera_profiles = sorted(camera_dir.glob("*.dcp")) if camera_dir else []

        file_sha256 = sha256(raw_path)
        result.update(
            {
                "size_bytes": raw_path.stat().st_size,
                "sha256": file_sha256,
                "source_sha256_matches": file_sha256 == sample.get("source_sha256"),
                "actual_make": actual_make,
                "actual_model": actual_model,
                "file_type": metadata.get("FileType", ""),
                "make_matches": normalized(actual_make) == normalized(sample["expected_make"]),
                "model_matches": normalized(actual_model) == normalized(sample["expected_model"]),
                "adobe_standard_dcp": str(adobe_standard) if adobe_standard else None,
                "camera_matching_directory": str(camera_dir) if camera_dir else None,
                "camera_matching_dcp_count": len(camera_profiles),
            }
        )
        result["status"] = (
            "ready"
            if result["make_matches"]
            and result["model_matches"]
            and result["source_sha256_matches"]
            and adobe_standard
            else "needs_attention"
        )
        results.append(result)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "exiftool": str(exiftool),
        "adobe_camera_profiles_root": str(ADOBE_ROOT),
        "summary": {
            "total": len(results),
            "ready": sum(result["status"] == "ready" for result in results),
            "missing": sum(result["status"] == "missing" for result in results),
            "needs_attention": sum(result["status"] == "needs_attention" for result in results),
        },
        "results": results,
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# RAW profile-generation preflight",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "| Brand | Camera | Format | EXIF model | Adobe Standard | Camera Matching DCPs | Status |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for result in results:
        lines.append(
            "| {brand} | {camera} | {format} | {model} | {base} | {count} | {status} |".format(
                brand=result["brand"],
                camera=result["camera"],
                format=result["format"],
                model=result.get("actual_model", "—"),
                base="yes" if result.get("adobe_standard_dcp") else "no",
                count=result.get("camera_matching_dcp_count", 0),
                status=result["status"],
            )
        )
    lines.extend(
        [
            "",
            "`ready` means the RAW identity and source hash match the manifest, and this machine has a usable Adobe Standard DCP for the exact model. Camera Matching DCPs are diagnostic only because some Fujifilm profiles are stored internally or as XMP wrappers.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(report["summary"], ensure_ascii=False))
    return 0 if report["summary"]["ready"] == report["summary"]["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
