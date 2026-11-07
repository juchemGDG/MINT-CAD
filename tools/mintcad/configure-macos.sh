#!/bin/sh
# MINT-CAD: Release-Konfiguration für macOS mit reduzierter Modulauswahl.
# Verwendung: tools/mintcad/configure-macos.sh   (danach: pixi run build-release)
set -e
cd "$(dirname "$0")/../.."
export SDKROOT="${SDKROOT:-/Library/Developer/CommandLineTools/SDKs/MacOSX14.5.sdk}"
pixi run cmake --preset conda-macos-release -C tools/mintcad/options.cmake -DCMAKE_OSX_SYSROOT="$SDKROOT"
