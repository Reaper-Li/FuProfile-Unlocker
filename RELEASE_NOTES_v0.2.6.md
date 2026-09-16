# FuProfile Unlocker v0.2.6

FuProfile Unlocker creates eight Fujifilm-look Camera Matching DCP profiles for supported
non-Fujifilm RAW cameras by using the camera's locally installed Adobe Standard profile.

## Downloads

- `FuProfile Unlocker-Windows-x64-v0.2.6.zip`: Windows 64-bit portable build.
- `FuProfile Unlocker-macOS-arm64-v0.2.6.zip`: Apple Silicon macOS application.
- `FuProfile Unlocker-source-v0.2.6.zip`: complete corresponding source and build files.
- `SHA256SUMS.txt`: SHA-256 values for release verification.

## Highlights

- Verified end-to-end generation for 554 traditional-camera models across 14 brands.
- Generates and verifies PROVIA, Velvia, ASTIA, Classic Chrome, REALA ACE, PRO Neg. Hi,
  PRO Neg. Std, and ETERNA profiles.
- Supports RAW drag and drop, light/dark appearance, and safe per-camera uninstall management.
- Uses one shared Windows/macOS source tree.

## Requirements and limitations

- Lightroom Classic or Adobe Camera Raw must already contain an Adobe Standard profile for
  the selected camera.
- The verified model list is limited by the RAW samples available for testing and is not an
  exhaustive compatibility list. Unlisted models may work when a matching Adobe Standard
  profile is installed; iPhone DNG files are known to work but were not systematically covered.
- Fujifilm-native RAW files are outside this release's scope.
- Windows requires 64-bit Windows. The macOS asset is for Apple Silicon only.
- This release is not backed by a commercial Windows code-signing certificate or Apple
  notarization. Verify the checksum and expect a first-launch system warning.

## 中文摘要

本版本已使用现有 RAW 样本验证 14 个品牌、554 个传统相机型号，可为兼容的非富士 RAW
相机生成并验证八种富士风格 DCP。该清单不是完整兼容性清单；未列出的型号仍可能可用，
iPhone DNG 即为已知可用但未系统验证的例子。使用前必须已经安装 Lightroom Classic 或
Adobe Camera Raw，并确保其中包含对应相机的 Adobe Standard 配置。富士原生 RAW 暂不属于本版范围。

## Licensing

Original application code is MIT-licensed. The style tables are CC BY-NC-SA 4.0 and retain
non-commercial and share-alike requirements. See `THIRD_PARTY_NOTICES.md` before redistribution.
