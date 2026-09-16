from __future__ import annotations

import queue
import threading
import tkinter as tk
import os
import platform
from pathlib import Path
from tkinter import filedialog
from typing import Callable

from tkinterdnd2 import COPY, DND_FILES, REFUSE_DROP, TkinterDnD

from . import __version__
from .core import STYLES, SUPPORTED_EXTENSIONS, generate_and_install
from .installations import InstalledCamera, scan_installations, uninstall_many
from .platforms import find_app_icon
from .theme import detect_theme, palette


RAW_TYPES = [
    (
        "相机 RAW",
        "*.3fr *.arw *.cr2 *.cr3 *.dng *.erf *.fff *.iiq *.kdc *.mef *.mos "
        "*.mrw *.nef *.nrw *.orf *.pef *.raf *.raw *.rw2 *.rwl *.sr2 *.srf *.srw *.x3f",
    ),
    ("所有文件", "*.*"),
]


def font_family() -> str:
    return "SF Pro Display" if platform.system() == "Darwin" else "Segoe UI"


def interactive_cursor() -> str:
    """Return Tk's platform-specific pointing-hand cursor name."""
    return "pointinghand" if platform.system() == "Darwin" else "hand2"


def dropped_paths(data: str, splitlist: Callable[[str], tuple[str, ...]]) -> tuple[Path, ...]:
    """Parse TkDND's Tcl file list without breaking paths that contain spaces."""
    return tuple(Path(value) for value in splitlist(data))


def scroll_units(delta: int) -> int:
    """Convert both high-resolution trackpad deltas and 120-step wheel deltas."""
    if delta == 0:
        return 0
    direction = -1 if delta > 0 else 1
    magnitude = max(1, min(5, abs(delta) // 60))
    return direction * magnitude


def unpack_touchpad_delta(delta: int) -> tuple[int, int]:
    """Decode Tk 9's packed signed 16-bit X/Y touchpad deltas."""
    packed = int(delta) & 0xFFFFFFFF
    delta_x = (packed >> 16) & 0xFFFF
    delta_y = packed & 0xFFFF
    if delta_x >= 0x8000:
        delta_x -= 0x10000
    if delta_y >= 0x8000:
        delta_y -= 0x10000
    return delta_x, delta_y


def rounded_rectangle(
    canvas: tk.Canvas,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    radius: int,
    **kwargs: object,
) -> int:
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)


class CanvasButton(tk.Canvas):
    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command: Callable[[], None],
        colors: dict[str, str],
        *,
        width: int = 180,
        height: int = 46,
        kind: str = "primary",
        font_size: int = 13,
    ) -> None:
        background = str(parent.cget("background"))
        super().__init__(
            parent,
            width=width,
            height=height,
            background=background,
            highlightthickness=0,
            bd=0,
            cursor=interactive_cursor(),
        )
        self.button_text = text
        self.command = command
        self.colors = colors
        self.kind = kind
        self.font_size = font_size
        self.disabled = False
        self.hovered = False
        self.bind("<Enter>", lambda _event: self._set_hover(True))
        self.bind("<Leave>", lambda _event: self._set_hover(False))
        self.bind("<ButtonRelease-1>", lambda _event: self._click())
        self._draw()

    def _fill(self) -> tuple[str, str, str]:
        if self.disabled:
            return self.colors["surface_alt"], self.colors["text_muted"], self.colors["border"]
        if self.kind == "danger":
            return (
                self.colors["danger_hover"] if self.hovered else self.colors["danger"],
                "#FFFFFF",
                self.colors["danger"],
            )
        if self.kind == "secondary":
            return (
                self.colors["surface_hover"] if self.hovered else self.colors["surface"],
                self.colors["text"],
                self.colors["border_strong"],
            )
        if self.kind == "ghost":
            return (
                self.colors["surface_hover"] if self.hovered else self.colors["surface_alt"],
                self.colors["text_secondary"],
                self.colors["surface_hover"] if self.hovered else self.colors["surface_alt"],
            )
        return (
            self.colors["accent_hover"] if self.hovered else self.colors["accent"],
            "#FFFFFF" if self.colors["accent"] != "#38B98B" else "#0D211A",
            self.colors["accent"],
        )

    def _draw(self) -> None:
        self.delete("all")
        width = int(self.cget("width"))
        height = int(self.cget("height"))
        fill, text, border = self._fill()
        rounded_rectangle(
            self, 1, 1, width - 1, height - 1, 12,
            fill=fill, outline=border, width=1,
        )
        self.create_text(
            width / 2,
            height / 2,
            text=self.button_text,
            fill=text,
            font=(font_family(), self.font_size, "bold"),
        )

    def _set_hover(self, value: bool) -> None:
        self.hovered = value
        self._draw()

    def _click(self) -> None:
        if not self.disabled:
            self.command()

    def set_disabled(self, value: bool) -> None:
        self.disabled = value
        self.configure(cursor="arrow" if value else interactive_cursor())
        self._draw()


class ConfirmDialog:
    def __init__(
        self,
        parent: tk.Tk,
        colors: dict[str, str],
        title: str,
        message: str,
        confirm_text: str,
    ) -> None:
        self.result = False
        window = tk.Toplevel(parent)
        self.window = window
        window.title(title)
        window.configure(background=colors["surface"])
        window.resizable(False, False)
        window.transient(parent)
        window.grab_set()
        width, height = 440, 230
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

        content = tk.Frame(window, background=colors["surface"], padx=28, pady=26)
        content.pack(fill="both", expand=True)
        tk.Label(
            content, text=title, background=colors["surface"], foreground=colors["text"],
            font=(font_family(), 18, "bold"), anchor="w",
        ).pack(fill="x")
        tk.Label(
            content, text=message, background=colors["surface"], foreground=colors["text_secondary"],
            font=(font_family(), 12), justify="left", anchor="w", wraplength=380,
        ).pack(fill="x", pady=(12, 24))
        actions = tk.Frame(content, background=colors["surface"])
        actions.pack(fill="x", side="bottom")
        CanvasButton(
            actions, "取消", window.destroy, colors, width=110, height=42, kind="secondary",
        ).pack(side="right", padx=(10, 0))
        CanvasButton(
            actions, confirm_text, self.confirm, colors, width=126, height=42, kind="danger",
        ).pack(side="right")
        window.protocol("WM_DELETE_WINDOW", window.destroy)

    def confirm(self) -> None:
        self.result = True
        self.window.destroy()

    def show(self) -> bool:
        self.window.wait_window()
        return self.result


class ProfileUnlockerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.theme_name = detect_theme()
        self.colors = palette(self.theme_name)
        self.page = os.environ.get("FUPROFILE_START_PAGE", "install")
        if self.page not in {"install", "manage"}:
            self.page = "install"
        self.busy = False
        self.status_text = "准备就绪"
        self.status_detail = "选择一张非富士 RAW 照片开始。"
        self.status_tone = "neutral"
        self.current_filename = ""
        self.selected_installations: set[str] = set()
        self.installations: list[InstalledCamera] = []
        self.shell: tk.Frame | None = None
        self.choose_button: CanvasButton | None = None
        self.status_title_label: tk.Label | None = None
        self.status_detail_label: tk.Label | None = None
        self.progress_canvas: tk.Canvas | None = None
        self.drop_zone: tk.Frame | None = None
        self.install_canvas: tk.Canvas | None = None
        self.scroll_indicator: tk.Canvas | None = None
        self.scroll_first = 0.0
        self.scroll_last = 1.0
        self.scroll_drag_y = 0
        self.scroll_drag_view = 0.0
        self.progress_position = 0
        self.app_icon: tk.PhotoImage | None = None
        self.header_icon: tk.PhotoImage | None = None

        root.title("FuProfile Unlocker")
        root.geometry("860x700")
        root.minsize(780, 640)
        self._apply_app_icon()
        self._apply_window_theme()
        self.build_ui()
        self.root.after(100, self.poll_events)
        self.root.after(1500, self.poll_theme)
        self.root.after(40, self.animate_progress)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        try:
            # Tk 9 no longer reports macOS/Windows two-finger gestures as MouseWheel.
            self.root.bind_all("<TouchpadScroll>", self._on_touchpad_scroll)
        except tk.TclError:
            # Tk 8.6 does not know this event and continues to use MouseWheel.
            pass

    def _apply_app_icon(self) -> None:
        icon_path = find_app_icon()
        if icon_path is None:
            return
        try:
            self.app_icon = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, self.app_icon)
            factor = max(1, round(self.app_icon.width() / 42))
            self.header_icon = self.app_icon.subsample(factor, factor)
        except tk.TclError:
            self.app_icon = None
            self.header_icon = None

    def _apply_window_theme(self) -> None:
        self.root.configure(background=self.colors["window"])
        try:
            self.root.tk.call(
                "tk::unsupported::MacWindowStyle", "appearance", self.root._w, self.theme_name
            )
        except tk.TclError:
            pass

    def label(
        self,
        parent: tk.Misc,
        text: str,
        size: int,
        color: str,
        weight: str = "normal",
        **kwargs: object,
    ) -> tk.Label:
        return tk.Label(
            parent,
            text=text,
            font=(font_family(), size, weight),
            background=str(parent.cget("background")),
            foreground=color,
            **kwargs,
        )

    def build_ui(self) -> None:
        if self.shell is not None:
            self.shell.destroy()
        c = self.colors
        self.root.configure(background=c["window"])
        self.shell = tk.Frame(self.root, background=c["window"])
        self.shell.pack(fill="both", expand=True)
        self.build_header(self.shell)
        content = tk.Frame(self.shell, background=c["window"], padx=38, pady=24)
        content.pack(fill="both", expand=True)
        if self.page == "manage":
            self.build_manage_page(content)
        else:
            self.build_install_page(content)

    def build_header(self, parent: tk.Frame) -> None:
        c = self.colors
        header = tk.Frame(
            parent, background=c["surface"], height=78,
            highlightthickness=1, highlightbackground=c["border"],
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        inner = tk.Frame(header, background=c["surface"], padx=34)
        inner.pack(fill="both", expand=True)

        brand = tk.Frame(inner, background=c["surface"])
        brand.pack(side="left", fill="y")
        logo = tk.Canvas(brand, width=44, height=44, background=c["surface"], highlightthickness=0)
        logo.pack(side="left", pady=17)
        if self.header_icon is not None:
            logo.create_image(22, 22, image=self.header_icon)
        else:
            rounded_rectangle(logo, 1, 1, 43, 43, 12, fill=c["accent"], outline=c["accent"])
            logo.create_text(22, 22, text="FU", fill="#FFFFFF", font=(font_family(), 13, "bold"))
        title_block = tk.Frame(brand, background=c["surface"])
        title_block.pack(side="left", padx=(12, 0), pady=15)
        self.label(title_block, "FuProfile Unlocker", 16, c["text"], "bold", anchor="w").pack(anchor="w")
        self.label(title_block, f"FREE  ·  v{__version__}", 9, c["text_muted"], "bold", anchor="w").pack(anchor="w", pady=(2, 0))

        navigation = tk.Frame(inner, background=c["surface"])
        navigation.pack(side="right", pady=16)
        self.nav_item(navigation, "安装配置", "install").pack(side="left", padx=(0, 6))
        self.nav_item(navigation, "管理与卸载", "manage").pack(side="left")

    def nav_item(self, parent: tk.Frame, text: str, page: str) -> tk.Canvas:
        c = self.colors
        active = self.page == page
        canvas = tk.Canvas(
            parent, width=112, height=42, background=c["surface"], highlightthickness=0,
            cursor="arrow" if active else interactive_cursor(),
        )
        fill = c["accent_soft"] if active else c["surface"]
        rounded_rectangle(canvas, 1, 1, 111, 41, 11, fill=fill, outline=fill)
        canvas.create_text(
            56, 21, text=text, fill=c["accent_text"] if active else c["text_secondary"],
            font=(font_family(), 12, "bold" if active else "normal"),
        )
        if not active:
            canvas.bind("<ButtonRelease-1>", lambda _event: self.switch_page(page))
        return canvas

    def build_install_page(self, parent: tk.Frame) -> None:
        c = self.colors
        hero = tk.Frame(parent, background=c["window"])
        hero.pack(fill="x")
        self.label(hero, "让每一张 RAW 都拥有富士色彩", 27, c["text"], "bold", anchor="w").pack(fill="x")
        self.label(
            hero,
            "自动识别相机、生成八种风格并安装到 Lightroom。原始照片与 Adobe 基础配置始终保持不变。",
            12,
            c["text_secondary"],
            anchor="w",
            justify="left",
            wraplength=720,
        ).pack(fill="x", pady=(8, 20))

        upload = tk.Frame(
            parent,
            background=c["surface"],
            padx=26,
            pady=22,
            highlightthickness=1,
            highlightbackground=c["border"],
        )
        upload.pack(fill="x")
        upload_left = tk.Frame(upload, background=c["surface"])
        upload_left.pack(side="left", fill="both", expand=True)
        icon = tk.Canvas(upload_left, width=48, height=48, background=c["surface"], highlightthickness=0)
        icon.pack(side="left", padx=(0, 16))
        icon.create_oval(1, 1, 47, 47, fill=c["accent_soft"], outline=c["accent_soft"])
        icon.create_text(24, 23, text="＋", fill=c["accent_text"], font=(font_family(), 25, "normal"))
        copy = tk.Frame(upload_left, background=c["surface"])
        copy.pack(side="left", fill="both", expand=True)
        self.label(copy, "选择或拖入一张非富士 RAW", 15, c["text"], "bold", anchor="w").pack(fill="x", pady=(2, 3))
        self.label(copy, "拖放到此区域；支持常见 RAW 格式，全程在本机处理", 11, c["text_secondary"], anchor="w").pack(fill="x")
        self.choose_button = CanvasButton(
            upload, "选择 RAW", self.choose_raw, c, width=150, height=46, kind="primary",
        )
        self.choose_button.pack(side="right", padx=(18, 0))
        self.choose_button.set_disabled(self.busy)
        self.drop_zone = upload
        self.register_drop_target(upload)

        self.progress_canvas = tk.Canvas(
            parent, height=4, background=c["window"], highlightthickness=0, bd=0,
        )
        self.progress_canvas.pack(fill="x", pady=(14, 0))

        status_color = {
            "success": c["accent_soft"], "error": c["danger_soft"],
            "warning": c["warning_soft"], "neutral": c["surface_alt"],
        }[self.status_tone]
        status_accent = {
            "success": c["success"], "error": c["danger"],
            "warning": c["warning"], "neutral": c["text_muted"],
        }[self.status_tone]
        status = tk.Frame(parent, background=status_color, padx=18, pady=14)
        status.pack(fill="x", pady=(12, 20))
        dot = tk.Canvas(status, width=18, height=34, background=status_color, highlightthickness=0)
        dot.pack(side="left", padx=(0, 9))
        dot.create_oval(5, 13, 13, 21, fill=status_accent, outline=status_accent)
        status_copy = tk.Frame(status, background=status_color)
        status_copy.pack(side="left", fill="x", expand=True)
        self.status_title_label = self.label(
            status_copy, self.status_text, 12, c["text"], "bold", anchor="w",
        )
        self.status_title_label.pack(fill="x")
        detail = self.status_detail
        if self.current_filename:
            detail = f"{self.current_filename}  ·  {detail}"
        self.status_detail_label = self.label(
            status_copy, detail, 10, c["text_secondary"], anchor="w",
        )
        self.status_detail_label.pack(fill="x", pady=(2, 0))

        section = tk.Frame(parent, background=c["window"])
        section.pack(fill="both", expand=True)
        heading = tk.Frame(section, background=c["window"])
        heading.pack(fill="x", pady=(0, 10))
        self.label(heading, "内置八种风格", 13, c["text"], "bold", anchor="w").pack(side="left")
        self.label(heading, "每种风格都会生成独立 DCP", 10, c["text_muted"], anchor="e").pack(side="right")
        grid = tk.Frame(section, background=c["window"])
        grid.pack(fill="x")
        for column in range(4):
            grid.grid_columnconfigure(column, weight=1, uniform="style")
        for index, (style_name, _filename) in enumerate(STYLES):
            chip = tk.Frame(
                grid, background=c["surface"], padx=12, pady=11,
                highlightthickness=1, highlightbackground=c["border"],
            )
            chip.grid(row=index // 4, column=index % 4, sticky="nsew", padx=(0 if index % 4 == 0 else 5, 0), pady=(0, 6))
            self.label(chip, "✓", 11, c["accent"], "bold").pack(side="left", padx=(0, 7))
            self.label(chip, style_name, 10, c["text"], "bold", anchor="w").pack(side="left")

        self.label(
            parent, "永久免费  ·  本地处理  ·  安装后请重启 Lightroom",
            10, c["text_muted"], anchor="center",
        ).pack(fill="x", pady=(11, 0))

    def build_manage_page(self, parent: tk.Frame) -> None:
        c = self.colors
        self.installations = scan_installations()
        valid_keys = {item.key for item in self.installations}
        self.selected_installations.intersection_update(valid_keys)

        heading = tk.Frame(parent, background=c["window"])
        heading.pack(fill="x", pady=(0, 18))
        title_block = tk.Frame(heading, background=c["window"])
        title_block.pack(side="left")
        self.label(title_block, "管理已安装配置", 27, c["text"], "bold", anchor="w").pack(fill="x")
        self.label(
            title_block, "按相机型号查看并安全移除本软件生成的 DCP。",
            12, c["text_secondary"], anchor="w",
        ).pack(fill="x", pady=(7, 0))
        CanvasButton(
            heading, "刷新列表", lambda: self.build_ui(), c,
            width=112, height=40, kind="secondary", font_size=11,
        ).pack(side="right", pady=(8, 0))

        toolbar = tk.Frame(parent, background=c["window"])
        toolbar.pack(fill="x", pady=(0, 10))
        all_selected = bool(self.installations) and len(self.selected_installations) == len(self.installations)
        self.checkbox(toolbar, all_selected, self.toggle_all).pack(side="left")
        self.label(toolbar, "全选", 11, c["text_secondary"], anchor="w").pack(side="left", padx=(7, 0))
        self.label(
            toolbar,
            f"已安装 {len(self.installations)} 台相机  ·  已选择 {len(self.selected_installations)} 项",
            10, c["text_muted"], anchor="e",
        ).pack(side="right")

        list_card = tk.Frame(
            parent, background=c["surface"], highlightthickness=1, highlightbackground=c["border"],
        )
        list_card.pack(fill="both", expand=True)
        if not self.installations:
            empty = tk.Frame(list_card, background=c["surface"])
            empty.place(relx=0.5, rely=0.5, anchor="center")
            icon = tk.Canvas(empty, width=58, height=58, background=c["surface"], highlightthickness=0)
            icon.pack()
            icon.create_oval(2, 2, 56, 56, fill=c["surface_alt"], outline=c["border"])
            icon.create_text(29, 28, text="✓", fill=c["text_muted"], font=(font_family(), 22, "bold"))
            self.label(empty, "还没有已安装的相机配置", 14, c["text"], "bold").pack(pady=(12, 4))
            self.label(empty, "前往“安装配置”选择一张 RAW 开始", 11, c["text_secondary"]).pack()
        else:
            canvas = tk.Canvas(list_card, background=c["surface"], highlightthickness=0, bd=0)
            self.install_canvas = canvas
            indicator = tk.Canvas(
                list_card, width=13, background=c["surface"], highlightthickness=0, bd=0,
                cursor=interactive_cursor(),
            )
            self.scroll_indicator = indicator
            rows = tk.Frame(canvas, background=c["surface"])
            rows.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
            window_id = canvas.create_window((0, 0), window=rows, anchor="nw")
            canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window_id, width=event.width))
            canvas.configure(
                # One-pixel units preserve Tk 9's high-resolution touchpad deltas.
                yscrollincrement=1,
                yscrollcommand=lambda first, last: self.draw_scroll_indicator(
                    indicator, float(first), float(last)
                )
            )
            canvas.pack(side="left", fill="both", expand=True)
            indicator.pack(side="right", fill="y", padx=(0, 2), pady=3)
            indicator.bind("<ButtonPress-1>", self.start_scroll_drag)
            indicator.bind("<B1-Motion>", self.drag_scroll_indicator)
            for index, item in enumerate(self.installations):
                self.installation_row(rows, item, index == len(self.installations) - 1).pack(fill="x")

        if self.status_text in {"卸载完成", "卸载失败"}:
            notice_bg = c["accent_soft"] if self.status_text == "卸载完成" else c["danger_soft"]
            notice_fg = c["success"] if self.status_text == "卸载完成" else c["danger"]
            notice = tk.Frame(parent, background=notice_bg, padx=12, pady=8)
            notice.pack(fill="x", pady=(10, 0))
            self.label(
                notice, f"{self.status_text}  ·  {self.status_detail}",
                10, notice_fg, "bold", anchor="w",
            ).pack(fill="x")

        actions = tk.Frame(parent, background=c["window"])
        actions.pack(fill="x", pady=(14, 0))
        selected_button = CanvasButton(
            actions, "卸载所选", self.uninstall_selected, c,
            width=132, height=44, kind="danger", font_size=11,
        )
        selected_button.pack(side="right", padx=(10, 0))
        selected_button.set_disabled(not self.selected_installations)
        all_button = CanvasButton(
            actions, "全部卸载", self.uninstall_all, c,
            width=120, height=44, kind="secondary", font_size=11,
        )
        all_button.pack(side="right")
        all_button.set_disabled(not self.installations)
        self.label(
            actions, "卸载仅移除本软件管理的 DCP，不会影响照片或 Adobe 原始文件。",
            10, c["text_muted"], anchor="w",
        ).pack(side="left", fill="x", expand=True)

    def installation_row(self, parent: tk.Frame, item: InstalledCamera, last: bool) -> tk.Frame:
        c = self.colors
        row = tk.Frame(parent, background=c["surface"], padx=18, pady=13)
        self.checkbox(
            row, item.key in self.selected_installations,
            lambda key=item.key: self.toggle_installation(key),
        ).pack(side="left", padx=(0, 13))
        info = tk.Frame(row, background=c["surface"])
        info.pack(side="left", fill="both", expand=True)
        top = tk.Frame(info, background=c["surface"])
        top.pack(fill="x")
        self.label(top, item.model, 13, c["text"], "bold", anchor="w").pack(side="left")
        brand = f"{item.brand}  ·  " if item.brand else ""
        self.label(
            info,
            f"{brand}{item.profile_count} 个配置  ·  {item.installed_at}",
            10, c["text_secondary"], anchor="w",
        ).pack(fill="x", pady=(3, 0))
        CanvasButton(
            row,
            "卸载",
            lambda current=item: self.uninstall_one(current),
            c,
            width=82,
            height=36,
            kind="secondary",
            font_size=10,
        ).pack(side="right", padx=(12, 0))
        if not last:
            tk.Frame(row, height=1, background=c["border"]).place(relx=0, rely=1, relwidth=1)
        return row

    def checkbox(self, parent: tk.Misc, selected: bool, command: Callable[[], None]) -> tk.Canvas:
        c = self.colors
        canvas = tk.Canvas(
            parent, width=22, height=22, background=str(parent.cget("background")),
            highlightthickness=0, cursor=interactive_cursor(),
        )
        fill = c["accent"] if selected else c["surface"]
        outline = c["accent"] if selected else c["border_strong"]
        rounded_rectangle(canvas, 2, 2, 20, 20, 5, fill=fill, outline=outline, width=1)
        if selected:
            canvas.create_text(11, 11, text="✓", fill="#FFFFFF", font=(font_family(), 11, "bold"))
        canvas.bind("<ButtonRelease-1>", lambda _event: command())
        return canvas

    def switch_page(self, page: str) -> None:
        self.page = page
        self.build_ui()

    def _on_mousewheel(self, event: tk.Event) -> None:
        canvas = self.install_canvas
        if self.page == "manage" and canvas is not None and canvas.winfo_exists():
            units = scroll_units(event.delta)
            if units:
                canvas.yview_scroll(units * 18, "units")

    def _on_touchpad_scroll(self, event: tk.Event) -> None:
        canvas = self.install_canvas
        if self.page == "manage" and canvas is not None and canvas.winfo_exists():
            _delta_x, delta_y = unpack_touchpad_delta(event.delta)
            if delta_y:
                canvas.yview_scroll(-delta_y, "units")

    def draw_scroll_indicator(self, indicator: tk.Canvas, first: float, last: float) -> None:
        if not indicator.winfo_exists():
            return
        self.scroll_first = first
        self.scroll_last = last
        indicator.delete("all")
        if first <= 0 and last >= 1:
            return
        height = max(indicator.winfo_height(), 1)
        top = max(2, int(first * height))
        bottom = min(height - 2, max(top + 28, int(last * height)))
        indicator.create_rectangle(
            4, 2, 9, height - 2, fill=self.colors["surface_alt"], outline=""
        )
        indicator.create_rectangle(
            3, top, 10, bottom, fill=self.colors["border_strong"], outline="",
            tags=("thumb",),
        )

    def start_scroll_drag(self, event: tk.Event) -> None:
        canvas = self.install_canvas
        indicator = self.scroll_indicator
        if canvas is None or indicator is None or self.scroll_last >= 1.0:
            return
        height = max(indicator.winfo_height(), 1)
        top = self.scroll_first * height
        bottom = self.scroll_last * height
        if event.y < top or event.y > bottom:
            visible = self.scroll_last - self.scroll_first
            canvas.yview_moveto(max(0.0, min(1.0 - visible, event.y / height - visible / 2)))
        self.scroll_drag_y = event.y
        self.scroll_drag_view = canvas.yview()[0]

    def drag_scroll_indicator(self, event: tk.Event) -> None:
        canvas = self.install_canvas
        indicator = self.scroll_indicator
        if canvas is None or indicator is None or self.scroll_last >= 1.0:
            return
        height = max(indicator.winfo_height(), 1)
        visible = self.scroll_last - self.scroll_first
        travel = max(1.0, height * (1.0 - visible))
        content_delta = (event.y - self.scroll_drag_y) / travel * (1.0 - visible)
        canvas.yview_moveto(max(0.0, min(1.0 - visible, self.scroll_drag_view + content_delta)))

    def choose_raw(self) -> None:
        selected = filedialog.askopenfilename(title="选择 RAW 照片", filetypes=RAW_TYPES)
        if not selected:
            return
        self.start_generation(Path(selected))

    def register_drop_target(self, widget: tk.Misc) -> None:
        """Make the upload card and each child widget accept native file drops."""
        try:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<DropEnter>>", self.on_drop_enter)
            widget.dnd_bind("<<DropLeave>>", self.on_drop_leave)
            widget.dnd_bind("<<Drop>>", self.on_raw_drop)
        except (AttributeError, tk.TclError):
            return
        for child in widget.winfo_children():
            self.register_drop_target(child)

    def set_drop_highlight(self, active: bool) -> None:
        zone = self.drop_zone
        if zone is not None and zone.winfo_exists():
            zone.configure(
                highlightbackground=self.colors["accent"] if active else self.colors["border"],
                highlightthickness=2 if active else 1,
            )

    def on_drop_enter(self, _event: tk.Event) -> str:
        if not self.busy:
            self.set_drop_highlight(True)
            return COPY
        return REFUSE_DROP

    def on_drop_leave(self, _event: tk.Event) -> str:
        self.set_drop_highlight(False)
        return COPY

    def show_drop_error(self, detail: str) -> None:
        self.status_text = "无法使用拖入的文件"
        self.status_detail = detail
        self.status_tone = "error"
        self.current_filename = ""
        if self.page == "install":
            self.root.after_idle(self.build_ui)

    def on_raw_drop(self, event: tk.Event) -> str:
        self.set_drop_highlight(False)
        if self.busy:
            return REFUSE_DROP
        try:
            paths = dropped_paths(str(getattr(event, "data", "")), self.root.tk.splitlist)
        except (tk.TclError, TypeError, ValueError):
            self.show_drop_error("无法读取拖放内容，请改用“选择 RAW”按钮。")
            return REFUSE_DROP
        if len(paths) != 1:
            self.show_drop_error("请一次只拖入一张 RAW 照片。")
            return REFUSE_DROP
        raw_path = paths[0]
        if not raw_path.is_file():
            self.show_drop_error("拖入的项目不是可读取的文件。")
            return REFUSE_DROP
        if raw_path.suffix.casefold() not in SUPPORTED_EXTENSIONS:
            self.show_drop_error("请选择相机 RAW 文件，而不是 JPEG、TIFF 或导出图片。")
            return REFUSE_DROP
        self.root.after_idle(lambda path=raw_path: self.start_generation(path))
        return COPY

    def start_generation(self, raw_path: Path) -> None:
        self.busy = True
        self.current_filename = raw_path.name
        self.status_text = "正在准备"
        self.status_detail = "正在读取 RAW 元数据……"
        self.status_tone = "neutral"
        self.build_ui()
        threading.Thread(target=self.run_generation, args=(raw_path,), daemon=True).start()

    def run_generation(self, raw_path: Path) -> None:
        try:
            result = generate_and_install(
                raw_path, status=lambda message: self.events.put(("status", message))
            )
            self.events.put(("done", result))
        except Exception as error:
            self.events.put(("error", str(error)))

    def poll_events(self) -> None:
        changed = False
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "status":
                    self.status_text = str(payload).rstrip("……")
                    self.status_detail = "正在安全处理配置文件，请不要退出软件。"
                    changed = True
                elif event == "done":
                    self.busy = False
                    self.status_tone = "success"
                    self.status_text = "八种风格已安装"
                    self.status_detail = (
                        "配置已经存在，无需重复生成；请重启 Lightroom。"
                        if payload.reused_cache
                        else "配置已通过校验；请完全退出并重新打开 Lightroom。"
                    )
                    changed = True
                elif event == "error":
                    self.busy = False
                    self.status_tone = "error"
                    self.status_text = "未能完成安装"
                    self.status_detail = str(payload)
                    changed = True
        except queue.Empty:
            pass
        if changed and self.page == "install":
            self.build_ui()
        self.root.after(100, self.poll_events)

    def animate_progress(self) -> None:
        canvas = self.progress_canvas
        if canvas is not None and canvas.winfo_exists():
            canvas.delete("all")
            width = max(canvas.winfo_width(), 1)
            if self.busy:
                segment = max(90, width // 5)
                self.progress_position = (self.progress_position + 8) % (width + segment)
                start = self.progress_position - segment
                canvas.create_rectangle(
                    start, 0, self.progress_position, 4,
                    fill=self.colors["accent"], outline=self.colors["accent"],
                )
            else:
                canvas.create_rectangle(0, 1, width, 3, fill=self.colors["border"], outline="")
        self.root.after(40, self.animate_progress)

    def poll_theme(self) -> None:
        detected = detect_theme()
        if detected != self.theme_name:
            self.theme_name = detected
            self.colors = palette(detected)
            self._apply_window_theme()
            self.build_ui()
        self.root.after(1500, self.poll_theme)

    def toggle_installation(self, key: str) -> None:
        if key in self.selected_installations:
            self.selected_installations.remove(key)
        else:
            self.selected_installations.add(key)
        self.build_ui()

    def toggle_all(self) -> None:
        all_keys = {item.key for item in self.installations}
        self.selected_installations = set() if self.selected_installations == all_keys else all_keys
        self.build_ui()

    def uninstall_one(self, camera: InstalledCamera) -> None:
        self.confirm_uninstall([camera], f"卸载 {camera.model}？")

    def uninstall_selected(self) -> None:
        targets = [item for item in self.installations if item.key in self.selected_installations]
        self.confirm_uninstall(targets, f"卸载选中的 {len(targets)} 台相机配置？")

    def uninstall_all(self) -> None:
        self.confirm_uninstall(list(self.installations), "卸载全部相机配置？")

    def confirm_uninstall(self, targets: list[InstalledCamera], title: str) -> None:
        if not targets:
            return
        count = sum(item.profile_count for item in targets)
        dialog = ConfirmDialog(
            self.root,
            self.colors,
            title,
            f"将移除 {count} 个由 FuProfile Unlocker 管理的 DCP。\n照片、目录和 Adobe 原始配置不会受到影响。",
            "确认卸载",
        )
        if not dialog.show():
            return
        try:
            removed = uninstall_many(targets)
            self.selected_installations.difference_update(item.key for item in targets)
            self.status_text = "卸载完成"
            self.status_detail = f"已移除 {removed} 个 DCP；请重启 Lightroom。"
            self.status_tone = "success"
        except Exception as error:
            self.status_text = "卸载失败"
            self.status_detail = str(error)
            self.status_tone = "error"
        self.build_ui()


def main() -> None:
    try:
        root = TkinterDnD.Tk()
    except tk.TclError:
        # Keep the ordinary file picker usable if the native DND extension
        # cannot be loaded on an unusual Tk installation.
        root = tk.Tk()
    ProfileUnlockerApp(root)
    root.mainloop()
