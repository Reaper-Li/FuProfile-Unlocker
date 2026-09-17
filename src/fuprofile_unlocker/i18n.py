from __future__ import annotations

import locale
import os
import re
from collections.abc import Callable

_ENVIRONMENT_VARIABLE = "FUPROFILE_LANGUAGE"

_ENGLISH: dict[str, str] = {
    "相机 RAW": "Camera RAW",
    "所有文件": "All files",
    "取消": "Cancel",
    "确认": "Confirm",
    "准备就绪": "Ready",
    "选择一张非富士 RAW 照片开始。": "Choose a non-Fujifilm RAW photo to begin.",
    "安装配置": "Create Profiles",
    "管理与卸载": "Manage & Uninstall",
    "让每一张 RAW 都拥有富士色彩": "Bring Fujifilm-inspired color to every RAW",
    "自动识别相机、生成八种风格并安装到 Lightroom。原始照片与 Adobe 基础配置始终保持不变。": (
        "Automatically identify the camera, create eight looks, and install them for Lightroom. "
        "Your RAW photo and Adobe's original profiles are never modified."
    ),
    "选择或拖入一张非富士 RAW": "Choose or drop a non-Fujifilm RAW",
    "拖放到此区域；支持常见 RAW 格式，全程在本机处理": (
        "Drop it here; common RAW formats are supported and everything stays on this computer"
    ),
    "选择 RAW": "Choose RAW",
    "内置八种风格": "Eight included looks",
    "每种风格都会生成独立 DCP": "Each look is generated as a separate DCP",
    "永久免费  ·  本地处理  ·  安装后请重启 Lightroom": (
        "FREE  ·  LOCAL PROCESSING  ·  RESTART LIGHTROOM AFTER INSTALLATION"
    ),
    "管理已安装配置": "Manage installed profiles",
    "按相机型号查看并安全移除本软件生成的 DCP。": (
        "Review profiles by camera model and safely remove DCPs created by this app."
    ),
    "刷新列表": "Refresh",
    "全选": "Select all",
    "还没有已安装的相机配置": "No camera profiles have been installed yet",
    "前往“安装配置”选择一张 RAW 开始": "Go to Create Profiles and choose a RAW photo to begin",
    "卸载完成": "Uninstall complete",
    "卸载失败": "Uninstall failed",
    "卸载所选": "Uninstall selected",
    "全部卸载": "Uninstall all",
    "卸载仅移除本软件管理的 DCP，不会影响照片或 Adobe 原始文件。": (
        "Uninstalling removes only DCPs managed by this app. Photos and original Adobe files are unaffected."
    ),
    "卸载": "Uninstall",
    "选择 RAW 照片": "Choose a RAW photo",
    "无法使用拖入的文件": "The dropped file cannot be used",
    "无法读取拖放内容，请改用“选择 RAW”按钮。": (
        "The dropped item could not be read. Please use the Choose RAW button."
    ),
    "请一次只拖入一张 RAW 照片。": "Please drop only one RAW photo at a time.",
    "拖入的项目不是可读取的文件。": "The dropped item is not a readable file.",
    "请选择相机 RAW 文件，而不是 JPEG、TIFF 或导出图片。": (
        "Choose a camera RAW file, not a JPEG, TIFF, or exported image."
    ),
    "正在准备": "Preparing",
    "正在读取 RAW 元数据……": "Reading RAW metadata...",
    "正在安全处理配置文件，请不要退出软件。": (
        "Profiles are being processed safely. Please keep the app open."
    ),
    "八种风格已安装": "Eight looks installed",
    "配置已经存在，无需重复生成；请重启 Lightroom。": (
        "The profiles are already installed. Restart Lightroom to use them."
    ),
    "配置已通过校验；请完全退出并重新打开 Lightroom。": (
        "The profiles passed verification. Quit Lightroom completely, then reopen it."
    ),
    "未能完成安装": "Installation could not be completed",
    "卸载全部相机配置？": "Uninstall profiles for all cameras?",
    "确认卸载": "Confirm uninstall",
    "正在识别相机……": "Identifying the camera...",
    "这台相机的八个配置已经安装。": "All eight profiles for this camera are already installed.",
    "正在安装配置文件……": "Installing profiles...",
    "安装完成，请重启 Lightroom。": "Installation complete. Please restart Lightroom.",
    "无法从这张 RAW 中识别相机型号。": "The camera model could not be identified from this RAW file.",
    "这款工具用于非富士 RAW；富士相机请直接使用 Lightroom 的 Camera Matching。": (
        "This tool is intended for non-Fujifilm RAW files. For Fujifilm cameras, "
        "use Lightroom's Camera Matching profiles."
    ),
    "拒绝卸载不在软件管理目录内的文件。": (
        "Refusing to uninstall a file outside the app-managed directory."
    ),
    "未找到 ExifTool。请安装 ExifTool，或通过 FUPROFILE_EXIFTOOL 指定它的位置。": (
        "ExifTool was not found. Install ExifTool or set its location with FUPROFILE_EXIFTOOL."
    ),
    "未找到随软件提供的 dcpTool。": "The bundled dcpTool was not found.",
    "未找到八套风格数据。": "The eight included style data files were not found.",
    "用于无界面测试的 RAW 文件": "RAW file for headless testing",
    "覆盖安装目录，仅用于测试": "Override the installation directory (testing only)",
}

DynamicTranslation = tuple[re.Pattern[str], Callable[[re.Match[str]], str]]

_DYNAMIC_ENGLISH: tuple[DynamicTranslation, ...] = (
    (
        re.compile(r"已安装 (\d+) 台相机  ·  已选择 (\d+) 项"),
        lambda match: f"{match[1]} camera(s) installed  ·  {match[2]} selected",
    ),
    (
        re.compile(r"(?:(.+?)  ·  )?(\d+) 个配置  ·  (.+)"),
        lambda match: (
            (f"{match[1]}  ·  " if match[1] else "")
            + f"{match[2]} profiles  ·  {match[3]}"
        ),
    ),
    (re.compile(r"卸载 (.+)？"), lambda match: f"Uninstall {match[1]}?"),
    (
        re.compile(r"卸载选中的 (\d+) 台相机配置？"),
        lambda match: f"Uninstall profiles for the {match[1]} selected camera(s)?",
    ),
    (
        re.compile(
            r"将移除 (\d+) 个由 FuProfile Unlocker 管理的 DCP。\n"
            r"照片、目录和 Adobe 原始配置不会受到影响。"
        ),
        lambda match: (
            f"This will remove {match[1]} DCP(s) managed by FuProfile Unlocker.\n"
            "Photos, catalogs, and original Adobe profiles will not be affected."
        ),
    ),
    (
        re.compile(r"已移除 (\d+) 个 DCP；请重启 Lightroom。"),
        lambda match: f"Removed {match[1]} DCP(s). Please restart Lightroom.",
    ),
    (re.compile(r"找不到 RAW 文件：(.+)"), lambda match: f"RAW file not found: {match[1]}"),
    (
        re.compile(r"当前 Lightroom/Camera Raw 中找不到 (.+) 的 Adobe Standard 配置。请先升级 Adobe 软件。"),
        lambda match: (
            f"No Adobe Standard profile for {match[1]} was found in the current Lightroom/Camera Raw installation. "
            "Please update your Adobe software first."
        ),
    ),
    (
        re.compile(r"风格数据结构不完整：(.+)"),
        lambda match: f"The style data is incomplete: {match[1]}",
    ),
    (
        re.compile(r"生成后的配置文件身份校验失败：(.+)"),
        lambda match: f"The generated profile failed its identity check: {match[1]}",
    ),
    (
        re.compile(r"生成后的配置文件缺少风格数据：(.+)"),
        lambda match: f"The generated profile is missing style data: {match[1]}",
    ),
    (
        re.compile(r"正在查找 (.+) 的 Adobe Standard……"),
        lambda match: f"Finding the Adobe Standard profile for {match[1]}...",
    ),
    (
        re.compile(r"正在生成 (\d+)/8：(.+)"),
        lambda match: f"Generating {match[1]}/8: {match[2]}",
    ),
)


def normalize_language(language: str | None) -> str:
    """Return the supported language code for a locale or user preference."""
    if not language:
        return "en"
    normalized = language.strip().lower().replace("_", "-")
    if normalized.startswith("zh") or normalized.startswith("chinese"):
        return "zh"
    return "en"


def detect_language() -> str:
    """Detect the UI language, honoring FUPROFILE_LANGUAGE when it is set."""
    override = os.environ.get(_ENVIRONMENT_VARIABLE)
    if override:
        return normalize_language(override)
    try:
        system_locale = locale.getlocale()[0]
    except (ValueError, TypeError):
        system_locale = None
    return normalize_language(system_locale)


_current_language = detect_language()


def set_language(language: str) -> None:
    global _current_language
    _current_language = normalize_language(language)


def current_language() -> str:
    return _current_language


def translate(text: str, language: str | None = None) -> str:
    """Translate a user-facing Chinese source string into the selected language."""
    selected = normalize_language(language) if language is not None else current_language()
    if selected == "zh":
        return text
    exact = _ENGLISH.get(text)
    if exact is not None:
        return exact
    for pattern, render in _DYNAMIC_ENGLISH:
        match = pattern.fullmatch(text)
        if match:
            return render(match)
    return text
