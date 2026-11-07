# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Vereinfachung der Werkzeugleisten und Menüs (WorkbenchManipulator).

Die Listen unten enthalten, was für den Unterricht ausgeblendet wird. Die Befehle bleiben
in FreeCAD vorhanden (Einstellungen > Anpassen), sie erscheinen nur nicht mehr standardmäßig.
Pro Aufruf entfernt der Manipulator das erste Vorkommen, daher wird jeder Befehl einmal gelistet.
"""

import FreeCADGui as Gui

# Ganze Werkzeugleisten (interne Namen)
HIDE_TOOLBARS = [
    # TechDraw: Zusatzleisten der Extension
    "TechDraw Attributes",
    "TechDraw Extend Dimensions",
    "TechDraw Stacking",
]

# Einzelne Befehle (aus Werkzeugleisten und Menüs)
HIDE_COMMANDS = [
    # Part Design: Hilfsfunktionen
    "PartDesign_SubShapeBinder",
    "PartDesign_Clone",
    # Part Design: Aufbau (Loft, Rohr, Wendel sind für den Einstieg zu speziell)
    "PartDesign_AdditiveLoft",
    "PartDesign_AdditivePipe",
    "PartDesign_AdditiveHelix",
    "PartDesign_SubtractiveLoft",
    "PartDesign_SubtractivePipe",
    "PartDesign_SubtractiveHelix",
    "PartDesign_Boolean",
    # Part Design: Verrundungen und Muster
    "PartDesign_Thickness",
    "PartDesign_Draft",
    "PartDesign_MultiTransform",
    # TechDraw: selten benötigte Ansichten, Hilfen und Symbole
    "TechDraw_BrokenView",
    "TechDraw_ActiveView",
    "TechDraw_DraftView",
    "TechDraw_ClipGroup",
    "TechDraw_AxoLengthDimension",
    "TechDraw_DimensionRepair",
    "TechDraw_RichTextAnnotation",
    "TechDraw_WeldSymbol",
    # Draft: Erzeugen
    "Draft_Facebinder",
    "Draft_ShapeString",
    "Draft_Hatch",
    "Draft_BSpline",
    "Draft_BezierTools",
    # Draft: Ändern
    "Draft_Stretch",
    "Draft_Clone",
    "Draft_SubelementHighlight",
    "Draft_Join",
    "Draft_Split",
    "Draft_Upgrade",
    "Draft_Downgrade",
    "Draft_WireToBSpline",
    "Draft_Slope",
    "Draft_FlipDimension",
    "Draft_Shape2DView",
    # Draft: Hilfsmittel
    "Draft_AnnotationStyleEditor",
    "Draft_AddNamedGroup",
    "Draft_SelectGroup",
    "Draft_AddToGroup",
    "Draft_AddConstruction",
    "Draft_WorkingPlaneProxy",
]


class _Simplifier:
    def modifyToolBars(self):
        return [{"remove": name} for name in HIDE_TOOLBARS + HIDE_COMMANDS]

    def modifyMenuBar(self):
        return [{"remove": name} for name in HIDE_COMMANDS]


_manipulator = None


def install():
    global _manipulator
    if _manipulator is None:
        _manipulator = _Simplifier()
        Gui.addWorkbenchManipulator(_manipulator)
