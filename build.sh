#!/usr/bin/env bash
# Build a self-contained BreathworkTimer-x86_64.AppImage on Linux x86_64.
# Embeds python-build-standalone (with Tkinter) inside the AppDir, then wraps
# with appimagetool. Run from the project root.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$ROOT/build"
APPDIR="$BUILD/BreathworkTimer.AppDir"
PY_VERSION="3.12.13"
PY_RELEASE="20260414"
PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PY_RELEASE}/cpython-${PY_VERSION}%2B${PY_RELEASE}-x86_64-unknown-linux-gnu-install_only.tar.gz"
APPIMAGETOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"

mkdir -p "$BUILD"
cd "$BUILD"

if [ ! -d python ]; then
  echo ">> downloading portable python..."
  curl -L -o python-portable.tar.gz "$PY_URL"
  tar xzf python-portable.tar.gz
fi

if [ ! -x appimagetool ]; then
  echo ">> downloading appimagetool..."
  curl -L -o appimagetool "$APPIMAGETOOL_URL"
  chmod +x appimagetool
fi

if [ ! -d squashfs-root ]; then
  echo ">> extracting appimagetool (avoids FUSE requirement)..."
  ./appimagetool --appimage-extract >/dev/null
fi

echo ">> generating icon..."
./python/bin/python3 "$ROOT/make_icon.py" icon.png morning

echo ">> assembling AppDir..."
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/lib" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp "$ROOT/main.py" "$APPDIR/usr/bin/main.py"
cp -r python "$APPDIR/usr/lib/python"

# Trim non-essential files from the embedded python tree.
rm -rf "$APPDIR/usr/lib/python/include" \
       "$APPDIR/usr/lib/python/share/man" \
       "$APPDIR/usr/lib/python/share/doc" \
       "$APPDIR/usr/lib/python/lib/pkgconfig" \
       "$APPDIR/usr/lib/python/lib/python3.12/test" \
       "$APPDIR/usr/lib/python/lib/python3.12/idlelib" \
       "$APPDIR/usr/lib/python/lib/python3.12/tkinter/test" \
       "$APPDIR/usr/lib/python/lib/python3.12/lib2to3" \
       "$APPDIR/usr/lib/python/lib/python3.12/ensurepip"
find "$APPDIR/usr/lib/python" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
find "$APPDIR/usr/lib/python" -name "*.pyc" -delete 2>/dev/null || true

cp icon.png "$APPDIR/breathwork-timer.png"
cp icon.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/breathwork-timer.png"

cat > "$APPDIR/breathwork-timer.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=Breathwork Timer
Comment=Guided breathwork — Morning Rise (Wim Hof) and Deep Calm (4-7-8)
Exec=AppRun
Icon=breathwork-timer
Categories=Utility;
Terminal=false
StartupNotify=true
DESKTOP
cp "$APPDIR/breathwork-timer.desktop" "$APPDIR/usr/share/applications/breathwork-timer.desktop"

cat > "$APPDIR/AppRun" <<'APPRUN'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export TCL_LIBRARY="$HERE/usr/lib/python/lib/tcl9.0"
export TK_LIBRARY="$HERE/usr/lib/python/lib/tk9.0"
exec "$HERE/usr/lib/python/bin/python3" "$HERE/usr/bin/main.py" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

echo ">> packaging AppImage..."
cd "$BUILD"
ARCH=x86_64 ./squashfs-root/AppRun "$APPDIR" "$ROOT/BreathworkTimer-x86_64.AppImage"
chmod +x "$ROOT/BreathworkTimer-x86_64.AppImage"

echo ""
echo "Built: $ROOT/BreathworkTimer-x86_64.AppImage"
ls -lh "$ROOT/BreathworkTimer-x86_64.AppImage"
