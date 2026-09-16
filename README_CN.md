# FuProfile Unlocker

[English](README.md)

一款免费的桌面工具，可为兼容的非富士 RAW 相机创建八种富士风格的 Camera Matching DCP 配置。它会读取所选 RAW，在用户本机的 Lightroom/Camera Raw 安装目录中查找准确匹配的 Adobe Standard DCP，生成并验证八种配置，然后将其安装到用户的 CameraRaw 配置目录。

## 下载

请从 [GitHub Releases](../../releases) 下载正式发布文件。v0.2.6 应选择：

- `FuProfile Unlocker-Windows-x64-v0.2.6.zip`：适用于 64 位 Windows。
- `FuProfile Unlocker-macOS-arm64-v0.2.6.zip`：适用于 Apple Silicon Mac。
- `SHA256SUMS.txt`：用于核验下载文件。

电脑必须已经安装 Lightroom Classic 或 Adobe Camera Raw，并且其中包含所选相机的
Adobe Standard 配置。运行前请完整解压整个压缩包。首个公开版本尚未使用商业 Windows
代码签名证书，也尚未完成 Apple 公证，因此 Windows SmartScreen 或 macOS Gatekeeper
可能要求额外确认。请只从本项目仓库下载发布文件，并核对 SHA-256。

## 功能

- 提供 Windows x64 与 Apple Silicon macOS 应用包。
- Windows 打包、内置 dcpTool 选择、拖放操作和传统相机 DCP 生成已经通过端到端测试。
- 两个平台共用相同的界面与配置生成核心。
- 不内置任何 Adobe DCP 文件。
- 界面会自动跟随操作系统的浅色或深色外观。
- 管理页面会记录已安装的相机型号，并支持按相机卸载、选择卸载和全部卸载。
- 安装列表支持 Tk 9 高分辨率 `TouchpadScroll`、传统鼠标滚轮滚动、点击滚动轨道和拖动滚动条滑块。

## 已验证的传统相机型号

以下 **554 个型号**均使用本项目已取得的对应 RAW 样本完成完整生成验证：每个型号均成功生成八个 DCP，并通过编译、反编译、相机身份、LookTable 和 ToneCurve 检查。

这是一份**已验证测试覆盖清单，并不是完整兼容性清单**。未列出的相机只要 RAW 能被正确识别，并且用户安装的 Lightroom/Camera Raw 中存在匹配的 Adobe Standard 配置，仍然可能正常使用。例如，iPhone DNG 已知可以处理，但由于手机 RAW 没有进行系统性覆盖验证，因此没有收入本表。该清单也取决于本次 Windows 审计环境中已有的 Adobe Standard 配置；Adobe 版本较旧时，可用型号可能更少。手机、无人机、运动相机、电影机、扫描仪及富士原生相机只是未纳入本型号清单，并不等于一定与软件不兼容。

### Canon

`EOS 1000D`, `EOS 100D`, `EOS 1100D`, `EOS 1200D`, `EOS 1300D`, `EOS 2000D`, `EOS 200D`, `EOS 200D II`, `EOS 20D`  
`EOS 250D`, `EOS 30D`, `EOS 350D DIGITAL`, `EOS 4000D`, `EOS 400D DIGITAL`, `EOS 40D`, `EOS 450D`, `EOS 500D`  
`EOS 50D`, `EOS 550D`, `EOS 5D`, `EOS 5D Mark II`, `EOS 5D Mark III`, `EOS 5D Mark IV`, `EOS 5DS`, `EOS 5DS R`  
`EOS 600D`, `EOS 60D`, `EOS 650D`, `EOS 6D`, `EOS 6D Mark II`, `EOS 700D`, `EOS 70D`, `EOS 750D`, `EOS 760D`, `EOS 77D`  
`EOS 7D`, `EOS 7D Mark II`, `EOS 800D`, `EOS 80D`, `EOS 850D`, `EOS 90D`, `EOS DIGITAL REBEL XSi`  
`EOS DIGITAL REBEL XT`, `EOS DIGITAL REBEL XTi`, `EOS Kiss Digital N`, `EOS Kiss F`, `EOS KISS M`, `EOS Kiss X3`  
`EOS Kiss X4`, `EOS Kiss X80`, `EOS Kiss X9`, `EOS M`, `EOS M10`, `EOS M100`, `EOS M2`, `EOS M200`, `EOS M3`, `EOS M5`  
`EOS M50`, `EOS M50m2`, `EOS M6`, `EOS M6 Mark II`, `EOS R`, `EOS R10`, `EOS R100`, `EOS R3`, `EOS R5`, `EOS R50`  
`EOS R50 V`, `EOS R5m2`, `EOS R6`, `EOS R6 Mark III`, `EOS R6m2`, `EOS R7`, `EOS R8`, `EOS REBEL SL1`, `EOS Rebel SL2`  
`EOS Rebel SL3`, `EOS Rebel T100`, `EOS REBEL T1i`, `EOS REBEL T2i`, `EOS REBEL T3`, `EOS REBEL T3i`  
`EOS REBEL T4i`, `EOS REBEL T5`, `EOS REBEL T5i`, `EOS Rebel T6`, `EOS Rebel T6i`, `EOS Rebel T6s`, `EOS Rebel T7`  
`EOS REBEL T7i`, `EOS RP`, `EOS-1D Mark II N`, `EOS-1D Mark III`, `EOS-1D Mark IV`, `EOS-1D X`, `EOS-1D X Mark II`  
`EOS-1D X Mark III`, `PowerShot G1 X`, `PowerShot G1 X Mark II`, `PowerShot G1 X Mark III`, `PowerShot G11`  
`PowerShot G12`, `PowerShot G15`, `PowerShot G16`, `PowerShot G3 X`, `PowerShot G5 X`, `PowerShot G5 X Mark II`  
`PowerShot G7 X`, `PowerShot G7 X Mark II`, `PowerShot G7 X Mark III`, `PowerShot G9`, `PowerShot G9 X`  
`PowerShot G9 X Mark II`, `PowerShot S100`, `PowerShot S110`, `PowerShot S120`, `PowerShot S95`  
`PowerShot SX50 HS`, `PowerShot SX60 HS`, `PowerShot SX70 HS`, `PowerShot V1`

### Kodak

`EasyShare Z981 Digital Camera`, `EasyShare Z990 Digital Camera`

### Leaf

`Aptus 22(LF10043    )/Mamiya 645 AFD`, `Credo 40`

### Leica

`C (Typ 112)`, `C-Lux`, `CL`, `D-LUX (Typ 109)`, `D-LUX 4`, `D-LUX 5`, `D-LUX 6`, `D-Lux 7`, `DIGILUX 3`, `M (Typ 240)`  
`M10`, `M10-R`, `M8 Digital Camera`, `M9 Digital Camera`, `Q (Typ 116)`, `Q2`, `SL (Typ 601)`, `SL2`  
`V-LUX (Typ 114)`, `V-LUX 4`, `V-Lux 5`, `X2`

### Minolta

`ALPHA SWEET DIGITAL`, `ALPHA-7 DIGITAL`, `DiMAGE 5`, `DiMAGE A2`, `DYNAX 5D`, `DYNAX 7D`, `MAXXUM 7D`

### Nikon

`1 AW1`, `1 J1`, `1 J2`, `1 J3`, `1 J4`, `1 J5`, `1 S1`, `1 V1`, `1 V2`, `1 V3`, `COOLPIX A`, `COOLPIX A1000`  
`COOLPIX B700`, `COOLPIX P1000`, `COOLPIX P1100`, `COOLPIX P330`, `COOLPIX P7700`, `COOLPIX P7800`, `COOLPIX P950`  
`D100`, `D1H`, `D1X`, `D200`, `D2H`, `D2Hs`, `D2X`, `D2Xs`, `D3`, `D300`, `D3000`, `D300S`, `D3100`, `D3200`, `D3300`  
`D3400`, `D3500`, `D3S`, `D3X`, `D4`, `D40`, `D40X`, `D4S`, `D5`, `D50`, `D500`, `D5000`, `D5100`, `D5200`, `D5300`, `D5500`  
`D5600`, `D6`, `D60`, `D600`, `D610`, `D70`, `D700`, `D7000`, `D70s`, `D7100`, `D7200`, `D750`, `D7500`, `D780`, `D80`  
`D800`, `D800E`, `D810`, `D850`, `D90`, `Df`, `Z 30`, `Z 5`, `Z 50`, `Z 6`, `Z 6_2`, `Z 7`, `Z 7_2`, `Z 8`, `Z 9`, `Z f`  
`Z fc`, `Z50_2`, `Z5_2`, `Z6_3`

### Olympus

`C5060WZ`, `C7070WZ`, `E-1`, `E-10`, `E-3`, `E-300`, `E-330`, `E-400`, `E-410`, `E-420`, `E-450`, `E-5`, `E-500`, `E-510`  
`E-620`, `E-M1`, `E-M10`, `E-M10 Mark III`, `E-M10MarkIIIS`, `E-M1X`, `E-M5`, `E-P1`, `E-P2`, `E-P3`, `E-P5`, `E-P7`  
`E-PL1`, `E-PL10`, `E-PL2`, `E-PL3`, `E-PL5`, `E-PL6`, `E-PL7`, `E-PL8`, `E-PL9`, `E-PM1`, `E-PM2`, `PEN-F`, `SH-2`  
`SP510UZ`, `SP550UZ`, `SP565UZ`, `SP570UZ`, `STYLUS1`, `STYLUS1,1s`, `TG-4`, `TG-5`, `TG-6`, `XZ-1`, `XZ-10`, `XZ-2`

### Panasonic

`DC-FZ10002`, `DC-FZ45`, `DC-FZ80`, `DC-FZ82`, `DC-G100`, `DC-G100D`, `DC-G110`, `DC-G9`, `DC-G90`, `DC-G91`, `DC-G95`  
`DC-G95D`, `DC-G9M2`, `DC-GF10`, `DC-GH5`, `DC-GH5M2`, `DC-GH5S`, `DC-GH6`, `DC-GH7`, `DC-GX7MK3`, `DC-GX800`  
`DC-GX850`, `DC-GX880`, `DC-GX9`, `DC-LX100M2`, `DC-S1`, `DC-S1H`, `DC-S1M2`, `DC-S1M2ES`, `DC-S1R`, `DC-S1RM2`, `DC-S5`  
`DC-S5M2`, `DC-S5M2X`, `DC-S9`, `DC-TZ200D`, `DC-TZ202`, `DC-TZ90`, `DC-TZ91`, `DC-TZ95`, `DC-TZ95D`, `DC-TZ96`  
`DC-ZS200D`, `DMC-FX150`, `DMC-FZ100`, `DMC-FZ1000`, `DMC-FZ150`, `DMC-FZ200`, `DMC-FZ2000`, `DMC-FZ2500`  
`DMC-FZ28`, `DMC-FZ300`, `DMC-FZ330`, `DMC-FZ35`, `DMC-FZ38`, `DMC-FZ45`, `DMC-FZ50`, `DMC-FZ70`, `DMC-FZ8`, `DMC-G10`  
`DMC-G2`, `DMC-G3`, `DMC-G5`, `DMC-G6`, `DMC-G7`, `DMC-G70`, `DMC-G80`, `DMC-G81`, `DMC-G85`, `DMC-GF1`, `DMC-GF2`  
`DMC-GF6`, `DMC-GF7`, `DMC-GF8`, `DMC-GH1`, `DMC-GH2`, `DMC-GH3`, `DMC-GH4`, `DMC-GM1`, `DMC-GM1S`, `DMC-GM5`, `DMC-GX1`  
`DMC-GX7MK2`, `DMC-GX8`, `DMC-GX80`, `DMC-GX85`, `DMC-LF1`, `DMC-LX1`, `DMC-LX100`, `DMC-LX3`, `DMC-LX7`, `DMC-TZ60`  
`DMC-TZ61`, `DMC-TZ70`, `DMC-TZ80`, `DMC-TZ81`, `DMC-ZS100`, `DMC-ZS40`, `DMC-ZS60`

### Pentax

`645D`, `645Z`, `K-01`, `K-1`, `K-1 Mark II`, `K-3`, `K-3 II`, `K-3 Mark III`, `K-30`, `K-5`, `K-5 II`, `K-5 II s`, `K-50`  
`K-500`, `K-7`, `K-70`, `K-r`, `K-S1`, `K-S2`, `K-x`, `K100D`, `K100D Super`, `K10D`, `K110D`, `K2000`, `K200D`, `K20D`  
`KF`, `KP`, `MX-1`, `Q`, `Q7`

### Phase One

`H 25`, `IQ150`, `IQ180`, `IQ3 100MP`, `IQ3 100MP Trichr`, `IQ4 150MP`, `P20+`, `P25+`, `P40+`, `P45+`, `P65+`

### Ricoh

`GR III`, `GR IIIx`, `S10 24-72mm F2.5-4.4 VC`

### Samsung

`EX1`, `GX-1L`, `GX10`, `GX20`, `NX mini`, `NX1`, `NX10`, `NX1000`, `NX11`, `NX1100`, `NX20`, `NX200`, `NX2000`, `NX210`  
`NX30`, `NX300`, `NX3000`, `NX3300`, `NX5`, `NX500`, `WB2000`

### Sigma

`fp`, `fp L`

### Sony

`DSC-F828`, `DSC-HX95`, `DSC-HX99`, `DSC-R1`, `DSC-RX0`, `DSC-RX0M2`, `DSC-RX1`, `DSC-RX10`, `DSC-RX100`, `DSC-RX100M2`  
`DSC-RX100M3`, `DSC-RX100M4`, `DSC-RX100M5`, `DSC-RX100M5A`, `DSC-RX100M6`, `DSC-RX100M7`, `DSC-RX100M7A`  
`DSC-RX10M3`, `DSC-RX10M4`, `DSC-RX1R`, `DSC-RX1RM2`, `DSC-RX1RM3`, `DSLR-A100`, `DSLR-A200`, `DSLR-A230`, `DSLR-A290`  
`DSLR-A350`, `DSLR-A380`, `DSLR-A390`, `DSLR-A450`, `DSLR-A500`, `DSLR-A560`, `DSLR-A700`, `DSLR-A900`, `ILCA-68`  
`ILCA-77M2`, `ILCA-99M2`, `ILCE-1`, `ILCE-1M2`, `ILCE-3000`, `ILCE-3500`, `ILCE-5000`, `ILCE-5100`, `ILCE-6000`  
`ILCE-6001`, `ILCE-6100`, `ILCE-6300`, `ILCE-6400`, `ILCE-6400A`, `ILCE-6500`, `ILCE-6600`, `ILCE-6700`, `ILCE-7`  
`ILCE-7C`, `ILCE-7CM2`, `ILCE-7CR`, `ILCE-7M2`, `ILCE-7M3`, `ILCE-7M4`, `ILCE-7M5`, `ILCE-7R`, `ILCE-7RM2`, `ILCE-7RM3`  
`ILCE-7RM3A`, `ILCE-7RM4`, `ILCE-7RM4A`, `ILCE-7RM5`, `ILCE-7S`, `ILCE-7SM2`, `ILCE-7SM3`, `ILCE-9`, `ILCE-9M2`  
`ILCE-9M3`, `ILCE-QX1`, `NEX-3N`, `NEX-5`, `NEX-5N`, `NEX-5T`, `NEX-6`, `NEX-C3`  
`NEX-F3`, `SLT-A33`, `SLT-A35`, `SLT-A37`, `SLT-A55V`, `SLT-A57`, `SLT-A58`, `SLT-A65V`, `SLT-A77V`, `SLT-A99V`, `ZV-1`  
`ZV-1M2`, `ZV-E1`, `ZV-E10`, `ZV-E10M2`

## 开发

贡献者环境配置与测试方法请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。
平台打包说明请参阅 [WINDOWS_BUILD_CN.md](WINDOWS_BUILD_CN.md) 和
[MACOS_BUILD_CN.md](MACOS_BUILD_CN.md)。

## 设计

- `src/fuprofile_unlocker/core.py`：跨平台的 RAW 身份识别、DCP 生成、验证、缓存和安装。
- `src/fuprofile_unlocker/platforms.py`：macOS/Windows Adobe 路径和内置工具发现。
- `src/fuprofile_unlocker/app.py`：两平台共用的轻量桌面界面。
- `src/fuprofile_unlocker/theme.py`：跨平台浅色/深色模式检测与颜色标记。
- `src/fuprofile_unlocker/installations.py`：安全的安装发现与卸载操作。
- `resources/style_models.json`：用于较旧 Lightroom 安装的兼容性提示。
- `packaging/build_app.py`：macOS/Windows 共用的打包入口；仅内置二进制文件因平台而异。

## 许可证与商标

FuProfile Unlocker 的原创代码使用 [MIT License](LICENSE)。八个风格数据表单独使用
CC BY-NC-SA 4.0，具有署名、相同方式共享和非商业限制。dcpTool、ExifTool、
tkinterdnd2 与 tkDnD 分别保留各自的许可证。重新分发前请阅读
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 和[许可证索引](licenses/README.md)。

Fujifilm、Adobe、Lightroom、Camera Raw 以及文中提及的配置名称均为其各自权利人的
商标，在此仅用于识别用途。本项目与 Fujifilm 或 Adobe 没有隶属关系，也未获得其官方背书。
