from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .platforms import install_root


PROFILE_PREFIX = "Camera FUJIFILM "


@dataclass(frozen=True)
class InstalledCamera:
    key: str
    brand: str
    model: str
    directory: str
    profile_count: int
    installed_at: str


def _display_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


def _profiles(directory: Path) -> list[Path]:
    return sorted(
        profile
        for profile in directory.glob("*.dcp")
        if profile.name.startswith(PROFILE_PREFIX)
    )


def _record(directory: Path, brand: str, model: str) -> InstalledCamera | None:
    profiles = _profiles(directory)
    if not profiles:
        return None
    latest = max(profile.stat().st_mtime for profile in profiles)
    return InstalledCamera(
        key=str(directory.resolve()),
        brand=brand,
        model=model,
        directory=str(directory),
        profile_count=len(profiles),
        installed_at=_display_time(latest),
    )


def _scan_manifest_layout(root: Path) -> list[InstalledCamera]:
    records: list[InstalledCamera] = []
    if not root.is_dir():
        return records
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        brand, model = "", directory.name
        manifest_path = directory / "manifest.json"
        if manifest_path.is_file():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                identity = manifest.get("identity", {})
                brand = str(identity.get("make", ""))
                model = str(identity.get("model", model))
            except (OSError, ValueError, TypeError):
                pass
        item = _record(directory, brand, model)
        if item:
            records.append(item)
    return records


def scan_installations(current_root: Path | None = None) -> list[InstalledCamera]:
    current_root = current_root or install_root()
    records = _scan_manifest_layout(current_root)
    records.sort(key=lambda item: (item.brand.casefold(), item.model.casefold()))
    return records


def _within(directory: Path, root: Path) -> bool:
    try:
        directory.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def uninstall_camera(
    camera: InstalledCamera,
    current_root: Path | None = None,
) -> int:
    current_root = current_root or install_root()
    directory = Path(camera.directory).resolve()
    if not _within(directory, current_root):
        raise ValueError("拒绝卸载不在软件管理目录内的文件。")

    removed = 0
    for profile in _profiles(directory):
        profile.unlink()
        removed += 1
    (directory / "manifest.json").unlink(missing_ok=True)

    stop = current_root.resolve()
    cursor = directory
    while cursor != stop and _within(cursor, stop):
        try:
            cursor.rmdir()
        except OSError:
            break
        cursor = cursor.parent
    return removed


def uninstall_many(
    cameras: list[InstalledCamera],
    current_root: Path | None = None,
) -> int:
    return sum(
        uninstall_camera(camera, current_root=current_root)
        for camera in cameras
    )
