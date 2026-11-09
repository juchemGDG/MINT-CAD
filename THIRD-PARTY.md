# Fremdsoftware in MINT-CAD

MINT-CAD ist eine veränderte Fassung von **FreeCAD** (© 2001–2026 FreeCAD Team und Mitwirkende, https://www.freecad.org)
unter der **GNU Lesser General Public License 2.1 oder neuer** (Datei `LICENSE`). Quellcode von MINT-CAD:
https://github.com/juchemGDG/MINT-CAD (Branch `main`; das Tag `1.1.4` ist die unveränderte FreeCAD-Basis).

Das fertige Programmpaket (DMG, Installer, AppImage) enthält zusätzlich freie Software anderer Autoren.
Jedes Teil gilt unter seiner eigenen Lizenz; MINT-CAD ändert daran nichts. Die vollständige Liste mit Versionen und Lizenzen:
[THIRD-PARTY-PACKAGES.md](THIRD-PARTY-PACKAGES.md). Die wichtigsten Teile:

| Programm / Bibliothek | Aufgabe | Lizenz |
|---|---|---|
| Qt 6, PySide6 | Oberfläche | LGPL-3.0 |
| OpenCASCADE (OCCT) | Geometrie-Kern | LGPL-2.1 (mit OCCT-Ausnahme) |
| SMESH | Netzerzeugung | LGPL-2.1+ |
| Coin3D, pivy | 3D-Ansicht | BSD-3-Clause |
| Python 3.11 und Standardbibliothek | Skriptsprache | Python-2.0 (PSF) |
| NumPy, SciPy, pandas, matplotlib, SymPy | Berechnungen | BSD-3-Clause / PSF |
| VTK, HDF5, Boost, Eigen, Xerces-C, yaml-cpp, OpenSSL u. a. | Bibliotheken | BSD, MIT, Apache-2.0, BSL, MPL-2.0 |
| **CalculiX** (`ccx`) | FEM-Berechnung | **GPL-2.0+** |
| **Gmsh** | Netzgenerierung für FEM | **GPL-2.0+** |
| Graphviz | Diagramme | EPL-1.0 |
| osifont (`osifont-lgpl3fe.ttf`) | Normschrift für Zeichnungen | GPL/LGPL mit Schrift-Ausnahme, siehe `data/examples/osifont.license` |

## Hinweise
- **CalculiX und Gmsh** laufen als eigene Programme neben MINT-CAD und stehen unter der GPL. Ihren Quellcode gibt es bei den Projekten
  (https://www.calculix.de, https://gmsh.info) und über die conda-forge-Rezepte (`calculix-feedstock`, `gmsh-feedstock`).
  Auf Anfrage an den Betreiber dieses Repositories stellen wir den Quellcode der in einem Paket enthaltenen Version bereit.
- Die Pakete stammen unverändert aus **conda-forge** (https://conda-forge.org). Jedes Paket verweist in seinem Rezept
  (`https://github.com/conda-forge/<Paketname>-feedstock`) auf die Originalquellen.
- Das Programmpaket enthält aus technischen Gründen einige weitere Pakete der Build-Umgebung (z. B. FFmpeg, Git, SWIG),
  die MINT-CAD nicht benötigt; sie sind in THIRD-PARTY-PACKAGES.md mit aufgeführt.
- Dank an das FreeCAD-Projekt und alle Mitwirkenden. MINT-CAD ist **kein** offizielles FreeCAD-Produkt;
  der Name FreeCAD gehört dem FreeCAD-Projekt.
- Alle Software wird ohne Gewährleistung bereitgestellt (siehe Lizenztexte).
