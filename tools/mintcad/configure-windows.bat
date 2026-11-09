@echo off
rem MINT-CAD: Release-Konfiguration fuer Windows (x64) mit reduzierter Modulauswahl.
rem Verwendung (Eingabeaufforderung im Quellordner):  tools\mintcad\configure-windows.bat
rem Danach:  pixi run build-release
cd /d "%~dp0\..\.."
set CFLAGS=
set CXXFLAGS=
set DEBUG_CFLAGS=
set DEBUG_CXXFLAGS=
pixi run cmake --preset conda-windows-release -DCMAKE_GENERATOR_PLATFORM= -DCMAKE_GENERATOR_TOOLSET= -C tools/mintcad/options.cmake
