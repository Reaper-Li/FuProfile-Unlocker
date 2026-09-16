#!/usr/bin/env python3
"""Generate local-only Fujifilm-look DCPs for every validated RAW camera."""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
PREFLIGHT_PATH = PROJECT_DIR / "reports" / "raw-compatibility.json"
OUTPUT_ROOT = PROJECT_DIR / "generated" / "profiles"
WORK_ROOT = PROJECT_DIR / "generated" / "work"
REPORT_PATH = PROJECT_DIR / "reports" / "profile-generation.json"
DCP_TOOL = (
    PROJECT_DIR
    / "tools"
    / "vendor"
    / "dcptool"
    / "dcpTool_1_10_0"
    / "Binaries"
    / "macOS"
    / "dcpTool"
)
TABLE_ROOT = (
    PROJECT_DIR
    / "tools"
    / "vendor"
    / "fujifilm-camera-profiles"
    / "FujifilmCameraProfiles-master"
    / "xml tables"
)

STYLES = {
    "PROVIA Standard": "provia.txt",
    "Velvia Vivid": "velvia.txt",
    "ASTIA Soft": "astia.txt",
    "Classic Chrome": "classic chrome.txt",
    "REALA ACE": "reala ace.txt",
    "PRO Neg. Hi": "pro neg hi.txt",
    "PRO Neg. Std": "pro neg std.txt",
    "ETERNA Cinema": "eterna.txt",
}


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", value).strip()


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def compatible_model(raw_model: str, profile_model: str) -> bool:
    raw_key = normalized(raw_model)
    profile_key = normalized(profile_model)
    return raw_key == profile_key or raw_key.endswith(profile_key) or profile_key.endswith(raw_key)


def decompile(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(DCP_TOOL), "-d", str(source), str(destination)],
        check=True,
        capture_output=True,
        text=True,
    )


def compile_profile(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(DCP_TOOL), "-c", str(source), str(destination)],
        check=True,
        capture_output=True,
        text=True,
    )


def load_style_fragment(path: Path) -> list[ET.Element]:
    text = path.read_text(encoding="utf-8")
    root = ET.fromstring(f"<fragment>{text}</fragment>")
    children = list(root)
    names = [child.tag for child in children]
    if names != ["LookTable", "ToneCurve"]:
        raise ValueError(f"Unexpected style fragment structure in {path}: {names}")
    return children


def set_text(root: ET.Element, name: str, value: str) -> None:
    element = root.find(name)
    if element is None:
        element = ET.SubElement(root, name)
    element.text = value


def replace_rendering(root: ET.Element, style_elements: list[ET.Element]) -> None:
    for tag in ("LookTable", "ToneCurve"):
        current = root.find(tag)
        if current is not None:
            root.remove(current)

    insertion_point = len(root)
    for index, child in enumerate(root):
        if child.tag in {
            "ProfileCalibrationSignature",
            "UniqueCameraModelRestriction",
            "ProfileLookTableEncoding",
            "BaselineExposureOffset",
            "DefaultBlackRender",
        }:
            insertion_point = index
            break

    for offset, element in enumerate(style_elements):
        root.insert(insertion_point + offset, copy.deepcopy(element))


def verify_profile(path: Path, expected_name: str, expected_model: str, verify_xml: Path) -> dict:
    decompile(path, verify_xml)
    root = ET.parse(verify_xml).getroot()
    actual_name = root.findtext("ProfileName", default="")
    actual_model = root.findtext("UniqueCameraModelRestriction", default="")
    return {
        "profile_name": actual_name,
        "camera_model_restriction": actual_model,
        "has_look_table": root.find("LookTable") is not None,
        "has_tone_curve": root.find("ToneCurve") is not None,
        "valid": actual_name == expected_name
        and compatible_model(expected_model, actual_model)
        and root.find("LookTable") is not None
        and root.find("ToneCurve") is not None,
    }


def main() -> int:
    if not DCP_TOOL.is_file():
        raise FileNotFoundError(f"dcpTool is missing: {DCP_TOOL}")
    preflight = json.loads(PREFLIGHT_PATH.read_text(encoding="utf-8"))
    style_fragments = {
        name: load_style_fragment(TABLE_ROOT / filename) for name, filename in STYLES.items()
    }
    generated = []
    seen_models = set()

    for camera in preflight["results"]:
        if camera["status"] != "ready":
            continue
        if camera.get("generate_test_profiles", True) is False:
            continue
        base_dcp = Path(camera["adobe_standard_dcp"])
        model = camera["actual_model"]
        model_key = normalized(model)
        if model_key in seen_models:
            continue
        seen_models.add(model_key)
        camera_work = WORK_ROOT / camera["brand"] / camera["camera"]
        base_xml = camera_work / "base.xml"
        decompile(base_dcp, base_xml)

        for style_name, fragment in style_fragments.items():
            tree = ET.parse(base_xml)
            root = tree.getroot()
            profile_name = f"Camera FUJIFILM {style_name}"
            replace_rendering(root, fragment)
            set_text(root, "ProfileName", profile_name)
            set_text(root, "ProfileLookTableEncoding", "1")
            set_text(root, "DefaultBlackRender", "1")

            output_name = safe_name(profile_name) + ".dcp"
            source_xml = camera_work / (safe_name(style_name) + ".xml")
            output_dcp = OUTPUT_ROOT / camera["brand"] / camera["camera"] / output_name
            tree.write(source_xml, encoding="utf-8", xml_declaration=True)
            compile_profile(source_xml, output_dcp)

            verification = verify_profile(
                output_dcp,
                profile_name,
                model,
                camera_work / (safe_name(style_name) + ".verify.xml"),
            )
            generated.append(
                {
                    "brand": camera["brand"],
                    "camera": camera["camera"],
                    "model": model,
                    "style": style_name,
                    "base_dcp": str(base_dcp),
                    "output_dcp": str(output_dcp.relative_to(PROJECT_DIR)),
                    **verification,
                }
            )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "dcpTool 1.10",
        "style_data": {
            "source": "https://github.com/abpy/FujifilmCameraProfiles",
            "license": "CC-BY-NC-SA-4.0",
            "redistribution": "Generated DCPs are local test artifacts and must not be redistributed with the application.",
        },
        "summary": {
            "cameras": len({item["model"] for item in generated}),
            "styles_per_camera": len(STYLES),
            "profiles_generated": len(generated),
            "profiles_valid": sum(item["valid"] for item in generated),
        },
        "profiles": generated,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    return 0 if report["summary"]["profiles_generated"] == report["summary"]["profiles_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
