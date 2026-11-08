#!/bin/bash
# SPDX-License-Identifier: LGPL-2.1-or-later
# MINT-CAD: baut aus dem Release-Build ein eigenständiges MINT-CAD.app und ein DMG (macOS, arm64).
# Aufruf aus dem Quellordner, nach "pixi run build-release":  tools/mintcad/make_macos_bundle.sh [Ausgabeordner]
# Angelehnt an package/rattler-build/osx/create_bundle.sh, verwendet aber den vorhandenen Build.
set -euo pipefail
# Hinweis: nicht mit '| tail' aufrufen, sonst geht der Fehlercode verloren

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/build/mintcad-dist}"
ENVDIR="$ROOT/.pixi/envs/default"
MAC="$ROOT/tools/mintcad/macos"
LAUNCHER="$ROOT/package/rattler-build/osx/launcher/FreeCAD.cpp"
TEMPLATE="$ROOT/package/rattler-build/osx/Info.plist.template"
ENTITLEMENTS="$ROOT/package/rattler-build/osx/entitlements.plist"
APP="$OUT/MINT-CAD.app"
RES="$APP/Contents/Resources"
STAGE="$OUT/stage"
VERSION="$(sed -En 's/^#define FCVersion(Major|Minor|Point) *"(.*)"/\2/p' "$ROOT/build/release/src/Build/Version.h" | paste -sd. -)"
export SDKROOT="${SDKROOT:-/Library/Developer/CommandLineTools/SDKs/MacOSX14.5.sdk}"

echo "== Vorbereiten ($VERSION)"
rm -rf "$OUT"
mkdir -p "$RES" "$APP/Contents/MacOS"

echo "== Abhängigkeiten kopieren"
cp -a "$ENVDIR"/ "$RES"/

echo "== MINT-CAD installieren (DESTDIR, damit die Entwicklungsumgebung unberührt bleibt)"
cd "$ROOT"
DESTDIR="$STAGE" pixi run cmake --install build/release >"$OUT/install.log"
cp -a "$STAGE$ENVDIR"/ "$RES"/
rm -rf "$STAGE"

echo "== Unnötiges entfernen"
cd "$RES"
rm -rf include man conda-meta var libexec/gcc share/doc share/man share/info share/gtk-doc \
       lib/clang lib/perl5 lib/cmake lib/pkgconfig lib/python3.11/test lib/libclang* lib/libLLVM*
find . -name '*.a' -delete
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
mv bin bin_tmp && mkdir bin
mv bin_tmp/FreeCAD bin/freecad
mv bin_tmp/FreeCADCmd bin/freecadcmd
for tool in ccx python python3 python3.11 pip pyside6-rcc dot unflatten gmsh; do
    if [ -e "bin_tmp/$tool" ]; then cp -a "bin_tmp/$tool" bin/; fi
done
rm -rf bin_tmp
if [ -f bin/pip ]; then sed -i '' '1s|.*|#!/usr/bin/env python|' bin/pip; fi

cp "$MAC/mintcad.icns" "$RES/mintcad.icns"
cp "$ROOT/LICENSE" "$RES/LICENSE"

echo "== Pfade der Bibliotheken bereinigen"
cd "$ROOT"
"$ENVDIR/bin/python" -I package/rattler-build/scripts/fix_macos_lib_paths.py "$RES/lib" -r >"$OUT/fixpaths.log"
# absolute RPATHs in die Entwicklungsumgebung entfernen
"$ENVDIR/bin/python" -I - "$RES" "$ROOT" <<'PY'
import os, subprocess, sys, re
res, root = sys.argv[1:3]
for base, _, names in os.walk(res):
    for n in names:
        p = os.path.join(base, n)
        if os.path.islink(p) or not (n.endswith((".dylib", ".so")) or os.sep + "bin" + os.sep in p):
            continue
        out = subprocess.run(["otool", "-l", p], capture_output=True, text=True).stdout
        for rp in re.findall(r"path (\S.*?) \(offset", out):
            if rp.startswith(root):
                subprocess.run(["install_name_tool", "-delete_rpath", rp, p], check=False)
PY

echo "== Startprogramm und Info.plist"
# SDKROOT wird hier bewusst nicht gesetzt: das normale SDK enthält die C++-Header, SDK 14.5 allein nicht
env -u SDKROOT /usr/bin/clang++ -std=c++17 -mmacosx-version-min=11.0 -o "$APP/Contents/MacOS/MINT-CAD" "$LAUNCHER"
sed -e 's/APPLICATION_MENU_NAME/MINT-CAD/' -e "s/FREECAD_VERSION/$VERSION/" \
    -e 's/<string>FreeCAD<\/string>/<string>MINT-CAD<\/string>/' \
    -e 's/freecad\.icns/mintcad.icns/' -e 's/org\.freecad\.FreeCAD/de.mint-checker.MINT-CAD/' \
    "$TEMPLATE" >"$APP/Contents/Info.plist"
cp "$ROOT/package/rattler-build/osx/resources/freecad-doc.icns" "$ROOT/package/rattler-build/osx/resources/freecad-script.icns" "$RES/"

echo "== Paket prüfen"
"$ENVDIR/bin/python" -I "$MAC/check_bundle.py" "$APP" "$ROOT" | tee "$OUT/check.log"

echo "== Ad-hoc signieren"
find "$RES" -type f \( -name '*.dylib' -o -name '*.so' -o -path '*/bin/*' \) -print0 \
    | xargs -0 -n 40 -P 8 codesign --force --sign - >/dev/null 2>&1 || true
codesign --force --sign - --entitlements "$ENTITLEMENTS" "$APP/Contents/MacOS/MINT-CAD"

echo "== Rauchtest"
env -i HOME="$OUT/smoke-home" PREFIX="$RES" PYTHONHOME="$RES" PYTHONPATH="$RES" \
    "$RES/bin/freecadcmd" -c "import FreeCAD, Part, Sketcher, PartDesign, TechDraw, Draft, Fem, Assembly, Mesh, Spreadsheet; print('Module OK', FreeCAD.getHomePath())"
rm -rf "$OUT/smoke-home"

echo "== DMG"
DMGROOT="$OUT/dmg"
mkdir -p "$DMGROOT"
cp -a "$APP" "$DMGROOT/"
ln -s /Applications "$DMGROOT/Programme"
cp "$MAC/HINWEIS.txt" "$DMGROOT/"
hdiutil create -volname "MINT-CAD" -srcfolder "$DMGROOT" -ov -format UDZO "$OUT/MINT-CAD-macOS-arm64.dmg" >/dev/null
rm -rf "$DMGROOT"
shasum -a 256 "$OUT/MINT-CAD-macOS-arm64.dmg" | tee "$OUT/MINT-CAD-macOS-arm64.dmg.sha256"
du -sh "$APP" "$OUT/MINT-CAD-macOS-arm64.dmg"
echo "== Fertig"
