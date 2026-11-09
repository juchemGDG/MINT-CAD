#!/bin/sh
# MINT-CAD: Release-Konfiguration für Linux (x86-64 oder aarch64) mit reduzierter Modulauswahl.
# Verwendung: tools/mintcad/configure-linux.sh   (danach: pixi run build-release)
set -e
cd "$(dirname "$0")/../.."
# Flags wie bei den pixi-Aufgaben "configure-release" (leer, sonst greifen GCC-Flags der Conda-Aktivierung)
CFLAGS="" CXXFLAGS="" DEBUG_CFLAGS="" DEBUG_CXXFLAGS="" \
    pixi run cmake --preset conda-linux-release -C tools/mintcad/options.cmake
