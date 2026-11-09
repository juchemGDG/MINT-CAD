#!/bin/sh
# MINT-CAD: Release-Konfiguration für Linux (x86-64 oder aarch64) mit reduzierter Modulauswahl.
# Verwendung: tools/mintcad/configure-linux.sh   (danach: pixi run build-release)
set -e
cd "$(dirname "$0")/../.."
pixi run cmake --preset conda-linux-release -C tools/mintcad/options.cmake
