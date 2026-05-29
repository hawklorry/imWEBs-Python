param(
    [string]$AppVersion = "0.1.4",
    [string]$PythonExe = "python",
    [switch]$SkipInstaller,
    [switch]$Quick,
    [switch]$DevBuild,
    [switch]$Strip,
    [switch]$Lean
)

$ErrorActionPreference = "Stop"

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' is not available in PATH."
    }
}

function Resolve-IsccPath {
    $cmd = Get-Command iscc -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $candidates = @(
        (Join-Path ${env:ProgramFiles} "Inno Setup 6\ISCC.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe")
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    return $null
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopAppDir = Split-Path -Parent $ScriptDir
$RepoRoot = Split-Path -Parent $DesktopAppDir
$OutputDir = Join-Path $DesktopAppDir "dist"
$BuildDir = Join-Path $DesktopAppDir "build"
$OneFolderDir = Join-Path $OutputDir "imWEBs-Desktop"
$InstallerDir = Join-Path $OutputDir "installer"

Write-Host "==> Building imWEBs Desktop standalone package" -ForegroundColor Cyan
Write-Host "Desktop app dir: $DesktopAppDir"
if ($Quick) {
    Write-Host "Quick mode: Skipping cache clear and PyInstaller reinstall (faster rebuild)" -ForegroundColor Yellow
}
if ($DevBuild) {
    Write-Host "DevBuild mode: Using faster (no-compress) installer" -ForegroundColor Yellow
}
if ($Strip) {
    Write-Host "Strip mode: Removing debug symbols (smaller bundle)" -ForegroundColor Yellow
}
if ($Lean) {
    Write-Host "Lean mode: Excluding optional heavy modules for faster builds" -ForegroundColor Yellow
}

Require-Command $PythonExe

Push-Location $DesktopAppDir
try {
    if (-not $Quick) {
        $pyInstallerCheck = & $PythonExe -m pip show pyinstaller 2>$null
        if (-not $pyInstallerCheck) {
            Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
            & $PythonExe -m pip install pyinstaller
        }
    }

    if (-not $Quick -and (Test-Path $BuildDir)) {
        Remove-Item $BuildDir -Recurse -Force
    }

    $IconPath = Join-Path $DesktopAppDir "imwebs_desktop\resources\app_icon.ico"
    $LogoPngPath = Join-Path $DesktopAppDir "imwebs_desktop\resources\IMWEBsLogo.png"

    if (Test-Path $LogoPngPath) {
        try {
            & $PythonExe -c "from PIL import Image; src=r'$LogoPngPath'; dst=r'$IconPath'; img=Image.open(src).convert('RGBA'); img.save(dst, format='ICO', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
        }
        catch {
            Write-Warning "Could not regenerate app icon from PNG. Using existing ICO if available."
        }
    }

    if (-not (Test-Path $IconPath)) {
        throw "App icon not found: $IconPath"
    }

    $PyInstallerDataArgs = @(
        "--add-data",
        "$IconPath;imwebs_desktop/resources"
    )

    $PyInstallerArgs = @(
        "--noconfirm",
        "--windowed",
        "--name", "imWEBs-Desktop",
        "--collect-all", "imWEBs",
        "--collect-all", "pyogrio",
        "--collect-submodules", "PySide6.QtCore",
        "--collect-submodules", "PySide6.QtGui",
        "--collect-submodules", "PySide6.QtWidgets",
        "--collect-submodules", "imwebs_desktop",
        "--collect-submodules", "imWEBs",
        "--exclude-module", "pandas.tests",
        "--exclude-module", "numpy.tests",
        "--exclude-module", "PySide6.examples",
        "--icon", $IconPath,
        "--paths", $DesktopAppDir,
        "--paths", $RepoRoot
    )

    if ($Lean) {
        $LeanExcludes = @(
            "PySide6.Qt3DAnimation",
            "PySide6.Qt3DCore",
            "PySide6.Qt3DExtras",
            "PySide6.Qt3DInput",
            "PySide6.Qt3DLogic",
            "PySide6.Qt3DRender",
            "PySide6.QtCharts",
            "PySide6.QtDataVisualization",
            "PySide6.QtGraphs",
            "PySide6.QtGraphsWidgets",
            "PySide6.QtHelp",
            "PySide6.QtHttpServer",
            "PySide6.QtLocation",
            "PySide6.QtMultimedia",
            "PySide6.QtMultimediaWidgets",
            "PySide6.QtNetworkAuth",
            "PySide6.QtNfc",
            "PySide6.QtPdf",
            "PySide6.QtPdfWidgets",
            "PySide6.QtPositioning",
            "PySide6.QtQuick",
            "PySide6.QtQuick3D",
            "PySide6.QtQuickControls2",
            "PySide6.QtQuickTest",
            "PySide6.QtQuickWidgets",
            "PySide6.QtRemoteObjects",
            "PySide6.QtScxml",
            "PySide6.QtSensors",
            "PySide6.QtSerialBus",
            "PySide6.QtSerialPort",
            "PySide6.QtSpatialAudio",
            "PySide6.QtSql",
            "PySide6.QtStateMachine",
            "PySide6.QtSvg",
            "PySide6.QtSvgWidgets",
            "PySide6.QtTest",
            "PySide6.QtTextToSpeech",
            "PySide6.QtUiTools",
            "PySide6.QtWebChannel",
            "PySide6.QtWebEngineCore",
            "PySide6.QtWebEngineQuick",
            "PySide6.QtWebEngineWidgets",
            "PySide6.QtWebSockets",
            "PySide6.QtWebView",
            "PySide6.QtXml",
            "IPython",
            "jedi",
            "nbformat",
            "jsonschema",
            "zmq",
            "tkinter"
        )

        foreach ($moduleName in $LeanExcludes) {
            $PyInstallerArgs += "--exclude-module"
            $PyInstallerArgs += $moduleName
        }
    }

    if (-not $Quick) {
        $PyInstallerArgs += "--clean"
    }

    if ($Strip) {
        $PyInstallerArgs += "--strip"
    }

    & $PythonExe -m PyInstaller $PyInstallerArgs $PyInstallerDataArgs `
        (Join-Path $DesktopAppDir "imwebs_desktop\__main__.py")

    if (-not (Test-Path $OneFolderDir)) {
        throw "Expected output folder not found: $OneFolderDir"
    }

    Write-Host "==> Standalone app created at: $OneFolderDir" -ForegroundColor Green

    if ($SkipInstaller) {
        Write-Host "Skipping installer generation because -SkipInstaller was set."
        return
    }

    $isccPath = Resolve-IsccPath
    if (-not $isccPath) {
        Write-Warning "Inno Setup compiler (iscc) not found. Install Inno Setup 6 or add ISCC.exe to PATH."
        Write-Host "Standalone app is still ready in: $OneFolderDir" -ForegroundColor Yellow
        return
    }

    Write-Host "==> Using Inno Setup compiler: $isccPath" -ForegroundColor Cyan

    if (-not (Test-Path $InstallerDir)) {
        New-Item -ItemType Directory -Path $InstallerDir | Out-Null
    }

    $issFile = Join-Path $ScriptDir "imwebs-desktop.iss"
    $isccArgs = @(
        "/DAppVersion=$AppVersion",
        "/DSourceDir=$OneFolderDir",
        "/DOutputDir=$InstallerDir",
        "/DInstallerIconFile=$IconPath"
    )

    if ($DevBuild) {
        $isccArgs += "/DCompressionMode=zip"
    }

    & $isccPath $isccArgs $issFile

    Write-Host "==> Installer created in: $InstallerDir" -ForegroundColor Green
}
finally {
    Pop-Location
}
