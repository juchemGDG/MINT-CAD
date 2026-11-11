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
    # Makro-Leiste
    "Macro",
    # FEM: Elektromagnetik, Strömung, Wärme und Spezialanalysen (Schwerpunkt: Statik)
    "Electromagnetic Boundary Conditions",
    "Fluid Boundary Conditions",
    "Thermal Boundary Conditions and Loads",
    "Geometrical Analysis Features",
]

# Ganze Menüs (interne Namen, englisch)
HIDE_MENUS = [
    "&Macro",
]

# Einzelne Befehle (aus Werkzeugleisten und Menüs)
HIDE_COMMANDS = [
    # Hilfe-Menü: Verweise auf Spenden, Entwickler- und Python-Handbuch
    "Std_FreeCADDonation",
    "Std_FreeCADWebsite",
    "Std_DevHandbook",
    "Std_PythonHelp",
    "Std_FreeCADForum",
    "Std_ReportBug",
    "Std_RestartInSafeMode",
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
    # Sketcher: Ellipsen, Hyperbeln, Parabeln und weitere B-Spline-Varianten
    "Sketcher_CreateEllipseByCenter",
    "Sketcher_CreateEllipseBy3Points",
    "Sketcher_CreateArcOfEllipse",
    "Sketcher_CreateArcOfHyperbola",
    "Sketcher_CreateArcOfParabola",
    "Sketcher_CreatePeriodicBSpline",
    "Sketcher_CreateBSplineByInterpolation",
    "Sketcher_CreatePeriodicBSplineByInterpolation",
    # FEM: Material, Elemente, Randbedingungen
    "FEM_MaterialFluid",
    "FEM_MaterialMechanicalNonlinear",
    "FEM_MaterialReinforced",
    "FEM_ElementRotation1D",
    "FEM_ElementFluid1D",
    "FEM_ConstraintRigidBody",
    "FEM_ConstraintTie",
    "FEM_ConstraintSpring",
    "FEM_ConstraintCentrif",
    # FEM: Netz und Löser
    "FEM_MeshBoundaryLayer",
    "FEM_MeshRegion",
    "FEM_MeshGroup",
    "FEM_FEMMesh2Mesh",
    "FEM_CompEmEquations",
    "FEM_EquationFlow",
    "FEM_EquationFlux",
    "FEM_EquationHeat",
    # FEM: Ergebnisfilter (Verformung, Konturen und Linienauswertung bleiben)
    "FEM_PostBranchFilter",
    "FEM_PostFilterClipScalar",
    "FEM_PostFilterCutFunction",
    "FEM_PostFilterClipRegion",
    "FEM_PostFilterGlyph",
    "FEM_PostFilterLinearizedStresses",
    "FEM_PostFilterDataAtPoint",
    "FEM_PostFilterCalculator",
    "FEM_PostCreateFunctions",
    "FEM_PostVisualization",
    # Assembly: Simulation und Spezialgelenke (Fest, Dreh, Schub, Kugel u. a. bleiben)
    "Assembly_CreateSimulation",
    "Assembly_CreateJointRackPinion",
    "Assembly_CreateJointScrew",
    "Assembly_CreateJointGearBelt",
]


# Sammelbefehle (Aufklappmenüs), deren Einträge sich nicht einzeln ausblenden lassen,
# werden in den Werkzeugleisten durch die gewünschten Einzelbefehle ersetzt.
REPLACE_GROUPS = {
    # Sketcher: nur Kreise (keine Ellipsen/Hyperbeln/Parabeln), nur der einfache B-Spline
    "Sketcher_CompCreateConic": ["Sketcher_CreateCircle", "Sketcher_Create3PointCircle"],
    "Sketcher_CompCreateBSpline": ["Sketcher_CreateBSpline"],
}


# Befehle, die in den Standard-Leisten fehlen, im Unterricht aber gebraucht werden (Befehl, Werkzeugleiste)
ADD_COMMANDS = [
    ("PartDesign_Plane", "Part Design Helper Features"),  # Bezugsebene
    ("PartDesign_Line", "Part Design Helper Features"),  # Referenzlinie
    ("MintCAD_Parameters", "Part Design Helper Features"),  # Parameter-Dialog (MintCADParams.py)
    ("TechDraw_ProjectionGroup", "TechDraw Views"),  # Ansichtsgruppe (Hauptansicht + Projektionen)
]


class _Simplifier:
    def modifyToolBars(self):
        actions = [{"append": cmd, "toolBar": tb} for cmd, tb in ADD_COMMANDS]
        for group, singles in REPLACE_GROUPS.items():
            for single in singles:
                actions.append({"insert": single, "toolItem": group})
            actions.append({"remove": group})
        actions += [{"remove": name} for name in HIDE_TOOLBARS + HIDE_COMMANDS]
        return actions

    def modifyMenuBar(self):
        # Kurzanleitung im Hilfe-Menü vor „Über“ einfügen
        actions = [{"insert": "MintCAD_QuickGuide", "menuItem": "Std_About"}]
        return actions + [{"remove": name} for name in HIDE_MENUS + HIDE_COMMANDS]


_manipulator = None


def install():
    global _manipulator
    if _manipulator is None:
        _manipulator = _Simplifier()
        Gui.addWorkbenchManipulator(_manipulator)
