# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: erzeugt die Screenshots für die Anleitungen (Skizze -> Körper -> Zeichnung).

Start (echtes Fenster, eigenes Profil, damit das Nutzerprofil unberührt bleibt):
    SHOTDIR=<Ausgabe> FREECAD_USER_HOME=<leerer Ordner> build/release/bin/FreeCAD tools/mintcad/docshots/shots.py

Das 3D-Bild wird per glReadPixels gelesen und in den Fenster-Screenshot einkopiert (QOpenGLWidget
liefert über grab() nur Schwarz). Jeder Schritt ist einzeln abgesichert; Fehler stehen in log.txt.
"""
import ctypes
import math
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher
from PySide6 import QtCore, QtGui, QtOpenGLWidgets, QtWidgets

OUT = os.environ.get("SHOTDIR", "/tmp/mintcad-shots")
os.makedirs(OUT, exist_ok=True)
V = App.Vector
GL = ctypes.CDLL("/System/Library/Frameworks/OpenGL.framework/OpenGL")
STEPS = []


def log(msg):
    with open(os.path.join(OUT, "log.txt"), "a", encoding="utf-8") as fh:
        fh.write(str(msg) + "\n")


def step(delay=1800):
    def deco(fn):
        STEPS.append((fn, delay))
        return fn

    return deco


def run(i=0):
    if i >= len(STEPS):
        log("fertig")
        os._exit(0)
    fn, delay = STEPS[i]
    try:
        fn()
    except Exception:
        log("FEHLER in %s\n%s" % (fn.__name__, traceback.format_exc()))
    QtCore.QTimer.singleShot(delay, lambda: run(i + 1))


# ----------------------------------------------------------------------------- Bildaufnahme
def mw():
    return Gui.getMainWindow()


def _largest(widgets):
    best, area = None, 0
    for w in widgets:
        if not w.isVisible() or w.visibleRegion().isEmpty():
            continue
        r = w.visibleRegion().boundingRect()
        if r.width() * r.height() > area:
            best, area = w, r.width() * r.height()
    return best


def gl_widget():
    """Das OpenGL-Widget der gerade aktiven 3D-Ansicht (verdeckte Reiter haben eine leere sichtbare Fläche)."""
    return _largest([g for g in mw().findChildren(QtOpenGLWidgets.QOpenGLWidget) if g.width() > 200])


def graphics_view():
    return _largest([v for v in mw().findChildren(QtWidgets.QGraphicsView) if v.width() > 300])


def read_gl(g):
    """3D-Bild direkt aus dem OpenGL-Puffer (grabFramebuffer liefert hier nur den Hintergrund)."""
    r = g.devicePixelRatio()
    w, h = int(g.width() * r), int(g.height() * r)
    g.makeCurrent()
    GL.glBindFramebuffer(0x8D40, g.defaultFramebufferObject())
    buf = ctypes.create_string_buffer(w * h * 4)
    GL.glReadPixels(0, 0, w, h, 0x1908, 0x1401, buf)
    g.doneCurrent()
    return QtGui.QImage(buf.raw, w, h, w * 4, QtGui.QImage.Format_RGBA8888).mirrored(False, True).copy()


def rect_in_window(widget):
    tl = widget.mapTo(mw(), QtCore.QPoint(0, 0))
    return QtCore.QRect(tl, widget.size())


def region(name):
    win = mw()
    W, H = win.width(), win.height()
    ribbon = win.findChild(QtWidgets.QToolBar, "MintRibbonToolBar")
    rb = rect_in_window(ribbon).bottom() + 1 if ribbon else 170
    g = gl_widget()
    if name == "alles":
        return QtCore.QRect(0, 0, W, H)
    if name == "band":
        return QtCore.QRect(0, 0, W, rb)
    if name == "gl":
        return rect_in_window(g)
    if name == "panel+gl":
        return QtCore.QRect(0, rb, W, H - rb - 30)
    if name == "panel":
        return QtCore.QRect(0, rb, 330, H - rb - 30)
    if name == "status":
        sb = win.statusBar()
        r = rect_in_window(sb)
        return QtCore.QRect(r.right() - 520, r.top(), 520, r.height())
    raise KeyError(name)


def is_3d():
    v = Gui.activeView()
    return v is not None and hasattr(v, "viewIsometric")


def shot(name, where="alles", width=1100):
    win = mw()
    QtWidgets.QApplication.processEvents()
    g = gl_widget()
    gl = None
    gpos = None
    if where in ("alles", "gl", "panel+gl"):
        if is_3d() and g is not None:
            # Coin-Ansicht: direkt aus dem OpenGL-Puffer lesen
            gl, gpos = read_gl(g), rect_in_window(g).topLeft()
        else:
            gv = graphics_view()
            if gv is not None:
                vp = gv.viewport()
                r0 = win.devicePixelRatio()
                gl = QtGui.QImage(int(vp.width() * r0), int(vp.height() * r0), QtGui.QImage.Format_RGBA8888)
                gl.setDevicePixelRatio(r0)
                gl.fill(QtGui.QColor("#f8fafc"))
                pp = QtGui.QPainter(gl)
                gv.render(pp)
                pp.end()
                gpos = rect_in_window(vp).topLeft()
    img = win.grab().toImage()
    dpr = img.devicePixelRatio() if img.devicePixelRatio() > 1 else img.width() / win.width()
    if gl is not None:
        p = QtGui.QPainter(img)
        gl.setDevicePixelRatio(img.devicePixelRatio())
        p.drawImage(gpos, gl)  # Painter arbeitet in logischen Koordinaten
        p.end()
    r = region(where)
    crop = img.copy(int(r.x() * dpr), int(r.y() * dpr), int(r.width() * dpr), int(r.height() * dpr))
    if crop.width() > width:
        crop = crop.scaledToWidth(width, QtCore.Qt.SmoothTransformation)
    crop.save(os.path.join(OUT, name + ".png"))
    log("Bild %s %dx%d" % (name, crop.width(), crop.height()))


# ----------------------------------------------------------------------------- Modellierung
def new_body(label):
    doc = App.newDocument(label)
    body = doc.addObject("PartDesign::Body", "Body")
    body.Label = "Körper"
    Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", body)
    doc.recompute()
    return doc, body


def origin_plane(body, role):
    return [f for f in body.Origin.OriginFeatures if f.Role == role][0]


def sketch_on(body, name, support, sub=""):
    sk = body.newObject("Sketcher::SketchObject", name)
    sk.AttachmentSupport = (support, [sub])
    sk.MapMode = "FlatFace"
    return sk


def polygon(sk, pts, dims=True, origin=True):
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
    if origin:
        sk.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
    if dims:
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
            c = None
            if abs(y1 - y0) < 1e-9 and abs(x1 - x0) > 1e-9:
                a, b = (1, 2) if x1 > x0 else (2, 1)
                c = Sketcher.Constraint("DistanceX", i, a, i, b, abs(x1 - x0))
            elif abs(x1 - x0) < 1e-9 and abs(y1 - y0) > 1e-9:
                a, b = (1, 2) if y1 > y0 else (2, 1)
                c = Sketcher.Constraint("DistanceY", i, a, i, b, abs(y1 - y0))
            if c is not None:
                idx = sk.addConstraint(c)
                if sk.solve() != 0 or sk.RedundantConstraints or sk.ConflictingConstraints:
                    sk.delConstraint(idx)
    return sk


def edit(sk):
    sk.Document.recompute()
    Gui.ActiveDocument.setEdit(sk.Name)


def leave():
    Gui.ActiveDocument.resetEdit()
    Gui.SendMsgToActiveView("ViewFit")


def fit():
    Gui.SendMsgToActiveView("ViewFit")


def iso():
    Gui.ActiveDocument.ActiveView.viewIsometric()
    fit()


def click_button(text):
    for b in mw().findChildren(QtWidgets.QPushButton):
        if b.isVisible() and b.text().replace("&", "") == text:
            b.click()
            return True
    return False


def close_dialog():
    Gui.Control.closeDialog()


def front_face(shape):
    """Fläche mit Normale -Y am kleinsten Y (Vorderseite bei Skizze auf der XZ-Ebene)."""
    ymin = shape.BoundBox.YMin
    for i, f in enumerate(shape.Faces):
        if abs(f.BoundBox.YMin - ymin) < 1e-6 and abs(f.BoundBox.YMax - ymin) < 1e-6:
            return "Face%d" % (i + 1)
    return None


def to_local(sk, gx, gy, gz):
    return sk.Placement.inverse().multVec(V(gx, gy, gz))


STATE = {}

# ============================================================================ Teil 1
P1 = [(0, 0), (40, 0), (40, 10), (25, 50), (15, 50), (15, 35), (0, 35)]


@step(2500)
def start():
    win = mw()
    Gui.activateWorkbench("PartDesignWorkbench")
    STATE["doc"], STATE["body"] = new_body("Bauteil_1")


@step(1500)
def s_band():
    shot("pd_01_band", "band")
    shot("pd_02_statusleiste", "status", width=520)


@step(1800)
def s_neue_skizze_dialog():
    Gui.Selection.clearSelection()
    Gui.runCommand("PartDesign_CompSketches", 0)
    # 3D-Ansicht schräg, damit die drei Ebenen zu sehen sind
    Gui.ActiveDocument.ActiveView.viewIsometric()
    fit()


@step(1800)
def s_ebenenwahl():
    shot("pd_03_ebenenwahl", "panel+gl")
    close_dialog()


@step(1500)
def s_skizze_umriss():
    body = STATE["body"]
    sk = sketch_on(body, "Skizze", origin_plane(body, "XZ_Plane"))
    polygon(sk, P1, dims=False, origin=False)
    STATE["sk1"] = sk
    edit(sk)
    fit()


@step(2200)
def s_umriss_shot():
    shot("pd_04_skizzentools", "band")
    shot("pd_05_umriss", "panel+gl")


@step(1500)
def s_bemasst():
    sk = STATE["sk1"]
    sk.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1))
    polygon_dims(sk, P1)
    sk.Document.recompute()
    fit()


def polygon_dims(sk, pts):
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        c = None
        if abs(y1 - y0) < 1e-9 and abs(x1 - x0) > 1e-9:
            a, b = (1, 2) if x1 > x0 else (2, 1)
            c = Sketcher.Constraint("DistanceX", i, a, i, b, abs(x1 - x0))
        elif abs(x1 - x0) < 1e-9 and abs(y1 - y0) > 1e-9:
            a, b = (1, 2) if y1 > y0 else (2, 1)
            c = Sketcher.Constraint("DistanceY", i, a, i, b, abs(y1 - y0))
        if c is not None:
            idx = sk.addConstraint(c)
            if sk.solve() != 0 or sk.RedundantConstraints or sk.ConflictingConstraints:
                sk.delConstraint(idx)


@step(2200)
def s_bemasst_shot():
    log("Skizze 1 voll bestimmt: %s" % STATE["sk1"].FullyConstrained)
    shot("pd_06_bemasst", "panel+gl")
    shot("pd_07_randbedingungen", "band")


@step(1500)
def s_pad_dialog():
    leave()
    sk = STATE["sk1"]
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sk)
    Gui.runCommand("PartDesign_Pad", 0)
    iso()


@step(2000)
def s_pad_shot():
    shot("pd_08_pad_dialog", "panel+gl")
    pad = STATE["body"].Tip
    pad.Label = "Grundkörper"
    pad.Length = 30
    click_button("OK")
    STATE["sk1"].Visibility = False
    STATE["doc"].recompute()
    STATE["pad"] = pad
    iso()


@step(1800)
def s_pad_ergebnis():
    shot("pd_09_pad_ergebnis", "gl", width=800)


@step(1500)
def s_tasche_skizze():
    body, pad = STATE["body"], STATE["pad"]
    face = front_face(pad.Shape)
    log("Vorderseite: %s (YMin=%.1f)" % (face, pad.Shape.BoundBox.YMin))
    Gui.ActiveDocument.ActiveView.viewFront()
    fit()
    sk = sketch_on(body, "Skizze_Tasche", pad, face)
    sk.Document.recompute()
    y = pad.Shape.BoundBox.YMin
    pts = [to_local(sk, x, y, z) for x, z in ((-5, 20), (45, 20), (45, 55), (-5, 55))]
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        sk.addGeometry(Part.LineSegment(V(a.x, a.y, 0), V(b.x, b.y, 0)), False)
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
        a, b = pts[i], pts[(i + 1) % 4]
        sk.addConstraint(Sketcher.Constraint("Horizontal" if abs(b.y - a.y) < 1e-6 else "Vertical", i))
    STATE["sk2"] = sk
    edit(sk)
    fit()


@step(2200)
def s_tasche_skizze_shot():
    shot("pd_10_tasche_skizze", "panel+gl")


@step(1500)
def s_tasche_dialog():
    leave()
    sk = STATE["sk2"]
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sk)
    Gui.runCommand("PartDesign_Pocket", 0)
    iso()


@step(2000)
def s_tasche_shot():
    shot("pd_11_tasche_dialog", "panel+gl")
    pocket = STATE["body"].Tip
    pocket.Label = "Stufe"
    pocket.Length = 15
    click_button("OK")
    STATE["sk2"].Visibility = False
    STATE["doc"].recompute()
    STATE["pocket"] = pocket
    iso()


@step(1800)
def s_tasche_ergebnis():
    shot("pd_12_tasche_ergebnis", "gl", width=800)


@step(1500)
def s_bohrung_skizze():
    body, pocket = STATE["body"], STATE["pocket"]
    face = front_face(pocket.Shape)
    Gui.ActiveDocument.ActiveView.viewFront()
    fit()
    sk = sketch_on(body, "Skizze_Bohrung", pocket, face)
    sk.Document.recompute()
    y = pocket.Shape.BoundBox.YMin
    c = to_local(sk, 20, y, 10)
    sk.addGeometry(Part.Circle(V(c.x, c.y, 0), V(0, 0, 1), 7.5), False)
    sk.addConstraint(Sketcher.Constraint("Diameter", 0, 15))
    STATE["sk3"] = sk
    edit(sk)
    fit()


@step(2200)
def s_bohrung_skizze_shot():
    shot("pd_13_bohrung_skizze", "panel+gl")


@step(1500)
def s_bohrung_dialog():
    leave()
    sk = STATE["sk3"]
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sk)
    Gui.runCommand("PartDesign_Hole", 0)
    iso()


@step(2200)
def s_bohrung_shot():
    shot("pd_14_bohrung_dialog", "panel+gl")
    hole = STATE["body"].Tip
    hole.Label = "Bohrung"
    hole.Threaded = False
    hole.Diameter = 15
    hole.DepthType = "ThroughAll"
    click_button("OK")
    STATE["sk3"].Visibility = False
    STATE["doc"].recompute()
    log("Bohrung gültig: %s" % hole.Shape.isValid())
    STATE["hole"] = hole
    iso()


@step(1800)
def s_teil1_fertig():
    shot("pd_15_teil1_fertig", "gl", width=800)
    # Teilebaum: Reiter "Modell" zeigen, alles aufklappen
    for tab in mw().findChildren(QtWidgets.QTabBar):
        for i in range(tab.count()):
            if tab.tabText(i) == "Modell":
                tab.setCurrentIndex(i)
    for tree in mw().findChildren(QtWidgets.QTreeWidget):
        if tree.isVisible():
            tree.expandAll()


@step(1500)
def s_baum():
    shot("pd_16_teilebaum", "panel", width=520)


# ============================================================================ Teil 2
@step(2000)
def teil2_start():
    STATE["doc"], STATE["body"] = new_body("Bauteil_2")
    body = STATE["body"]
    sk = sketch_on(body, "Skizze", origin_plane(body, "XZ_Plane"))
    pts = [(4, 0), (10, 0), (10, 20), (6, 20), (6, 16), (4, 16)]
    polygon(sk, pts, dims=False, origin=False)
    sk.addConstraint(Sketcher.Constraint("Coincident", 0, 1, -1, 1)) if False else None
    STATE["sk4"] = sk
    edit(sk)
    fit()


@step(2200)
def teil2_skizze_shot():
    shot("pd_17_rotation_skizze", "panel+gl")


@step(1500)
def teil2_dialog():
    leave()
    sk = STATE["sk4"]
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sk)
    Gui.runCommand("PartDesign_Revolution", 0)
    iso()


@step(2200)
def teil2_dialog_shot():
    shot("pd_18_rotation_dialog", "panel+gl")
    rev = STATE["body"].Tip
    rev.ReferenceAxis = (STATE["sk4"], ["V_Axis"])
    rev.Angle = 180
    click_button("OK")
    STATE["sk4"].Visibility = False
    STATE["doc"].recompute()
    STATE["rev"] = rev
    iso()


@step(1800)
def teil2_ergebnis():
    shot("pd_19_rotation_ergebnis", "gl", width=800)


@step(1500)
def fase_dialog():
    rev = STATE["rev"]
    # eine Kante der Außenseite oben wählen (Kreisbogen mit Radius 10 bei z=20)
    for i, e in enumerate(rev.Shape.Edges):
        if abs(e.BoundBox.ZMin - 20) < 1e-6 and abs(e.BoundBox.ZMax - 20) < 1e-6 and e.BoundBox.XMax > 9.9:
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(STATE["doc"].Name, "Body", "Revolution.Edge%d" % (i + 1))
            break
    Gui.runCommand("PartDesign_Chamfer", 0)
    iso()


@step(2200)
def fase_shot():
    shot("pd_20_fase_dialog", "panel+gl")
    close_dialog()


@step(1500)
def bezugsebene_dialog():
    body = STATE["body"]
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(STATE["doc"].Name, origin_plane(body, "XZ_Plane").Name)
    Gui.runCommand("PartDesign_Plane", 0)
    iso()


@step(2200)
def bezugsebene_shot():
    shot("pd_21_bezugsebene_dialog", "panel+gl")
    close_dialog()


# ============================================================================ Muster
@step(2000)
def muster_start():
    STATE["doc"], STATE["body"] = new_body("Bauteil_3")
    body = STATE["body"]
    sk = sketch_on(body, "Skizze", origin_plane(body, "XY_Plane"))
    pts = [(-30, -30), (30, -30), (30, 30), (-30, 30)]
    polygon(sk, pts, dims=False, origin=False)
    sk.Document.recompute()
    pad = body.newObject("PartDesign::Pad", "Pad")
    pad.Profile = sk
    pad.Length = 10
    sk.Visibility = False
    STATE["doc"].recompute()
    top = [i for i, f in enumerate(pad.Shape.Faces) if abs(f.BoundBox.ZMin - 10) < 1e-6 and abs(f.BoundBox.ZMax - 10) < 1e-6][0]
    sk2 = sketch_on(body, "Skizze_Loch", pad, "Face%d" % (top + 1))
    sk2.Document.recompute()
    c = to_local(sk2, 20, 0, 10)
    sk2.addGeometry(Part.Circle(V(c.x, c.y, 0), V(0, 0, 1), 4), False)
    sk2.addConstraint(Sketcher.Constraint("Diameter", 0, 8))
    sk2.Document.recompute()
    pocket = body.newObject("PartDesign::Pocket", "Loch")
    pocket.Profile = sk2
    pocket.Type = 1
    sk2.Visibility = False
    STATE["doc"].recompute()
    STATE["loch"] = pocket
    iso()


@step(1800)
def polar_dialog():
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(STATE["doc"].Name, "Body", "Loch.")
    Gui.runCommand("PartDesign_PolarPattern", 0)
    iso()


@step(2200)
def polar_shot():
    shot("pd_22_polar_dialog", "panel+gl")
    pp = STATE["body"].Tip
    pp.Angle = 360
    pp.Occurrences = 4
    click_button("OK")
    STATE["doc"].recompute()
    iso()


def origin_axis(body, role):
    return [f for f in body.Origin.OriginFeatures if f.Role == role][0]


@step(1500)
def polar_vier():
    pp = STATE["body"].Tip
    pp.Occurrences = 4  # der Dialog übernimmt beim Bestätigen seinen eigenen Standardwert
    STATE["doc"].recompute()
    iso()


@step(1800)
def polar_ergebnis():
    shot("pd_23_polar_ergebnis", "gl", width=800)


# ============================================================================ Zeichnung (TechDraw)
@step(2500)
def td_start():
    # Bauteil 1 nochmals öffnen: aus dem fertigen Dokument ableiten
    STATE["doc"] = App.getDocument("Bauteil_1")
    App.setActiveDocument("Bauteil_1")
    Gui.ActiveDocument = Gui.getDocument("Bauteil_1")
    Gui.ActiveDocument.ActiveView.viewFront()
    fit()
    Gui.activateWorkbench("TechDrawWorkbench")


@step(2000)
def td_band():
    shot("td_01_band", "band")


@step(1500)
def td_seite():
    Gui.runCommand("TechDraw_PageDefault", 0)


@step(1500)
def td_seite_zeigen():
    page = [o for o in App.getDocument("Bauteil_1").Objects if o.TypeId == "TechDraw::DrawPage"]
    STATE["page"] = page[0] if page else None
    log("Seite: %s" % (page[0].Name if page else "keine"))
    page[0].ViewObject.doubleClicked()  # Zeichenblatt als aktive Ansicht öffnen


@step(2500)
def td_seite_shot():
    shot("td_02_seite_leer", "alles", width=1100)


@step(1500)
def td_ansicht_dialog():
    doc = App.getDocument("Bauteil_1")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(doc.Name, "Body")
    Gui.runCommand("TechDraw_ProjectionGroup", 0)


@step(2500)
def td_ansicht_shot():
    shot("td_03_ansichten_dialog", "panel", width=520)
    # Standardwerte aus der Anleitung: Skalieren benutzerdefiniert 1:1, Auto-Verteilung aus
    for b in mw().findChildren(QtWidgets.QCheckBox):
        if b.isVisible() and "Automatische" in b.text():
            b.setChecked(False)
    click_button("OK")


def export_page(name, crop=None, width=1400):
    """Zeichenblatt über TechDraw als SVG ausgeben und als Bild speichern (zeigt das echte Ergebnis)."""
    import TechDrawGui
    from PySide6.QtSvg import QSvgRenderer

    svg = os.path.join(OUT, name + ".svg")
    TechDrawGui.exportPageAsSvg(STATE["page"], svg)
    r = QSvgRenderer(svg)
    size = r.defaultSize()
    h = int(width * size.height() / size.width())
    img = QtGui.QImage(width, h, QtGui.QImage.Format_ARGB32)
    img.fill(QtGui.QColor("white"))
    p = QtGui.QPainter(img)
    p.setRenderHint(QtGui.QPainter.Antialiasing)
    r.render(p)
    p.end()
    if crop:
        x, y, w, hh = crop
        img = img.copy(int(x * width), int(y * h), int(w * width), int(hh * h))
    img.save(os.path.join(OUT, name + ".png"))
    os.remove(svg)
    log("Zeichnung %s %dx%d" % (name, img.width(), img.height()))


@step(2500)
def td_ansicht_fertig():
    """Projektionsgruppe lässt sich per Skript nicht zuverlässig ausrichten: für die Abbildungen
    werden dieselben Ansichten als Einzelansichten mit Projektionsrichtung (1. Methode) angelegt."""
    doc = App.getDocument("Bauteil_1")
    page, body = STATE["page"], doc.getObject("Body")
    for name in [o.Name for o in doc.Objects if o.TypeId == "TechDraw::DrawProjGroup"]:
        try:
            for item in list(doc.getObject(name).Views):
                try:
                    doc.removeObject(item.Name)
                except Exception:
                    pass
            doc.removeObject(name)
        except Exception as exc:
            log("Entfernen: %s" % exc)
    doc.recompute()
    specs = [("Vorne", V(0, -1, 0), V(1, 0, 0), 70, 140, False), ("Oben", V(0, 0, 1), V(1, 0, 0), 70, 85, True),
             ("Links", V(-1, 0, 0), V(0, -1, 0), 135, 140, True)]
    STATE["views"] = {}
    for name, direction, xdir, x, y, hidden in specs:
        v = doc.addObject("TechDraw::DrawViewPart", name)
        page.addView(v)
        v.Source = [body]
        v.Direction = direction
        v.XDirection = xdir
        v.X, v.Y = x, y
        v.HardHidden = hidden
        v.CoarseView = False
        STATE["views"][name] = v
    doc.recompute()
    doc.recompute()
    STATE["front"] = STATE["views"]["Vorne"]
    log("Ansichten erzeugt, Vorne: %d Kanten" % len(STATE["front"].getVisibleEdges()))


@step(2500)
def td_ansicht_bild():
    export_page("td_04_ansichten_angeordnet")


@step(2000)
def td_bemassung():
    doc = App.getDocument("Bauteil_1")
    front, page = STATE["front"], STATE["page"]
    verts = []
    i = 0
    while i < 80:
        try:
            v = front.getVertexByIndex(i)
        except Exception:
            break
        verts.append((i, v.X, v.Y))
        i += 1
    log("Vorne: %d Punkte" % len(verts))
    ymin = min(v[2] for v in verts)
    base = [v for v in verts if abs(v[2] - ymin) < 0.1]
    base.sort(key=lambda v: v[1])
    xs = [v[1] for v in verts]
    left = [v for v in verts if abs(v[1] - min(xs)) < 0.1]
    left.sort(key=lambda v: v[2])
    log("Unterkante: %s | linke Kante: %s" % (base, left))
    made = 0
    if len(base) >= 2:
        d = doc.addObject("TechDraw::DrawViewDimension", "Bemassung_Breite")
        d.Type = "DistanceX"
        d.References2D = [(front, "Vertex%d" % base[0][0]), (front, "Vertex%d" % base[-1][0])]
        page.addView(d)
        made += 1
    if len(left) >= 2:
        d = doc.addObject("TechDraw::DrawViewDimension", "Bemassung_Hoehe")
        d.Type = "DistanceY"
        d.References2D = [(front, "Vertex%d" % left[0][0]), (front, "Vertex%d" % left[-1][0])]
        page.addView(d)
        made += 1
    doc.recompute()
    log("Maße: %d" % made)


@step(2500)
def td_bemassung_bild():
    export_page("td_05_bemassung")
    page = STATE["page"]
    page.Template.setEditFieldContent("title", "Winkelstück")
    page.Template.setEditFieldContent("creator", "Name Vorname")
    page.Template.setEditFieldContent("class", "10a")
    page.Template.setEditFieldContent("date_of_issue", "08.11.2026")
    App.getDocument("Bauteil_1").recompute()


@step(2500)
def td_felder_bild():
    export_page("td_06_schriftfeld", crop=(0.33, 0.78, 0.67, 0.22), width=2000)
    shot("td_01_band_zeichnung", "band")


QtCore.QTimer.singleShot(7000, run)
