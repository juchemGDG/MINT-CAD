# MINT-CAD: Modulauswahl (Initial-Cache, Verwendung: cmake -C tools/mintcad/options.cmake ...)
# Jede Zeile entspricht einem eigenen Commit der Reduktion (siehe docs/nitcad/PLAN.md).
set(BUILD_BIM OFF CACHE BOOL "MINT-CAD: BIM deaktiviert" FORCE)
set(BUILD_CAM OFF CACHE BOOL "MINT-CAD: CAM deaktiviert" FORCE)
set(BUILD_ROBOT OFF CACHE BOOL "MINT-CAD: Robot deaktiviert" FORCE)
set(BUILD_OPENSCAD OFF CACHE BOOL "MINT-CAD: OpenSCAD deaktiviert" FORCE)
set(BUILD_REVERSEENGINEERING OFF CACHE BOOL "MINT-CAD: ReverseEngineering deaktiviert" FORCE)
set(BUILD_INSPECTION OFF CACHE BOOL "MINT-CAD: Inspection deaktiviert" FORCE)
set(BUILD_POINTS OFF CACHE BOOL "MINT-CAD: Points deaktiviert" FORCE)
