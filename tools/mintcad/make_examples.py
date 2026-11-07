# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: erzeugt die Schulbeispiele (Skizze -> Körper -> technische Zeichnung).

Aufruf (aus dem Quellordner):
    MINTCAD_OUT=data/examples build/release/bin/FreeCADCmd tools/mintcad/make_examples.py
"""
import math
import os
import zipfile

import FreeCAD as App
import Part
import Sketcher

OUT = os.environ.get("MINTCAD_OUT", "data/examples")
TEMPLATE = os.path.join(App.getResourceDir(), "Mod/TechDraw/Templates/MINT-CAD/MINTCAD_A4_Querformat.svg")
V = App.Vector


# ---------------------------------------------------------------- Hilfsfunktionen
def origin_feature(body, role):
    for f in body.Origin.OriginFeatures:
        if f.Role == role:
            return f
    raise KeyError(role)


def new_sketch(body, name, plane_role, offset=None):
    sk = body.newObject("Sketcher::SketchObject", name)
    sk.AttachmentSupport = (origin_feature(body, plane_role), [""])
    sk.MapMode = "FlatFace"
    if offset is not None:
        sk.AttachmentOffset = App.Placement(offset, App.Rotation())
    return sk


def try_add(sk, constraint):
    """Fügt eine Randbedingung nur hinzu, wenn sie nicht überbestimmt."""
    idx = sk.addConstraint(constraint)
    if sk.solve() != 0 or sk.RedundantConstraints or sk.ConflictingConstraints:
        sk.delConstraint(idx)
        return False
    return True


def polygon(sk, pts):
    """Geschlossener Linienzug mit Koinzident-, Waagerecht-/Senkrecht- und Maßbedingungen."""
    n = len(pts)
    for i in range(n):
        sk.addGeometry(Part.LineSegment(V(*pts[i], 0), V(*pts[(i + 1) % n], 0)), False)
    for i in range(n):
        sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % n, 1))
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if abs(y1 - y0) < 1e-9:
            sk.addConstraint(Sketcher.Constraint("Horizontal", i))
        elif abs(x1 - x0) < 1e-9:
            sk.addConstraint(Sketcher.Constraint("Vertical", i))
    sk.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1)) if pts[0] == (0, 0) else None
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if abs(y1 - y0) < 1e-9 and abs(x1 - x0) > 1e-9:
            a, b = (1, 2) if x1 > x0 else (2, 1)
            try_add(sk, Sketcher.Constraint("DistanceX", i, a, i, b, abs(x1 - x0)))
        elif abs(x1 - x0) < 1e-9 and abs(y1 - y0) > 1e-9:
            a, b = (1, 2) if y1 > y0 else (2, 1)
            try_add(sk, Sketcher.Constraint("DistanceY", i, a, i, b, abs(y1 - y0)))
    return sk


def circles(sk, centers, radius):
    first = None
    for c in centers:
        g = sk.addGeometry(Part.Circle(V(c[0], c[1], 0), V(0, 0, 1), radius), False)
        if first is None:
            first = g
            sk.addConstraint(Sketcher.Constraint("Radius", g, radius))
        else:
            sk.addConstraint(Sketcher.Constraint("Equal", first, g))
        try_add(sk, Sketcher.Constraint("DistanceX", -1, 1, g, 3, c[0]))
        try_add(sk, Sketcher.Constraint("DistanceY", -1, 1, g, 3, c[1]))
    return sk


def pad(body, sk, length, name="Pad"):
    p = body.newObject("PartDesign::Pad", name)
    p.Profile = sk
    p.Length = length
    sk.Visibility = False
    return p


def pocket_through(body, sk, name="Bohrung"):
    p = body.newObject("PartDesign::Pocket", name)
    p.Profile = sk
    p.Type = 1  # ThroughAll
    p.SideType = "Symmetric"
    sk.Visibility = False
    return p


# ---------------------------------------------------------------- Vorschaubild
def thumbnail(shape, path, size=256):
    """Einfache Software-Darstellung (Z-Puffer, flache Schattierung, Kanten) in Isometrie."""
    import numpy as np
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QGuiApplication, QImage

    QGuiApplication.instance() or QGuiApplication([])
    cam = np.array([1.0, -1.0, 1.0])
    cam /= np.linalg.norm(cam)
    right = np.array([1.0, 1.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.array([-1.0, 1.0, 2.0])
    up /= np.linalg.norm(up)
    light = np.array([0.35, -0.6, 0.75])
    light /= np.linalg.norm(light)

    tris = []  # (face_id, 3x3-Punkte)
    for fid, face in enumerate(shape.Faces):
        verts, ts = face.tessellate(0.1)
        for a, b, c in ts:
            tris.append((fid, np.array([[*verts[a]], [*verts[b]], [*verts[c]]])))
    allp = np.vstack([t[1] for t in tris])
    sx, sy = allp @ right, allp @ up
    S = size * 2  # doppelt rendern, dann verkleinern (Kantenglättung)
    k = S * 0.80 / max(sx.max() - sx.min(), sy.max() - sy.min())
    ox = S / 2 - k * (sx.max() + sx.min()) / 2
    oy = S / 2 + k * (sy.max() + sy.min()) / 2

    zbuf = np.full((S, S), -np.inf)
    ids = np.full((S, S), -1, dtype=np.int32)
    shade = np.zeros((S, S))
    for fid, p in tris:
        n = np.cross(p[1] - p[0], p[2] - p[0])
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        n /= ln
        if n @ cam < 0:
            n = -n
        sh = 0.30 + 0.70 * max(0.0, n @ light)
        xs = ox + k * (p @ right)
        ys = oy - k * (p @ up)
        zs = p @ cam
        x0, x1 = int(max(0, np.floor(xs.min()))), int(min(S - 1, np.ceil(xs.max())))
        y0, y1 = int(max(0, np.floor(ys.min()))), int(min(S - 1, np.ceil(ys.max())))
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(d) < 1e-12:
            continue
        w0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
        w1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
        sub = zbuf[y0 : y1 + 1, x0 : x1 + 1]
        upd = inside & (z > sub)
        sub[upd] = z[upd]
        ids[y0 : y1 + 1, x0 : x1 + 1][upd] = fid
        shade[y0 : y1 + 1, x0 : x1 + 1][upd] = sh

    lo, hi = np.array([100, 116, 139]), np.array([219, 234, 254])  # slate-500 .. blue-100
    rgb = (lo + (hi - lo) * shade[..., None]).astype(np.uint8)
    bg = np.array([248, 250, 252], dtype=np.uint8)
    empty = ids < 0
    rgb[empty] = bg
    # Kanten: Flächenwechsel und Silhouette
    edge = np.zeros((S, S), dtype=bool)
    edge[:, 1:] |= ids[:, 1:] != ids[:, :-1]
    edge[1:, :] |= ids[1:, :] != ids[:-1, :]
    rgb[edge] = (30, 41, 59)
    img = QImage(rgb.data, S, S, S * 3, QImage.Format_RGB888).copy()
    img = img.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    img.save(path)


def embed_thumbnail(fcstd, png):
    with zipfile.ZipFile(fcstd, "a") as z:
        z.write(png, "thumbnails/Thumbnail.png")


# ---------------------------------------------------------------- Zeichnung
def add_page(doc, title, material="S235JR", scale=1.0):
    page = doc.addObject("TechDraw::DrawPage", "Zeichnung")
    tpl = doc.addObject("TechDraw::DrawSVGTemplate", "Vorlage")
    tpl.Template = TEMPLATE
    page.Template = tpl
    tpl.setEditFieldContent("title", title)
    tpl.setEditFieldContent("part_material", material)
    page.Scale = scale
    tpl.setEditFieldContent("scale", "%d : %d" % ((1, round(1 / scale)) if scale < 1 else (round(scale), 1)))
    tpl.setEditFieldContent("date_of_issue", "TT.MM.JJJJ")
    return page


def add_view(doc, page, body, name, direction, x, y, hidden=False, xdir=None):
    v = doc.addObject("TechDraw::DrawViewPart", name)
    page.addView(v)
    v.Source = [body]
    v.Direction = direction
    if xdir is not None:
        v.XDirection = xdir
    v.X = x
    v.Y = y
    v.CoarseView = False
    v.HardHidden = hidden
    return v


def check_layout(doc, page):
    """Prüft, ob alle Ansichten im Zeichenrahmen liegen und das Schriftfeld nicht berühren."""
    doc.recompute()
    ok = True
    for o in doc.Objects:
        if o.isDerivedFrom("TechDraw::DrawViewPart"):
            edges = o.getVisibleEdges() + (o.getHiddenEdges() if o.HardHidden else [])
            bb = edges[0].BoundBox
            for e in edges[1:]:
                bb.add(e.BoundBox)
            k = page.Scale
            ox, oy = o.X.Value, o.Y.Value
            x0, x1 = ox + bb.XMin * k, ox + bb.XMax * k
            y0, y1 = oy - bb.YMax * k, oy - bb.YMin * k  # Y der Ansichtsgeometrie ist gespiegelt
            y0, y1 = min(y0, y1), max(y0, y1)
            inside = x0 >= 22 and x1 <= 285 and y0 >= 12 and y1 <= 198
            title = x1 > 105 and y0 < 60
            print("   %-14s x %6.1f..%6.1f  y %6.1f..%6.1f  %s" % (o.Name, x0, x1, y0, y1, "OK" if inside and not title else "PROBLEM"))
            ok = ok and inside and not title
    return ok


# ---------------------------------------------------------------- Beispiele
def build_winkel(doc):
    body = doc.addObject("PartDesign::Body", "Winkelstueck")
    body.Label = "Winkelstück"
    sk = new_sketch(body, "Profil", "XY_Plane")
    polygon(sk, [(0, 0), (60, 0), (60, 10), (10, 10), (10, 50), (0, 50)])
    doc.recompute()
    pad(body, sk, 30)
    doc.recompute()
    s1 = new_sketch(body, "Bohrung_Schenkel_1", "YZ_Plane")
    circles(s1, [(35, 15)], 4)
    pocket_through(body, s1, "Bohrung1")
    s2 = new_sketch(body, "Bohrung_Schenkel_2", "XZ_Plane")
    circles(s2, [(40, 15)], 4)
    pocket_through(body, s2, "Bohrung2")
    doc.recompute()
    page = add_page(doc, "Winkelstück")
    add_view(doc, page, body, "Hauptansicht", V(0, 0, 1), 70, 140, True)
    add_view(doc, page, body, "Ansicht_von_oben", V(0, 1, 0), 70, 88, True, V(1, 0, 0))
    add_view(doc, page, body, "Ansicht_von_links", V(-1, 0, 0), 127, 140, True, V(0, 0, 1))
    add_view(doc, page, body, "Isometrie", V(1, -1, 1), 215, 140)
    check_layout(doc, page)
    return body


def build_welle(doc):
    body = doc.addObject("PartDesign::Body", "Welle")
    body.Label = "Welle mit Absatz"
    sk = new_sketch(body, "Profil", "XY_Plane")
    polygon(sk, [(0, 0), (0, 10), (40, 10), (40, 7), (100, 7), (100, 0)])
    doc.recompute()
    rev = body.newObject("PartDesign::Revolution", "Drehen")
    rev.Profile = sk
    rev.ReferenceAxis = (sk, ["H_Axis"])
    rev.Angle = 360
    sk.Visibility = False
    doc.recompute()
    page = add_page(doc, "Welle mit Absatz")
    add_view(doc, page, body, "Hauptansicht", V(0, -1, 0), 80, 150)
    add_view(doc, page, body, "Seitenansicht", V(-1, 0, 0), 152, 150, True, V(0, -1, 0))
    add_view(doc, page, body, "Isometrie", V(1, -1, 1), 220, 120)
    check_layout(doc, page)
    return body


def build_platte(doc):
    body = doc.addObject("PartDesign::Body", "Platte")
    body.Label = "Platte mit Bohrungen"
    sk = new_sketch(body, "Profil", "XY_Plane")
    polygon(sk, [(0, 0), (80, 0), (80, 50), (0, 50)])
    doc.recompute()
    pad(body, sk, 10)
    doc.recompute()
    s1 = new_sketch(body, "Bohrungen", "XY_Plane")
    circles(s1, [(10, 10), (70, 10), (10, 40), (70, 40)], 4)
    pocket_through(body, s1, "Bohrungen")
    doc.recompute()
    page = add_page(doc, "Platte mit Bohrungen")
    add_view(doc, page, body, "Hauptansicht", V(0, 0, 1), 80, 150)
    add_view(doc, page, body, "Ansicht_von_oben", V(0, 1, 0), 80, 108, True, V(1, 0, 0))
    add_view(doc, page, body, "Isometrie", V(1, -1, 1), 200, 140)
    check_layout(doc, page)
    return body


EXAMPLES = [
    ("01_Winkelstueck", build_winkel),
    ("02_Welle", build_welle),
    ("03_Platte", build_platte),
]

if __name__ == "__main__" or True:  # FreeCADCmd führt das Skript nicht als __main__ aus
    os.makedirs(OUT, exist_ok=True)
    only = os.environ.get("MINTCAD_ONLY")
    for fname, builder in EXAMPLES:
        if only and only not in fname:
            continue
        doc = App.newDocument(fname)
        body = builder(doc)
        sketches = [o for o in doc.Objects if o.isDerivedFrom("Sketcher::SketchObject")]
        for s in sketches:
            print(fname, s.Name, "DoF=%d" % s.solve() if False else "", "FG" if s.FullyConstrained else "nicht voll bestimmt")
        print(fname, "valid:", body.Shape.isValid(), "Volumen: %.1f" % body.Shape.Volume)
        path = os.path.join(OUT, fname + ".FCStd")
        doc.saveAs(path)
        png = os.path.join(OUT, fname + ".png")
        thumbnail(body.Shape, png)
        embed_thumbnail(path, png)
        os.remove(png)
        App.closeDocument(doc.Name)
