# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Einrichtung der Benutzeroberfläche für den Schulbetrieb."""

import FreeCAD

# Erhöhen, wenn sich die Voreinstellungen ändern: dann werden sie beim nächsten Start einmal neu gesetzt.
SETUP_VERSION = 1

# Reihenfolge der sichtbaren Workbenches (Arbeitsablauf: Konstruieren -> Zeichnung -> ...)
ENABLED_WORKBENCHES = [
    "PartDesignWorkbench",
    "SketcherWorkbench",
    "TechDrawWorkbench",
    "DraftWorkbench",
    "AssemblyWorkbench",
    "FemWorkbench",
    "PartWorkbench",
    "SpreadsheetWorkbench",
]

# Für den Unterricht ausgeblendet (über Einstellungen > Workbenches wieder einblendbar)
DISABLED_WORKBENCHES = [
    "MeshWorkbench",
    "TestWorkbench",
    "MaterialWorkbench",
]


def apply_workbench_selection():
    """Setzt Sichtbarkeit und Reihenfolge der Workbenches einmal je SETUP_VERSION."""
    mint = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD")
    if mint.GetInt("SetupVersion", 0) >= SETUP_VERSION:
        return
    wbs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Workbenches")
    wbs.SetString("Ordered", ",".join(ENABLED_WORKBENCHES))
    wbs.SetString("Disabled", ",".join(DISABLED_WORKBENCHES))
    mint.SetInt("SetupVersion", SETUP_VERSION)
