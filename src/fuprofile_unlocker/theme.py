from __future__ import annotations

import os
import platform
import subprocess


PALETTES = {
    "light": {
        "window": "#F4F5F7",
        "surface": "#FFFFFF",
        "surface_alt": "#F8F9FB",
        "surface_hover": "#F0F3F6",
        "border": "#DDE1E7",
        "border_strong": "#C9CFD8",
        "text": "#18201D",
        "text_secondary": "#68716D",
        "text_muted": "#909994",
        "accent": "#13795B",
        "accent_hover": "#0F654B",
        "accent_soft": "#E5F4EE",
        "accent_text": "#0B5E45",
        "danger": "#C43D4B",
        "danger_hover": "#A9323E",
        "danger_soft": "#FCEBED",
        "warning": "#9A6412",
        "warning_soft": "#FFF4D8",
        "success": "#13795B",
        "shadow": "#E6E8EC",
    },
    "dark": {
        "window": "#151918",
        "surface": "#1E2422",
        "surface_alt": "#252C29",
        "surface_hover": "#2D3532",
        "border": "#343D39",
        "border_strong": "#46504C",
        "text": "#F3F6F4",
        "text_secondary": "#ADB7B2",
        "text_muted": "#7D8983",
        "accent": "#38B98B",
        "accent_hover": "#55C99E",
        "accent_soft": "#163C30",
        "accent_text": "#79DAB6",
        "danger": "#EE6975",
        "danger_hover": "#F2828C",
        "danger_soft": "#47242A",
        "warning": "#E5B35C",
        "warning_soft": "#44371F",
        "success": "#58C99F",
        "shadow": "#101312",
    },
}


def detect_theme() -> str:
    override = os.environ.get("FUPROFILE_THEME", "").casefold()
    if override in PALETTES:
        return override
    system = platform.system().lower()
    if system == "darwin":
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True,
            check=False,
        )
        return "dark" if "dark" in result.stdout.casefold() else "light"
    if system == "windows":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            ) as key:
                value, _kind = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if value else "dark"
        except OSError:
            pass
    return "light"


def palette(name: str) -> dict[str, str]:
    return PALETTES[name]
