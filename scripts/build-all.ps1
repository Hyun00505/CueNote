# CueNote Full Build Script (Windows PowerShell)
# Usage: .\scripts\build-all.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CueNote Build Script for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Move to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
Set-Location $RootDir

Write-Host "[0/5] Running Python type check..." -ForegroundColor Yellow

# Check Pyright installation and run type check
$pyrightInstalled = $null
try { $pyrightInstalled = pip show pyright 2>&1 | Out-String } catch {}
if (-not $pyrightInstalled -or $pyrightInstalled -match "not found") {
    Write-Host "  Installing Pyright..." -ForegroundColor Gray
    pip install pyright
}

# Run type check
Write-Host "  Checking for type errors..." -ForegroundColor Gray
$typeCheckResult = pyright apps/core 2>&1
$typeCheckExitCode = $LASTEXITCODE

if ($typeCheckExitCode -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Type errors found!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host $typeCheckResult -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please fix type errors and rebuild." -ForegroundColor Red
    Write-Host "Press Enter to continue anyway (not recommended)" -ForegroundColor Yellow
    Read-Host
}
else {
    Write-Host "  Type check passed!" -ForegroundColor Green
}

Write-Host "[1/5] Preparing Python backend build..." -ForegroundColor Yellow

# Check PyInstaller installation
$pyinstallerInstalled = $null
try { $pyinstallerInstalled = pip show pyinstaller 2>&1 | Out-String } catch {}
if (-not $pyinstallerInstalled -or $pyinstallerInstalled -match "not found") {
    Write-Host "  Installing PyInstaller..." -ForegroundColor Gray
    pip install pyinstaller
}

Write-Host "[2/5] Building Python backend..." -ForegroundColor Yellow
Set-Location "$RootDir\apps\core"

# Build with PyInstaller
pyinstaller cuenote-core.spec --noconfirm

# Copy build output to desktop/core-dist
$CoreDistDir = "$RootDir\apps\core-dist"
if (Test-Path $CoreDistDir) {
    Remove-Item -Recurse -Force $CoreDistDir
}
Copy-Item -Recurse "dist\cuenote-core" $CoreDistDir

Write-Host "  Python backend build complete!" -ForegroundColor Green

Write-Host "[3/5] Building Electron renderer..." -ForegroundColor Yellow
Set-Location "$RootDir\apps\desktop"

# Build renderer with Vite
pnpm build:renderer

# Copy preload.js
Copy-Item "renderer\preload.js" "dist\preload.js" -Force

Write-Host "  Renderer build complete!" -ForegroundColor Green

Write-Host "[4/5] Packaging Electron app..." -ForegroundColor Yellow

# Create Windows installer with electron-builder
pnpm exec electron-builder --win

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Build complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installer location: apps\desktop\release\" -ForegroundColor Cyan
Write-Host ""

# Open output folder
explorer.exe "$RootDir\apps\desktop\release"
