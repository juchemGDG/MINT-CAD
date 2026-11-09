#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: erzeugt THIRD-PARTY-PACKAGES.md (alle Fremdpakete mit Version und Lizenz) aus conda-meta.

Aufruf (aus dem Quellordner):  python3 -I tools/mintcad/make_third_party.py [Programmordner-Resources]
Mit Programmordner (z. B. build/mintcad-dist/MINT-CAD.app/Contents/Resources) werden nur Pakete aufgenommen,
von denen Dateien im Paket liegen. Stand der Daten: Umgebung .pixi/envs/default (macOS arm64).
"""
import glob, json, os, sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
env = os.path.join(root, ".pixi", "envs", "default")
res = sys.argv[1] if len(sys.argv) > 1 else None
rows = []
for f in glob.glob(os.path.join(env, "conda-meta", "*.json")):
    d = json.load(open(f, encoding="utf-8"))
    files = [x for x in d.get("files", []) if not x.endswith("/")]
    if res and not any(os.path.lexists(os.path.join(res, x)) for x in files):
        continue
    rows.append((d["name"], d["version"], d.get("license") or "unbekannt"))
rows.sort()
out = ["# Enthaltene Fremdpakete (automatisch erzeugt)", "",
       "%d Pakete aus conda-forge (und dem FreeCAD-Kanal) mit Version und Lizenz laut Paketangaben. "
       "Quellcode jedes Pakets: `https://github.com/conda-forge/<Paketname>-feedstock` (Verweis auf die Originalquellen) "
       "oder über https://anaconda.org/conda-forge/<Paketname>. Erzeugt mit `tools/mintcad/make_third_party.py`." % len(rows), "",
       "| Paket | Version | Lizenz |", "|---|---|---|"]
out += ["| %s | %s | %s |" % r for r in rows]
target = os.path.join(root, "THIRD-PARTY-PACKAGES.md")
open(target, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(rows), "Pakete ->", target)
