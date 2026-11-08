# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Einrichtung der Benutzeroberfläche für den Schulbetrieb."""

import os
import xml.etree.ElementTree as ET

import FreeCAD
import FreeCADGui as Gui

# Erhöhen, wenn sich die Voreinstellungen ändern: dann werden sie beim nächsten Start einmal neu gesetzt.
SETUP_VERSION = 6

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


THEME_PACK = "MINT-CAD"
# Erhöhen, wenn sich das Theme ändert: wird dann einmal neu angewendet (ohne andere Einstellungen anzufassen).
THEME_VERSION = 4


def _apply_cfg_group(node, grp):
    """Überträgt eine FreeCAD-Parameterdatei (XML) rekursiv in eine Parametergruppe."""
    for child in node:
        name = child.get("Name")
        value = child.get("Value")
        if child.tag == "FCParamGroup":
            _apply_cfg_group(child, grp.GetGroup(name))
        elif child.tag == "FCText":
            grp.SetString(name, child.text or "")
        elif child.tag == "FCBool":
            grp.SetBool(name, value == "1")
        elif child.tag == "FCInt":
            grp.SetInt(name, int(value))
        elif child.tag == "FCUInt":
            grp.SetUnsigned(name, int(value))
        elif child.tag == "FCFloat":
            grp.SetFloat(name, float(value))


def apply_theme(pack=THEME_PACK):
    """Wendet das Preference-Pack (Theme) an. Das Stylesheet greift nach einem Neustart."""
    path = os.path.join(FreeCAD.getResourceDir(), "Gui", "PreferencePacks", pack, pack + ".cfg")
    if not os.path.isfile(path):
        FreeCAD.Console.PrintWarning("MINT-CAD: Theme-Datei fehlt: %s\n" % path)
        return
    root = ET.parse(path).getroot()  # <FCParameters><FCParamGroup Name="Root">...
    top = root.find("FCParamGroup")
    for sub in top:
        if sub.tag == "FCParamGroup":
            _apply_cfg_group(sub, FreeCAD.ParamGet("User parameter:" + sub.get("Name")))


def apply_defaults():
    """Setzt die Schul-Voreinstellungen einmal je SETUP_VERSION (Nutzer können sie danach ändern)."""
    mint = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD")
    if mint.GetInt("SetupVersion", 0) >= SETUP_VERSION:
        if mint.GetInt("ThemeVersion", 0) < THEME_VERSION:
            apply_theme()
            mint.SetInt("ThemeVersion", THEME_VERSION)
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

    # TechDraw: Schulvorlage als Standard-Zeichenblatt
    tpl_dir = os.path.join(FreeCAD.getResourceDir(), "Mod", "TechDraw", "Templates", "MINT-CAD")
    files = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Files")
    files.SetString("TemplateDir", tpl_dir)
    files.SetString("TemplateFile", os.path.join(tpl_dir, "MINTCAD_A4_Querformat.svg"))

    # Punktfang: Sketcher fängt an Objekten; Draft mit Endpunkt, Mitte, Zentrum, Schnittpunkt u. a.
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Sketcher/Snap").SetBool("SnapToObjects", True)
    draft = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
    snap_order = ["Lock", "Near", "Extension", "Parallel", "Grid", "Endpoint", "Midpoint", "Perpendicular",
                  "Angle", "Center", "Ortho", "Intersection", "Special", "Dimensions", "WorkingPlane"]
    snap_on = {"Lock", "Grid", "Endpoint", "Midpoint", "Perpendicular", "Center", "Ortho", "Intersection", "Dimensions"}
    draft.SetString("snapModes", "".join("1" if n in snap_on else "0" for n in snap_order))
    draft.SetBool("alwaysSnap", True)

    # Layout: linkes Panel (Modell/Aufgaben) beim nächsten Start auf eine schmale Breite setzen
    mint.SetBool("ApplyLayout", True)

    # Design (Theme): Stylesheet wird beim nächsten Start geladen
    apply_theme()
    mint.SetInt("ThemeVersion", THEME_VERSION)

    # Sprache sofort umschalten (sonst erst beim nächsten Start wirksam)
    try:
        Gui.setLocale("German")
    except Exception as exc:  # Übersetzung fehlt o. ä. – kein Grund zum Abbruch
        FreeCAD.Console.PrintWarning("MINT-CAD: Sprache konnte nicht umgestellt werden: %s\n" % exc)

    mint.SetInt("SetupVersion", SETUP_VERSION)


def apply_layout():
    """Setzt einmalig das Layout: Aufgaben und Modell als Reiter im linken Panel, ca. 300 px breit."""
    mint = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD")
    if not mint.GetBool("ApplyLayout", False):
        return
    mint.SetBool("ApplyLayout", False)
    from PySide6 import QtCore, QtWidgets

    mw = Gui.getMainWindow()
    model = tasks = None
    for dock in mw.findChildren(QtWidgets.QDockWidget):
        name = dock.widget().objectName() if dock.widget() else dock.objectName()
        if name == "Model":
            model = dock
        elif name == "Tasks":
            tasks = dock
    if model is None:
        return
    if tasks is not None and not tasks.isFloating():
        mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, model)
        mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, tasks)
        mw.tabifyDockWidget(model, tasks)
        model.raise_()
    mw.resizeDocks([model], [300], QtCore.Qt.Horizontal)
