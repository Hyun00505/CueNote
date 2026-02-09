#!/bin/bash
# CueNote Full Build Script (macOS)
# Usage: bash scripts/build-all.sh

set -e

echo "========================================"
echo "  CueNote Build Script for macOS"
echo "========================================"
echo ""

# Move to project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# 앱 데이터 초기화 (빌드 전 깨끗한 상태로 리셋)
echo "[INIT] Resetting app data to clean state..."
DATA_DIR="$ROOT_DIR/apps/core/data"

# environments.json 초기화
echo '{"environments": [], "current_id": null}' > "$DATA_DIR/environments.json"

# 그래프 캐시 삭제
if [ -d "$DATA_DIR/.graph_cache" ]; then
    rm -rf "$DATA_DIR/.graph_cache"
    echo "  Cleared .graph_cache"
fi

# SQLite DB 삭제 (프로덕션에서는 AppData에서 새로 생성됨)
if [ -f "$DATA_DIR/cuenote.db" ]; then
    rm -f "$DATA_DIR/cuenote.db"
    echo "  Cleared cuenote.db"
fi

echo "  App data reset complete!"
echo ""

echo "[0/5] Running Python type check..."

# Check Pyright installation and run type check
if ! pip show pyright > /dev/null 2>&1; then
    echo "  Installing Pyright..."
    pip install pyright
fi

echo "  Checking for type errors..."
if ! pyright "$ROOT_DIR/apps/core" 2>&1; then
    echo ""
    echo "========================================"
    echo "  Type errors found!"
    echo "========================================"
    echo ""
    echo "Please fix type errors and rebuild."
    read -p "Press Enter to continue anyway (not recommended)..." 
fi
echo "  Type check passed!"

echo "[1/5] Preparing Python backend build..."

# Check PyInstaller installation
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "  Installing PyInstaller..."
    pip install pyinstaller
fi

echo "[2/5] Building Python backend..."
pushd "$ROOT_DIR/apps/core" > /dev/null

# Build with PyInstaller
pyinstaller cuenote-core.spec --noconfirm

# Copy build output to desktop/core-dist
CORE_DIST_DIR="$ROOT_DIR/apps/core-dist"
if [ -d "$CORE_DIST_DIR" ]; then
    rm -rf "$CORE_DIST_DIR"
fi
cp -r dist/cuenote-core "$CORE_DIST_DIR"

popd > /dev/null
echo "  Python backend build complete!"

echo "[3/5] Building Electron renderer..."
pushd "$ROOT_DIR/apps/desktop" > /dev/null

# Build renderer with Vite
pnpm build:renderer

# Copy preload.js
cp renderer/preload.js dist/preload.js

popd > /dev/null
echo "  Renderer build complete!"

echo "[4/5] Packaging Electron app..."
pushd "$ROOT_DIR/apps/desktop" > /dev/null

# Create macOS installer with electron-builder
pnpm exec electron-builder --mac

popd > /dev/null

echo ""
echo "========================================"
echo "  Build complete!"
echo "========================================"
echo ""
echo "Installer location: apps/desktop/release/"
echo ""

# Open output folder
open "$ROOT_DIR/apps/desktop/release"
