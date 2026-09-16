#!/usr/bin/env python3
"""Build the current platform's desktop bundle with PyInstaller."""

from __future__ import annotations

import os
import platform
import plistlib
import subprocess
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from fuprofile_unlocker import __version__  # noqa: E402
from fuprofile_unlocker.platforms import find_exiftool  # noqa: E402


STYLE_ROOT = (
    PROJECT
    / "tools/vendor/fujifilm-camera-profiles/FujifilmCameraProfiles-master/xml tables"
)
STYLE_FILES = (
    "provia.txt",
    "velvia.txt",
    "astia.txt",
    "classic chrome.txt",
    "reala ace.txt",
    "pro neg hi.txt",
    "pro neg std.txt",
    "eterna.txt",
)
APP_NAME = "FuProfile Unlocker"


def add_data(command: list[str], source: Path, destination: str) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Build resource is missing: {source}")
    command.extend(["--add-data", f"{source}:{destination}"])


def add_binary(command: list[str], source: Path, destination: str) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Build binary is missing: {source}")
    command.extend(["--add-binary", f"{source}:{destination}"])


def main() -> None:
    system = platform.system().lower()
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name",
        APP_NAME,
        "--specpath",
        str(PROJECT / "build/spec"),
        "--additional-hooks-dir",
        str(PROJECT / "packaging/hooks"),
        "--paths",
        str(PROJECT / "src"),
    ]
    if system == "darwin":
        command.extend(
            [
                "--osx-bundle-identifier",
                "org.fuprofileunlocker.app",
                "--icon",
                str(PROJECT / "resources/app_icon.icns"),
            ]
        )

    for filename in STYLE_FILES:
        add_data(command, STYLE_ROOT / filename, "resources/styles")
    add_data(command, PROJECT / "resources/style_models.json", "resources")
    add_data(command, PROJECT / "resources/app_icon.png", "resources")
    add_data(command, PROJECT / "LICENSE", ".")
    add_data(command, PROJECT / "THIRD_PARTY_NOTICES.md", ".")
    add_data(command, PROJECT / "licenses", "licenses")

    exiftool = find_exiftool()
    if system == "darwin":
        add_binary(
            command,
            PROJECT / "tools/vendor/dcptool/dcpTool_1_10_0/Binaries/macOS/dcpTool",
            "resources/bin/darwin",
        )
        add_data(command, exiftool, "resources/bin/darwin")
        if (exiftool.parent / "lib").is_dir():
            add_data(command, exiftool.parent / "lib", "resources/bin/darwin/lib")
    elif system == "windows":
        command.extend(["--icon", str(PROJECT / "resources/app_icon.ico")])
        windows_bin = PROJECT / "tools/vendor/dcptool/dcpTool_1_10_0/Binaries/Windows"
        for filename in ("dcpTool.exe", "iconv.dll", "libxml2.dll", "zlib1.dll"):
            add_binary(command, windows_bin / filename, "resources/bin/windows")
        add_binary(command, exiftool, "resources/bin/windows")
        exiftool_files = exiftool.parent / "exiftool_files"
        if exiftool_files.is_dir():
            add_data(command, exiftool_files, "resources/bin/windows/exiftool_files")
    else:
        raise RuntimeError("Packaging currently supports macOS and Windows only")

    command.append(str(PROJECT / "run_app.py"))
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(PROJECT / "src")
    environment["PYINSTALLER_CONFIG_DIR"] = str(PROJECT / "build/pyinstaller-config")
    if system == "windows":
        import tkinter

        if tkinter.TclVersion >= 9:
            # Python's Tcl 9 Windows builds keep their scripts inside the DLL's
            # zipfs. PyInstaller probes Tk in an isolated child process, which
            # needs these explicit paths to discover the embedded libraries.
            environment.setdefault("TCL_LIBRARY", "//zipfs:/lib/tcl/tcl_library")
            environment.setdefault("TK_LIBRARY", "//zipfs:/lib/tk/tk_library")
    subprocess.run(command, cwd=PROJECT, env=environment, check=True)
    if system == "darwin":
        app = PROJECT / "dist" / f"{APP_NAME}.app"
        info_path = app / "Contents/Info.plist"
        with info_path.open("rb") as plist_file:
            info = plistlib.load(plist_file)
        info["CFBundleDisplayName"] = APP_NAME
        info["CFBundleName"] = APP_NAME
        info["CFBundleShortVersionString"] = __version__
        info["CFBundleVersion"] = __version__
        with info_path.open("wb") as plist_file:
            plistlib.dump(info, plist_file)
        subprocess.run(
            ["codesign", "--force", "--deep", "--sign", "-", "--timestamp=none", str(app)],
            check=True,
        )


if __name__ == "__main__":
    main()
