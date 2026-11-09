@echo off
rem MINT-CAD: Release-Konfiguration fuer Windows (x64) mit reduzierter Modulauswahl.
rem Verwendung (Eingabeaufforderung im Quellordner):  tools\mintcad\configure-windows.bat
rem Danach:  pixi run build-release
cd /d "%~dp0\..\.."
pixi run cmake --preset conda-windows-release -C tools/mintcad/options.cmake
