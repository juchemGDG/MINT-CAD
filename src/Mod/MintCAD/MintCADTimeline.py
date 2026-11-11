# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Zeitleiste (Feature-Historie) am unteren Rand, wie in Fusion.

Zeigt die Skizzen und Features des aktiven Körpers (PartDesign::Body) in der Reihenfolge ihrer
Entstehung. Die Leiste liest nur und setzt vorhandene Eigenschaften (Tip, Suppressed, Label); es gibt
keine eigene Datenhaltung.

Bedienung: Klick = markieren, Doppelklick = bearbeiten, Rechtsklick = Menü (Umbenennen, Unterdrücken,
Zurückrollen, Löschen). Der blaue Marker zeigt den Stand (Tip) an und lässt sich ziehen (Zurückrollen/Springen).
Die Reihenfolge der Schritte lässt sich bewusst nicht ändern (Rundungen/Fasen hängen an Kantennamen).
"""

import FreeCAD
import FreeCADGui as Gui
from PySide6 import QtCore, QtGui, QtWidgets

STYLE = """
#MintTimeline { background: #0f172a; }
#MintTimeline QToolButton { background: #1e293b; color: #e2e8f0; border: 1px solid #334155;
    border-radius: 6px; padding: 3px 6px; font-size: 11px; }
#MintTimeline QToolButton:hover { border-color: #64748b; }
#MintTimeline QToolButton:checked { background: #2563eb; border-color: #1d4ed8; }
#MintTimeline QToolButton[suppressed="true"] { color: #64748b; background: #0f172a; border-style: dashed; }
#MintTimeline QToolButton[after="true"] { color: #64748b; background: #111827; }
#MintTimeline QLabel { color: #94a3b8; font-size: 11px; padding: 0 6px; }
#MintTimelineMarker { background: #2563eb; border-radius: 3px; }
#MintTimelineMarker:hover { background: #60a5fa; }
"""

ICON_FALLBACK = {
    "Sketcher::SketchObject": "Sketcher_Sketch",
    "PartDesign::Pad": "PartDesign_Pad",
    "PartDesign::Pocket": "PartDesign_Pocket",
    "PartDesign::Revolution": "PartDesign_Revolution",
    "PartDesign::Groove": "PartDesign_Groove",
    "PartDesign::Hole": "PartDesign_Hole",
    "PartDesign::Fillet": "PartDesign_Fillet",
    "PartDesign::Chamfer": "PartDesign_Chamfer",
    "PartDesign::Mirrored": "PartDesign_Mirrored",
    "PartDesign::LinearPattern": "PartDesign_LinearPattern",
    "PartDesign::PolarPattern": "PartDesign_PolarPattern",
    "PartDesign::Plane": "PartDesign_Plane",
}


def _icon(obj):
    """Icon des Objekts: bevorzugt das der Ansichtsklasse, sonst nach Typ."""
    try:
        vo = obj.ViewObject
        ic = vo.Icon if vo is not None else None
        if isinstance(ic, QtGui.QIcon) and not ic.isNull():
            return ic
    except Exception:
        pass
    name = ICON_FALLBACK.get(obj.TypeId)
    if name:
        try:
            return Gui.getIcon(name)
        except Exception:
            pass
    return QtGui.QIcon()


def active_body():
    try:
        view = Gui.ActiveDocument.ActiveView
        return view.getActiveObject("pdbody")
    except Exception:
        return None


def current_body():
    """Aktiver Körper; sonst der Körper der Auswahl; sonst der einzige (bzw. erste) Körper des Dokuments.

    Nach dem Öffnen einer Datei ist in FreeCAD kein Körper aktiv, die Zeitleiste soll trotzdem etwas zeigen."""
    body = active_body()
    if body is not None:
        return body
    doc = FreeCAD.ActiveDocument
    if doc is None:
        return None
    try:
        for o in Gui.Selection.getSelection():
            b = getattr(o, "_Body", None) or (o if o.TypeId == "PartDesign::Body" else None)
            if b is not None:
                return b
    except Exception:
        pass
    bodies = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"]
    return bodies[0] if bodies else None


class _Chip(QtWidgets.QToolButton):
    def __init__(self, obj, number, timeline, after_tip):
        super().__init__()
        self.obj_name = obj.Name
        self._tl = timeline
        self.setCheckable(True)
        self.setAutoRaise(False)
        self.setIcon(_icon(obj))
        self.setIconSize(QtCore.QSize(20, 20))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        text = obj.Label
        self.setText(text if len(text) <= 14 else text[:13] + "…")
        self.setToolTip("%s (%s)\nDoppelklick: bearbeiten, Rechtsklick: Menü" % (obj.Label, obj.TypeId.split("::")[-1]))
        self.setProperty("suppressed", bool(getattr(obj, "Suppressed", False)))
        self.setProperty("after", after_tip)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda pos: timeline.context_menu(self, self.mapToGlobal(pos)))
        self.clicked.connect(lambda: timeline.select(self.obj_name))

    def mouseDoubleClickEvent(self, ev):
        self._tl.edit(self.obj_name)


class _Marker(QtWidgets.QFrame):
    """Blauer Rollback-Marker: lässt sich in der Zeitleiste ziehen."""

    def __init__(self, timeline):
        super().__init__()
        self.setObjectName("MintTimelineMarker")
        self.setFixedSize(8, 28)
        self.setCursor(QtCore.Qt.SizeHorCursor)
        self.setToolTip("Aktueller Stand – nach links/rechts ziehen zum Zurückrollen")
        self._tl = timeline
        self._press = None

    def mousePressEvent(self, ev):
        self._press = ev.position().toPoint()

    def mouseMoveEvent(self, ev):
        if self._press is not None and (ev.position().toPoint() - self._press).manhattanLength() > 4:
            self._press = None
            self._tl.start_drag(self, "tip")


class _Strip(QtWidgets.QWidget):
    """Fläche mit den Chips: nimmt Ziehen/Ablegen an und zeigt die Einfügemarke."""

    def __init__(self, timeline):
        super().__init__()
        self._tl = timeline
        self._x = None
        self.setAcceptDrops(True)

    def _slot(self, x):
        """Position (Index in den Chips) und x-Koordinate der Einfügemarke zu einer Mausposition."""
        chips = [self.layout().itemAt(i).widget() for i in range(self.layout().count())]
        chips = [c for c in chips if isinstance(c, _Chip)]
        for i, c in enumerate(chips):
            if x < c.geometry().center().x():
                return i, c.geometry().left() - 2
        return len(chips), (chips[-1].geometry().right() + 2 if chips else 0)

    def dragEnterEvent(self, ev):
        if ev.mimeData().hasText() and ev.mimeData().text() == "tip":
            ev.acceptProposedAction()

    def dragMoveEvent(self, ev):
        self._x = self._slot(ev.position().x())[1]
        self.update()
        ev.acceptProposedAction()

    def dragLeaveEvent(self, ev):
        self._x = None
        self.update()

    def dropEvent(self, ev):
        index, _x = self._slot(ev.position().x())
        text = ev.mimeData().text()  # sofort lesen: das Ereignis ist nach der Rückkehr gelöscht
        self._x = None
        self.update()
        ev.acceptProposedAction()
        QtCore.QTimer.singleShot(0, lambda t=text, i=index: self._tl.dropped(t, i))

    def paintEvent(self, ev):
        super().paintEvent(ev)
        if self._x is not None:
            p = QtGui.QPainter(self)
            p.fillRect(QtCore.QRect(int(self._x) - 1, 2, 3, self.height() - 4), QtGui.QColor("#f59e0b"))


class Timeline(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MintTimeline")
        self.setStyleSheet(STYLE)
        self.setMinimumHeight(46)
        outer = QtWidgets.QHBoxLayout(self)
        outer.setContentsMargins(6, 3, 6, 3)
        self.caption = QtWidgets.QLabel("Zeitleiste")
        outer.addWidget(self.caption)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; } QScrollBar:horizontal { height: 8px; }")
        self.inner = _Strip(self)
        self.row = QtWidgets.QHBoxLayout(self.inner)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(4)
        self.scroll.setWidget(self.inner)
        outer.addWidget(self.scroll, 1)
        self._signature = None
        self._dirty = True
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(600)

    # -- Anzeige ---------------------------------------------------------------------------
    @staticmethod
    def _items(body):
        return [o for o in body.Group if o.isDerivedFrom("PartDesign::Feature") or o.TypeId == "Sketcher::SketchObject"
                or o.TypeId == "PartDesign::Plane" or o.TypeId == "PartDesign::Line" or o.TypeId == "PartDesign::Point"]

    def _sig(self, body):
        if body is None:
            return None
        tip = body.Tip.Name if body.Tip else ""
        sel = tuple(o.Name for o in Gui.Selection.getSelection())
        return (body.Name, body.Label, tip, sel, tuple((o.Name, o.Label, getattr(o, "Suppressed", False))
                                                        for o in self._items(body)))

    def refresh(self, force=False):
        try:
            self._refresh(force)
        except Exception as exc:  # z. B. Dokument wurde gerade geschlossen: beim nächsten Takt neu versuchen
            self._signature = None
            FreeCAD.Console.PrintLog("MINT-CAD: Zeitleiste: %s\n" % exc)

    def _refresh(self, force=False):
        if not self.isVisible():
            return
        body = current_body()
        sig = self._sig(body) if body is not None else ("none",)
        if sig == self._signature and not force:
            return
        self._signature = sig
        while self.row.count():
            item = self.row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if body is None:
            self.caption.setText("Zeitleiste – kein aktiver Körper")
            self.row.addStretch(1)
            return
        self.caption.setText("Zeitleiste: " + body.Label)
        tip = body.Tip
        past_tip = False
        selected = {o.Name for o in Gui.Selection.getSelection()}
        for n, obj in enumerate(self._items(body), 1):
            chip = _Chip(obj, n, self, past_tip)
            chip.setChecked(obj.Name in selected)
            self.row.addWidget(chip)
            if tip is not None and obj == tip:
                self.row.addWidget(_Marker(self))
                past_tip = True
        self.row.addStretch(1)
        # Style neu auswerten (dynamische Properties)
        self.inner.setStyleSheet("")
        self.style().unpolish(self.inner)
        self.style().polish(self.inner)

    # -- Ziehen: Umsortieren und Zurückrollen --------------------------------------------------
    def start_drag(self, widget, text):
        drag = QtGui.QDrag(widget)
        mime = QtCore.QMimeData()
        mime.setText(text)
        drag.setMimeData(mime)
        drag.setPixmap(widget.grab())
        drag.exec(QtCore.Qt.MoveAction)

    def dropped(self, text, index):
        body = current_body()
        if body is None or text != "tip":
            return
        self._move_tip(body, self._items(body), index)

    @staticmethod
    def _is_solid(o):
        return o.isDerivedFrom("PartDesign::Feature")

    def _move_tip(self, body, items, index):
        """Marker vor Position 'index' ablegen: Tip = letztes Solid-Feature davor."""
        before = [o for o in items[:index] if self._is_solid(o)]
        if before:
            self._set(body, "Tip", before[-1], "Zurückrollen")

    # -- Aktionen ----------------------------------------------------------------------------
    def _obj(self, name):
        doc = FreeCAD.ActiveDocument
        return doc.getObject(name) if doc else None

    def select(self, name):
        obj = self._obj(name)
        if obj is None:
            return
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(obj)

    def edit(self, name):
        obj = self._obj(name)
        if obj is None:
            return
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(obj)
        try:
            Gui.ActiveDocument.setEdit(obj.Name, 0)
        except Exception as exc:
            FreeCAD.Console.PrintWarning("MINT-CAD: Bearbeiten nicht möglich: %s\n" % exc)

    def context_menu(self, chip, pos):
        obj = self._obj(chip.obj_name)
        body = current_body()
        if obj is None or body is None:
            return
        menu = QtWidgets.QMenu(self)
        menu.addAction("Bearbeiten", lambda: self.edit(obj.Name))
        menu.addAction("Umbenennen …", lambda: self._rename(obj))
        if hasattr(obj, "Suppressed"):
            act = menu.addAction("Unterdrückt (Feature ausschalten)")
            act.setCheckable(True)
            act.setChecked(bool(obj.Suppressed))
            act.triggered.connect(lambda on: self._set(obj, "Suppressed", bool(on), "Unterdrücken"))
        if obj.isDerivedFrom("PartDesign::Feature") and obj.TypeId != "PartDesign::Plane":
            menu.addAction("Hierher zurückrollen", lambda: self._set(body, "Tip", obj, "Zurückrollen"))
        menu.addSeparator()
        menu.addAction("Löschen", lambda: self._delete(obj))
        menu.exec(pos)

    @staticmethod
    def _set(target, prop, value, title):
        doc = target.Document
        doc.openTransaction(title)
        try:
            setattr(target, prop, value)
            doc.commitTransaction()
            doc.recompute()
        except Exception as exc:
            doc.abortTransaction()
            FreeCAD.Console.PrintWarning("MINT-CAD: %s: %s\n" % (title, exc))

    def _rename(self, obj):
        text, ok = QtWidgets.QInputDialog.getText(self, "Umbenennen", "Neuer Name:", text=obj.Label)
        if ok and text.strip():
            self._set(obj, "Label", text.strip(), "Umbenennen")

    def _delete(self, obj):
        doc = obj.Document
        if QtWidgets.QMessageBox.question(self, "Löschen", "„%s“ löschen?" % obj.Label) != QtWidgets.QMessageBox.Yes:
            return
        doc.openTransaction("Löschen")
        try:
            doc.removeObject(obj.Name)
            doc.commitTransaction()
            doc.recompute()
        except Exception as exc:
            doc.abortTransaction()
            FreeCAD.Console.PrintWarning("MINT-CAD: Löschen: %s\n" % exc)


_dock = None


def install():
    """Legt die Zeitleiste als Dock am unteren Rand an (ein-/ausblendbar über Ansicht > Bedienfelder)."""
    global _dock
    mw = Gui.getMainWindow()
    if mw is None or _dock is not None:
        return
    _dock = QtWidgets.QDockWidget("Zeitleiste", mw)
    _dock.setObjectName("MintTimelineDock")
    _dock.setWidget(Timeline())
    _dock.setTitleBarWidget(QtWidgets.QWidget())  # ohne Titelleiste: schlanker Streifen wie in Fusion
    _dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
    mw.addDockWidget(QtCore.Qt.BottomDockWidgetArea, _dock)
    _dock.setMaximumHeight(60)
    # Nur in Part Design sichtbar. Der gespeicherte Fensterzustand (QMainWindow) kann das Dock beim Start
    # ausblenden oder erst nach dem Einrichten wiederherstellen; deshalb wird die Sichtbarkeit laufend abgeglichen.
    def sync():
        wb = Gui.activeWorkbench()
        name = wb.name() if wb else ""
        doc = FreeCAD.ActiveDocument
        has_body = bool(doc and any(o.TypeId == "PartDesign::Body" for o in doc.Objects))
        # Part Design immer; Start/Sketcher/Part, sobald das Dokument einen Körper hat (z. B. frisch geöffnete Datei)
        want = name == "PartDesignWorkbench" or (has_body and name in ("StartWorkbench", "SketcherWorkbench", "PartWorkbench"))
        if _dock.isVisible() != want:
            _dock.setVisible(want)

    timer = QtCore.QTimer(_dock)
    timer.timeout.connect(sync)
    timer.start(500)
    sync()
