# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Schulanpassungen. Wird beim Start der Oberfläche geladen."""

import MintCADSetup

MintCADSetup.apply_defaults()

import MintCADSimplify

MintCADSimplify.install()

import MintCADHelp

MintCADHelp.register()

import MintCADRibbon
from PySide6 import QtCore as _QtCore

if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD").GetBool("Ribbon", True):
    _QtCore.QTimer.singleShot(500, MintCADRibbon.install)
