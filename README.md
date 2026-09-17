# FuProfile Unlocker

[简体中文](README_CN.md)

A free desktop utility that creates eight Fujifilm-look Camera Matching DCP profiles for compatible non-Fujifilm RAW cameras. It reads the selected RAW, finds the exact Adobe Standard DCP in the user's local Lightroom/Camera Raw installation, generates and verifies eight profiles, and installs them in the user's CameraRaw profile directory.

## Downloads

Download published builds from [GitHub Releases](../../releases). For v0.2.7, choose:

- `FuProfile Unlocker-Windows-x64-v0.2.7.zip` for 64-bit Windows.
- `FuProfile Unlocker-macOS-arm64-v0.2.7.zip` for Apple Silicon macOS.
- `SHA256SUMS.txt` to verify the downloaded archive.

Lightroom Classic or Adobe Camera Raw must already be installed, including an Adobe Standard
profile for the selected camera. Extract the complete archive before running the application.
The first public build is not backed by a commercial Windows signing certificate or Apple
notarization, so Windows SmartScreen or macOS Gatekeeper may ask for additional confirmation.
Only download release files from this repository and verify their SHA-256 values.

## Features

- Provides Windows x64 and Apple Silicon macOS application bundles.
- Provides English and Simplified Chinese interfaces, follows the system language, and includes an in-app language switch.
- Windows packaging, bundled dcpTool selection, drag-and-drop, and traditional-camera DCP generation are tested end to end.
- The interface and profile-generation core are shared across both platforms.
- No Adobe DCP file is bundled.
- The interface automatically follows the operating system's light or dark appearance.
- The management page records installed camera models and supports per-camera, selected, and complete uninstall actions.
- The installation list supports Tk 9 high-resolution `TouchpadScroll`, legacy mouse-wheel scrolling, track clicking, and draggable scroll thumbs.

## Verified traditional camera models

All **554 models** below were fully validated with the RAW samples available to this project. Each model successfully generated eight DCP profiles and passed compilation, decompilation, camera-identity, LookTable, and ToneCurve checks.

This is a **verified test-coverage list, not an exhaustive compatibility list**. A camera that is not listed may still work when its RAW can be identified and the user's Lightroom/Camera Raw installation contains a matching Adobe Standard profile. iPhone DNG files, for example, are known to work but are not included because phone RAW coverage was not systematically validated. The list also reflects the Adobe Standard profiles installed in the Windows audit environment; an older Adobe installation may support fewer models. Phones, drones, action cameras, cinema cameras, scanners, and native Fujifilm cameras are outside the scope of the model list, not necessarily incompatible with the application.

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

## Development

Contributor setup and test instructions are in [CONTRIBUTING.md](CONTRIBUTING.md).
Platform-specific packaging instructions are available in
[WINDOWS_BUILD_CN.md](WINDOWS_BUILD_CN.md) and [MACOS_BUILD_CN.md](MACOS_BUILD_CN.md).

## Design

- `src/fuprofile_unlocker/core.py`: platform-neutral RAW identity, DCP generation, verification, caching, and installation.
- `src/fuprofile_unlocker/platforms.py`: macOS/Windows Adobe paths and bundled-tool discovery.
- `src/fuprofile_unlocker/app.py`: shared small desktop interface.
- `src/fuprofile_unlocker/theme.py`: cross-platform light/dark detection and color tokens.
- `src/fuprofile_unlocker/installations.py`: safe installation discovery and uninstall operations.
- `resources/style_models.json`: compatibility hints for older Lightroom installations.
- `packaging/build_app.py`: the shared macOS/Windows packaging entry point; only bundled binaries differ by platform.

## Licensing and trademarks

Original FuProfile Unlocker code is licensed under the [MIT License](LICENSE). The eight style
tables are separately licensed under CC BY-NC-SA 4.0 and therefore carry attribution,
share-alike, and non-commercial requirements. dcpTool, ExifTool, tkinterdnd2, and tkDnD retain
their respective licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and the
[license map](licenses/README.md) before redistribution.

Fujifilm, Adobe, Lightroom, Camera Raw, and the referenced profile names are trademarks of
their respective owners and are used only for identification. This project is not affiliated
with or endorsed by Fujifilm or Adobe.
