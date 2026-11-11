# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Schulanpassungen. Wird beim Start der Oberfläche geladen."""

import MintCADSetup

MintCADSetup.apply_defaults()
MintCADSetup.register_fonts()

import MintCADParams

MintCADParams.register()

import MintCADFusion

MintCADFusion.apply_defaults()

import MintCADSimplify

MintCADSimplify.install()

import MintCADHelp

MintCADHelp.register()

import MintCADRibbon
from PySide6 import QtCore as _QtCore

if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD").GetBool("Ribbon", True):
    _QtCore.QTimer.singleShot(500, MintCADRibbon.install)

import MintCADFusion
import MintCADTimeline
import MintCADRadial

_QtCore.QTimer.singleShot(900, MintCADFusion.install)
if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD").GetBool("Timeline", True):
    _QtCore.QTimer.singleShot(1000, MintCADTimeline.install)
_QtCore.QTimer.singleShot(1100, MintCADRadial.install)

import MintCADParams

_QtCore.QTimer.singleShot(1200, MintCADParams.install_fields)
