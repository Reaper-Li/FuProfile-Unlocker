# macOS 构建与验证说明

本文用于在 macOS 上从锁定的 v0.2.7 源码构建 FuProfile Unlocker `.app`。PyInstaller 不能从 Windows 交叉编译 macOS 应用，因此必须在真实 macOS 环境中完成。

## 一、环境要求

- macOS 13 或更高版本。
- Python 3.11 或更高版本，建议使用稳定的 64 位 Python 3.12 或 3.13。
- 系统 Python 必须包含可用的 Tkinter。
- ExifTool。
- Xcode Command Line Tools（用于系统工具和后续签名流程）。

使用 Homebrew 时可执行：

```sh
xcode-select --install
brew install python@3.13 exiftool
```

确认环境：

```sh
python3 --version
python3 -c 'import tkinter; print(tkinter.TkVersion)'
exiftool -ver
```

## 二、解压后的权限处理

Windows 创建的 ZIP 不保证保留 Unix 可执行权限。进入项目根目录后执行：

```sh
chmod +x tools/vendor/dcptool/dcpTool_1_10_0/Binaries/macOS/dcpTool
chmod +x tools/download_raw_samples.sh
```

项目内的 macOS dcpTool 是包含 Intel x86_64 与 Apple Silicon arm64 的通用 Mach-O 文件。

## 三、建立构建环境

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-build.txt
```

如果 `exiftool` 不在默认 `PATH` 中：

```sh
export FUPROFILE_EXIFTOOL="$(command -v exiftool)"
```

## 四、构建前测试

```sh
export PYTHONPATH="$PWD/src"
.venv/bin/python -m unittest discover -s tests -v
```

全部测试通过后再构建：

```sh
.venv/bin/python packaging/build_app.py
```

预期输出：

```text
dist/FuProfile Unlocker.app
```

## 五、最低发布验证

1. 双击或执行 `open "dist/FuProfile Unlocker.app"`，确认主窗口正常出现且显示 v0.2.7。
2. 确认英文系统默认显示英文，并用标题栏 `中文 / EN` 按钮往返切换，检查两种语言均完整显示。
3. 检查两种语言下的浅色/深色主题、图标、滚动与“管理与卸载”页面。
4. 分别使用按钮和拖放方式选择一张传统相机 RAW。
5. 确认应用能找到本机 Adobe Standard，并生成 8 个 DCP。
6. 确认配置安装到：
   `~/Library/Application Support/Adobe/CameraRaw/CameraProfiles/FuProfile Unlocker/`。
7. 重启 Lightroom，确认八个配置可见。
8. 在管理页面验证单项卸载和选择卸载。
9. 确认 `.app/Contents/Resources` 内包含 `LICENSE`、`THIRD_PARTY_NOTICES.md` 和 `licenses/`。
10. 确认包内没有 Adobe Standard 或 Camera Matching DCP。
11. 所有资源修改必须发生在最终签名与公证之前，否则签名会失效。
12. 在最终压缩后把 SHA-256 加入 Release 的 `SHA256SUMS.txt`。

建议至少使用一张 Canon、Nikon 或 Sony RAW 完成端到端验证。不要把富士原生 RAW 或手机 DNG 作为首发验收样本。

## 六、生成交付压缩包

macOS 应用建议使用 `ditto` 打包，以保留资源分叉和应用包结构：

```sh
ditto -c -k --sequesterRsrc --keepParent \
  "dist/FuProfile Unlocker.app" \
  "dist/FuProfile Unlocker-macOS-arm64-v0.2.7.zip"

shasum -a 256 "dist/FuProfile Unlocker-macOS-arm64-v0.2.7.zip"
```

## 七、签名和公证

未签名版本只能用于内部测试。公开分发时建议使用 Apple Developer ID Application 证书完成 `codesign`，再通过 `notarytool` 提交公证并执行 `stapler`。签名、公证凭据和证书不应写入源码包。

## 八、常见问题

- 找不到 ExifTool：设置 `FUPROFILE_EXIFTOOL` 为实际可执行文件路径。
- dcpTool 权限被拒绝：重新执行 `chmod +x`。
- 找不到 Adobe Standard：先安装或更新 Lightroom / Adobe Camera Raw。
- 拖放不可用：确认 `tkinterdnd2==0.6.3` 已安装，并从新构建的 `.app` 启动。
- Gatekeeper 阻止启动：内部测试可由用户在 Finder 中右键选择“打开”；公开发行应完成签名和公证，不应指导用户关闭系统安全功能。
