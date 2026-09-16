$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    throw "此脚本只能在 Windows PowerShell 或 Windows 上的 PowerShell 7 中运行。"
}

$Version = (Select-String -Path "src\fuprofile_unlocker\__init__.py" -Pattern '__version__ = "([^"]+)"').Matches[0].Groups[1].Value
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.11 -m venv .venv
    }
    if (-not (Test-Path $VenvPython) -and (Get-Command python -ErrorAction SilentlyContinue)) {
        & python -m venv .venv
    }
    if (-not (Test-Path $VenvPython)) {
        throw "未找到 Python。请先安装 64 位 Python 3.11 或更高版本。"
    }
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements-build.txt

if (-not $env:FUPROFILE_EXIFTOOL) {
    $BundledExifTool = Join-Path $ProjectRoot "tools\vendor\exiftool\windows\exiftool.exe"
    if (Test-Path $BundledExifTool) {
        $env:FUPROFILE_EXIFTOOL = $BundledExifTool
    } else {
        $LocatedExifTool = Get-Command exiftool.exe -ErrorAction SilentlyContinue
        if ($LocatedExifTool) {
            $env:FUPROFILE_EXIFTOOL = $LocatedExifTool.Source
        } else {
            throw "未找到 exiftool.exe。请按照 WINDOWS_BUILD_CN.md 放置文件或设置 FUPROFILE_EXIFTOOL。"
        }
    }
}

$env:PYTHONPATH = Join-Path $ProjectRoot "src"
& $VenvPython -m unittest discover -s tests -v
& $VenvPython packaging\build_app.py

$AppDirectory = Join-Path $ProjectRoot "dist\FuProfile Unlocker"
$Archive = Join-Path $ProjectRoot "dist\FuProfile Unlocker-Windows-x64-v$Version.zip"
if (-not (Test-Path (Join-Path $AppDirectory "FuProfile Unlocker.exe"))) {
    throw "构建结束但没有找到 FuProfile Unlocker.exe。"
}

Compress-Archive -Path $AppDirectory -DestinationPath $Archive -Force
Write-Host ""
Write-Host "构建完成：$AppDirectory"
Write-Host "分发包：$Archive"
