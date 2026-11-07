# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Einrichtung der Benutzeroberfläche für den Schulbetrieb."""

import FreeCAD
import FreeCADGui as Gui

# Erhöhen, wenn sich die Voreinstellungen ändern: dann werden sie beim nächsten Start einmal neu gesetzt.
SETUP_VERSION = 2

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


def apply_defaults():
    """Setzt die Schul-Voreinstellungen einmal je SETUP_VERSION (Nutzer können sie danach ändern)."""
    mint = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD")
    if mint.GetInt("SetupVersion", 0) >= SETUP_VERSION:
        return

    # Workbench-Auswahl und Reihenfolge
    wbs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Workbenches")
    wbs.SetString("Ordered", ",".join(ENABLED_WORKBENCHES))
    wbs.SetString("Disabled", ",".join(DISABLED_WORKBENCHES))

    # Sprache: Deutsch; Einheiten: mm/kg/s/Grad
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").SetString("Language", "German")
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema", 0)

    # Startseite: Einrichtungsassistent (FirstStart) überspringen, Beispiele zeigen
    start = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Start")
    start.SetBool("FirstStart2024", False)
    start.SetBool("ShowExamples", True)

    # Sprache sofort umschalten (sonst erst beim nächsten Start wirksam)
    try:
        Gui.setLocale("German")
    except Exception as exc:  # Übersetzung fehlt o. ä. – kein Grund zum Abbruch
        FreeCAD.Console.PrintWarning("MINT-CAD: Sprache konnte nicht umgestellt werden: %s\n" % exc)

    mint.SetInt("SetupVersion", SETUP_VERSION)
