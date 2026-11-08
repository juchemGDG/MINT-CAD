# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: handgezeichnete Icons (24x24-Raster, 1.75 px Linie, abgerundet, Duotone).

Linienfarbe L (hell), Akzent A (blau) für das Wesentliche, R (rosé) für Entfernen/Randbedingungen.
Die Icons überschreiben beim Bauen die automatisch umgefärbten Originale gleichen Namens.
"""
import os

L = "#e2e8f0"
A = "#60a5fa"
R = "#fb7185"
G = "#4ade80"


def wrap(body):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" '
        'fill="none" stroke="%s" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">%s</svg>'
        % (L, body)
    )


def dot(x, y, c=A, r=1.9):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="none"/>' % (x, y, r, c)


def poly(points, fill="none", op=0.3, stroke=None, extra=""):
    pts = " ".join("%s,%s" % p for p in points)
    f = ' fill="%s" fill-opacity="%s"' % (fill, op) if fill != "none" else ' fill="none"'
    s = ' stroke="%s"' % stroke if stroke else ""
    return '<polygon points="%s"%s%s %s/>' % (pts, f, s, extra)


def path(d, fill="none", op=0.3, stroke=None, extra=""):
    f = ' fill="%s" fill-opacity="%s"' % (fill, op) if fill != "none" else ' fill="none"'
    s = ' stroke="%s"' % stroke if stroke else ""
    return '<path d="%s"%s%s %s/>' % (d, f, s, extra)


# ---- Isometrischer Block ---------------------------------------------------------------
TOP = [(12, 4), (20, 8.5), (12, 13), (4, 8.5)]
LEFT = [(4, 8.5), (12, 13), (12, 21), (4, 16.5)]
RIGHT = [(12, 13), (20, 8.5), (20, 16.5), (12, 21)]


def block(top=A, top_op=0.45, side=None, side_op=0.18, dashed=False):
    ex = 'stroke-dasharray="2 2"' if dashed else ""
    out = poly(LEFT, side or "none", side_op, extra=ex) + poly(RIGHT, side or "none", side_op, extra=ex)
    out += poly(TOP, top, top_op, extra=ex)
    return out


ICONS = {}


def add(name, body):
    ICONS[name] = wrap(body)


# ---- Part Design -----------------------------------------------------------------------
add("PartDesign_Body", block(A, 0.55, A, 0.2))
add("PartDesign_Pad", block(A, 0.6) + path("M12 4 V1.5 M9.7 3.7 L12 1.5 L14.3 3.7", stroke=A))
add(
    "PartDesign_Pocket",
    block("none")
    + poly([(12, 6.2), (16, 8.5), (12, 10.8), (8, 8.5)], R, 0.5, extra='stroke="%s"' % R),
)
add("PartDesign_Hole", block("none") + '<ellipse cx="12" cy="8.5" rx="3.6" ry="1.8" fill="%s" fill-opacity="0.5" stroke="%s"/>' % (R, R))
add(
    "PartDesign_Revolution",
    '<ellipse cx="12" cy="7" rx="6" ry="2.5" fill="%s" fill-opacity="0.45"/>' % A
    + '<path d="M6 7 V17 M18 7 V17 M6 17 A6 2.5 0 0 0 18 17"/>'
    + '<path d="M12 2 V22" stroke="%s" stroke-dasharray="1.5 2"/>' % A,
)
add(
    "PartDesign_Groove",
    '<ellipse cx="12" cy="7" rx="6" ry="2.5"/>'
    + '<path d="M6 7 V17 M18 7 V17 M6 17 A6 2.5 0 0 0 18 17"/>'
    + '<path d="M6 12 A6 2.5 0 0 0 18 12" stroke="%s" stroke-width="2.6"/>' % R,
)
add(
    "PartDesign_Fillet",
    path("M5 19 V10 Q5 5 10 5 H19 V19 Z", A, 0.25) + path("M5 10 Q5 5 10 5", stroke=A, extra='stroke-width="2.6"'),
)
add(
    "PartDesign_Chamfer",
    path("M5 19 V10 L10 5 H19 V19 Z", A, 0.25) + path("M5 10 L10 5", stroke=A, extra='stroke-width="2.6"'),
)
add(
    "PartDesign_LinearPattern",
    '<rect x="2.5" y="8" width="5.5" height="8" rx="1" fill="%s" fill-opacity="0.55"/>' % A
    + '<rect x="9.25" y="8" width="5.5" height="8" rx="1" stroke-dasharray="2 2" fill="%s" fill-opacity="0.2"/>' % A
    + '<rect x="16" y="8" width="5.5" height="8" rx="1" stroke-dasharray="2 2" fill="%s" fill-opacity="0.2"/>' % A,
)
add(
    "PartDesign_PolarPattern",
    '<circle cx="12" cy="12" r="7.5" stroke-dasharray="2 2.4"/>'
    + '<rect x="10" y="2.5" width="4" height="4" rx="1" fill="%s" fill-opacity="0.8" stroke="%s"/>' % (A, A)
    + '<rect x="15.8" y="13.6" width="4" height="4" rx="1" fill="%s" fill-opacity="0.45" stroke="%s"/>' % (A, A)
    + '<rect x="4.2" y="13.6" width="4" height="4" rx="1" fill="%s" fill-opacity="0.45" stroke="%s"/>' % (A, A),
)
add(
    "PartDesign_Mirrored",
    '<rect x="2.5" y="7" width="6" height="10" rx="1" fill="%s" fill-opacity="0.55"/>' % A
    + '<path d="M12 3 V21" stroke="%s" stroke-dasharray="2 2"/>' % R
    + '<rect x="15.5" y="7" width="6" height="10" rx="1" stroke-dasharray="2 2" fill="%s" fill-opacity="0.2"/>' % A,
)
add("PartDesign_AdditiveBox", block(A, 0.55, A, 0.3))
add("PartDesign_SubtractiveBox", block(R, 0.5, R, 0.22, dashed=True))
add(
    "PartDesign_AdditiveCylinder",
    '<ellipse cx="12" cy="6.5" rx="6" ry="2.5" fill="%s" fill-opacity="0.55"/>' % A
    + '<path d="M6 6.5 V17.5 M18 6.5 V17.5 M6 17.5 A6 2.5 0 0 0 18 17.5"/>',
)
add(
    "PartDesign_SubtractiveCylinder",
    '<ellipse cx="12" cy="6.5" rx="6" ry="2.5" fill="%s" fill-opacity="0.5" stroke-dasharray="2 2"/>' % R
    + '<path d="M6 6.5 V17.5 M18 6.5 V17.5 M6 17.5 A6 2.5 0 0 0 18 17.5" stroke-dasharray="2 2"/>',
)

# ---- Skizze ----------------------------------------------------------------------------
PLANE = [(3, 18), (7.5, 6.5), (21, 6.5), (16.5, 18)]
add(
    "Sketcher_NewSketch",
    poly(PLANE, A, 0.18) + path("M8 14.5 L11 10.5 L16 13 L18 9.5", stroke=A) + dot(8, 14.5, A, 1.5) + dot(18, 9.5, A, 1.5),
)
add(
    "Sketcher_EditSketch",
    poly(PLANE, A, 0.18) + path("M8 14.5 L11 10.5 L16 13 L18 9.5", stroke=A) + dot(8, 14.5, A, 1.5) + dot(18, 9.5, A, 1.5),
)

add("Sketcher_CreatePoint", dot(12, 12, A, 3) + '<circle cx="12" cy="12" r="7" stroke-dasharray="2 2.5"/>')
add("Sketcher_CreateLine", path("M5 19 L19 5") + dot(5, 19) + dot(19, 5))
add("Sketcher_CreatePolyline", path("M4 18 L9 7 L15 15 L20 5") + dot(4, 18) + dot(9, 7) + dot(15, 15) + dot(20, 5))
add("Sketcher_CreateArc", path("M5 18 A10 10 0 0 1 19 18") + dot(5, 18) + dot(19, 18) + dot(12, 18, L, 1.2))
add("Sketcher_Create3PointArc", path("M5 18 A10 10 0 0 1 19 18") + dot(5, 18) + dot(19, 18) + dot(12, 7.9))
add("Sketcher_CreateCircle", '<circle cx="12" cy="12" r="7.5"/>' + dot(12, 12) + path("M12 12 L17.3 6.7", stroke=A, extra='stroke-width="1.2"'))
add("Sketcher_Create3PointCircle", '<circle cx="12" cy="12" r="7.5"/>' + dot(12, 4.5) + dot(18.5, 15.75) + dot(5.5, 15.75))
add("Sketcher_CreateRectangle", '<rect x="4" y="6.5" width="16" height="11" rx="0.5"/>' + dot(4, 6.5) + dot(20, 17.5))
add("Sketcher_CreateRectangle_Center", '<rect x="4" y="6.5" width="16" height="11" rx="0.5"/>' + dot(12, 12) + dot(20, 17.5))
add("Sketcher_CreateOblong", '<rect x="3.5" y="6.5" width="17" height="11" rx="4"/>' + dot(6.5, 9.5, A, 1.5) + dot(17.5, 14.5, A, 1.5))
add("Sketcher_CreateSlot", '<rect x="3" y="8" width="18" height="8" rx="4"/>' + dot(7, 12) + dot(17, 12))
add("Sketcher_CreateArcSlot", path("M4.5 17 A10 10 0 0 1 19.5 17 L16.3 14 A5.6 5.6 0 0 0 7.7 14 Z") + dot(6, 15.5, A, 1.5) + dot(18, 15.5, A, 1.5))
add("Sketcher_CreateTriangle", poly([(12, 4.5), (20, 19), (4, 19)]) + dot(12, 4.5, A, 1.5) + dot(20, 19, A, 1.5) + dot(4, 19, A, 1.5))
add("Sketcher_CreateSquare", '<rect x="5" y="5" width="14" height="14"/>' + dot(5, 5, A, 1.5) + dot(19, 19, A, 1.5))
add("Sketcher_CreatePentagon", poly([(12, 3.5), (20.5, 9.7), (17.2, 19.5), (6.8, 19.5), (3.5, 9.7)]) + dot(12, 3.5, A, 1.5))
add("Sketcher_CreateHexagon", poly([(12, 3.5), (19.4, 7.75), (19.4, 16.25), (12, 20.5), (4.6, 16.25), (4.6, 7.75)]) + dot(12, 3.5, A, 1.5))
add("Sketcher_CreateHeptagon", poly([(12, 3.5), (18.8, 6.8), (20.5, 14.2), (15.8, 20.2), (8.2, 20.2), (3.5, 14.2), (5.2, 6.8)]) + dot(12, 3.5, A, 1.5))
add("Sketcher_CreateOctagon", poly([(8.5, 3.5), (15.5, 3.5), (20.5, 8.5), (20.5, 15.5), (15.5, 20.5), (8.5, 20.5), (3.5, 15.5), (3.5, 8.5)]) + dot(8.5, 3.5, A, 1.5))
add("Sketcher_CreateRegularPolygon", poly([(12, 3.5), (19.4, 7.75), (19.4, 16.25), (12, 20.5), (4.6, 16.25), (4.6, 7.75)]) + dot(12, 12, A, 1.8))
add(
    "Sketcher_CreateBSpline",
    path("M4 17 C7 4 12 4 12 12 S17 20 20 7")
    + path("M4 17 L8 6 L12 14 L16 18 L20 7", stroke=A, extra='stroke-width="1" stroke-dasharray="1.5 2"')
    + dot(4, 17, A, 1.4) + dot(20, 7, A, 1.4),
)
add("Sketcher_ToggleConstruction", path("M4 18 L20 6", extra='stroke-dasharray="3 3"') + dot(4, 18, L, 1.3) + dot(20, 6, L, 1.3))
add("Sketcher_CreateFillet", path("M5 4.5 V13 Q5 19 11 19 H19.5") + path("M5 13 Q5 19 11 19", stroke=A, extra='stroke-width="2.4"'))
add("Sketcher_CreateChamfer", path("M5 4.5 V13 L11 19 H19.5") + path("M5 13 L11 19", stroke=A, extra='stroke-width="2.4"'))
add(
    "Sketcher_Trimming",
    path("M3 12 H21")
    + path("M12 4 V20")
    + path("M12 12 H21", stroke=R, extra='stroke-width="2.6"'),
)
add("Sketcher_Extend", path("M3 12 H15") + path("M15 12 H20 M17.5 9.5 L20 12 L17.5 14.5", stroke=A) + path("M21 4 V20", extra='stroke-dasharray="2 2"'))
add("Sketcher_Split", path("M3 12 H21") + '<circle cx="12" cy="12" r="2.4" fill="%s" stroke="%s"/>' % (A, L) + path("M12 4 V8 M12 16 V20", stroke=A))

# ---- Randbedingungen -------------------------------------------------------------------
add("Constraint_Horizontal", path("M4 12 H20", extra='stroke-width="2.4"') + dot(4, 12, A, 2) + dot(20, 12, A, 2))
add("Constraint_Vertical", path("M12 4 V20", extra='stroke-width="2.4"') + dot(12, 4, A, 2) + dot(12, 20, A, 2))
add("Constraint_HorVer", path("M3 12 H11 M17 6 V18", extra='stroke-width="2.2"'))
add("Constraint_Parallel", path("M7 20 L14 4") + path("M13 20 L20 4"))
add("Constraint_Perpendicular", path("M12 4 V19 H20", extra='stroke-width="2.2"') + path("M12 15 H16 V19", stroke=A, extra='stroke-width="1.5"'))
add("Constraint_Tangent", '<circle cx="12" cy="10" r="6"/>' + path("M3 16 H21", stroke=A) + dot(12, 16, A, 1.8))
add("Constraint_EqualLength", path("M5 9 H19 M5 15 H19", extra='stroke-width="2.4"'))
add("Constraint_Symmetric", path("M12 3 V21", extra='stroke-dasharray="2 2"') + path("M4 12 L9 8 V16 Z M20 12 L15 8 V16 Z", fill=A, op=0.5))
add("Constraint_Coincident", '<circle cx="10" cy="12" r="4.5"/><circle cx="14" cy="12" r="4.5"/>' + dot(12, 12, A, 2))
add("Constraint_PointOnPoint", '<circle cx="10" cy="12" r="4.5"/><circle cx="14" cy="12" r="4.5"/>' + dot(12, 12, A, 2))
add("Constraint_PointOnObject", path("M3 17 L21 7") + dot(12, 12, A, 2.4) + '<circle cx="12" cy="12" r="5" stroke-dasharray="2 2"/>')
add("Constraint_Concentric", '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/>' + dot(12, 12, A, 1.6))
add("Constraint_Block", '<rect x="5" y="11" width="14" height="9" rx="1.5" fill="%s" fill-opacity="0.35"/>' % A + path("M8 11 V8 A4 4 0 0 1 16 8 V11"))
add("Constraint_Lock", '<rect x="5" y="11" width="14" height="9" rx="1.5" fill="%s" fill-opacity="0.35"/>' % A + path("M8 11 V8 A4 4 0 0 1 16 8 V11"))
add(
    "Constraint_Dimension",
    path("M5 6 V18 M19 6 V18", extra='stroke-width="1.4"')
    + path("M5 12 H19 M5 12 L8.5 9.5 M5 12 L8.5 14.5 M19 12 L15.5 9.5 M19 12 L15.5 14.5", stroke=A),
)
add("Constraint_Length", path("M5 6 V18 M19 6 V18", extra='stroke-width="1.4"') + path("M5 12 H19 M5 12 L8.5 9.5 M5 12 L8.5 14.5 M19 12 L15.5 9.5 M19 12 L15.5 14.5", stroke=A))
add("Constraint_HorizontalDistance", path("M5 6 V18 M19 6 V18", extra='stroke-width="1.4"') + path("M5 12 H19 M5 12 L8.5 9.5 M5 12 L8.5 14.5 M19 12 L15.5 9.5 M19 12 L15.5 14.5", stroke=A))
add("Constraint_VerticalDistance", path("M6 5 H18 M6 19 H18", extra='stroke-width="1.4"') + path("M12 5 V19 M12 5 L9.5 8.5 M12 5 L14.5 8.5 M12 19 L9.5 15.5 M12 19 L14.5 15.5", stroke=A))
add("Constraint_Radius", '<circle cx="12" cy="12" r="8.5"/>' + path("M12 12 L18 6", stroke=A) + dot(12, 12, A, 1.6) + path("M15.5 6 H18 V8.5", stroke=A, extra='stroke-width="1.4"'))
add("Constraint_Diameter", '<circle cx="12" cy="12" r="8.5"/>' + path("M5.9 18.1 L18.1 5.9", stroke=A) + path("M5.9 18.1 H9 M5.9 18.1 V15 M18.1 5.9 H15 M18.1 5.9 V9", stroke=A, extra='stroke-width="1.4"'))
add("Constraint_Radiam", '<circle cx="12" cy="12" r="8.5"/>' + path("M12 12 L18 6", stroke=A) + dot(12, 12, A, 1.6))
add("Constraint_InternalAngle", path("M4 19 H20") + path("M4 19 L16 6") + path("M10 19 A6 6 0 0 0 8.7 14.3", stroke=A))
add("Constraint_ExternalAngle", path("M4 19 H20") + path("M4 19 L16 6") + path("M10 19 A6 6 0 0 0 8.7 14.3", stroke=A))


# ======================= Teil 2: Standard, TechDraw, Draft, Assembly, FEM =====================
def rect(x, y, w, h, rx=0, fill="none", op=0.3, stroke=None, extra=""):
    f = ' fill="%s" fill-opacity="%s"' % (fill, op) if fill != "none" else ' fill="none"'
    s = ' stroke="%s"' % stroke if stroke else ""
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s"%s%s %s/>' % (x, y, w, h, rx, f, s, extra)


def circ(cx, cy, r, fill="none", op=0.3, stroke=None, extra=""):
    f = ' fill="%s" fill-opacity="%s"' % (fill, op) if fill != "none" else ' fill="none"'
    s = ' stroke="%s"' % stroke if stroke else ""
    return '<circle cx="%s" cy="%s" r="%s"%s%s %s/>' % (cx, cy, r, f, s, extra)


def scaled(body, tx, ty, k):
    return '<g transform="translate(%s %s) scale(%s)">%s</g>' % (tx, ty, k, body)


DASH = 'stroke-dasharray="2 2"'

# ---- Standard ----------------------------------------------------------------------------
PAGE = "M6 3 H14 L19 8 V21 H6 Z"
add("document-new", path(PAGE) + path("M14 3 V8 H19") + path("M12.5 12.5 V18.5 M9.5 15.5 H15.5", stroke=A))
add("document-open", path("M3 18.5 V6 H9 L11 8 H18 V11") + path("M3 18.5 L6 11 H21 L18 18.5 Z", A, 0.25))
add("document-save", path("M5 3 H16.5 L21 7.5 V21 H3 V5 A2 2 0 0 1 5 3 Z") + path("M7 3 V8 H15 V3") + rect(7, 14, 10, 7, 0.5, A, 0.35))
add("edit-undo", path("M9 14.5 L4 9.5 L9 4.5") + path("M4 9.5 H15 A5 5 0 0 1 15 19.5 H11", stroke=A))
add("edit-redo", path("M15 14.5 L20 9.5 L15 4.5") + path("M20 9.5 H9 A5 5 0 0 0 9 19.5 H13", stroke=A))
add("view-refresh", path("M20 11 A8 8 0 0 0 5.6 7") + path("M5 3 V7.5 H9.5") + path("M4 13 A8 8 0 0 0 18.4 17", stroke=A) + path("M19 21 V16.5 H14.5", stroke=A))
add("zoom-all", path("M4 9 V4 H9 M15 4 H20 V9 M20 15 V20 H15 M9 20 H4 V15") + rect(8.5, 8.5, 7, 7, 1, A, 0.45, A))
add("zoom-selection", circ(10.5, 10.5, 6.5) + path("M15.3 15.3 L21 21") + rect(8, 8, 5, 5, 0.5, A, 0.45, A))
add("view-axonometric", block(A, 0.4))
add("view-isometric", block(A, 0.4))
add("view-front", poly(TOP) + poly(RIGHT) + poly(LEFT, A, 0.55))
add("view-top", poly(LEFT) + poly(RIGHT) + poly(TOP, A, 0.55))
add("view-right", poly(TOP) + poly(LEFT) + poly(RIGHT, A, 0.55))
add("view-left", poly(TOP) + poly(RIGHT) + poly(LEFT, A, 0.55))
add("view-rear", poly(TOP) + poly(LEFT) + poly(RIGHT, A, 0.55))
add("view-bottom", poly(LEFT) + poly(RIGHT) + poly(TOP, "none") + path("M4 16.5 L12 21 L20 16.5", stroke=A, extra='stroke-width="2.6"'))
add("DrawStyleAsIs", block(A, 0.35, A, 0.35))
add("WhatsThis", circ(12, 12, 9) + path("M9.5 9.5 A2.6 2.6 0 1 1 12.6 12 C12 12.4 12 13 12 13.8", stroke=A) + dot(12, 17, A, 1.2))
add("umf-measurement", path("M3 16 L16 3 L21 8 L8 21 Z", A, 0.2) + path("M7 12.5 L9 14.5 M10 9.5 L12 11.5 M13 6.5 L15 8.5"))

# ---- TechDraw ------------------------------------------------------------------------------
PG = rect(4, 4, 16, 16, 1.5)
add("actions/TechDraw_PageDefault", rect(3, 5, 18, 14, 1) + rect(5.5, 7.5, 13, 8, 0, A, 0.2, A) + path("M5.5 15.5 H18.5 M12 15.5 V18"))
add("actions/TechDraw_PageTemplate", rect(3, 5, 18, 14, 1) + rect(5.5, 7.5, 13, 8, 0) + path("M5.5 15.5 H18.5 M12 15.5 V18 M9 15.5 V18", stroke=A))
add("actions/TechDraw_View", rect(3.5, 10.5, 10, 9, 0.5, A, 0.35, A) + rect(3.5, 4, 10, 4.5, 0.5) + rect(15.5, 10.5, 5, 9, 0.5))
add("actions/TechDraw_DetailView", circ(8.5, 8.5, 4.5, extra=DASH, stroke=A) + circ(15.5, 15.5, 5.5) + path("M11.8 11.8 L10.5 10.5", stroke=A))
add("actions/TechDraw_SectionView", rect(4, 4, 16, 16, 1) + path("M7 17 L17 7 M7 12 L12 7 M12 17 L17 12", stroke=A) + path("M2 12 H6 M18 12 H22", stroke=R, extra='stroke-width="2"'))
add("TechDraw_Balloon", circ(9, 9, 5.5, A, 0.25) + path("M13 13 L20.5 20.5") + dot(20.5, 20.5, A, 1.6))
add("actions/TechDraw_ExportPageSVG", path(PAGE) + path("M14 3 V8 H19") + path("M12.5 12 V19 M9.5 16 L12.5 19 L15.5 16", stroke=A))
add("actions/TechDraw_ExportPageDXF", path(PAGE) + path("M14 3 V8 H19") + path("M12.5 12 V19 M9.5 16 L12.5 19 L15.5 16", stroke=R))
add("actions/TechDraw_FillTemplateFields", rect(3.5, 5, 17, 14, 1) + path("M7 9.5 H11 M7 13 H14", stroke=A) + path("M15 18 L16.2 15 L21 10.2 L23 12.2 L18.2 17 Z", extra='transform="translate(-2 1)"'))
add("actions/TechDraw_RedrawPage", rect(3.5, 5, 17, 14, 1) + path("M16 12 A4 4 0 1 1 14.8 9.2", stroke=A) + path("M16 8 V10.5 H13.5", stroke=A))
add("actions/TechDraw_PrintAll", path("M7 8 V3 H17 V8") + rect(3, 8, 18, 9, 1.5) + rect(7, 14, 10, 7, 0, A, 0.3, A) + dot(17.5, 11.5, A, 1))
add("actions/TechDraw_ToggleFrame", rect(3.5, 5.5, 17, 13, 1, extra=DASH) + path("M3.5 9 H6 M18 5.5 V8", stroke=A))
add("actions/TechDraw_Hatch", rect(4, 4, 16, 16, 1.5) + path("M7 17 L17 7 M4.5 12.5 L12.5 4.5 M11.5 19.5 L19.5 11.5", stroke=A))
add("actions/TechDraw_GeometricHatch", rect(4, 4, 16, 16, 1.5) + path("M7 17 L17 7 M4.5 12.5 L12.5 4.5 M11.5 19.5 L19.5 11.5", stroke=A))
add("actions/TechDraw_Annotation", path("M4 5 H20 V16 H11 L7 20 V16 H4 Z") + path("M8 9 H16 M8 12.2 H13", stroke=A))
add("actions/TechDraw_LeaderLine", path("M4 19 L11 10 H20") + path("M4 19 L4.5 15.2 M4 19 L7.8 18.5", stroke=A, extra='stroke-width="2"'))
add("actions/TechDraw_Line2Points", path("M5 19 L19 5") + dot(5, 19) + dot(19, 5))

# ---- Draft -----------------------------------------------------------------------------------
add("Draft_Line", path("M5 19 L19 5") + dot(5, 19) + dot(19, 5))
add("Draft_Wire", path("M4 18 L9 7 L15 15 L20 5") + dot(4, 18) + dot(9, 7) + dot(15, 15) + dot(20, 5))
add("Draft_Fillet", path("M5 4.5 V13 Q5 19 11 19 H19.5") + path("M5 13 Q5 19 11 19", stroke=A, extra='stroke-width="2.4"'))
add("Draft_Circle", circ(12, 12, 7.5) + dot(12, 12) + path("M12 12 L17.3 6.7", stroke=A, extra='stroke-width="1.2"'))
add("Draft_Ellipse", '<ellipse cx="12" cy="12" rx="9" ry="5.5"/>' + dot(12, 12))
add("Draft_Rectangle", rect(4, 6.5, 16, 11, 0.5) + dot(4, 6.5) + dot(20, 17.5))
add("Draft_Polygon", poly([(12, 3.5), (19.4, 7.75), (19.4, 16.25), (12, 20.5), (4.6, 16.25), (4.6, 7.75)]) + dot(12, 12, A, 1.8))
add("Draft_Point", dot(12, 12, A, 3) + circ(12, 12, 7, extra='stroke-dasharray="2 2.5"'))
add("Draft_Text", path("M5 19 L12 5 L19 19") + path("M8 14 H16", stroke=A))
add("Draft_Label", path("M4 18 L11 10 H20") + dot(4, 18, A, 1.8) + path("M12 6 H20", stroke=A))
add("Draft_Dimension", path("M5 6 V18 M19 6 V18", extra='stroke-width="1.4"') + path("M5 12 H19 M5 12 L8.5 9.5 M5 12 L8.5 14.5 M19 12 L15.5 9.5 M19 12 L15.5 14.5", stroke=A))
add("Draft_Move", path("M12 3 V21 M3 12 H21 M9 6 L12 3 L15 6 M9 18 L12 21 L15 18 M6 9 L3 12 L6 15 M18 9 L21 12 L18 15", stroke=A))
add("Draft_Rotate", path("M20 12 A8 8 0 1 1 15.5 5") + path("M15 2 L15.5 5.5 L19 5", stroke=A) + dot(12, 12, A, 1.8))
add("Draft_Scale", rect(4, 11, 9, 9, 1, A, 0.25) + rect(4, 11, 9, 9, 1, extra=DASH) + path("M13 11 L20 4 M15.5 4 H20 V8.5", stroke=A))
add("Draft_Mirror", rect(2.5, 7, 6, 10, 1, A, 0.5, A) + path("M12 3 V21", stroke=R, extra=DASH) + rect(15.5, 7, 6, 10, 1, extra=DASH))
add("Draft_Offset", rect(3.5, 3.5, 17, 17, 3) + rect(8, 8, 8, 8, 1.5, A, 0.35, A))
add("Draft_Trimex", path("M3 12 H21") + path("M12 4 V20") + path("M12 12 H21", stroke=R, extra='stroke-width="2.6"'))
add("Draft_Array", "".join(rect(3 + i * 6.5, 3 + j * 6.5, 5, 5, 1, A, 0.35 if (i, j) != (0, 0) else 0.7, A) for i in range(3) for j in range(3)))
add("Draft_Edit", path("M4 20 L5 15.5 L16 4.5 L19.5 8 L8.5 19 Z") + path("M13.5 7 L17 10.5", stroke=A))
add("Draft_Draft2Sketch", rect(3, 6, 7, 12, 1) + path("M11.5 12 H17 M15 9.5 L17.5 12 L15 14.5", stroke=A) + circ(19, 12, 2.5, A, 0.5, A))
add("Draft_Grid", path("M4 4 H20 V20 H4 Z M4 9.3 H20 M4 14.6 H20 M9.3 4 V20 M14.6 4 V20", extra='stroke-width="1.3"') + dot(9.3, 9.3, A, 1.5))
add("Draft_LayerManager", poly([(12, 3.5), (21, 8), (12, 12.5), (3, 8)], A, 0.35) + path("M3 12 L12 16.5 L21 12 M3 16 L12 20.5 L21 16"))
add("Draft_AddToLayer", poly([(12, 3.5), (21, 8), (12, 12.5), (3, 8)], A, 0.35) + path("M3 12 L12 16.5 L21 12 M3 16 L12 20.5 L21 16"))
add("Draft_SwitchMode", rect(4, 4, 16, 16, 1.5) + path("M8 12 H16 M12 8 V16", stroke=A))

# ---- Assembly -------------------------------------------------------------------------------
def mini_block(tx, ty, k, top=A, op=0.5):
    return scaled(block(top, op, top, 0.18), tx, ty, k)


add("Geoassembly", mini_block(0, 7, 0.62, A, 0.55) + mini_block(9.5, 0, 0.62, "none", 0.0))
add("Assembly_CreateAssembly", mini_block(0, 7, 0.62, A, 0.55) + mini_block(9.5, 0, 0.62, "none", 0.0))
add("Assembly_InsertLink", block("none") + path("M16 3 V9 M13 6 H19", stroke=A))
add("Assembly_SolveAssembly", block("none") + path("M7 21 L10 18 L16 24", stroke=A, extra='transform="translate(5 -9) scale(1)"'))
add("Assembly_ExplodedView", mini_block(5, -2, 0.55, A, 0.5) + mini_block(5, 8, 0.55, A, 0.3) + path("M12 9 V11.5", stroke=L, extra=DASH))
add("Assembly_BillOfMaterials", path("M9 6 H20 M9 12 H20 M9 18 H20") + dot(4.8, 6, A, 1.6) + dot(4.8, 12, A, 1.6) + dot(4.8, 18, A, 1.6))
add("Assembly_ToggleGrounded", rect(6, 4, 12, 8, 1, A, 0.4) + path("M3 15 H21 M5 21 L8 15 M10 21 L13 15 M15 21 L18 15"))
add("Assembly_CreateJointFixed", rect(3.5, 7, 8, 10, 1) + rect(12.5, 7, 8, 10, 1, A, 0.35) + dot(12, 12, A, 1.8))
add("Assembly_CreateJointRevolute", circ(12, 12, 4.5) + dot(12, 12, A, 1.8) + path("M20 12 A8 8 0 0 0 12 4", stroke=A) + path("M10 2 L12.3 4 L10.2 6.5", stroke=A))
add("Assembly_CreateJointCylindrical", path("M7 6 V18 M17 6 V18") + '<ellipse cx="12" cy="6" rx="5" ry="2"/><path d="M7 18 A5 2 0 0 0 17 18"/>' + path("M12 3 V21", stroke=A, extra=DASH))
add("Assembly_CreateJointSlider", path("M3 18 H21") + rect(8, 8, 8, 8, 1, A, 0.4, A) + path("M3 12 H6 M18 12 H21 M19 10 L21 12 L19 14 M5 10 L3 12 L5 14", stroke=L))
add("Assembly_CreateJointBall", circ(12, 12, 8) + '<ellipse cx="12" cy="12" rx="8" ry="3" stroke-dasharray="2 2"/>' + dot(12, 12, A, 2.2))
add("Assembly_CreateJointDistance", path("M5 4 V20 M19 4 V20") + path("M5 12 H19 M5 12 L8.5 9.5 M5 12 L8.5 14.5 M19 12 L15.5 9.5 M19 12 L15.5 14.5", stroke=A, extra='stroke-width="1.5"'))
add("Assembly_CreateJointParallel", path("M7 20 L14 4") + path("M13 20 L20 4"))
add("Assembly_CreateJointPerpendicular", path("M12 4 V19 H20", extra='stroke-width="2.2"') + path("M12 15 H16 V19", stroke=A, extra='stroke-width="1.5"'))
add("Assembly_CreateJointAngle", path("M4 19 H20") + path("M4 19 L16 6") + path("M10 19 A6 6 0 0 0 8.7 14.3", stroke=A))

# ---- FEM ---------------------------------------------------------------------------------------
def mesh_tri(extra=""):
    return (poly([(3, 18), (12, 4), (21, 18)], A, 0.18) + path("M7.5 11 H16.5 M3 18 L12 11 L21 18 M12 4 V11 M7.5 11 L12 18 L16.5 11", extra='stroke-width="1.2"'))


add("FEM_Analysis", mesh_tri())
add("FEM_MaterialSolid", block(A, 0.35, A, 0.25) + dot(10, 15.5, L, 0.9) + dot(15, 14, L, 0.9))
add("FEM_ElementGeometry1D", path("M5 5 H19 M12 5 V19 M5 19 H19", extra='stroke-width="2.2"') + path("M3 12 H21", stroke=A, extra=DASH))
add("FEM_ElementGeometry2D", poly([(3, 17), (8, 6), (21, 6), (16, 17)], A, 0.3) + path("M3 17 L3 20 M16 17 V20 M8 6 V9", extra='stroke-width="1.2"'))
add("FEM_ConstraintFixed", rect(6, 3, 12, 9, 1, A, 0.35) + path("M3 15 H21 M5 21 L8 15 M10 21 L13 15 M15 21 L18 15") + path("M12 12 V15", stroke=L))
add("FEM_ConstraintDisplacement", rect(4, 8, 9, 9, 1, A, 0.35) + rect(4, 8, 9, 9, 1, extra=DASH, stroke=L) + path("M15 12.5 H21 M18.5 10 L21 12.5 L18.5 15", stroke=A))
add("FEM_ConstraintContact", rect(3, 4, 18, 7, 1, A, 0.3) + rect(3, 13, 18, 7, 1, A, 0.3) + path("M12 8 V16 M9.5 13.5 L12 16 L14.5 13.5", stroke=R, extra='stroke-width="1.6"'))
add("FEM_ConstraintForce", rect(4, 14, 16, 6, 1, A, 0.35) + path("M12 3 V13 M8.5 9.5 L12 13 L15.5 9.5", stroke=R, extra='stroke-width="2.2"'))
add("FEM_ConstraintPressure", rect(4, 15, 16, 5, 1, A, 0.35) + path("M7 4 V13 M12 4 V13 M17 4 V13 M5 10 L7 13 L9 10 M10 10 L12 13 L14 10 M15 10 L17 13 L19 10", stroke=R, extra='stroke-width="1.6"'))
add("FEM_ConstraintSelfWeight", rect(6, 4, 12, 9, 1, A, 0.35) + path("M12 15 V21 M9 18.5 L12 21.5 L15 18.5", stroke=R, extra='stroke-width="2"'))
add("FEM_MeshGmshFromShape", mesh_tri())
add("FEM_MeshNetgenFromShape", poly([(3, 12), (12, 4), (21, 12), (12, 20)], A, 0.18) + path("M3 12 H21 M12 4 V20 M7.5 8 L16.5 16 M16.5 8 L7.5 16", extra='stroke-width="1.2"'))
add("FEM_SolverStandard", circ(12, 12, 3.2, A, 0.4, A) + path("M12 2.5 V6 M12 18 V21.5 M2.5 12 H6 M18 12 H21.5 M5.3 5.3 L7.8 7.8 M16.2 16.2 L18.7 18.7 M5.3 18.7 L7.8 16.2 M16.2 7.8 L18.7 5.3") + circ(12, 12, 6.5))
add("FEM_SolverControl", path("M4 7 H20 M4 12 H20 M4 17 H20") + dot(9, 7, A, 2.4) + dot(15, 12, A, 2.4) + dot(8, 17, A, 2.4))
add("FEM_SolverRun", circ(12, 12, 9) + poly([(10, 8), (16, 12), (10, 16)], A, 0.8, A))
add("FEM_ResultShow", rect(3, 5, 4, 14, 1, "#4ade80", 0.7, "#4ade80") + rect(9.5, 5, 4, 14, 1, "#fbbf24", 0.7, "#fbbf24") + rect(16, 5, 4, 14, 1, R, 0.7, R))
add("FEM_ResultsPurge", path("M4 7 H20 M9 7 V4 H15 V7 M6 7 L7 20 H17 L18 7 M10 11 V16 M14 11 V16"))
add("FEM_PostPipelineFromResult", rect(3, 9, 5, 6, 1, A, 0.4, A) + rect(16, 9, 5, 6, 1) + path("M8 12 H16 M13.5 9.5 L16 12 L13.5 14.5", stroke=A))
add("FEM_PostFilterWarp", path("M3 7 Q8 3 12 7 T21 7 M3 12 Q8 8 12 12 T21 12 M3 17 Q8 13 12 17 T21 17", extra='stroke-width="1.4"') + path("M3 20 H21", stroke=A, extra=DASH))
add("FEM_PostFilterContours", circ(12, 12, 8.5) + circ(12, 12, 5.5, stroke=A) + circ(12, 12, 2.5, A, 0.5, A))
add("FEM_PostFilterDataAlongLine", path("M3 20 H21 M3 20 V4") + path("M5 16 L9 10 L13 13 L19 5", stroke=A) + dot(9, 10, A, 1.4) + dot(13, 13, A, 1.4))


def write(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    # Programmsymbol: auch dort, wo FreeCAD intern das Symbol "freecad" verwendet
    logo = os.path.join(os.path.dirname(__file__), "..", "..", "src", "Gui", "Icons", "mintcad.svg")
    with open(logo, encoding="utf-8") as fh:
        ICONS["freecad"] = fh.read()
    for name, svg in ICONS.items():
        target = os.path.join(out_dir, name + ".svg")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(svg)
    return len(ICONS)


if __name__ == "__main__":
    import sys

    print(write(sys.argv[1]), "handgezeichnete Icons")
