# CueNote Python 타입 검사 스크립트
# 사용법: .\scripts\typecheck.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
Set-Location $RootDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Python 타입 검사 (Pyright)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Pyright 설치 확인
$pyrightInstalled = pip show pyright 2>$null
if (-not $pyrightInstalled) {
    Write-Host "Pyright 설치 중..." -ForegroundColor Yellow
    pip install pyright
}

# 타입 검사 실행
Write-Host "검사 중: apps/core" -ForegroundColor Gray
Write-Host ""

pyright apps/core

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  타입 검사 통과!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  타입 오류가 발견되었습니다." -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "해결 방법:" -ForegroundColor Yellow
    Write-Host "  1. Optional 타입 사용: str = None -> Optional[str] = None" -ForegroundColor Gray
    Write-Host "  2. from typing import Optional 추가" -ForegroundColor Gray
    Write-Host "  3. 타입 무시: # type: ignore[error-code]" -ForegroundColor Gray
}
