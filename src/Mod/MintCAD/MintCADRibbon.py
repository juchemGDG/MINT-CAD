# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Menüband (Ribbon) mit Registerkarten, Gruppen und großen Icons.

Das Menüband baut seine Schaltflächen aus den vorhandenen FreeCAD-Werkzeugleisten auf und
verwendet dieselben Befehle (QAction): Zustand (aktiv/gedrückt), Ausklappmenüs und Tastenkürzel
bleiben erhalten. Die ursprünglichen Werkzeugleisten werden ausgeblendet.

Die Zuordnung "Arbeitsbereich -> Registerkarten -> Gruppen -> Werkzeugleiste" steht in RIBBON.
"""

import FreeCAD
import FreeCADGui as Gui
from PySide6 import QtCore, QtGui, QtWidgets

# Werkzeugleisten, die immer sichtbar bleiben (obere Schnellzugriffszeile)
QUICK_TOOLBARS = ("File", "Edit", "Workbench")

# Registerkarte für alle Arbeitsbereiche
VIEW_TAB = ("Ansicht", [("Ansicht", "View"), ("Standardansichten", "Individual Views")])

# Arbeitsbereich -> [(Registerkarte, [(Gruppenname, interne Name der Werkzeugleiste), ...]), ...]
RIBBON = {
    "PartDesignWorkbench": [
        (
            "Modell",
            [
                ("Körper und Skizze", "Part Design Helper Features"),
                ("Erzeugen", "Part Design Modeling Features"),
                ("Ändern", "Part Design Dress-Up Features"),
                ("Anordnen", "Part Design Transformation Features"),
            ],
        ),
    ],
    "TechDrawWorkbench": [
        ("Blatt und Ansichten", [("Blatt", "TechDraw Pages"), ("Ansichten", "TechDraw Views")]),
        ("Bemaßen", [("Maße", "TechDraw Dimensions"), ("Mittellinien", "TechDraw Centerlines")]),
        ("Beschriften", [("Beschriftung", "TechDraw Annotation"), ("Schraffur", "TechDraw Decoration")]),
        ("Ausgabe", [("Export", "TechDraw File Access")]),
    ],
    "DraftWorkbench": [
        ("Zeichnen", [("Erzeugen", "Draft Creation")]),
        ("Ändern", [("Ändern", "Draft Modification")]),
        ("Beschriften", [("Beschriften", "Draft Annotation"), ("Hilfen", "Draft Utility")]),
    ],
    "AssemblyWorkbench": [
        ("Baugruppe", [("Baugruppe", "Assembly"), ("Verbindungen", "Assembly Joints")]),
    ],
    "FemWorkbench": [
        ("Modell", [("Analyse", "Model")]),
        ("Randbedingungen", [("Mechanisch", "Mechanical Boundary Conditions and Loads")]),
        ("Netz und Lösen", [("Netz", "Mesh"), ("Löser", "Solve")]),
        ("Ergebnisse", [("Ergebnisse", "Results"), ("Hilfen", "Utilities")]),
    ],
}

# Während der Skizzenbearbeitung (zusätzliche Registerkarte, wird automatisch gewählt)
SKETCH_TAB = (
    "Skizze",
    [
        ("Beenden", "Edit Mode"),
        ("Zeichnen", "Geometries"),
        ("Randbedingungen", "Constraints"),
        ("Werkzeuge", "Sketcher Tools"),
        ("Hilfen", "Visual Helpers"),
    ],
)

# Kurze deutsche Beschriftungen für große Schaltflächen (Befehl -> Text); sonst die FreeCAD-Übersetzung
LABELS = {
    "MintCAD_Parameters": "Parameter",
    "PartDesign_Body": "Körper",
    "PartDesign_CompSketches": "Skizze",
    "Sketcher_ValidateSketch": "Prüfen",
    "Part_CheckGeometry": "Geometrie",
    "PartDesign_Pad": "Pad",
    "PartDesign_Revolution": "Drehen",
    "PartDesign_CompPrimitiveAdditive": "Grundkörper +",
    "PartDesign_CompPrimitiveSubtractive": "Grundkörper −",
    "PartDesign_Pocket": "Tasche",
    "PartDesign_Hole": "Bohrung",
    "PartDesign_Groove": "Nut",
    "PartDesign_Fillet": "Rundung",
    "PartDesign_Chamfer": "Fase",
    "PartDesign_Plane": "Bezugsebene",
    "PartDesign_Line": "Referenzlinie",
    "TechDraw_ProjectionGroup": "Ansichten",
    "PartDesign_Mirrored": "Spiegeln",
    "PartDesign_LinearPattern": "Muster",
    "PartDesign_PolarPattern": "Kreismuster",
    "Sketcher_NewSketch": "Neue Skizze",
    "Sketcher_LeaveSketch": "Beenden",
    "Sketcher_ViewSketch": "Ansicht",
    "Sketcher_ViewSection": "Schnitt",
    "TechDraw_PageDefault": "Standardblatt",
    "TechDraw_PageTemplate": "Blatt (Vorlage)",
    "TechDraw_FillTemplateFields": "Felder füllen",
    "TechDraw_RedrawPage": "Aktualisieren",
    "TechDraw_PrintAll": "Drucken",
    "TechDraw_View": "Ansicht",
    "TechDraw_SectionGroup": "Schnitt",
    "TechDraw_DetailView": "Detail",
    "TechDraw_Balloon": "Positionsnr.",
    "TechDraw_ExportPageSVG": "SVG",
    "TechDraw_ExportPageDXF": "DXF",
}

LARGE_ICON = 36
SMALL_ICON = 28
COMPACT_ICON = 36  # Gruppen mit nur einer Zeile von Icons (z. B. Ansicht) wie die großen Schaltflächen
LARGE_MAX_BUTTONS = 7  # Gruppen mit mehr Schaltflächen werden kompakt (nur Icons) dargestellt
BUTTON_WIDTH = 84
RIBBON_HEIGHT = 128

STYLE = """
#MintRibbon { background: #0f172a; }
#MintRibbon QTabBar::tab { background: transparent; color: #94a3b8; padding: 5px 14px; margin-right: 2px;
    border: none; border-bottom: 2px solid transparent; font-size: 13px; }
#MintRibbon QTabBar::tab:selected { color: #f8fafc; border-bottom: 2px solid #2563eb; }
#MintRibbon QTabBar::tab:hover:!selected { color: #e2e8f0; }
#MintRibbonPage { background: #0f172a; border-top: 1px solid #1e293b; }
#MintRibbonGroup QLabel { color: #94a3b8; font-size: 11px; }
#MintRibbonSep { background: #1e293b; }
#MintRibbon QToolButton { background: transparent; color: #e2e8f0; border: 1px solid transparent;
    border-radius: 6px; padding: 3px; font-size: 11px; }
#MintRibbon QToolButton:hover { background: #1e293b; border-color: #334155; }
#MintRibbon QToolButton:checked { background: #2563eb; border-color: #1d4ed8; }
#MintRibbon QToolButton:disabled { color: #475569; }
#MintRibbon QToolButton::menu-indicator { image: none; }
"""


def _find_toolbar(name):
    for tb in Gui.getMainWindow().findChildren(QtWidgets.QToolBar):
        if tb.objectName() == name:
            return tb
    return None


def _command_icon(action, size):
    """Icon in ausreichender Größe: bevorzugt das Befehls-Icon, sonst das der QAction (ggf. skaliert)."""
    name = str(action.data() or "")
    icon = None
    if name:
        try:
            pix = Gui.Command.get(name).getInfo().get("pixmap", "")
            if pix:
                icon = Gui.getIcon(pix)
        except Exception:
            icon = None
    if icon is None or icon.isNull():
        icon = action.icon()
    pm = icon.pixmap(QtCore.QSize(size, size))
    if not pm.isNull() and pm.width() < size * pm.devicePixelRatio() * 0.9:
        pm = pm.scaled(size * 2, size * 2, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        pm.setDevicePixelRatio(2.0)
    return QtGui.QIcon(pm)


class _ProxyButton(QtWidgets.QToolButton):
    """Schaltfläche, die eine bestehende QAction auslöst und deren Zustand spiegelt."""

    def __init__(self, action, native_button, large, parent=None, compact_size=None):
        super().__init__(parent)
        self._action = action
        self._large = large
        self._icon = LARGE_ICON if large else (compact_size or SMALL_ICON)
        self.setAutoRaise(True)
        self.setCheckable(action.isCheckable())
        self.setIconSize(QtCore.QSize(self._icon, self._icon))
        if large:
            self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            self.setFixedWidth(BUTTON_WIDTH)
        else:
            self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        menu = native_button.menu() if isinstance(native_button, QtWidgets.QToolButton) else None
        if menu is not None:
            self.setMenu(menu)
            self.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.clicked.connect(self._on_click)
        action.changed.connect(self._sync)
        self._sync()

    def _on_click(self):
        self._action.trigger()

    def _sync(self):
        a = self._action
        self.setIcon(_command_icon(a, self._icon))
        self.setEnabled(a.isEnabled())
        self.setToolTip(a.toolTip() or a.text())
        self.setStatusTip(a.statusTip())
        if self.isCheckable():
            self.setChecked(a.isChecked())
        if self._large:
            text = LABELS.get(str(a.data()), a.text()).replace("&", "").replace("...", "").replace("…", "")
            fm = QtGui.QFontMetrics(self.font())
            self.setText(fm.elidedText(text, QtCore.Qt.ElideRight, BUTTON_WIDTH - 8))


class _Group(QtWidgets.QWidget):
    def __init__(self, caption, toolbar, parent=None):
        super().__init__(parent)
        self.setObjectName("MintRibbonGroup")
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(6, 2, 6, 2)
        lay.setSpacing(0)
        items = []
        for a in toolbar.actions():
            if a.isSeparator() or not a.isVisible():
                continue
            w = toolbar.widgetForAction(a)
            if w is not None and not isinstance(w, QtWidgets.QToolButton):
                continue  # z. B. Arbeitsbereichs-Auswahl
            items.append((a, w))
        labels = [LABELS.get(str(a.data()), a.text()).replace("&", "") for a, _ in items]
        large = 0 < len(items) <= LARGE_MAX_BUTTONS and all(len(t) <= 16 for t in labels)
        self.count = len(items)
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(2)
        grid.setContentsMargins(0, 0, 0, 0)
        rows = 1 if (large or len(items) <= 8) else 2
        cols = (len(items) + rows - 1) // rows
        for i, (a, w) in enumerate(items):
            btn = _ProxyButton(a, w, large, self, COMPACT_ICON if rows == 1 else None)
            grid.addWidget(btn, i // cols if rows > 1 else 0, i % cols if rows > 1 else i)
        lay.addLayout(grid)
        lay.addStretch(1)
        label = QtWidgets.QLabel(caption)
        label.setAlignment(QtCore.Qt.AlignHCenter)
        lay.addWidget(label)


class Ribbon(QtWidgets.QToolBar):
    def __init__(self, mw):
        super().__init__("MINT-CAD Menüband", mw)
        self.setObjectName("MintRibbonToolBar")
        self.setMovable(False)
        self.setFloatable(False)
        self._mw = mw
        self._tabs_def = []
        self._in_edit = False
        self._building = False
        host = QtWidgets.QWidget()
        host.setObjectName("MintRibbon")
        host.setStyleSheet(STYLE)
        v = QtWidgets.QVBoxLayout(host)
        v.setContentsMargins(6, 0, 6, 4)
        v.setSpacing(0)
        self.tabbar = QtWidgets.QTabBar()
        self.tabbar.setExpanding(False)
        self.tabbar.setDrawBase(False)
        self.tabbar.currentChanged.connect(self._show_page)
        v.addWidget(self.tabbar)
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setObjectName("MintRibbonPage")
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.stack)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setFixedHeight(RIBBON_HEIGHT)
        scroll.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        scroll.setStyleSheet("QScrollArea { background: transparent; } QScrollBar:horizontal { height: 8px; }")
        v.addWidget(scroll)
        host.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.addWidget(host)

    # -- Aufbau ----------------------------------------------------------------------------
    def rebuild(self, keep_tab=None):
        if self._building:
            return
        self._building = True
        try:
            wb = Gui.activeWorkbench().name() if Gui.activeWorkbench() else ""
            tabs = list(RIBBON.get(wb, []))
            in_edit = self._sketch_in_edit()
            if tabs or in_edit:
                tabs.append(VIEW_TAB)
            if in_edit:
                tabs.insert(0, SKETCH_TAB)
            self._tabs_def = tabs
            previous = keep_tab if keep_tab is not None else self.tabbar.tabText(self.tabbar.currentIndex())
            while self.tabbar.count():
                self.tabbar.removeTab(0)
            while self.stack.count():
                w = self.stack.widget(0)
                self.stack.removeWidget(w)
                w.deleteLater()
            for title, groups in tabs:
                self.tabbar.addTab(title)
                self.stack.addWidget(self._make_page(groups))
            index = 0
            if in_edit:
                index = 0  # Skizzenregister automatisch wählen
            else:
                for i in range(self.tabbar.count()):
                    if self.tabbar.tabText(i) == previous:
                        index = i
            if self.tabbar.count():
                self.tabbar.setCurrentIndex(index)
                self.stack.setCurrentIndex(index)
            self.setVisible(bool(tabs))
            self._hide_native_toolbars(bool(tabs))
        finally:
            self._building = False

    def _make_page(self, groups):
        page = QtWidgets.QWidget()
        lay = QtWidgets.QHBoxLayout(page)
        lay.setContentsMargins(4, 4, 4, 0)
        lay.setSpacing(0)
        first = True
        for caption, tbname in groups:
            tb = _find_toolbar(tbname)
            if tb is None:
                continue
            g = _Group(caption, tb, page)
            if not g.count:
                g.deleteLater()
                continue
            if not first:
                sep = QtWidgets.QFrame()
                sep.setObjectName("MintRibbonSep")
                sep.setFixedWidth(1)
                lay.addWidget(sep)
            lay.addWidget(g)
            first = False
        lay.addStretch(1)
        return page

    def _show_page(self, index):
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)

    # -- Werkzeugleisten ----------------------------------------------------------------------
    def _hide_native_toolbars(self, hide_all):
        if not hide_all:
            return
        for tb in self._mw.findChildren(QtWidgets.QToolBar):
            if tb is self or tb.objectName() in QUICK_TOOLBARS:
                continue
            tb.setVisible(False)

    @staticmethod
    def _sketch_in_edit():
        try:
            doc = Gui.ActiveDocument
            return bool(doc and doc.getInEdit() and doc.getInEdit().Object.TypeId == "Sketcher::SketchObject")
        except Exception:
            return False


_ribbon = None


class _Observer:
    """Reagiert auf Skizzenbearbeitung."""

    def slotInEdit(self, *_):
        _schedule()

    def slotResetEdit(self, *_):
        _schedule()


def _schedule(delay=60):
    QtCore.QTimer.singleShot(delay, lambda: _ribbon and _ribbon.rebuild())


def install():
    """Wird nach dem Start der Oberfläche aufgerufen."""
    global _ribbon
    mw = Gui.getMainWindow()
    if mw is None or _ribbon is not None:
        return
    mw.addToolBarBreak(QtCore.Qt.TopToolBarArea)
    _ribbon = Ribbon(mw)
    mw.addToolBar(QtCore.Qt.TopToolBarArea, _ribbon)
    mw.workbenchActivated.connect(lambda *_: _schedule(150))
    Gui.addDocumentObserver(_Observer())
    _schedule(300)
    import MintCADSetup

    QtCore.QTimer.singleShot(800, MintCADSetup.apply_layout)
