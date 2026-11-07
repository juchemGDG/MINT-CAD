# Build unter macOS (Apple Silicon)

Getestet: macOS 27.2, arm64, Command Line Tools, FreeCAD 1.1.4 (Basis von MINT-CAD).

## Voraussetzungen
- Xcode Command Line Tools, Homebrew, `brew install pixi`
- Bei externer SSD (exFAT): APFS-Sparsebundle verwenden
  `hdiutil create -size 150g -type SPARSEBUNDLE -fs APFS -volname MINTCAD <Pfad>/MINTCAD.sparsebundle`
- Freier Platz: ca. 25-40 GB

## Wichtig: SDK
Der Conda-Compiler (clang 18) kommt mit dem neuesten macOS-SDK (27.x) nicht zurecht
(`INFINITY` undeclared, vermischte Framework-Header). Ein älteres, vollständiges SDK verwenden
(`ls /Library/Developer/CommandLineTools/SDKs`; hier 14.5) und `SDKROOT` setzen:

```sh
export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX14.5.sdk
```

## Schritte
```sh
pixi install
pixi run cmake --preset conda-macos-release -DCMAKE_OSX_SYSROOT=$SDKROOT
pixi run build-release          # ca. 1-2 h beim ersten Mal (ccache beschleunigt Wiederholungen)
pixi run build/release/bin/FreeCAD
```
Bei SDK-Wechsel `build/release` vollständig löschen (CMake-Cache enthält SDK-Pfade).

## Prüfung
```sh
pixi run build/release/bin/FreeCADCmd -c "import Part, Sketcher, PartDesign, TechDraw, Draft, Fem; print('OK')"
```

## MINT-CAD-Konfiguration
Statt des direkten `cmake --preset ...` das Skript `tools/mintcad/configure-macos.sh` verwenden;
es lädt `tools/mintcad/options.cmake` (abgeschaltete Module). Nach dem Abschalten eines Moduls
alte Ausgabeordner `build/release/Mod/<Modul>` löschen, sonst wirken sie noch.
