# MINT-CAD – FreeCAD für den Schulunterricht

Basis: FreeCAD 1.1.4 (LGPL-2.1+). Branch `nitcad` (Änderungen), Tag `1.1.4` = unveränderte Basis.
Entwicklung auf SSD (APFS-Sparsebundle /Volumes/T7/MINTCAD.sparsebundle, Volume "MINTCAD").
Erste Zielplattform: macOS (arm64). Später: Windows, Linux.

## Entscheidungen
- Behalten: Sketcher, PartDesign, Part (Grundkörper), TechDraw, Draft (2D, einfache Maße), Assembly (einfache Baugruppen), FEM (Kursstufe), Spreadsheet.
- Entfernt: BIM, CAM, Robot, OpenSCAD, ReverseEngineering, Inspection, Points, Surface (Schalter in tools/mintcad/options.cmake). Mesh bleibt wegen STL-Export für den 3D-Druck.
- Vorgehen: erst CMake-Optionen/Konfiguration/Python, C++-Kern nur im Notfall.
- Design: PAP-Editor-Stil (siehe design/tokens.md).

## Phasen
0. Vorbereitung (Repo, Plan, Design-Tokens)                       <- erledigt
1. Baseline bauen (pixi, macOS arm64) und Build-Anleitung        <- erledigt
2. Umfang reduzieren (ein Modul je Commit)                      <- erledigt: BIM, CAM, Robot, OpenSCAD, ReverseEngineering, Inspection, Points, Surface aus; Mesh bleibt (STL für 3D-Druck)
3. Vereinfachte Workbenches (Mod/MintCAD, WorkbenchManipulator)       <- erledigt: Part Design, Sketcher, TechDraw, Draft, FEM, Assembly gekürzt
   (Abweichung: keine neue Gesamt-Workbench, da Skizzen-Leisten an Sketcher/PartDesign hängen)
4. Oberfläche vereinfachen                                          <- erledigt: Startseite (BIM-Knopf -> Technische Zeichnung), Deutsch/mm als Voreinstellung, Makro-Menü weg;
   offen: Einstellungsdialog kürzen (braucht C++-Eingriff), vertagt
5. Modernes Design (Qt-Stylesheet hell/dunkel, Icons, 3D-Ansicht)
6. Unterrichtshilfen (Vorlagen, Beispiele, Hilfe)
7. Branding & Paketierung (Name, Logo, Installer macOS/Windows/Linux)
8. Test mit Schülern, Upstream-Pflege

## Commit-Konventionen
`docs:`, `build:`, `feat:`, `style:`, `chore:` – ein Thema pro Commit, Start jeweils geprüft.

## Ausgeblendete Befehle wieder einblenden
Liste in `src/Mod/MintCAD/MintCADSimplify.py` (HIDE_TOOLBARS, HIDE_COMMANDS, REPLACE_GROUPS):
Eintrag löschen, neu bauen. Die Befehle bleiben unter Einstellungen > Anpassen immer erreichbar.
