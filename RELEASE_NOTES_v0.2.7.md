# FuProfile Unlocker v0.2.7

## Windows asset refresh — 2026-09-17

The Windows ZIP was rebuilt in place to fix intermittent `dcpTool` crashes with
exit code `0xC0000142` when profile generation was started from the windowed
application. The Windows build now launches bundled command-line tools with an
independent hidden console. The application version and macOS asset are
unchanged.

This release adds a complete English interface while preserving the existing
Simplified Chinese experience. Profile generation and camera compatibility are
unchanged from v0.2.6.

## Downloads

- `FuProfile Unlocker-Windows-x64-v0.2.7.zip`: Windows 64-bit portable build.
- `FuProfile Unlocker-macOS-arm64-v0.2.7.zip`: Apple Silicon macOS application.
- `FuProfile Unlocker-source-v0.2.7.zip`: complete corresponding source and build files.
- `SHA256SUMS.txt`: SHA-256 checksums for the release archives.

## What changed

- Added complete English and Simplified Chinese interfaces.
- Added automatic language detection. Chinese system locales start in Simplified
  Chinese; other locales start in English.
- Added an `EN / 中文` button in the header for immediate language switching.
- Localized the install page, profile manager, drag-and-drop messages, progress
  states, errors, confirmation dialogs, file picker, and headless CLI mode.
- Fixed macOS/Tk layout clipping in the English interface by reserving the
  Choose RAW button before the expanding copy area, widening navigation items,
  and wrapping the profile-manager safety note.
- Added automated tests for locale normalization, environment overrides, exact
  translations, and dynamic status translations.
- Kept RAW identification, Adobe Standard matching, DCP generation, verification,
  installation, and uninstall behavior unchanged.

## Requirements and scope

- Lightroom Classic or Adobe Camera Raw must already be installed and contain a
  matching Adobe Standard profile for the selected camera.
- No Adobe DCP file is included in the application.
- The verified 554-model list remains a test-coverage list, not an exhaustive
  compatibility list.
- The Windows build is unsigned, and the macOS build may use ad-hoc signing.

## 中文摘要

- 新增完整英文界面，同时保留简体中文界面。
- 中文系统默认显示中文，其他系统语言默认显示英文。
- 标题栏新增 `EN / 中文` 按钮，可在运行时即时切换语言。
- 首页、管理页、拖放提示、处理进度、错误信息、确认框、文件选择器及命令行模式均已完成本地化。
- 修复 macOS/Tk 下英文界面的 Choose RAW 按钮挤出、导航文字裁切及管理页说明文字布局问题。
- 相机匹配、DCP 生成、验证、安装与卸载逻辑未发生变化。
