# 源码包内容

此统一归档用于构建和验证锁定的 FuProfile Unlocker v0.2.7 Windows 与 macOS 版本。

包含：

- `src/`：应用源码。
- `tests/`：单元测试。
- `packaging/`：macOS/Windows 公共构建脚本与 Windows 一键构建脚本。
- `resources/`：Windows ICO、macOS ICNS、应用图标源文件和相机兼容性提示数据。
- `tools/vendor/dcptool/`：构建需要的 dcpTool 二进制、GPL 文本和对应源码。
- `tools/vendor/fujifilm-camera-profiles/.../xml tables/`：运行时实际使用的八份风格表。
- `licenses/`：第三方许可证副本与风格数据署名记录。
- `RAW/manifest.json`：921 个 CC0 RAW 样张的可复现清单。
- `RAW/README.md`：RAW 语料说明。
- `tools/sync_raw_corpus.py`：按清单重新下载 RAW 的工具。
- `README.md`、`README_CN.md`：英文和中文项目说明及 554 个已验证传统相机型号。
- `VERSION_HISTORY_CN.md`：本轮接手后的版本变化与冻结状态。
- `MACOS_BUILD_CN.md`：macOS 构建、验证、压缩与签名提示。
- `MACOS_HANDOFF_CN.md`：交给 Mac 构建人员的版本基线、操作步骤、验收和回传清单。
- `WINDOWS_BUILD_CN.md`：Windows 编译、验证和故障排查说明。
- `THIRD_PARTY_NOTICES.md`：第三方许可与分发注意事项。

有意不包含：

- 约 21 GB 的 RAW 二进制样张；可在 Windows 上按需重新下载。
- `.venv/` Python 虚拟环境。
- `build/`、`dist/` 旧构建产物。
- `generated/` 本机测试生成的 DCP。
- Windows/macOS 应用包和本机缓存。
- `reports/` 本机兼容性审计过程记录；最终支持结论已经整理到 README。
- Adobe 的任何基础 DCP。
- 上游 `FujifilmCameraProfiles` 中包含 Adobe 配置的 `dcp examples/` 目录，以及本项目未使用的 LUT 和示例资源。

构建端应首先阅读 `VERSION_HISTORY_CN.md` 以及对应平台的构建文档。macOS 解压后必须恢复 dcpTool 的可执行权限，再运行测试和构建。两个平台应始终使用同一份版本源码，平台端只负责原生打包和验证。

统一源码包必须通过 `python packaging/build_source.py` 生成，不应直接压缩整个工作目录。
