# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Radialmenü (Marking Menu) auf der rechten Maustaste in der 3D-Ansicht.

Das Radialmenü ersetzt das normale Kontextmenü in Part Design, solange keine Skizze bearbeitet wird
(dort bleibt die rechte Maustaste "Werkzeug abbrechen"). Der Sektor "Mehr …" öffnet das normale
FreeCAD-Kontextmenü. Abschalten: Parameter BaseApp/Preferences/MintCAD/Radial = false.
"""

import math

import shiboken6

import FreeCAD
import FreeCADGui as Gui
from PySide6 import QtCore, QtGui, QtWidgets

# (Beschriftung, Befehl) je Sektor, im Uhrzeigersinn ab oben. Befehl "@more" = normales Kontextmenü.
SECTORS = [
    ("Skizze", "PartDesign_NewSketch"),
    ("Pad", "PartDesign_Pad"),
    ("Tasche", "PartDesign_Pocket"),
    ("Bohrung", "PartDesign_Hole"),
    ("Rückgängig", "Std_Undo"),
    ("Fase", "PartDesign_Chamfer"),
    ("Rundung", "PartDesign_Fillet"),
    ("Mehr …", "@more"),
]
CENTER = ("Alles zeigen", "Std_ViewFitAll")
R_IN, R_OUT, SIZE = 44, 128, 300
GAP = 2.0  # Grad Lücke zwischen den Sektoren


def _cmd_active(name):
    if name.startswith("@"):
        return True
    try:
        return bool(Gui.Command.get(name).isActive())
    except Exception:
        return False


def _cmd_icon(name):
    try:
        pix = Gui.Command.get(name).getInfo().get("pixmap", "")
        return Gui.getIcon(pix) if pix else QtGui.QIcon()
    except Exception:
        return QtGui.QIcon()


class RadialMenu(QtWidgets.QWidget):
    def __init__(self, host, on_more):
        super().__init__(None, QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint | QtCore.Qt.NoDropShadowWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setFixedSize(SIZE, SIZE)
        self._on_more = on_more
        self._hover = -2  # -2 nichts, -1 Mitte, 0.. Sektor
        self._items = [(t, c, _cmd_active(c), _cmd_icon(c)) for t, c in SECTORS]
        self._center = (CENTER[0], CENTER[1], _cmd_active(CENTER[1]), _cmd_icon(CENTER[1]))

    def popup_at(self, global_pos):
        self.move(global_pos - QtCore.QPoint(SIZE // 2, SIZE // 2))
        self.show()

    # -- Geometrie -----------------------------------------------------------------------------
    def _hit(self, pos):
        dx, dy = pos.x() - SIZE / 2, pos.y() - SIZE / 2
        r = math.hypot(dx, dy)
        if r < R_IN:
            return -1
        if r > R_OUT + 20:
            return -2
        ang = (math.degrees(math.atan2(dx, -dy)) + 360 + 22.5) % 360  # 0 = oben, im Uhrzeigersinn
        return int(ang // 45)

    def _sector_path(self, i):
        c = QtCore.QPointF(SIZE / 2, SIZE / 2)
        start = 90 - (i * 45 - 22.5) - GAP / 2  # Qt: 0 Grad = 3 Uhr, gegen den Uhrzeigersinn
        span = -(45 - GAP)
        outer = QtCore.QRectF(c.x() - R_OUT, c.y() - R_OUT, 2 * R_OUT, 2 * R_OUT)
        inner = QtCore.QRectF(c.x() - R_IN, c.y() - R_IN, 2 * R_IN, 2 * R_IN)
        p = QtGui.QPainterPath()
        p.arcMoveTo(outer, start)
        p.arcTo(outer, start, span)
        p.arcTo(inner, start + span, -span)
        p.closeSubpath()
        return p

    # -- Zeichnen ------------------------------------------------------------------------------
    def paintEvent(self, _):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        font = p.font()
        font.setPixelSize(12)
        p.setFont(font)
        for i, (text, _cmd, active, icon) in enumerate(self._items):
            hot = i == self._hover and active
            p.setPen(QtGui.QPen(QtGui.QColor("#334155"), 1))
            p.setBrush(QtGui.QColor("#2563eb" if hot else "#0f172a"))
            p.setOpacity(0.96)
            p.drawPath(self._sector_path(i))
            p.setOpacity(1.0)
            mid = math.radians(i * 45)
            rc = (R_IN + R_OUT) / 2
            cx = SIZE / 2 + rc * math.sin(mid)
            cy = SIZE / 2 - rc * math.cos(mid)
            if not icon.isNull():
                mode = QtGui.QIcon.Normal if active else QtGui.QIcon.Disabled
                icon.paint(p, QtCore.QRect(int(cx - 12), int(cy - 22), 24, 24), QtCore.Qt.AlignCenter, mode)
            p.setPen(QtGui.QColor("#f8fafc" if active else "#64748b"))
            p.drawText(QtCore.QRectF(cx - 40, cy + 3, 80, 18), QtCore.Qt.AlignCenter, text)
        # Mitte
        hot = self._hover == -1 and self._center[2]
        p.setPen(QtGui.QPen(QtGui.QColor("#334155"), 1))
        p.setBrush(QtGui.QColor("#2563eb" if hot else "#0f172a"))
        p.setOpacity(0.96)
        p.drawEllipse(QtCore.QPointF(SIZE / 2, SIZE / 2), R_IN - 4, R_IN - 4)
        p.setOpacity(1.0)
        p.setPen(QtGui.QColor("#f8fafc" if self._center[2] else "#64748b"))
        p.drawText(QtCore.QRectF(SIZE / 2 - 36, SIZE / 2 - 10, 72, 20), QtCore.Qt.AlignCenter, self._center[0])

    # -- Eingabe -------------------------------------------------------------------------------
    def mouseMoveEvent(self, ev):
        h = self._hit(ev.position().toPoint())
        if h != self._hover:
            self._hover = h
            self.update()

    def mouseReleaseEvent(self, ev):
        h = self._hit(ev.position().toPoint())
        item = self._center if h == -1 else (self._items[h] if h >= 0 else None)
        if item is None:
            if ev.button() == QtCore.Qt.LeftButton:
                self.close()
            return  # rechte Taste losgelassen außerhalb: Menü bleibt offen
        _text, cmd, active, _icon = item
        if not active:
            return
        self.close()
        if cmd == "@more":
            QtCore.QTimer.singleShot(0, self._on_more)
        else:
            QtCore.QTimer.singleShot(0, lambda: Gui.runCommand(cmd))

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()


class _Filter(QtCore.QObject):
    """Fängt die rechte Maustaste auf der 3D-Fläche ab (Drücken schlucken, beim Loslassen Menü zeigen)."""

    def __init__(self, parent):
        super().__init__(parent)
        self._pressed_at = None
        self._passthrough = False
        self._menu = None

    def _applicable(self):
        wb = Gui.activeWorkbench()
        if not wb or wb.name() != "PartDesignWorkbench":
            return False
        try:
            return Gui.ActiveDocument is not None and Gui.ActiveDocument.getInEdit() is None
        except Exception:
            return False

    def eventFilter(self, obj, ev):
        t = ev.type()
        if t not in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease):
            return False
        if ev.button() != QtCore.Qt.RightButton or self._passthrough or not self._applicable():
            return False
        if ev.modifiers() != QtCore.Qt.NoModifier:
            return False
        if t == QtCore.QEvent.MouseButtonPress:
            self._pressed_at = ev.globalPosition().toPoint()
            return True
        if self._pressed_at is None:
            return False
        self._pressed_at = None
        self._open(obj, ev)
        return True

    def _open(self, widget, ev):
        local = ev.position()
        gpos = ev.globalPosition().toPoint()

        def more():
            # normales FreeCAD-Menü: dieselbe Rechtsklick-Folge noch einmal, diesmal durchgelassen
            self._passthrough = True
            try:
                for typ, buttons in ((QtCore.QEvent.MouseButtonPress, QtCore.Qt.RightButton),
                                     (QtCore.QEvent.MouseButtonRelease, QtCore.Qt.NoButton)):
                    e = QtGui.QMouseEvent(typ, local, gpos, QtCore.Qt.RightButton, buttons, QtCore.Qt.NoModifier)
                    QtWidgets.QApplication.sendEvent(widget, e)
            finally:
                self._passthrough = False

        self._menu = RadialMenu(widget, more)
        self._menu.popup_at(gpos)


_filter = None
_hooked = set()


def _hook_view(sub):
    """Hängt den Filter an die 3D-Fläche eines MDI-Fensters (einmal je Fenster)."""
    try:
        w = sub.widget() if sub is not None and shiboken6.isValid(sub) else None
    except RuntimeError:
        return  # Fenster wurde inzwischen geschlossen
    if w is None or not shiboken6.isValid(w) or id(w) in _hooked:
        return
    if "View3DInventor" not in w.metaObject().className():
        return
    _hooked.add(id(w))
    key = id(w)
    w.destroyed.connect(lambda *_: _hooked.discard(key))
    for child in [w] + w.findChildren(QtWidgets.QWidget):
        child.installEventFilter(_filter)


def install():
    global _filter
    mw = Gui.getMainWindow()
    if mw is None or _filter is not None:
        return
    if not FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD").GetBool("Radial", True):
        return
    _filter = _Filter(mw)
    area = mw.findChild(QtWidgets.QMdiArea)
    if area is None:
        return
    area.subWindowActivated.connect(lambda sub: QtCore.QTimer.singleShot(200, lambda: _hook_view(sub)))
    _hook_view(area.activeSubWindow())
