#!/bin/bash
# SPDX-License-Identifier: LGPL-2.1-or-later
# MINT-CAD: baut aus dem Release-Build ein AppImage (Linux x86-64 oder aarch64).
# Aufruf auf einem Linux-Rechner im Quellordner, nach "tools/mintcad/configure-linux.sh" und "pixi run build-release":
#   tools/mintcad/make_linux_appimage.sh [Ausgabeordner]
# Angelehnt an package/rattler-build/linux/create_bundle.sh, verwendet aber den vorhandenen Build.
# Hinweis: nicht mit '| tail' aufrufen, sonst geht der Fehlercode verloren.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/build/mintcad-dist-linux}"
ENVDIR="$ROOT/.pixi/envs/default"
LIN="$ROOT/tools/mintcad/linux"
APPDIR="$OUT/AppDir"
USR="$APPDIR/usr"
STAGE="$OUT/stage"
ARCH="$(uname -m)"
VERSION="$(sed -En 's/^#define FCVersion(Major|Minor|Point) *"(.*)"/\2/p' "$ROOT/build/release/src/Build/Version.h" | paste -sd. -)"
NAME="MINT-CAD-${VERSION}-Linux-${ARCH}"

echo "== Vorbereiten ($VERSION, $ARCH)"
rm -rf "$OUT"
mkdir -p "$USR"

echo "== Abhängigkeiten kopieren"
cp -a "$ENVDIR"/. "$USR"/

echo "== MINT-CAD installieren (DESTDIR, damit die Entwicklungsumgebung unberührt bleibt)"
cd "$ROOT"
DESTDIR="$STAGE" pixi run cmake --install build/release >"$OUT/install.log"
cp -a "$STAGE$ENVDIR"/. "$USR"/
rm -rf "$STAGE"

echo "== Unnötiges entfernen"
cd "$USR"
rm -rf include conda-meta doc/global share/gtk-doc share/man share/info lib/cmake lib/pkgconfig lib/python3.11/test
find . -name '*.a' -delete
find . -name '*.h' -type f -delete
find . -name '*.cmake' -type f -delete
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -type f -delete
mv bin bin_tmp && mkdir bin
mv bin_tmp/FreeCAD bin/freecad 2>/dev/null || cp -a bin_tmp/freecad bin/freecad
mv bin_tmp/FreeCADCmd bin/freecadcmd 2>/dev/null || cp -a bin_tmp/freecadcmd bin/freecadcmd
for tool in ccx python python3 python3.11 pip pyside6-rcc dot unflatten gmsh; do
    if [ -e "bin_tmp/$tool" ]; then cp -a "bin_tmp/$tool" bin/; fi
done
rm -rf bin_tmp
if [ -f bin/pip ]; then sed -i '1s|.*|#!/usr/bin/env python|' bin/pip; fi

echo "== Suchpfade der Bibliotheken relativ machen (patchelf)"
command -v patchelf >/dev/null || { echo "patchelf fehlt (Ubuntu: sudo apt install patchelf)"; exit 1; }
"$USR/bin/python" -I - "$USR" "$ENVDIR" "$ROOT" <<'PY'
import os, subprocess, sys
usr, env, root = (os.path.realpath(x) for x in sys.argv[1:4])
lib = os.path.join(usr, "lib")
n = 0
for base, _, names in os.walk(usr):
    for f in names:
        p = os.path.join(base, f)
        if os.path.islink(p) or not os.path.isfile(p):
            continue
        with open(p, "rb") as fh:
            if fh.read(4) != b"\x7fELF":
                continue
        rp = subprocess.run(["patchelf", "--print-rpath", p], capture_output=True, text=True).stdout.strip()
        entries = [e for e in rp.split(":") if e]
        rel = os.path.relpath(lib, base)
        origin = "$ORIGIN" + ("" if rel == "." else "/" + rel)
        bad = [e for e in entries if e.startswith(env) or e.startswith(root)]
        if bad or (not entries and (os.sep + "bin" + os.sep in p or base == lib)):
            new = [origin] + [e for e in entries if e not in bad and e != origin]
            subprocess.run(["patchelf", "--set-rpath", ":".join(new), p], check=True)
            n += 1
print("RPATH angepasst:", n)
PY
echo "== Prüfen: fehlende Bibliotheken"
missing="$(find "$USR/bin" "$USR/lib" -type f \( -name '*.so*' -o -path '*/bin/*' \) -print0 | xargs -0 ldd 2>/dev/null | grep 'not found' | sort | uniq -c || true)"
if [ -n "$missing" ]; then echo "$missing" | head -30; fi
echo "== Programmsymbol, Startskript, Desktop-Datei"
cp "$LIN/AppRun" "$APPDIR/AppRun"
chmod a+x "$APPDIR/AppRun"
cp "$LIN/de.mint-checker.MINT-CAD.desktop" "$APPDIR/"
cp "$LIN/de.mint-checker.MINT-CAD.svg" "$LIN/de.mint-checker.MINT-CAD.png" "$APPDIR/"
mkdir -p "$USR/share/icons/hicolor/scalable/apps" "$USR/share/icons/hicolor/256x256/apps" "$USR/share/applications"
cp "$LIN/de.mint-checker.MINT-CAD.svg" "$USR/share/icons/hicolor/scalable/apps/"
cp "$LIN/de.mint-checker.MINT-CAD.png" "$USR/share/icons/hicolor/256x256/apps/"
cp "$LIN/de.mint-checker.MINT-CAD.desktop" "$USR/share/applications/"
cp "$ROOT/LICENSE" "$ROOT/THIRD-PARTY.md" "$ROOT/THIRD-PARTY-PACKAGES.md" "$APPDIR/"
ln -sf de.mint-checker.MINT-CAD.png "$APPDIR/.DirIcon"
pixi list -e default > "$APPDIR/packages.txt" 2>/dev/null || true

echo "== Rauchtest"
mkdir -p "$OUT/smoke-home"
env -i HOME="$OUT/smoke-home" PREFIX="$USR" PYTHONHOME="$USR" PYTHONPATH="$USR" \
    "$USR/bin/freecadcmd" -c "import FreeCAD, Part, Sketcher, PartDesign, TechDraw, Draft, Fem, Assembly, Mesh, Spreadsheet; print('Module OK', FreeCAD.getHomePath())"
rm -rf "$OUT/smoke-home"

echo "== AppImage"
TOOL="$OUT/appimagetool-$ARCH.AppImage"
curl -fL -o "$TOOL" "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$ARCH.AppImage"
chmod a+x "$TOOL"
# --appimage-extract-and-run: funktioniert auch ohne FUSE (z. B. in Containern)
ARCH="$ARCH" "$TOOL" --appimage-extract-and-run --comp zstd \
    --mksquashfs-opt -Xcompression-level --mksquashfs-opt 22 \
    "$APPDIR" "$OUT/$NAME.AppImage"
rm -f "$TOOL"
(cd "$OUT" && sha256sum "$NAME.AppImage" | tee "$NAME.AppImage.sha256")
du -sh "$OUT/$NAME.AppImage"
echo "== Fertig: $OUT/$NAME.AppImage"
