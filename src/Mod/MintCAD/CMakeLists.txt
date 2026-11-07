# SPDX-License-Identifier: LGPL-2.1-or-later
# MINT-CAD: Anpassungen für den Schulbetrieb (Workbench-Auswahl, vereinfachte Werkzeugleisten, Design)

SET(MintCAD_SRCS
    InitGui.py
    MintCADSetup.py
    MintCADSimplify.py
)
SOURCE_GROUP("" FILES ${MintCAD_SRCS})

ADD_CUSTOM_TARGET(MintCAD ALL
    SOURCES ${MintCAD_SRCS}
)

fc_copy_sources(MintCAD "${CMAKE_BINARY_DIR}/Mod/MintCAD" ${MintCAD_SRCS})

INSTALL(
    FILES
        ${MintCAD_SRCS}
    DESTINATION
        Mod/MintCAD
)
