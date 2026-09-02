#!/usr/bin/env bash
#
# Build Pomodoro.app for macOS.
#
#   ./packaging/build.sh            # build dist/Pomodoro.app
#   ./packaging/build.sh --dmg      # ...and wrap it in dist/Pomodoro.dmg
#
# Requires: macOS, Python 3.10+, and the project's "package" extra
# (pip install -e ".[package]"), which this script installs for you.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
cd "$ROOT"

if [[ "$(uname)" != "Darwin" ]]; then
    echo "This build script only runs on macOS." >&2
    exit 1
fi

# Prefer the project's virtualenv if it exists.
if [[ -f .venv/bin/activate ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

echo "==> Installing build dependencies"
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -e ".[package]"

echo "==> Generating app icon"
python "$HERE/make_icon.py"

echo "==> Cleaning previous build"
rm -rf build dist

echo "==> Running PyInstaller"
pyinstaller --noconfirm --clean "$HERE/Pomodoro.spec"

APP="dist/Pomodoro.app"

echo "==> Ad-hoc code signing (required on Apple Silicon)"
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP" && echo "    signature OK"

if [[ "${1:-}" == "--dmg" ]]; then
    echo "==> Building dist/Pomodoro.dmg"
    rm -f dist/Pomodoro.dmg
    STAGING="$(mktemp -d)"
    cp -R "$APP" "$STAGING/"
    ln -s /Applications "$STAGING/Applications"
    hdiutil create -volname "Pomodoro" -srcfolder "$STAGING" -ov -format UDZO dist/Pomodoro.dmg
    rm -rf "$STAGING"
fi

echo
echo "Done. Built $APP"
echo "Install it with:  cp -R \"$APP\" /Applications/"
