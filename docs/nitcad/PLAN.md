# MINT-CAD – FreeCAD für den Schulunterricht

Basis: FreeCAD 1.1.4 (LGPL-2.1+). Branch `nitcad` (Änderungen), Tag `1.1.4` = unveränderte Basis.
Entwicklung auf SSD (APFS-Sparsebundle /Volumes/T7/MINTCAD.sparsebundle, Volume "MINTCAD").
Erste Zielplattform: macOS (arm64). Später: Windows, Linux.

## Entscheidungen
- Behalten: Sketcher, PartDesign, Part (Grundkörper), TechDraw, Draft (2D, einfache Maße), Assembly (einfache Baugruppen), FEM (Kursstufe), Spreadsheet.
- Entfernen/abschalten: CAM, BIM/Arch, Robot, OpenSCAD, Mesh-Werkzeuge, Points, Reverse Engineering, Surface (jeweils eigener Commit).
- Vorgehen: erst CMake-Optionen/Konfiguration/Python, C++-Kern nur im Notfall.
- Design: PAP-Editor-Stil (siehe design/tokens.md).

## Phasen
0. Vorbereitung (Repo, Plan, Design-Tokens)                       <- erledigt
1. Baseline bauen (pixi, macOS arm64) und Build-Anleitung
2. Umfang reduzieren (ein Modul je Commit, danach Startprüfung)
3. Workbench "Schule": Skizze -> Körper -> Zeichnung (+ Draft, Assembly, FEM erreichbar)
4. Oberfläche vereinfachen (Menüs, Einstellungen, Startseite, Deutsch)
5. Modernes Design (Qt-Stylesheet hell/dunkel, Icons, 3D-Ansicht)
6. Unterrichtshilfen (Vorlagen, Beispiele, Hilfe)
7. Branding & Paketierung (Name, Logo, Installer macOS/Windows/Linux)
8. Test mit Schülern, Upstream-Pflege

## Commit-Konventionen
`docs:`, `build:`, `feat:`, `style:`, `chore:` – ein Thema pro Commit, Start jeweils geprüft.
