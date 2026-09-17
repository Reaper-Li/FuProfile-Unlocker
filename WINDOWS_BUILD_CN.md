# Windows 编译与验证说明

本文档用于在 Windows 10/11 x64 上从源码构建 FuProfile Unlocker v0.2.7。
界面、DCP 生成逻辑和测试代码与 macOS 共用；Windows 仅使用不同的 Adobe
目录、ExifTool 和 dcpTool 可执行文件。

## 一、源码包已经包含的内容

- Python/Tkinter 应用源码与自动化测试。
- PyInstaller 跨平台构建脚本。
- Windows 版 `dcpTool.exe`、`iconv.dll`、`libxml2.dll`、`zlib1.dll`。
- dcpTool 的 GPL 许可、源码和原始归档。
- 八套风格所需的 XML 表格及其第三方许可说明。
- RAW 样张清单和可续传下载工具，但不包含约 21 GB 的 RAW 二进制文件。

源码包不包含 Adobe 的基础 DCP。软件运行时只会在用户已经安装的
Lightroom/Camera Raw 目录中查找，绝不随应用复制或分发 Adobe DCP。

## 二、准备环境

1. 安装 64 位 Python 3.11，并在安装器中启用 `py` launcher。
2. 下载 ExifTool 官方 Windows executable package。
3. 解压后把 `exiftool(-k).exe` 改名为 `exiftool.exe`。
4. 在源码中建立以下目录，并将文件放进去：

```text
tools\vendor\exiftool\windows\
├─ exiftool.exe
└─ exiftool_files\
```

如果所下载版本没有 `exiftool_files` 文件夹，只放置 `exiftool.exe` 即可。
也可以不复制文件，而是在构建前设置：

```powershell
$env:FUPROFILE_EXIFTOOL = "C:\完整路径\exiftool.exe"
```

## 三、一键构建

在源码根目录打开 PowerShell：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\packaging\build_windows.ps1
```

脚本将自动完成：

1. 创建 `.venv`；
2. 安装固定版本的 PyInstaller；
3. 运行全部单元测试；
4. 检查 dcpTool、风格数据和 ExifTool；
5. 构建 Windows 应用目录；
6. 生成可分发 ZIP。

构建结果：

```text
dist\FuProfile Unlocker\FuProfile Unlocker.exe
dist\FuProfile Unlocker-Windows-x64-v0.2.7.zip
```

如系统没有 `py` launcher，可手动执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe packaging\build_app.py
```

## 四、Windows 运行验证

建议至少执行以下检查：

1. 双击 `dist\FuProfile Unlocker\FuProfile Unlocker.exe`。
2. 确认中文系统默认显示简体中文，并用标题栏 `EN / 中文` 按钮往返切换，检查两种语言均完整显示。
3. 确认两种语言在浅色、深色主题下文字和按钮可读。
4. 在安装页面选择一张非富士 RAW。
5. 确认软件正确显示品牌、型号，并生成八个 DCP。
6. 确认文件写入：

```text
%APPDATA%\Adobe\CameraRaw\CameraProfiles\FuProfile Unlocker\<相机型号>\
```

7. 重启 Lightroom，在 Camera Matching 中确认八种风格。
8. 在管理页面以英文和中文测试单项、复选和全部卸载。
9. 使用鼠标滚轮和触控板滚动卸载列表，并拖动右侧滚动条。
10. 确认应用目录内包含 `LICENSE`、`THIRD_PARTY_NOTICES.md` 和 `licenses/`。
11. 确认包内没有 Adobe Standard 或 Camera Matching DCP。
12. 如使用代码签名证书，应先签署最终 EXE，再生成 ZIP 和校验值。
13. 在生成 ZIP 后计算 SHA-256，并把结果加入 Release 的 `SHA256SUMS.txt`。

软件会在下列位置寻找 Adobe Standard：

```text
%PROGRAMDATA%\Adobe\CameraRaw\CameraProfiles\Adobe Standard\
%APPDATA%\Adobe\CameraRaw\CameraProfiles\Adobe Standard\
```

若某型号提示找不到基础配置，先升级 Lightroom/Adobe Camera Raw，再重新启动软件。

## 五、常见问题

### 提示找不到 ExifTool

确认文件名是 `exiftool.exe`，不是 `exiftool(-k).exe`；或设置
`FUPROFILE_EXIFTOOL` 为完整路径后重新构建。

### 提示缺少 dcpTool 或 DLL

确认以下四个文件没有被杀毒软件隔离：

```text
tools\vendor\dcptool\dcpTool_1_10_0\Binaries\Windows\dcpTool.exe
tools\vendor\dcptool\dcpTool_1_10_0\Binaries\Windows\iconv.dll
tools\vendor\dcptool\dcpTool_1_10_0\Binaries\Windows\libxml2.dll
tools\vendor\dcptool\dcpTool_1_10_0\Binaries\Windows\zlib1.dll
```

### Windows Defender 警告未知发布者

当前测试包没有商业代码签名证书。请只在自己构建、校验过的源码包上测试。
正式发布时可再配置 Authenticode 签名，这不影响功能验证。

### 直接复制单个 EXE 后无法运行

当前使用 PyInstaller `--onedir`，必须分发整个
`dist\FuProfile Unlocker` 文件夹或脚本生成的 ZIP，不能只复制 EXE。

## 六、重要第三方许可

构建或分发前请阅读 `THIRD_PARTY_NOTICES.md`：

- 风格数据使用 CC BY-NC-SA 4.0，不允许商业使用，并有署名与相同方式共享要求。
- dcpTool 使用 GPL v2 or later；分发二进制时需要保留许可与相应源码。
- Adobe 基础 DCP 不在源码包和应用包中。
