# MINT-CAD: Modulauswahl (Initial-Cache, Verwendung: cmake -C tools/mintcad/options.cmake ...)
# Jede Zeile entspricht einem eigenen Commit der Reduktion (siehe docs/nitcad/PLAN.md).
set(BUILD_BIM OFF CACHE BOOL "MINT-CAD: BIM deaktiviert" FORCE)
set(BUILD_CAM OFF CACHE BOOL "MINT-CAD: CAM deaktiviert" FORCE)
