# CueNote 빌드 가이드라인

Windows exe 파일 빌드를 위한 가이드입니다.

---

## 📋 목차

1. [필수 요구사항](#필수-요구사항)
2. [빌드 전 캐시 정리](#빌드-전-캐시-정리)
3. [의존성 설치](#의존성-설치)
4. [빌드 명령어](#빌드-명령어)
5. [빌드 결과물](#빌드-결과물)
6. [문제 해결](#문제-해결)

---

## 필수 요구사항

### Node.js & pnpm
```bash
# Node.js 18+ 권장
node -v

# pnpm 설치
npm install -g pnpm
```

### Python 환경
```bash
# Python 3.10+ 권장
python --version

# Conda 환경 활성화 (선택사항)
conda activate CueNote

# PyInstaller 설치
pip install pyinstaller
```

### 필수 도구
- **Git** - 버전 관리
- **Visual Studio Build Tools** - electron-builder에 필요

---

## 빌드 전 캐시 정리

> ⚠️ **중요**: 빌드 문제 발생 시 캐시를 정리하고 다시 시도하세요.

### 방법 1: 전체 캐시 정리 (권장)
```powershell
# 프로젝트 루트에서 실행
cd C:\Users\SSAFY\Desktop\git\CueNote

# 1. pnpm 스토어 정리
pnpm store prune

# 2. node_modules 삭제
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
  node_modules, `
  apps\desktop\node_modules, `
  apps\desktop\dist, `
  packages\contracts\node_modules, `
  packages\shared\node_modules

# 3. Python 빌드 캐시 삭제
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
  apps\core\build, `
  apps\core\dist, `
  apps\core-dist

# 4. 의존성 재설치
pnpm install
```

### 방법 2: 간단한 정리
```powershell
# pnpm 캐시만 정리
pnpm store prune

# Electron 빌드 캐시만 삭제
Remove-Item -Recurse -Force apps\desktop\dist
Remove-Item -Recurse -Force apps\desktop\release
```

---

## 의존성 설치

### Node.js 패키지
```powershell
# 프로젝트 루트에서 실행
pnpm install
```

### Python 패키지
```powershell
# Conda 환경 활성화
conda activate CueNote

# 의존성 설치
cd apps\core
pip install -r requirements.txt
```

---

## 빌드 명령어

### 🚀 전체 빌드 (권장)
```powershell
# 프로젝트 루트에서 실행
pnpm build:all
# 또는
powershell -ExecutionPolicy Bypass -File scripts/build-all.ps1
```

이 명령은 다음 순서로 실행됩니다:
1. Python 백엔드 → exe로 패키징 (PyInstaller)
2. Vue 렌더러 → 정적 파일로 빌드 (Vite)
3. Electron 앱 → 설치 파일 생성 (electron-builder)

### 부분 빌드

#### Python 백엔드만 빌드
```powershell
cd apps\core
pyinstaller cuenote-core.spec --noconfirm

# 결과물을 core-dist로 복사
xcopy /E /I /Y dist\cuenote-core ..\core-dist
```

#### Electron 데스크톱만 빌드
```powershell
# 프로젝트 루트에서
pnpm build:desktop

# 또는 apps\desktop에서 직접
cd apps\desktop
pnpm build:all
```

#### 렌더러만 빌드 (Vite)
```powershell
cd apps\desktop
pnpm build:renderer
```

---

## 빌드 결과물

| 결과물 | 위치 |
|--------|------|
| Python exe | `apps/core/dist/cuenote-core/` |
| 복사된 Python exe | `apps/core-dist/` |
| 렌더러 정적 파일 | `apps/desktop/dist/` |
| **포터블 버전** | `apps/desktop/release/win-unpacked/` |
| **설치 파일 (최종)** | `apps/desktop/release/CueNote Setup x.x.x.exe` |

---

## 📦 win-unpacked (포터블 버전)

### win-unpacked란?
`win-unpacked` 폴더는 **설치 없이 바로 실행 가능한 포터블 버전**입니다.

```
apps/desktop/release/win-unpacked/
├── CueNote.exe          ← 메인 실행 파일 (바로 실행 가능!)
├── resources/           ← 앱 리소스 (core 백엔드 포함)
├── locales/             ← 언어 파일
├── ffmpeg.dll           ← 미디어 관련
├── *.dll                ← Electron/Chromium 의존성
└── ...
```

### win-unpacked 사용법

#### 바로 실행하기
```powershell
# 포터블 버전 바로 실행
.\apps\desktop\release\win-unpacked\CueNote.exe
```

#### 다른 PC로 배포하기
1. `win-unpacked` 폴더 전체를 복사
2. 압축하여 전달 (예: `CueNote-portable.zip`)
3. 받은 사람은 압축 해제 후 `CueNote.exe` 실행

> ⚠️ **주의**: 폴더 구조를 유지해야 합니다. `CueNote.exe`만 복사하면 실행 안됨!

---

## 🔧 NSIS 설치 파일 생성

### win-unpacked만 생성된 경우

`pnpm build:all` 실행 중 NSIS 패키징 단계에서 중단되었을 수 있습니다.

#### 방법 1: 설치 파일만 다시 생성
```powershell
cd apps\desktop
pnpm exec electron-builder --win --prepackaged release/win-unpacked
```

#### 방법 2: Electron 빌드 전체 다시 실행
```powershell
cd apps\desktop
pnpm exec electron-builder --win
```

#### 방법 3: 프로젝트 루트에서 실행
```powershell
cd C:\Users\SSAFY\Desktop\git\CueNote
pnpm build:desktop
```

### 빌드 완료 시 생성되는 파일들

| 파일 | 설명 | 용도 |
|------|------|------|
| `win-unpacked/` | 포터블 버전 폴더 | 설치 없이 테스트/배포 |
| `CueNote Setup x.x.x.exe` | NSIS 설치 프로그램 | 일반 사용자 배포용 |
| `builder-debug.yml` | 빌드 디버그 정보 | 문제 해결용 |
| `builder-effective-config.yaml` | 적용된 빌드 설정 | 설정 확인용 |

### 설치 파일 형식
- `CueNote Setup x.x.x.exe` - NSIS 설치 프로그램 (권장)
- 설치 시 바탕화면/시작메뉴 바로가기 생성
- 설치 경로 변경 가능

### win-unpacked vs 설치 파일 비교

| 항목 | win-unpacked (포터블) | Setup.exe (설치 파일) |
|------|----------------------|----------------------|
| 설치 필요 | ❌ 없음 | ✅ 필요 |
| 레지스트리 등록 | ❌ 없음 | ✅ 등록됨 |
| 바로가기 생성 | ❌ 수동 | ✅ 자동 |
| 제어판 표시 | ❌ 없음 | ✅ 표시됨 |
| 업데이트 | 수동 교체 | 자동 업데이트 가능 |
| 용도 | 개발/테스트/임시 배포 | 정식 배포 |

---

## 문제 해결

### ❌ `ENOENT` 또는 모듈을 찾을 수 없음
```powershell
# 캐시 정리 후 재설치
pnpm store prune
Remove-Item -Recurse -Force node_modules
pnpm install
```

### ❌ PyInstaller 빌드 실패
```powershell
# PyInstaller 재설치
pip uninstall pyinstaller -y
pip install pyinstaller

# 캐시 정리
Remove-Item -Recurse -Force apps\core\build, apps\core\dist
```

### ❌ electron-builder 오류
```powershell
# Electron 캐시 삭제
Remove-Item -Recurse -Force $env:LOCALAPPDATA\electron
Remove-Item -Recurse -Force $env:LOCALAPPDATA\electron-builder

# 재빌드
pnpm build:desktop
```

### ❌ `extraResources` 경로 오류
Python 백엔드가 먼저 빌드되어 `apps/core-dist/`에 있어야 합니다.
```powershell
# 순서대로 실행
pnpm build:core
pnpm build:desktop
```

### ❌ 빌드는 되지만 앱 실행 안됨
1. `apps/desktop/release/` 폴더에서 설치 파일 실행
2. 설치 후 로그 확인: `%APPDATA%\CueNote\logs\`
3. 개발 모드로 디버깅:
```powershell
cd apps\desktop
pnpm dev
```

---

## 🔧 빌드 설정 파일

| 파일 | 용도 |
|------|------|
| `apps/core/cuenote-core.spec` | PyInstaller 설정 |
| `apps/desktop/package.json` → `build` | electron-builder 설정 |
| `apps/desktop/vite.config.ts` | Vite 빌드 설정 |
| `scripts/build-all.ps1` | 전체 빌드 스크립트 |

---

## 📝 빌드 체크리스트

빌드 전 확인사항:

- [ ] Node.js 18+ 설치됨
- [ ] pnpm 설치됨
- [ ] Python 3.10+ 설치됨
- [ ] PyInstaller 설치됨
- [ ] `pnpm install` 완료
- [ ] Python 의존성 설치 완료
- [ ] 이전 빌드 캐시 정리 (필요시)

빌드 후 확인사항:

- [ ] `apps/desktop/release/` 에 설치 파일 생성됨
- [ ] 설치 파일 용량 확인 (정상: 100MB~300MB)
- [ ] 설치 테스트 완료
- [ ] 앱 실행 테스트 완료

---

## 버전 관리

빌드 전 버전 업데이트:

```powershell
# 루트 package.json
# apps/desktop/package.json
# 두 파일의 version 필드를 동일하게 수정
```

버전 형식: `MAJOR.MINOR.PATCH` (예: `0.1.0`, `1.0.0`)
