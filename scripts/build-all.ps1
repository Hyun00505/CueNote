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

Write-Host "[0/5] Python 타입 검사 중..." -ForegroundColor Yellow

# Pyright 설치 확인 및 타입 검사 실행
$pyrightInstalled = pip show pyright 2>$null
if (-not $pyrightInstalled) {
    Write-Host "  Pyright 설치 중..." -ForegroundColor Gray
    pip install pyright
}

# 타입 검사 실행
Write-Host "  타입 오류 검사 중..." -ForegroundColor Gray
$typeCheckResult = pyright apps/core 2>&1
$typeCheckExitCode = $LASTEXITCODE

if ($typeCheckExitCode -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  타입 오류가 발견되었습니다!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host $typeCheckResult -ForegroundColor Yellow
    Write-Host ""
    Write-Host "타입 오류를 수정한 후 다시 빌드해주세요." -ForegroundColor Red
    Write-Host "빌드를 계속하려면 Enter를 누르세요 (권장하지 않음)" -ForegroundColor Yellow
    Read-Host
}
else {
    Write-Host "  타입 검사 통과!" -ForegroundColor Green
}

Write-Host "[1/5] Python 백엔드 빌드 준비..." -ForegroundColor Yellow

# PyInstaller 설치 확인
$pyinstallerInstalled = pip show pyinstaller 2>$null
if (-not $pyinstallerInstalled) {
    Write-Host "  PyInstaller 설치 중..." -ForegroundColor Gray
    pip install pyinstaller
}

Write-Host "[2/5] Python 백엔드 빌드 중..." -ForegroundColor Yellow
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

Write-Host "[3/5] Electron 렌더러 빌드 중..." -ForegroundColor Yellow
Set-Location "$RootDir\apps\desktop"

# preload.js를 dist 폴더에도 복사하도록 vite 빌드 후 처리
pnpm build:renderer

# preload.js 복사
Copy-Item "renderer\preload.js" "dist\preload.js" -Force

Write-Host "  렌더러 빌드 완료!" -ForegroundColor Green

Write-Host "[4/5] Electron 앱 패키징 중..." -ForegroundColor Yellow

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
