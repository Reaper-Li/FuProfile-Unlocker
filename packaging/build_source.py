#!/usr/bin/env python3
"""Create the public, redistributable FuProfile Unlocker source archive."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from fuprofile_unlocker import __version__  # noqa: E402


ARCHIVE_ROOT = f"FuProfile Unlocker-source-v{__version__}"
TOP_LEVEL_FILES = (
    ".gitattributes",
    ".gitignore",
    "CONTRIBUTING.md",
    "LICENSE",
    "MACOS_BUILD_CN.md",
    "MACOS_HANDOFF_CN.md",
    "README.md",
    "README_CN.md",
    f"RELEASE_NOTES_v{__version__}.md",
    "SECURITY.md",
    "SOURCE_PACKAGE_CONTENTS.md",
    "THIRD_PARTY_NOTICES.md",
    "VERSION_HISTORY_CN.md",
    "WINDOWS_BUILD_CN.md",
    "pyproject.toml",
    "requirements-build.txt",
    "run_app.py",
)
PROJECT_DIRECTORIES = (".github", "licenses", "packaging", "resources", "src", "tests")
TOOL_FILES = (
    "download_raw_samples.sh",
    "generate_test_profiles.py",
    "sync_raw_corpus.py",
    "validate_raw_corpus.py",
)


def ignored_project_files(_directory: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name in {"__pycache__", ".pytest_cache", ".DS_Store"}}
    ignored.update(name for name in names if name.endswith((".pyc", ".pyo")))
    return ignored


def ignored_dcptool_files(_directory: str, names: list[str]) -> set[str]:
    ignored = ignored_project_files(_directory, names)
    ignored.update(name for name in names if name == "xcuserdata")
    if Path(_directory).name == "Documentation":
        ignored.update(name for name in names if name == "Example_files")
    return ignored


def copy_required(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Required source-package input is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, ignore=ignored_project_files)
    else:
        shutil.copy2(source, destination)


def stage_source(root: Path) -> None:
    for name in TOP_LEVEL_FILES:
        copy_required(PROJECT / name, root / name)

    for name in PROJECT_DIRECTORIES:
        copy_required(PROJECT / name, root / name)

    raw_destination = root / "RAW"
    copy_required(PROJECT / "RAW/README.md", raw_destination / "README.md")
    copy_required(PROJECT / "RAW/manifest.json", raw_destination / "manifest.json")

    tools_destination = root / "tools"
    for name in TOOL_FILES:
        copy_required(PROJECT / "tools" / name, tools_destination / name)

    dcptool_source = PROJECT / "tools/vendor/dcptool/dcpTool_1_10_0"
    dcptool_destination = tools_destination / "vendor/dcptool/dcpTool_1_10_0"
    if not dcptool_source.is_dir():
        raise FileNotFoundError(f"Required dcpTool source tree is missing: {dcptool_source}")
    dcptool_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(dcptool_source, dcptool_destination, ignore=ignored_dcptool_files)

    fuji_source = (
        PROJECT
        / "tools/vendor/fujifilm-camera-profiles/FujifilmCameraProfiles-master"
    )
    fuji_destination = (
        tools_destination
        / "vendor/fujifilm-camera-profiles/FujifilmCameraProfiles-master"
    )
    copy_required(fuji_source / "README.md", fuji_destination / "README.md")
    copy_required(fuji_source / "xml tables", fuji_destination / "xml tables")


def validate_staged_source(root: Path) -> None:
    forbidden_parts = {".venv", "build", "dist", "transport", "__pycache__", "dcp examples"}
    raw_allowed = {"README.md", "manifest.json"}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if forbidden_parts.intersection(relative.parts):
            raise RuntimeError(f"Forbidden source-package path: {relative}")
        if path.is_file() and path.suffix.lower() in {".pyc", ".pyo", ".dcp"}:
            raise RuntimeError(f"Forbidden source-package file: {relative}")
        if path.is_file() and relative.parts[0] == "RAW" and path.name not in raw_allowed:
            raise RuntimeError(f"RAW binary unexpectedly staged: {relative}")


def write_zip(root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                archive.write(path, Path(root.name) / path.relative_to(root))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT / "dist" / f"{ARCHIVE_ROOT}.zip",
        help="destination ZIP path",
    )
    parser.add_argument("--force", action="store_true", help="replace an existing archive")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        if not args.force:
            raise FileExistsError(f"Output already exists; use --force to replace it: {output}")
        output.unlink()

    with tempfile.TemporaryDirectory(prefix="fuprofile-source-") as temporary:
        root = Path(temporary) / ARCHIVE_ROOT
        root.mkdir()
        stage_source(root)
        validate_staged_source(root)
        write_zip(root, output)

    print(output)


if __name__ == "__main__":
    main()
