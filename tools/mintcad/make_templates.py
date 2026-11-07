#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: erzeugt die Zeichnungsvorlagen (Rahmen nach DIN EN ISO 5457, vereinfachtes Schriftfeld).

Aufruf: python3 tools/mintcad/make_templates.py src/Mod/TechDraw/Templates/MINT-CAD
Die Felder sind für TechDraw („Vorlagenfelder ausfüllen“) bearbeitbar (freecad:editable).
"""
import os
import sys

FONT = "osifont,'Open Sans',sans-serif"

# Schriftfeld 180 x 36 mm, unten rechts im Rahmen. (Name, Beschriftung, x0, x1, y0, y1, editable, Autofill)
# Koordinaten relativ zur rechten unteren Rahmenecke; y nach unten positiv gerechnet von der Oberkante des Feldes.
CELLS = [
    ("title", "Benennung", -180, -60, -36, -24, "title", "title"),
    ("sheet_number", "Blatt", -60, -30, -36, -24, "sheet_number", "sheet"),
    ("scale", "Maßstab", -30, 0, -36, -24, "scale", "scale"),
    ("part_material", "Werkstoff", -180, -60, -24, -12, "part_material", None),
    ("general_tolerances", "Allgemeintoleranz", -60, 0, -24, -12, "general_tolerances", None),
    ("creator", "Name", -180, -100, -12, 0, "creator", "author"),
    ("class", "Klasse", -100, -60, -12, 0, "class", None),
    ("date_of_issue", "Datum", -60, 0, -12, 0, "date_of_issue", "date"),
]
DEFAULTS = {
    "title": "Benennung",
    "sheet_number": "1 / 1",
    "scale": "1 : 1",
    "part_material": "S235JR",
    "general_tolerances": "ISO 2768-m",
    "creator": "",
    "class": "",
    "date_of_issue": "TT.MM.JJJJ",
}


def sheet(w, h, name):
    left, other = 20.0, 10.0
    x0, y0, x1, y1 = left, other, w - other, h - other
    out = []
    out.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    out.append(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:freecad="https://www.freecad.org/wiki/index.php?title=Svg_Namespace" '
        'width="%gmm" height="%gmm" viewBox="0 0 %g %g" version="1.1">' % (w, h, w, h)
    )
    out.append("  <title>MINT-CAD %s</title>" % name)
    # Blattrand (dünn) und Zeichenrahmen (0,7 mm)
    out.append('  <rect x="0" y="0" width="%g" height="%g" style="fill:none;stroke:#000000;stroke-width:0.25"/>' % (w, h))
    out.append(
        '  <rect id="frame" x="%g" y="%g" width="%g" height="%g" style="fill:none;stroke:#000000;stroke-width:0.7"/>'
        % (x0, y0, x1 - x0, y1 - y0)
    )
    # Mittenmarken
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    marks = [(cx, 5, cx, 10), (cx, h - 10, cx, h - 5), (15, cy, 20, cy), (w - 10, cy, w - 5, cy)]
    out.append('  <g style="stroke:#000000;stroke-width:0.5">')
    for a, b, c, d in marks:
        out.append('    <line x1="%g" y1="%g" x2="%g" y2="%g"/>' % (a, b, c, d))
    out.append("  </g>")
    # Schriftfeld
    ox, oy = x1, y1
    out.append('  <g id="title_block" transform="translate(%g %g)" style="fill:none;stroke:#000000;stroke-width:0.35">' % (ox, oy))
    out.append('    <rect x="-180" y="-36" width="180" height="36" style="stroke-width:0.7"/>')
    # Trennlinien
    out.append('    <path d="M -180,-24 H 0 M -180,-12 H 0"/>')
    out.append('    <path d="M -60,-36 V -12 M -30,-36 V -24 M -100,-12 V 0 M -60,-12 V 0"/>')
    out.append("  </g>")
    # Beschriftungen und Felder
    out.append('  <g id="title_block_labels" transform="translate(%g %g)" style="font-size:2.2px;font-family:%s;fill:#444444;stroke:none">' % (ox, oy, FONT))
    for cname, label, cx0, cx1, cy0, cy1, ed, auto in CELLS:
        out.append('    <text x="%g" y="%g">%s</text>' % (cx0 + 1.2, cy0 + 3.2, label))
    out.append("  </g>")
    out.append('  <g id="title_block_data_fields" transform="translate(%g %g)" style="font-size:5px;font-family:%s;fill:#000000;stroke:none">' % (ox, oy, FONT))
    for cname, label, cx0, cx1, cy0, cy1, ed, auto in CELLS:
        attrs = 'freecad:editable="%s"' % ed
        if auto:
            attrs += ' freecad:autofill="%s"' % auto
        out.append(
            '    <text id="%s_data_field" x="%g" y="%g" %s><tspan>%s</tspan></text>'
            % (cname, cx0 + 2.0, cy1 - 3.0, attrs, DEFAULTS[cname])
        )
    out.append("  </g>")
    # Projektionssymbol (1. Projektionsmethode) über dem Schriftfeld, rechts
    out.append('  <g id="projection_symbol" transform="translate(%g %g)" style="fill:none;stroke:#000000;stroke-width:0.4">' % (ox, oy))
    out.append('    <path d="m -22,-48 -9,2.5 v 5 l 9,2.5 z"/>')
    out.append('    <circle cx="-12" cy="-43.5" r="2.5"/><circle cx="-12" cy="-43.5" r="5"/>')
    out.append("  </g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    for fname, w, h, name in (
        ("MINTCAD_A4_Querformat.svg", 297, 210, "A4 Querformat"),
        ("MINTCAD_A4_Hochformat.svg", 210, 297, "A4 Hochformat"),
        ("MINTCAD_A3_Querformat.svg", 420, 297, "A3 Querformat"),
    ):
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as fh:
            fh.write(sheet(w, h, name))
        print("erzeugt:", fname)


if __name__ == "__main__":
    main()
