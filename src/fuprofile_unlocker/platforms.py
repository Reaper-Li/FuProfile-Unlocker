from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path


APP_FOLDER = "FuProfile Unlocker"


def system_name() -> str:
    return platform.system().lower()


def resource_roots() -> list[Path]:
    roots: list[Path] = []
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        roots.append(Path(bundle_root))
    roots.extend(
        [
            Path(__file__).resolve().parents[2],
            Path(__file__).resolve().parents[2].parent,
        ]
    )
    return roots


def adobe_standard_roots() -> list[Path]:
    home = Path.home()
    if system_name() == "darwin":
        return [
            Path("/Library/Application Support/Adobe/CameraRaw/CameraProfiles/Adobe Standard"),
            home / "Library/Application Support/Adobe/CameraRaw/CameraProfiles/Adobe Standard",
        ]
    if system_name() == "windows":
        program_data = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))
        app_data = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))
        return [
            program_data / "Adobe/CameraRaw/CameraProfiles/Adobe Standard",
            app_data / "Adobe/CameraRaw/CameraProfiles/Adobe Standard",
        ]
    return [home / ".local/share/Adobe/CameraRaw/CameraProfiles/Adobe Standard"]


def install_root() -> Path:
    home = Path.home()
    if system_name() == "darwin":
        return home / "Library/Application Support/Adobe/CameraRaw/CameraProfiles" / APP_FOLDER
    if system_name() == "windows":
        app_data = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))
        return app_data / "Adobe/CameraRaw/CameraProfiles" / APP_FOLDER
    return home / ".local/share/Adobe/CameraRaw/CameraProfiles" / APP_FOLDER


def find_exiftool() -> Path:
    executable = "exiftool.exe" if system_name() == "windows" else "exiftool"
    candidates: list[Path] = []
    configured = os.environ.get("FUPROFILE_EXIFTOOL")
    if configured:
        candidates.append(Path(configured))
    for root in resource_roots():
        candidates.extend(
            [
                root / "resources/bin" / system_name() / executable,
                root / "tools/vendor/exiftool" / system_name() / executable,
            ]
        )
    located = shutil.which(executable)
    if located:
        candidates.append(Path(located))
    if system_name() == "darwin":
        candidates.extend(
            [
                Path("/opt/homebrew/bin/exiftool"),
                Path("/usr/local/bin/exiftool"),
                Path("/Applications/Telemetry Overlay.app/Contents/Resources/static/exiftool"),
                Path("/Applications/XnViewMP.app/Contents/Resources/AddOn/exiftool"),
                Path("/Applications/Pixea.app/Contents/Resources/exiftool/exiftool"),
            ]
        )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "未找到 ExifTool。请安装 ExifTool，或通过 FUPROFILE_EXIFTOOL 指定它的位置。"
    )


def find_dcptool() -> Path:
    relative = (
        Path("tools/vendor/dcptool/dcpTool_1_10_0/Binaries/Windows/dcpTool.exe")
        if system_name() == "windows"
        else Path("tools/vendor/dcptool/dcpTool_1_10_0/Binaries/macOS/dcpTool")
    )
    packaged = (
        Path("resources/bin/windows/dcpTool.exe")
        if system_name() == "windows"
        else Path("resources/bin/darwin/dcpTool")
    )
    for root in resource_roots():
        for candidate in (root / packaged, root / relative):
            if candidate.is_file():
                return candidate
    raise FileNotFoundError("未找到随软件提供的 dcpTool。")


def find_style_root() -> Path:
    relative = Path(
        "tools/vendor/fujifilm-camera-profiles/FujifilmCameraProfiles-master/xml tables"
    )
    for root in resource_roots():
        for candidate in (root / "resources/styles", root / relative):
            if candidate.is_dir():
                return candidate
    raise FileNotFoundError("未找到八套风格数据。")


def find_app_icon() -> Path | None:
    for root in resource_roots():
        candidate = root / "resources/app_icon.png"
        if candidate.is_file():
            return candidate
    return None
