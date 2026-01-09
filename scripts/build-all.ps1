# CueNote 전체 빌드 스크립트 (Windows PowerShell)
# 사용법: .\scripts\build-all.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CueNote Build Script for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 프로젝트 루트로 이동
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
Set-Location $RootDir

Write-Host "[1/4] Python 백엔드 빌드 준비..." -ForegroundColor Yellow

# PyInstaller 설치 확인
$pyinstallerInstalled = pip show pyinstaller 2>$null
if (-not $pyinstallerInstalled) {
    Write-Host "  PyInstaller 설치 중..." -ForegroundColor Gray
    pip install pyinstaller
}

Write-Host "[2/4] Python 백엔드 빌드 중..." -ForegroundColor Yellow
Set-Location "$RootDir\apps\core"

# PyInstaller로 빌드
pyinstaller cuenote-core.spec --noconfirm

# 빌드 결과를 desktop/core-dist로 복사
$CoreDistDir = "$RootDir\apps\core-dist"
if (Test-Path $CoreDistDir) {
    Remove-Item -Recurse -Force $CoreDistDir
}
Copy-Item -Recurse "dist\cuenote-core" $CoreDistDir

Write-Host "  Python 백엔드 빌드 완료!" -ForegroundColor Green

Write-Host "[3/4] Electron 렌더러 빌드 중..." -ForegroundColor Yellow
Set-Location "$RootDir\apps\desktop"

# preload.js를 dist 폴더에도 복사하도록 vite 빌드 후 처리
pnpm build:renderer

# preload.js 복사
Copy-Item "renderer\preload.js" "dist\preload.js" -Force

Write-Host "  렌더러 빌드 완료!" -ForegroundColor Green

Write-Host "[4/4] Electron 앱 패키징 중..." -ForegroundColor Yellow

# electron-builder로 Windows 설치 파일 생성
pnpm exec electron-builder --win

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  빌드 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "설치 파일 위치: apps\desktop\release\" -ForegroundColor Cyan
Write-Host ""

# 결과 폴더 열기
explorer.exe "$RootDir\apps\desktop\release"
