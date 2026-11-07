# SPDX-License-Identifier: LGPL-2.1-or-later
# MINT-CAD: Anpassungen für den Schulbetrieb (Workbench-Auswahl, vereinfachte Werkzeugleisten, Design)

SET(MintCAD_SRCS
    InitGui.py
    MintCADSetup.py
    MintCADSimplify.py
    MintCADHelp.py
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

# Einheitlicher MINT-CAD-Icon-Satz: aus den FreeCAD-Icons erzeugt und unter <Home>/icons abgelegt.
# Dieser Ordner hat in der BitmapFactory Vorrang vor den eingebetteten Icons.
set(MintCAD_ICON_DIR "${CMAKE_BINARY_DIR}/icons")
add_custom_target(MintCADIcons ALL
    COMMAND ${Python3_EXECUTABLE} -I "${CMAKE_SOURCE_DIR}/tools/mintcad/make_icons.py" "${MintCAD_ICON_DIR}"
    COMMENT "MINT-CAD: Icon-Satz erzeugen"
    VERBATIM
)
install(DIRECTORY "${MintCAD_ICON_DIR}/" DESTINATION icons FILES_MATCHING PATTERN "*.svg")
