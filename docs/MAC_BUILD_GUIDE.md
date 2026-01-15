# CueNote macOS 빌드 가이드라인

macOS용 .dmg 및 .app 설치 파일 빌드를 위한 가이드입니다.

---

## 📋 목차

1. [필수 요구사항](#필수-요구사항)
2. [프로젝트 설정](#프로젝트-설정)
3. [빌드 전 캐시 정리](#빌드-전-캐시-정리)
4. [의존성 설치](#의존성-설치)
5. [빌드 명령어](#빌드-명령어)
6. [빌드 결과물](#빌드-결과물)
7. [코드 서명 및 공증](#코드-서명-및-공증)
8. [문제 해결](#문제-해결)

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
python3 --version

# Conda 환경 활성화 (선택사항)
conda activate CueNote

# PyInstaller 설치
pip install pyinstaller
```

### Xcode Command Line Tools

```bash
# Xcode CLI 도구 설치 (필수)
xcode-select --install

# 설치 확인
xcode-select -p
# 출력: /Library/Developer/CommandLineTools
```

### 필수 도구

- **Git** - 버전 관리
- **Homebrew** - macOS 패키지 관리자 (권장)

---

## 프로젝트 설정

### package.json Mac 빌드 설정 추가

`apps/desktop/package.json`의 `build` 섹션에 다음을 추가해야 합니다:

```json
{
  "build": {
    "mac": {
      "icon": "../../assets/icon.png",
      "category": "public.app-category.productivity",
      "target": [
        {
          "target": "dmg",
          "arch": ["x64", "arm64"]
        },
        {
          "target": "zip",
          "arch": ["x64", "arm64"]
        }
      ],
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "entitlements.mac.plist",
      "entitlementsInherit": "entitlements.mac.plist"
    },
    "dmg": {
      "contents": [
        {
          "x": 130,
          "y": 220
        },
        {
          "x": 410,
          "y": 220,
          "type": "link",
          "path": "/Applications"
        }
      ],
      "window": {
        "width": 540,
        "height": 380
      }
    }
  }
}
```

### package.json 스크립트 추가

`apps/desktop/package.json`의 `scripts` 섹션에 추가:

```json
{
  "scripts": {
    "build:mac": "pnpm build:renderer && electron-builder --mac",
    "build:mac:dmg": "pnpm build:renderer && electron-builder --mac dmg",
    "build:mac:universal": "pnpm build:renderer && electron-builder --mac --universal"
  }
}
```

### Entitlements 파일 생성

`apps/desktop/entitlements.mac.plist` 파일을 생성합니다:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
```

---

## 빌드 전 캐시 정리

> ⚠️ **중요**: 빌드 문제 발생 시 캐시를 정리하고 다시 시도하세요.

### 방법 1: 전체 캐시 정리 (권장)

```bash
# 프로젝트 루트에서 실행
cd ~/Desktop/github_bunhine0452/CueNote

# 1. pnpm 스토어 정리
pnpm store prune

# 2. node_modules 삭제
rm -rf node_modules \
  apps/desktop/node_modules \
  apps/desktop/dist \
  packages/contracts/node_modules \
  packages/shared/node_modules

# 3. Python 빌드 캐시 삭제
rm -rf apps/core/build \
  apps/core/dist \
  apps/core-dist

# 4. 의존성 재설치
pnpm install
```

### 방법 2: 간단한 정리

```bash
# pnpm 캐시만 정리
pnpm store prune

# Electron 빌드 캐시만 삭제
rm -rf apps/desktop/dist
rm -rf apps/desktop/release
```

---

## 의존성 설치

### Node.js 패키지

```bash
# 프로젝트 루트에서 실행
pnpm install
```

### Python 패키지

```bash
# Conda 환경 활성화 (선택사항)
conda activate CueNote

# 의존성 설치
cd apps/core
pip install -r requirements.txt
```

---

## 빌드 명령어

### 🚀 전체 빌드 (권장)

```bash
# 프로젝트 루트에서 실행
./scripts/build-mac.sh
```

이 명령은 다음 순서로 실행됩니다:

1. Python 백엔드 → macOS 바이너리로 패키징 (PyInstaller)
2. Vue 렌더러 → 정적 파일로 빌드 (Vite)
3. Electron 앱 → .dmg 설치 파일 생성 (electron-builder)

### 부분 빌드

#### Python 백엔드만 빌드

```bash
cd apps/core

# macOS용 PyInstaller 빌드
pyinstaller cuenote-core.spec --noconfirm

# 결과물을 core-dist로 복사
cp -r dist/cuenote-core ../core-dist
```

#### Electron 데스크톱만 빌드 (Mac)

```bash
# 프로젝트 루트에서
pnpm build:mac

# 또는 apps/desktop에서 직접
cd apps/desktop
pnpm build:mac
```

#### 특정 아키텍처만 빌드

```bash
# Intel Mac (x64)만
cd apps/desktop
pnpm exec electron-builder --mac --x64

# Apple Silicon (arm64)만
pnpm exec electron-builder --mac --arm64

# Universal 바이너리 (둘 다 포함)
pnpm exec electron-builder --mac --universal
```

#### 렌더러만 빌드 (Vite)

```bash
cd apps/desktop
pnpm build:renderer
```

---

## 빌드 결과물

| 결과물                   | 위치                                          |
| ------------------------ | --------------------------------------------- |
| Python 바이너리          | `apps/core/dist/cuenote-core/`                |
| 복사된 Python 바이너리   | `apps/core-dist/`                             |
| 렌더러 정적 파일         | `apps/desktop/dist/`                          |
| **Mac 앱 번들**          | `apps/desktop/release/mac/` 또는 `mac-arm64/` |
| **DMG 설치 파일 (최종)** | `apps/desktop/release/CueNote-x.x.x.dmg`      |
| **ZIP 파일**             | `apps/desktop/release/CueNote-x.x.x-mac.zip`  |

---

## 📦 Mac 앱 번들 구조

### .app 번들이란?

macOS에서 앱은 `.app` 확장자를 가진 **번들(Bundle)** 형태로 배포됩니다.

```
CueNote.app/
├── Contents/
│   ├── Info.plist          ← 앱 메타데이터
│   ├── MacOS/
│   │   └── CueNote         ← 메인 실행 파일
│   ├── Resources/
│   │   ├── app.asar        ← Electron 앱 리소스
│   │   ├── core/           ← Python 백엔드
│   │   ├── icon.icns       ← 앱 아이콘
│   │   └── ...
│   └── Frameworks/         ← Electron/Chromium 프레임워크
└── ...
```

### 빌드 결과물 비교

| 파일 형식 | 설명             | 용도                                            |
| --------- | ---------------- | ----------------------------------------------- |
| `.app`    | Mac 앱 번들      | 직접 실행 (드래그하여 Applications 폴더에 복사) |
| `.dmg`    | 디스크 이미지    | 설치 안내 UI 포함, 일반 배포용                  |
| `.zip`    | 압축 파일        | 자동 업데이트, Sparkle 호환                     |
| `.pkg`    | 패키지 설치 파일 | 기업 배포, MDM 배포용                           |

---

## 🔐 코드 서명 및 공증

> ⚠️ **중요**: macOS Catalina(10.15) 이상에서는 공증(Notarization)이 필수입니다.
> 서명/공증 없이 배포하면 "확인되지 않은 개발자" 경고가 표시됩니다.

### Apple Developer 계정 필요

코드 서명 및 공증을 위해서는:

1. **Apple Developer Program** 가입 필요 (연간 $99)
2. **Developer ID Application** 인증서 발급
3. **App-specific password** 생성 (공증용)

### 환경 변수 설정

코드 서명을 위한 환경 변수:

```bash
# ~/.zshrc 또는 ~/.bash_profile에 추가
export CSC_LINK="path/to/certificate.p12"
export CSC_KEY_PASSWORD="인증서 비밀번호"

# 공증을 위한 Apple ID 정보
export APPLE_ID="your-apple-id@example.com"
export APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
export APPLE_TEAM_ID="XXXXXXXXXX"
```

### package.json 공증 설정 추가

```json
{
  "build": {
    "afterSign": "scripts/notarize.js",
    "mac": {
      "hardenedRuntime": true,
      "gatekeeperAssess": false
    }
  }
}
```

### 공증 스크립트 생성

`scripts/notarize.js` 파일 생성:

```javascript
const { notarize } = require("@electron/notarize");

exports.default = async function notarizing(context) {
  const { electronPlatformName, appOutDir } = context;

  if (electronPlatformName !== "darwin") {
    return;
  }

  const appName = context.packager.appInfo.productFilename;

  return await notarize({
    appBundleId: "com.cuenote.app",
    appPath: `${appOutDir}/${appName}.app`,
    appleId: process.env.APPLE_ID,
    appleIdPassword: process.env.APPLE_APP_SPECIFIC_PASSWORD,
    teamId: process.env.APPLE_TEAM_ID,
  });
};
```

### 공증 없이 로컬 테스트

개발 및 테스트 목적으로 공증 없이 실행하려면:

```bash
# Gatekeeper 우회 (본인 Mac에서만)
sudo spctl --master-disable

# 또는 특정 앱만 허용
xattr -cr /Applications/CueNote.app
```

---

## 빌드 스크립트

### Mac 빌드 스크립트 생성

`scripts/build-mac.sh` 파일을 생성합니다:

```bash
#!/bin/bash
# CueNote 전체 빌드 스크립트 (macOS)
# 사용법: ./scripts/build-mac.sh

set -e

echo "========================================"
echo "  CueNote Build Script for macOS"
echo "========================================"
echo ""

# 프로젝트 루트로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "[1/4] Python 백엔드 빌드 준비..."

# PyInstaller 설치 확인
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "  PyInstaller 설치 중..."
    pip install pyinstaller
fi

echo "[2/4] Python 백엔드 빌드 중..."
cd "$ROOT_DIR/apps/core"

# PyInstaller로 빌드
pyinstaller cuenote-core.spec --noconfirm

# 빌드 결과를 core-dist로 복사
CORE_DIST_DIR="$ROOT_DIR/apps/core-dist"
if [ -d "$CORE_DIST_DIR" ]; then
    rm -rf "$CORE_DIST_DIR"
fi
cp -r dist/cuenote-core "$CORE_DIST_DIR"

echo "  Python 백엔드 빌드 완료!"

echo "[3/4] Electron 렌더러 빌드 중..."
cd "$ROOT_DIR/apps/desktop"

# Vite 빌드
pnpm build:renderer

# preload.js 복사
cp renderer/preload.js dist/preload.js

echo "  렌더러 빌드 완료!"

echo "[4/4] Electron 앱 패키징 중..."

# electron-builder로 macOS 설치 파일 생성
pnpm exec electron-builder --mac

echo ""
echo "========================================"
echo "  빌드 완료!"
echo "========================================"
echo ""
echo "설치 파일 위치: apps/desktop/release/"
echo ""

# 결과 폴더 열기
open "$ROOT_DIR/apps/desktop/release"
```

실행 권한 부여:

```bash
chmod +x scripts/build-mac.sh
```

---

## 문제 해결

### ❌ `ENOENT` 또는 모듈을 찾을 수 없음

```bash
# 캐시 정리 후 재설치
pnpm store prune
rm -rf node_modules
pnpm install
```

### ❌ PyInstaller 빌드 실패

```bash
# PyInstaller 재설치
pip uninstall pyinstaller -y
pip install pyinstaller

# 캐시 정리
rm -rf apps/core/build apps/core/dist
```

### ❌ electron-builder 오류

```bash
# Electron 캐시 삭제
rm -rf ~/Library/Caches/electron
rm -rf ~/Library/Caches/electron-builder

# 재빌드
pnpm build:mac
```

### ❌ `extraResources` 경로 오류

Python 백엔드가 먼저 빌드되어 `apps/core-dist/`에 있어야 합니다.

```bash
# 순서대로 실행
pnpm build:core
pnpm build:mac
```

### ❌ 코드 서명 오류

```bash
# 인증서 확인
security find-identity -v -p codesigning

# 환경 변수 확인
echo $CSC_LINK
echo $CSC_KEY_PASSWORD
```

### ❌ "확인되지 않은 개발자" 경고

```bash
# Gatekeeper 속성 제거 (테스트용)
xattr -cr /Applications/CueNote.app

# 또는 시스템 환경설정 > 보안 및 개인정보에서 "확인 없이 열기" 클릭
```

### ❌ Apple Silicon에서 Intel 빌드 실행 안됨

```bash
# Rosetta 2 설치 필요
softwareupdate --install-rosetta --agree-to-license
```

### ❌ DMG 생성 실패

```bash
# hdiutil 권한 확인
sudo diskutil list

# 임시 폴더 정리
rm -rf /tmp/dmg-*
```

---

## 🔧 빌드 설정 파일

| 파일                                  | 용도                  |
| ------------------------------------- | --------------------- |
| `apps/core/cuenote-core.spec`         | PyInstaller 설정      |
| `apps/desktop/package.json` → `build` | electron-builder 설정 |
| `apps/desktop/vite.config.ts`         | Vite 빌드 설정        |
| `apps/desktop/entitlements.mac.plist` | macOS 권한 설정       |
| `scripts/build-mac.sh`                | macOS 빌드 스크립트   |
| `scripts/notarize.js`                 | Apple 공증 스크립트   |

---

## 📝 빌드 체크리스트

빌드 전 확인사항:

- [ ] Node.js 18+ 설치됨
- [ ] pnpm 설치됨
- [ ] Python 3.10+ 설치됨
- [ ] PyInstaller 설치됨
- [ ] Xcode Command Line Tools 설치됨
- [ ] `pnpm install` 완료
- [ ] Python 의존성 설치 완료
- [ ] 이전 빌드 캐시 정리 (필요시)
- [ ] `package.json`에 Mac 빌드 설정 추가됨

빌드 후 확인사항:

- [ ] `apps/desktop/release/` 에 .dmg 파일 생성됨
- [ ] DMG 파일 용량 확인 (정상: 100MB~300MB)
- [ ] DMG 마운트 후 앱 설치 테스트
- [ ] 앱 실행 테스트 완료

배포 전 확인사항 (선택):

- [ ] 코드 서명 완료
- [ ] Apple 공증 완료
- [ ] 다른 Mac에서 설치/실행 테스트

---

## 아키텍처 가이드

### Intel vs Apple Silicon

| 아키텍처  | 대상 Mac                 | 빌드 옵션     |
| --------- | ------------------------ | ------------- |
| x64       | Intel Mac (2020년 이전)  | `--x64`       |
| arm64     | Apple Silicon (M1/M2/M3) | `--arm64`     |
| universal | 모든 Mac                 | `--universal` |

### Universal 빌드 권장

Universal 빌드는 두 아키텍처를 모두 포함하여 모든 Mac에서 실행 가능합니다:

```bash
pnpm exec electron-builder --mac --universal
```

> ⚠️ Universal 빌드는 파일 크기가 약 2배가 됩니다.

---

## 버전 관리

빌드 전 버전 업데이트:

```bash
# 루트 package.json
# apps/desktop/package.json
# 두 파일의 version 필드를 동일하게 수정
```

버전 형식: `MAJOR.MINOR.PATCH` (예: `0.1.0`, `1.0.0`)
