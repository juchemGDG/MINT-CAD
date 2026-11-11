# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Bedienung im Stil von Fusion (Navigation, Tastenkürzel, Schnellleiste nach der Skizze).

- Navigation: Mausrad = Zoom zum Mauszeiger, mittlere Taste = Verschieben, Umschalt + mittlere Taste = Drehen.
- Einbuchstaben-Kürzel wie in Fusion (E = Pad, H = Bohrung, F = Rundung ...). Ein Kürzel wird nur gesetzt,
  wenn es nicht schon einem anderen Befehl gehört.
- Nach "Skizze beenden" erscheint in der 3D-Ansicht eine Schnellleiste mit Pad, Tasche, Drehen und Nut.
"""

import FreeCAD
import FreeCADGui as Gui
from PySide6 import QtCore, QtGui, QtWidgets

FUSION_VERSION = 1

# Fusion-Kürzel (Befehl -> Taste). Skizzen-Kürzel gelten nur im Skizzen-Modus, weil Sketcher-Befehle
# außerhalb der Skizze nicht aktiv sind.
SHORTCUTS = {
    "PartDesign_Pad": "E",
    "PartDesign_Pocket": "P",
    "PartDesign_Revolution": "R",
    "PartDesign_Hole": "H",
    "PartDesign_Fillet": "F",
    "PartDesign_Chamfer": "C",
    "PartDesign_Mirrored": "M",
    "PartDesign_LinearPattern": "U",
    "PartDesign_NewSketch": "S",
    "Sketcher_CreateLine": "L",
    "Sketcher_CreateRectangle": "T",
    "Sketcher_CreateCircle": "O",
    "Sketcher_CreateArc": "A",
    "Sketcher_CreatePolyline": "W",
    "Sketcher_ConstrainDistance": "D",
    "Sketcher_Trimming": "X",
}


def apply_defaults():
    """Einmal je FUSION_VERSION: Navigation und Kürzel setzen (Nutzer können beides später ändern)."""
    mint = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD")
    if mint.GetInt("FusionVersion", 0) >= FUSION_VERSION:
        return
    view = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
    view.SetString("NavigationStyle", "Gui::RevitNavigationStyle")
    view.SetBool("ZoomAtCursor", True)
    view.SetBool("InvertZoom", False)
    view.SetBool("DisableTouchTilt", True)
    mint.SetInt("FusionVersion", FUSION_VERSION)


def apply_shortcuts():
    """Setzt die Fusion-Kürzel, soweit die Taste frei ist."""
    mint = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/MintCAD")
    if not mint.GetBool("FusionShortcuts", True):
        return
    # Frühere Version hatte S fälschlich auf dem allgemeinen Sketcher-Befehl (ohne Körper-Bezug): zurücksetzen
    try:
        old = Gui.Command.get("Sketcher_NewSketch")
        if old is not None and old.getShortcut() == "S":
            old.resetShortcut()
    except Exception:
        pass
    used = {}
    for name in Gui.Command.listAll():
        try:
            key = Gui.Command.get(name).getShortcut()
        except Exception:
            key = ""
        if key:
            used.setdefault(key.upper(), []).append(name)
    for name, key in SHORTCUTS.items():
        try:
            cmd = Gui.Command.get(name)
        except Exception:
            cmd = None
        if cmd is None:
            continue
        owners = [n for n in used.get(key.upper(), []) if n != name]
        if owners:
            FreeCAD.Console.PrintLog("MINT-CAD: Kürzel %s für %s übersprungen (belegt von %s)\n" % (key, name, owners))
            continue
        try:
            if cmd.getShortcut() != key:
                cmd.setShortcut(key)
        except Exception as exc:
            FreeCAD.Console.PrintLog("MINT-CAD: Kürzel %s: %s\n" % (name, exc))


# ----------------------------------------------------------------------------- Schnellleiste
QUICK_STYLE = """
#MintQuickBar { background: rgba(15, 23, 42, 235); border: 1px solid #334155; border-radius: 10px; }
#MintQuickBar QLabel { color: #94a3b8; font-size: 11px; padding: 0 6px; }
#MintQuickBar QToolButton { color: #e2e8f0; background: transparent; border: 1px solid transparent;
    border-radius: 6px; padding: 4px 8px; font-size: 12px; }
#MintQuickBar QToolButton:hover { background: #1e293b; border-color: #334155; }
#MintQuickBar QToolButton:disabled { color: #475569; }
#MintQuickBar QToolButton#close { color: #94a3b8; padding: 2px 6px; }
"""
QUICK_COMMANDS = [
    ("PartDesign_Pad", "Pad"),
    ("PartDesign_Pocket", "Tasche"),
    ("PartDesign_Revolution", "Drehen"),
    ("PartDesign_Groove", "Nut"),
]


class QuickBar(QtWidgets.QFrame):
    """Schwebende Leiste unten in der 3D-Ansicht; verschwindet bei Klick oder nach einigen Sekunden."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("MintQuickBar")
        self.setStyleSheet(QUICK_STYLE)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(2)
        lay.addWidget(QtWidgets.QLabel("Skizze fertig – weiter mit:"))
        for cmd, text in QUICK_COMMANDS:
            btn = QtWidgets.QToolButton()
            btn.setText(text)
            btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            try:
                pix = Gui.Command.get(cmd).getInfo().get("pixmap", "")
                if pix:
                    btn.setIcon(Gui.getIcon(pix))
            except Exception:
                pass
            btn.clicked.connect(lambda _=False, c=cmd: self._run(c))
            lay.addWidget(btn)
        close = QtWidgets.QToolButton()
        close.setObjectName("close")
        close.setText("✕")
        close.clicked.connect(self.hide)
        lay.addWidget(close)
        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self.hide()

    def _run(self, cmd):
        self.hide()
        try:
            Gui.runCommand(cmd)
        except Exception as exc:
            FreeCAD.Console.PrintWarning("MINT-CAD: %s: %s\n" % (cmd, exc))

    def popup(self, seconds=12):
        host = self.parentWidget()
        if host is None:
            return
        self.adjustSize()
        self.move((host.width() - self.width()) // 2, host.height() - self.height() - 24)
        self.show()
        self.raise_()
        self._timer.start(seconds * 1000)


def _view_widget():
    """Das Widget der aktiven 3D-Ansicht (Ankerfläche für die Schnellleiste)."""
    mw = Gui.getMainWindow()
    area = mw.findChild(QtWidgets.QMdiArea)
    sub = area.activeSubWindow() if area else None
    return sub.widget() if sub else None


class _Observer:
    """Merkt sich die Skizze, die gerade bearbeitet wird, und zeigt nach dem Beenden die Schnellleiste."""

    def __init__(self):
        self._edited = None
        self._bar = None

    def slotInEdit(self, vp):
        try:
            obj = vp.Object
            self._edited = obj.Name if obj.TypeId == "Sketcher::SketchObject" else None
        except Exception:
            self._edited = None

    def slotResetEdit(self, vp):
        name, self._edited = self._edited, None
        if not name:
            return
        QtCore.QTimer.singleShot(150, lambda: self._offer(name))

    def _offer(self, name):
        doc = FreeCAD.ActiveDocument
        sketch = doc.getObject(name) if doc else None
        if sketch is None or not sketch.Shape.Wires:
            return
        if any(o.TypeId.startswith("PartDesign::") and getattr(o, "Profile", None) and o.Profile[0] == sketch
               for o in sketch.InList):
            return  # Skizze wird schon benutzt (Skizze wurde nur nachbearbeitet)
        host = _view_widget()
        if host is None:
            return
        if self._bar is None or self._bar.parentWidget() is not host:
            self._bar = QuickBar(host)
        # Skizze markieren, damit Pad/Tasche sie sofort als Profil übernehmen
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(sketch)
        self._bar.popup()


def install():
    Gui.addDocumentObserver(_Observer())
    apply_shortcuts()
    # Befehle eines Arbeitsbereichs gibt es erst nach dessen Laden: Kürzel bei jedem Wechsel nachziehen
    Gui.getMainWindow().workbenchActivated.connect(lambda *_: QtCore.QTimer.singleShot(400, apply_shortcuts))
