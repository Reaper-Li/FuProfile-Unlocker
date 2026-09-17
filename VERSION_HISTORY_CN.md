# FuProfile Unlocker 版本更新记录

本文记录本轮接手后的主要版本变化。当前版本为 **v0.2.7**。

## v0.2.7 — 英文界面与双语切换

- 新增完整英文界面，同时保留简体中文界面。
- 启动时自动检测系统语言：中文环境默认使用简体中文，其他环境默认使用英文。
- 在窗口标题栏加入 `EN / 中文` 切换按钮，无需重启即可切换界面语言。
- 补齐首页、管理页、拖放提示、进度状态、错误信息、卸载确认框和文件选择器的英文文本。
- 命令行测试模式的帮助、进度与错误信息也会使用当前语言。
- 新增语言规范化、环境变量覆盖、静态文本与动态文本的自动化测试。
- 修复 macOS/Tk 下英文 Choose RAW 按钮被挤出、导航文字裁切和管理页说明文字布局问题。
- macOS arm64 回传包已核验 Bundle ID、v0.2.7 版本、arm64 架构、许可证资源及无 DCP 内置。
- Windows x64 已使用合并后的同一份源码重新构建，并完成英文与中文冷启动验证。
- 配置生成、相机匹配、安装目录和卸载逻辑保持不变。
- Windows x64 与 macOS arm64 发布包版本同步提升至 v0.2.7。

## v0.2.6 — 传统相机兼容性与首发候选版锁定

- Windows 与 macOS 使用统一的应用名、安装目录、包名和 `org.fuprofileunlocker.app` 标识。
- 将相机型号匹配改为严格匹配，避免使用任意后缀或模糊字符串选中错误传感器的 DCP。
- 增加经过明确审核的地区型号、市场型号和 EXIF 命名别名。
- 支持 `Adobe Standard`、`Adobe_Standard` 及其 `v2` 文件名写法。
- 修正 `DC-FZ45` 的错误候选映射，改为使用与 RAW 结构相符的 `Panasonic DC-FZ80 Adobe Standard.dcp`。
- 对 85 个别名型号完成 8/8 DCP 全流程验证。
- 对其余传统相机 RAW 语料完成逐型号验证，最终确认 14 个品牌、554 个传统相机型号可用。
- 每个收录型号均实际生成 8 个 DCP，并通过编译、反编译、相机身份、LookTable 和 ToneCurve 检查。
- 新增按品牌分类的支持型号清单，并提供英文 `README.md` 与中文 `README_CN.md`。
- 修复 Python 3.14 / Tcl 9 环境下 PyInstaller 可能错误排除 `tkinter` 的问题。
- Windows 最终 ZIP 已完成“解压后真实启动”测试。
- Windows x64 发布包命名为 `FuProfile Unlocker-Windows-x64-v0.2.6.zip`。
- macOS arm64 发布包已由 Mac 端完成构建，应用包名称与窗口显示名称均为 `FuProfile Unlocker`。
- Windows 最终包已在更名后重新构建；同时用 Canon EOS R 样张完成 8/8 DCP 生成验证。
- 新增统一源码归档，包含 Windows ICO、macOS ICNS 和两平台构建脚本。
- 补充公开仓库所需的 MIT 主许可证、第三方许可证索引、贡献指南、安全策略、Issue 模板和双平台测试工作流。
- 源码打包流程只保留实际使用的八份 XML 风格表，明确排除上游包含 Adobe 配置的 `dcp examples/` 与本项目未使用的 LUT。
- 风格表继续按照 CC BY-NC-SA 4.0 进行非商业分发；项目声明不会将其重新授权为 MIT，也不声称获得 Adobe 或 Fujifilm 官方背书。

## v0.2.5 — 应用图标与发布资源

- 生成并接入 FuProfile Unlocker 专用应用图标。
- 提供 PNG 主图、预览图和 Windows ICO 文件。
- 在应用窗口、任务栏和 Windows 可执行文件中使用新图标。
- 将图标、风格数据和第三方声明纳入打包资源。

## v0.2.4 — RAW 文件拖放与滚动交互

- 集成 `tkinterdnd2`，允许把单张 RAW 直接拖入选择区域。
- 正确解析包含空格的 Windows/macOS 文件路径。
- 对多文件拖入、非文件内容和不支持的格式给出明确提示。
- 增加拖入区域高亮反馈。
- 完善鼠标滚轮、触控板高分辨率滚动、轨道点击和滚动条拖动行为。
- 增加相关界面辅助函数单元测试。

## v0.2.3 — Windows 启动错误修复

- 修复 Windows Tk 不支持 `pointinghand` 光标而导致应用启动时抛出 `TclError` 的问题。
- macOS 继续使用 `pointinghand`，Windows 改用受支持的 `hand2`。
- 增加跨平台光标名称测试，防止同类回归。

## v0.2.2 — Windows 可构建基线

- 建立 macOS/Windows 共用的 Python、Tkinter 和 DCP 生成代码路径。
- 增加 Windows Adobe Standard 搜索路径和 CameraRaw 安装路径。
- 接入 Windows 版 dcpTool 及其运行时 DLL。
- 增加 PyInstaller Windows x64 文件夹式打包和 ZIP 分发流程。
- 提供 Windows 构建、验证和故障排查说明。

## 当前版本范围

- 应用源码版本：`0.2.7`。
- Windows 与 macOS 发布包均使用 `FuProfile Unlocker` 名称。
- 已验证型号清单受现有 RAW 样本范围限制，并非完整兼容性清单；未列出的型号仍可能可用，iPhone DNG 即为已知可用但未系统验证的例子。
- `transport/` 保留 Mac 端回传的 v0.2.7 arm64 包和修改后源码；`release/v0.2.7/` 保存最终三类发布包与统一校验文件。
- 两个平台必须使用同一份 v0.2.7 源码构建，平台端不得维护独立功能分支。

## 跨平台维护原则

Windows 和 macOS 必须使用同一份版本源码，不得在两个平台分别维护功能代码。平台端只应进行原生构建、必要的权限处理、启动验证，以及可选的签名和公证。如果构建时发现必须修改共用源码，应先回到主代码库统一修改并提升版本号，再同时重建两个平台。
