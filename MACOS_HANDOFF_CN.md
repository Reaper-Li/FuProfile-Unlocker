# FuProfile Unlocker v0.2.7 macOS 构建交接说明

本文供 macOS 构建人员使用。请只使用随本交接包提供的
`FuProfile Unlocker-source-v0.2.7.zip`，不要使用此前保存的源码或 `.app`。
PyInstaller 不能在 Windows 上交叉编译 macOS 应用，因此最终 `.app` 必须在真实 Mac 上生成。

## 一、本次交接基线

- 产品名称：`FuProfile Unlocker`
- 源码版本：`0.2.7`
- 目标产物：Apple Silicon（arm64）macOS 应用
- Bundle ID：`org.fuprofileunlocker.app`
- 最终文件名：`FuProfile Unlocker-macOS-arm64-v0.2.7.zip`
- Python 包名已经正式改为 `fuprofile_unlocker`。
- 构建环境变量使用 `FUPROFILE_EXIFTOOL`；不要再使用旧缩写。
- 不需要保留或迁移任何早期应用名称、安装目录或内部模块名。

README 中的 554 个型号是使用现有 RAW 样本完成验证的测试覆盖清单，并非完整兼容性清单。
未列出的型号仍可能正常使用；iPhone DNG 即为已知可用但未做系统性覆盖验证的例子。
首发验收仍应使用清单内的传统相机 RAW，以便得到可重复的结果。

## 二、收到文件后先验证

交接目录应至少包含：

- `FuProfile Unlocker-source-v0.2.7.zip`
- `MACOS_HANDOFF_CN.md`
- `SHA256SUMS.txt`

在 Terminal 中进入交接目录并核验源码包：

```sh
shasum -a 256 "FuProfile Unlocker-source-v0.2.7.zip"
cat SHA256SUMS.txt
```

输出必须与 `SHA256SUMS.txt` 中的源码包记录完全一致。校验不一致时不要继续构建。

## 三、构建环境

建议配置：

- Apple Silicon Mac，macOS 13 或更高版本。
- 原生 arm64 Python 3.12 或 3.13，并带有可用的 Tkinter。
- ExifTool。
- Xcode Command Line Tools。
- 已安装 Lightroom Classic 或 Adobe Camera Raw，并至少包含验收相机的 Adobe Standard DCP。

使用 Homebrew 时可执行：

```sh
xcode-select --install
brew install python@3.13 exiftool
```

确认所有工具均以 Apple Silicon 环境运行：

```sh
uname -m
python3 --version
python3 -c 'import platform, tkinter; print(platform.machine(), tkinter.TkVersion)'
exiftool -ver
```

`uname -m` 和 Python 的 `platform.machine()` 都应显示 `arm64`。不要在 Rosetta 的 x86_64
Python 环境中构建本次 arm64 发布包。

## 四、解压并建立环境

```sh
ditto -x -k \
  "FuProfile Unlocker-source-v0.2.7.zip" \
  "FuProfile Unlocker-source-v0.2.7-unpacked"

cd "FuProfile Unlocker-source-v0.2.7-unpacked/FuProfile Unlocker-source-v0.2.7"

chmod +x tools/vendor/dcptool/dcpTool_1_10_0/Binaries/macOS/dcpTool
chmod +x tools/download_raw_samples.sh

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-build.txt

export PYTHONPATH="$PWD/src"
export FUPROFILE_EXIFTOOL="$(command -v exiftool)"
```

## 五、测试并构建

先运行单元测试：

```sh
.venv/bin/python -m unittest discover -s tests -v
```

应有 22 项测试全部通过。随后构建：

```sh
.venv/bin/python packaging/build_app.py
```

预期生成：

```text
dist/FuProfile Unlocker.app
```

构建脚本会进行 ad-hoc codesign。检查应用信息和二进制架构：

```sh
/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' \
  "dist/FuProfile Unlocker.app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' \
  "dist/FuProfile Unlocker.app/Contents/Info.plist"
file "dist/FuProfile Unlocker.app/Contents/MacOS/FuProfile Unlocker"
codesign --verify --deep --strict --verbose=2 "dist/FuProfile Unlocker.app"
```

预期 Bundle ID 为 `org.fuprofileunlocker.app`、版本为 `0.2.7`，主程序架构包含 `arm64`。

## 六、发布验收

请在真实 Lightroom/Camera Raw 环境中完成以下检查：

1. 双击应用，确认窗口名称和界面内名称均为 `FuProfile Unlocker`，版本为 `v0.2.7`。
2. 在英文系统语言下启动，确认默认显示英文；点击 `中文` 后确认完整切换为简体中文，再点击 `EN` 切回英文。
3. 验证两种语言下的浅色与深色外观、应用图标、滚动和“管理与卸载”页面。
4. 使用按钮选择一张已验证列表内的传统相机 RAW，确认识别成功。
5. 再使用拖放方式选择 RAW，确认拖放逻辑正常。
6. 生成八个 DCP，确认英文进度与完成信息正确，且全部通过应用内验证并安装到：
   `~/Library/Application Support/Adobe/CameraRaw/CameraProfiles/FuProfile Unlocker/`。
7. 重启 Lightroom，确认八个配置可见且可以应用。
8. 在管理页面验证英文与中文的单项卸载和选择卸载。
9. 确认应用资源中包含 `LICENSE`、`THIRD_PARTY_NOTICES.md` 和 `licenses/`。
10. 确认 `.app` 内没有任何 Adobe Standard、Adobe Camera Matching 或其他 `.dcp` 文件：

```sh
find "dist/FuProfile Unlocker.app" -type f -iname '*.dcp' -print
```

上述命令应无输出。验收时不要把用户的 Adobe DCP、私人 RAW 或签名凭据放回源码包。

## 七、生成最终 ZIP

使用 `ditto` 保留 macOS 应用包结构：

```sh
ditto -c -k --sequesterRsrc --keepParent \
  "dist/FuProfile Unlocker.app" \
  "dist/FuProfile Unlocker-macOS-arm64-v0.2.7.zip"

shasum -a 256 "dist/FuProfile Unlocker-macOS-arm64-v0.2.7.zip"
```

如果有 Apple Developer ID，请在压缩前完成正式签名、公证和 stapling；任何资源修改都必须
发生在最终签名之前。没有证书时请保留 ad-hoc 签名，不要关闭 Gatekeeper，也不要把证书、
密码或公证凭据写入项目文件。

## 八、请回传的内容

请回传：

- `FuProfile Unlocker-macOS-arm64-v0.2.7.zip`
- 该 ZIP 的 SHA-256
- 单元测试通过结果
- macOS 版本、Mac 芯片、Python 版本和 ExifTool 版本
- Bundle ID、应用版本、主程序 arm64 架构和 `codesign --verify` 的检查结果
- 使用的验收相机型号，以及生成 8/8 DCP、Lightroom 显示和卸载测试结果
- 是否已完成 Developer ID 签名与 Apple 公证；未完成时明确写“ad-hoc 签名、未公证”

不要回传 Adobe DCP、测试 RAW、Apple 证书或任何账号凭据。

更详细的构建与故障排查说明见 `MACOS_BUILD_CN.md`。
