# MINT-CAD: Installationsdateien für Windows und Linux bauen

Die Pakete lassen sich **nicht auf dem Mac** erzeugen (Cross-Kompilieren geht mit pixi/conda nicht).
Gebaut wird auf einem Rechner mit dem jeweiligen System. Der Quellordner (Branch `nitcad`) wird dorthin kopiert oder geklont.

| System | Ergebnis | Skript |
|---|---|---|
| macOS (arm64) | `MINT-CAD-macOS-arm64.dmg` | `tools/mintcad/make_macos_bundle.sh` |
| Windows (x64) | `MINT-CAD-<Version>-Windows-x86_64-installer.exe` und `.7z` (portabel) | `tools/mintcad/make_windows_installer.sh` |
| Linux (x86-64 oder aarch64) | `MINT-CAD-<Version>-Linux-<Arch>.AppImage` | `tools/mintcad/make_linux_appimage.sh` |

Alle Skripte legen zusätzlich eine `.sha256`-Datei an. **Stand: Windows- und Linux-Skripte sind geschrieben, aber noch nicht auf den Zielsystemen getestet.**

## Gemeinsame Voraussetzung
[pixi](https://pixi.sh) installieren, dann im Quellordner `pixi install`.

## Linux
Getestet werden sollte auf einer älteren Distribution (z. B. Ubuntu 22.04), damit das AppImage auch auf älteren Systemen läuft.
```sh
tools/mintcad/configure-linux.sh
pixi run build-release
tools/mintcad/make_linux_appimage.sh
```
Ergebnis in `build/mintcad-dist-linux/`. Benötigt `curl` (lädt `appimagetool`). Nutzer: Datei ausführbar machen (`chmod +x`) und starten.
Unter Ubuntu 22.04+ braucht ein AppImage `libfuse2` (`sudo apt install libfuse2`) oder den Start mit `--appimage-extract-and-run`.

## Windows
Zusätzlich nötig: Visual Studio 2022 Build Tools (C++), Git for Windows (Git-Bash), 7-Zip (im `PATH`) und
[NSIS 3](https://nsis.sourceforge.io/Download) mit den zwei Spezialversionen *Large strings* und *Advanced logging*
(Anleitung in `package/WindowsInstaller/README.md`). Alternativ `pixi install -e package` in `package/rattler-build`, das enthält NSIS.
Liegt `makensis.exe` woanders, vorher `export MAKENSIS=/c/Pfad/makensis.exe` setzen.
```bat
tools\mintcad\configure-windows.bat
pixi run build-release
```
Dann in der **Git-Bash**:
```sh
tools/mintcad/make_windows_installer.sh
```
Ergebnis in `build/mintcad-dist-windows/`. Hinweis: Das Skript installiert MINT-CAD in die pixi-Umgebung (`.pixi/envs/default/Library`).
Die Programmdateien heißen im Paket `MINT-CAD.exe` und `MINT-CADcmd.exe`. Der Installer ist nicht signiert; Windows zeigt deshalb
beim ersten Start „Windows hat Ihren PC geschützt“ → *Weitere Informationen* → *Trotzdem ausführen*.

## Grafiken
Programmsymbol und Installer-Bilder (`tools/mintcad/windows`, `tools/mintcad/linux`) sind bereits erzeugt. Neu erzeugen:
`pixi run python -I tools/mintcad/make_installer_assets.py`.

## Beim ersten Test prüfen
- Windows: Installer läuft durch, Startmenü-Eintrag „MINT-CAD“, Start, Beispieldatei öffnen, Deinstallation. Beim Umbenennen von `freecad.exe` zu `MINT-CAD.exe` darf nichts fehlen (Rauchtest im Skript prüft nur `freecadcmd`).
- Linux: Fenstersymbol und Name in der Startleiste (`StartupWMClass=MINT-CAD` in `tools/mintcad/linux/de.mint-checker.MINT-CAD.desktop` evtl. anpassen), FEM/CalculiX.
