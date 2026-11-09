#!/bin/bash
# SPDX-License-Identifier: LGPL-2.1-or-later
# MINT-CAD: baut aus dem Release-Build einen Windows-Installer (NSIS) und ein 7z-Archiv (portabel).
# Aufruf unter Windows in der Git-Bash im Quellordner, nach "tools\mintcad\configure-windows.bat" und "pixi run build-release":
#   tools/mintcad/make_windows_installer.sh [Ausgabeordner]
# Voraussetzungen: Git for Windows (Git-Bash), 7-Zip im PATH, NSIS 3 mit "Large strings" und "Advanced logging"
# (siehe docs/nitcad/BUILD-windows-linux.md). Pfad zu makensis.exe notfalls mit  MAKENSIS=/c/.../makensis.exe  angeben.
# Angelehnt an package/rattler-build/windows/create_bundle.sh, verwendet aber den vorhandenen Build.
# Hinweis: Die Installation (cmake --install) geht in die Entwicklungsumgebung (.pixi/envs/default/Library).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/build/mintcad-dist-windows}"
ENVDIR="$ROOT/.pixi/envs/default"
WIN="$ROOT/tools/mintcad/windows"
VERSION="$(sed -En 's/^#define FCVersion(Major|Minor|Point) *"(.*)"/\2/p' "$ROOT/build/release/src/Build/Version.h" | tr -d '\r' | paste -sd. -)"
NAME="MINT-CAD-${VERSION}-Windows-x86_64"
APP="$OUT/$NAME"          # der fertige Programmordner
INST="$OUT/installer"     # Arbeitskopie der NSIS-Skripte

MAKENSIS="${MAKENSIS:-}"
if [ -z "$MAKENSIS" ]; then
    for c in "$ENVDIR/NSIS/makensis.exe" "/c/Program Files (x86)/NSIS/makensis.exe" "/c/Program Files/NSIS/makensis.exe"; do
        if [ -x "$c" ]; then MAKENSIS="$c"; break; fi
    done
fi
[ -n "$MAKENSIS" ] || { echo "makensis.exe nicht gefunden (siehe docs/nitcad/BUILD-windows-linux.md, Variable MAKENSIS)"; exit 1; }
command -v 7z >/dev/null || { echo "7z nicht im PATH"; exit 1; }

echo "== Vorbereiten ($VERSION)"
rm -rf "$OUT"
mkdir -p "$APP/bin"

echo "== MINT-CAD installieren"
cd "$ROOT"
pixi run cmake --install build/release >"$OUT/install.log"

echo "== Programmordner zusammenstellen"
# Python und Laufzeit
cp -a "$ENVDIR/DLLs" "$APP/bin/DLLs"
cp -a "$ENVDIR/Lib" "$APP/bin/Lib"
cp -a "$ENVDIR/Scripts" "$APP/bin/Scripts"
cp -a "$ENVDIR"/python*.* "$ENVDIR"/msvc*.* "$ENVDIR"/ucrt*.* "$APP/bin/" 2>/dev/null || true
# Hilfsprogramme (CalculiX, Gmsh, Graphviz)
for t in ccx gmsh dot unflatten; do
    [ -e "$ENVDIR/Library/bin/$t.exe" ] && cp -a "$ENVDIR/Library/bin/$t.exe" "$APP/bin/"
done
[ -d "$ENVDIR/Library/mingw-w64/bin" ] && cp -a "$ENVDIR/Library/mingw-w64/bin/." "$APP/bin/"
cp -a "$ENVDIR/Library/share" "$APP/share"
cp -a "$ENVDIR"/Library/bin/*.dll "$APP/bin/"
cp -a "$ENVDIR"/Library/bin/[Ff]ree[Cc][Aa][Dd]*.exe "$APP/bin/"
cp -a "$ENVDIR/Library/data" "$APP/data"
cp -a "$ENVDIR/Library/Ext" "$APP/Ext"
cp -a "$ENVDIR/Library/lib" "$APP/lib"
cp -a "$ENVDIR/Library/Mod" "$APP/Mod"
mkdir -p "$APP/doc"
cp -a "$ENVDIR"/Library/doc/{ThirdPartyLibraries.html,LICENSE.html} "$APP/doc/" 2>/dev/null || true
cp "$ROOT/LICENSE" "$APP/doc/LICENSE.txt"

echo "== Unnötiges entfernen"
find "$APP" \( -name '*.a' -o -name '*.lib' -o -name '*arm*.exe' -o -name '__pycache__' -prune \) -exec rm -rf {} + 2>/dev/null || true
rm -rf "$APP/bin/Lib/test" "$APP/bin/Lib/idlelib" "$APP/bin/Lib/tkinter" "$APP/bin/Lib/turtledemo"

echo "== Patches wie bei FreeCAD (SSL-Modul, Qt-Pfad)"
cp "$ROOT/package/rattler-build/windows/ssl-patch.py" "$APP/bin/Lib/ssl.py"
printf '[Paths]\nPrefix = ../lib/qt6\n' > "$APP/bin/qt6.conf"

echo "== Programmdateien umbenennen (MINT-CAD.exe, MINT-CADcmd.exe)"
mv "$APP/bin/freecad.exe" "$APP/bin/MINT-CAD.exe"
mv "$APP/bin/freecadcmd.exe" "$APP/bin/MINT-CADcmd.exe"
cp "$WIN/mintcad.ico" "$APP/mintcad.ico"

echo "== Rauchtest"
"$APP/bin/MINT-CADcmd.exe" --safe-mode -c "import FreeCAD, Part, Sketcher, PartDesign, TechDraw, Draft, Fem, Assembly, Mesh, Spreadsheet; print('Module OK', FreeCAD.getHomePath())"

echo "== Portables Archiv"
cd "$OUT"
7z a -t7z -mx9 -mmt="${NUMBER_OF_PROCESSORS:-4}" "$NAME.7z" "$NAME" -bso0 -bsp0
sha256sum "$NAME.7z" > "$NAME.7z.sha256"

echo "== Installer (NSIS)"
cp -a "$ROOT/package/WindowsInstaller" "$INST"
cp "$WIN/mintcad.ico" "$INST/icons/mintcad.ico"
cp "$WIN/header.bmp" "$WIN/banner.bmp" "$INST/graphics/"
# Versionsdatei mit MINT-CAD-Namen statt Abfrage von freecadcmd
cat > "$INST/write_version_nsh.py" <<PY
import datetime, os
v = "$VERSION".split(".")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.nsh"), "w", encoding="utf-8").write(
    '!define COPYRIGHT_YEAR %d\n!define APP_VERSION_MAJOR "%s"\n!define APP_VERSION_MINOR "%s"\n'
    '!define APP_VERSION_PATCH "%s"\n!define APP_VERSION_REVISION "0"\n!define APP_NAME "MINT-CAD"\n'
    % (datetime.date.today().year, v[0], v[1], v[2]))
PY
sed -i "s|bin\\\\freecadcmd.exe|bin\\\\MINT-CADcmd.exe|" "$INST/Settings.nsh"
D="$INST/include/declarations.nsh"
sed -i \
    -e 's|^!define APP_SHORTCUT_INFO .*|!define APP_SHORTCUT_INFO "${APP_NAME} - Skizzieren, Konstruieren, Zeichnen"|' \
    -e 's|^!define APP_WEBPAGE_INFO .*|!define APP_WEBPAGE_INFO "FreeCAD Website"|' \
    -e 's|^!define APP_WIKI_INFO .*|!define APP_WIKI_INFO "FreeCAD Wiki"|' \
    -e 's|^!define APP_COPYRIGHT .*|!define APP_COPYRIGHT "${APP_NAME} basiert auf FreeCAD (LGPL 2.1 oder neuer), Copyright 2001-${COPYRIGHT_YEAR} FreeCAD Team"|' \
    -e 's|^!define SETUP_ICON .*|!define SETUP_ICON "icons\\mintcad.ico"|' \
    "$D"
# Installer erzeugen (Windows-Pfade für makensis)
WAPP="$(cygpath -w "$APP")"
cd "$INST"
"$MAKENSIS" -V3 -D"ExeFile=$NAME-installer.exe" -D"FILES_FREECAD=$WAPP" -X'SetCompressor /FINAL lzma' FreeCAD-installer.nsi
mv "$INST/$NAME-installer.exe" "$OUT/"
cd "$OUT"
sha256sum "$NAME-installer.exe" | tee "$NAME-installer.exe.sha256"
rm -rf "$INST"
du -sh "$APP" "$NAME.7z" "$NAME-installer.exe"
echo "== Fertig: $OUT/$NAME-installer.exe"
