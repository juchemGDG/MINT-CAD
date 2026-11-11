# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Parameter-Dialog (wie "Parameter ändern" in Fusion).

Zwei Register:
- Eigene Parameter: Tabelle "Parameter" (Tabellenblatt) mit Name, Wert und Kommentar. Der Name wird als
  Alias der Zelle gesetzt; in jedem Maßfeld kann man dann  =Parameter.Name  eintragen.
- Modellmaße: alle treibenden Maße der Skizzen und die Längen/Radien/Durchmesser der Part-Design-Features.
  Ein Wert kann als Zahl (mm bzw. Grad) oder als Formel mit "=" beginnend eingegeben werden.
"""

import re

import FreeCAD
import FreeCADGui as Gui
from PySide6 import QtCore, QtGui, QtWidgets

SHEET_NAME = "Parameter"

# Feature-Typ -> [(Eigenschaft, Anzeigename)]
FEATURE_PROPS = {
    "PartDesign::Pad": [("Length", "Länge")],
    "PartDesign::Pocket": [("Length", "Tiefe")],
    "PartDesign::Revolution": [("Angle", "Winkel")],
    "PartDesign::Groove": [("Angle", "Winkel")],
    "PartDesign::Hole": [("Diameter", "Durchmesser"), ("Depth", "Tiefe")],
    "PartDesign::Fillet": [("Radius", "Radius")],
    "PartDesign::Chamfer": [("Size", "Größe")],
    "PartDesign::LinearPattern": [("Length", "Länge"), ("Occurrences", "Anzahl")],
    "PartDesign::PolarPattern": [("Angle", "Winkel"), ("Occurrences", "Anzahl")],
}
DATUM_TYPES = ("Distance", "DistanceX", "DistanceY", "Radius", "Diameter", "Angle")


def _split_name(label):
    """Erlaubt nur gültige Aliasnamen (Buchstaben, Ziffern, _); sonst None."""
    return label if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", label or "") else None


def _is_unit(name):
    try:
        FreeCAD.Units.Quantity("1 " + name)
        return True
    except Exception:
        return False


def _fmt(value):
    try:
        return value.UserString
    except Exception:
        return str(value)


def _quantity(text, default_unit):
    """Text -> Quantity; reine Zahlen erhalten die Standardeinheit."""
    text = text.strip().replace(",", ".")
    if re.fullmatch(r"[-+]?\d+(\.\d+)?", text):
        text += " " + default_unit
    return FreeCAD.Units.Quantity(text)


class ParamDialog(QtWidgets.QDialog):
    def __init__(self, doc, parent=None):
        super().__init__(parent or Gui.getMainWindow())
        self.doc = doc
        self.setWindowTitle("Parameter")
        self.resize(720, 480)
        lay = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        lay.addWidget(self.tabs)

        # Eigene Parameter
        w1 = QtWidgets.QWidget()
        l1 = QtWidgets.QVBoxLayout(w1)
        l1.addWidget(QtWidgets.QLabel(
            "Eigene Parameter gelten im ganzen Dokument. In ein Maßfeld schreibt man  =Parameter.Name"))
        self.user = QtWidgets.QTableWidget(0, 3)
        self.user.setHorizontalHeaderLabels(["Name", "Wert / Formel", "Kommentar"])
        self.user.horizontalHeader().setStretchLastSection(True)
        self.user.setColumnWidth(0, 160)
        self.user.setColumnWidth(1, 200)
        l1.addWidget(self.user)
        row = QtWidgets.QHBoxLayout()
        add = QtWidgets.QPushButton("＋ Parameter")
        add.clicked.connect(lambda: self._add_user_row("", "", ""))
        row.addWidget(add)
        row.addStretch(1)
        l1.addLayout(row)
        self.tabs.addTab(w1, "Eigene Parameter")

        # Modellmaße
        w2 = QtWidgets.QWidget()
        l2 = QtWidgets.QVBoxLayout(w2)
        l2.addWidget(QtWidgets.QLabel("Maße der Skizzen und Features. Zahl = mm bzw. Grad; Formel mit =  beginnen."))
        self.model = QtWidgets.QTableWidget(0, 3)
        self.model.setHorizontalHeaderLabels(["Objekt", "Maß", "Wert / Formel"])
        self.model.horizontalHeader().setStretchLastSection(True)
        self.model.setColumnWidth(0, 200)
        self.model.setColumnWidth(1, 200)
        l2.addWidget(self.model)
        self.tabs.addTab(w2, "Modellmaße")

        self.msg = QtWidgets.QLabel("")
        self.msg.setStyleSheet("color: #dc2626;")
        lay.addWidget(self.msg)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Apply | QtWidgets.QDialogButtonBox.Close)
        buttons.button(QtWidgets.QDialogButtonBox.Apply).setText("Übernehmen")
        buttons.button(QtWidgets.QDialogButtonBox.Close).setText("Schließen")
        buttons.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.apply)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)
        self._model_rows = []
        self.load()

    # -- Laden -------------------------------------------------------------------------------
    def load(self):
        self.user.setRowCount(0)
        sheet = self.doc.getObject(SHEET_NAME)
        if sheet is not None:
            r = 1
            while True:
                alias = sheet.getAlias("B%d" % r)
                content = sheet.getContents("B%d" % r)
                if not alias and not content:
                    break
                self._add_user_row(alias or "", content, sheet.getContents("C%d" % r))
                r += 1
        if self.user.rowCount() == 0:
            self._add_user_row("", "", "")
        self._load_model()

    def _add_user_row(self, name, value, comment):
        r = self.user.rowCount()
        self.user.insertRow(r)
        for c, text in enumerate((name, value, comment)):
            self.user.setItem(r, c, QtWidgets.QTableWidgetItem(text))

    def _load_model(self):
        self.model.setRowCount(0)
        self._model_rows = []
        for obj in self.doc.Objects:
            if obj.TypeId == "Sketcher::SketchObject":
                for i, con in enumerate(obj.Constraints):
                    if con.Type in DATUM_TYPES and con.Driving:
                        name = con.Name or "Maß %d" % (i + 1)
                        expr = dict((p, e) for p, e in obj.ExpressionEngine)
                        key = "Constraints.%s" % con.Name if con.Name else None
                        text = "=" + expr[key] if key and key in expr else _fmt(obj.getDatum(i))
                        self._add_model_row(obj.Label, name, text, ("sketch", obj.Name, i))
            elif obj.TypeId in FEATURE_PROPS:
                expr = dict((p, e) for p, e in obj.ExpressionEngine)
                for prop, label in FEATURE_PROPS[obj.TypeId]:
                    if not hasattr(obj, prop):
                        continue
                    text = "=" + expr[prop] if prop in expr else _fmt(getattr(obj, prop))
                    self._add_model_row(obj.Label, label, text, ("feature", obj.Name, prop))

    def _add_model_row(self, obj_label, name, text, ref):
        r = self.model.rowCount()
        self.model.insertRow(r)
        a = QtWidgets.QTableWidgetItem(obj_label)
        b = QtWidgets.QTableWidgetItem(name)
        for it in (a, b):
            it.setFlags(it.flags() & ~QtCore.Qt.ItemIsEditable)
        self.model.setItem(r, 0, a)
        self.model.setItem(r, 1, b)
        self.model.setItem(r, 2, QtWidgets.QTableWidgetItem(text))
        self._model_rows.append((ref, text))

    # -- Übernehmen ----------------------------------------------------------------------------
    def apply(self):
        self.msg.setText("")
        errors = []
        self.doc.openTransaction("Parameter ändern")
        try:
            self._apply_user(errors)
            self._apply_model(errors)
            self.doc.recompute()
            self.doc.commitTransaction()
        except Exception as exc:
            self.doc.abortTransaction()
            errors.append(str(exc))
        if errors:
            self.msg.setText("; ".join(errors[:3]))
        self._load_model_after_apply()

    def _load_model_after_apply(self):
        # Anzeige neu aufbauen, damit berechnete Werte stimmen
        self.load()

    def _apply_user(self, errors):
        rows = []
        for r in range(self.user.rowCount()):
            name, value, comment = (self.user.item(r, c).text().strip() if self.user.item(r, c) else ""
                                    for c in range(3))
            if not name and not value:
                continue
            if _split_name(name) is None:
                errors.append("Ungültiger Name „%s“ (nur Buchstaben, Ziffern, _)" % name)
                continue
            if _is_unit(name):
                errors.append("„%s“ ist eine Einheit und kann nicht als Name dienen" % name)
                continue
            rows.append((name, value, comment))
        if not rows:
            return
        sheet = self.doc.getObject(SHEET_NAME)
        if sheet is None:
            sheet = self.doc.addObject("Spreadsheet::Sheet", SHEET_NAME)
            sheet.Label = SHEET_NAME
        for r in range(1, 200):
            if sheet.getContents("B%d" % r) or sheet.getAlias("B%d" % r):
                sheet.clear("A%d:C%d" % (r, r))
                sheet.setAlias("B%d" % r, "")
        for r, (name, value, comment) in enumerate(rows, 1):
            sheet.set("A%d" % r, name)
            sheet.set("B%d" % r, value if value.startswith("=") else "=" + value.replace(",", "."))
            if comment:
                sheet.set("C%d" % r, comment)
            sheet.setAlias("B%d" % r, name)
        sheet.recompute()

    def _apply_model(self, errors):
        for r, (ref, old) in enumerate(self._model_rows):
            item = self.model.item(r, 2)
            text = item.text().strip() if item else old
            if text == old:
                continue
            kind, name, key = ref
            obj = self.doc.getObject(name)
            try:
                if kind == "sketch":
                    self._set_sketch(obj, key, text)
                else:
                    self._set_feature(obj, key, text)
            except Exception as exc:
                errors.append("%s: %s" % (obj.Label if obj else name, exc))

    @staticmethod
    def _set_sketch(sketch, index, text):
        con = sketch.Constraints[index]
        if text.startswith("="):
            if not con.Name:
                sketch.renameConstraint(index, "Mass%d" % (index + 1))
                con = sketch.Constraints[index]
            sketch.setExpression("Constraints.%s" % con.Name, text[1:].strip())
            return
        if con.Name:
            sketch.setExpression("Constraints.%s" % con.Name, None)
        unit = "deg" if con.Type == "Angle" else "mm"
        sketch.setDatum(index, _quantity(text, unit))

    @staticmethod
    def _set_feature(obj, prop, text):
        if text.startswith("="):
            obj.setExpression(prop, text[1:].strip())
            return
        obj.setExpression(prop, None)
        current = getattr(obj, prop)
        if isinstance(current, (int,)) and not hasattr(current, "Unit"):
            setattr(obj, prop, int(float(text.replace(",", "."))))
            return
        unit = "deg" if prop == "Angle" else "mm"
        setattr(obj, prop, _quantity(text, unit))


# ----------------------------------------------------------------------------- Namen direkt in Maßfeldern
_TOKEN = re.compile(r"(?<![\w.])([A-Za-z_]\w*)(?!\s*\()")


def param_names(doc=None):
    """Namen (Aliase) der eigenen Parameter im aktiven Dokument."""
    doc = doc or FreeCAD.ActiveDocument
    sheet = doc.getObject(SHEET_NAME) if doc else None
    names = {}
    if sheet is None:
        return names
    for r in range(1, 200):
        alias = sheet.getAlias("B%d" % r)
        if alias:
            names[alias] = r
        elif not sheet.getContents("B%d" % r):
            break
    return names


def expand_names(text, doc=None):
    """'Breite/2' -> 'Parameter.Breite/2' (ohne führendes '='), None wenn kein Parameter vorkommt.

    Eine angehängte Einheit ("Breite mm", weil das Feld sie stehen ließ) wird entfernt, wenn der Parameter
    selbst schon eine Einheit hat."""
    names = param_names(doc)
    if not names or not text or text.lstrip().startswith("="):
        return None
    hit = {}

    def repl(m):
        tok = m.group(1)
        if tok in names:
            hit[tok] = True
            return SHEET_NAME + "." + tok
        return tok

    out = _TOKEN.sub(repl, text.strip())
    if not hit:
        return None
    sheet = (doc or FreeCAD.ActiveDocument).getObject(SHEET_NAME)
    m = re.search(r"\s+([A-Za-z]+)$", out)
    if m and _is_unit(m.group(1)) and m.group(1) not in names:
        has_unit = False
        for tok in hit:
            try:
                has_unit = has_unit or hasattr(sheet.get(tok), "Unit") and str(sheet.get(tok).Unit) != "Unit: (0,0,0,0,0,0,0,0)"
            except Exception:
                pass
        if has_unit:
            out = out[: m.start()]
    return out.replace(",", ".") if re.fullmatch(r"[\w.+\-*/() ]+", out.replace(",", ".")) else out


class _FieldFilter(QtCore.QObject):
    """Maßfelder: Parametername tippen (Enter oder kurze Pause) -> Formel =Parameter.Name wird gesetzt."""

    def __init__(self, parent):
        super().__init__(parent)

    @staticmethod
    def _spin_of(widget):
        sp = widget.parent()
        if isinstance(sp, QtWidgets.QAbstractSpinBox) and "QuantitySpinBox" in sp.metaObject().className():
            return sp
        return None

    def watch(self, line):
        if line.property("mintParamHook"):
            return
        line.setProperty("mintParamHook", True)
        line.installEventFilter(self)
        timer = QtCore.QTimer(line)  # gehört dem Feld und endet mit ihm
        timer.setObjectName("mintParamTimer")
        timer.setSingleShot(True)
        timer.timeout.connect(lambda tm=timer: self._convert(tm.parent(), False))
        line.textEdited.connect(lambda _t, tm=timer: tm.start(900))

    def _schedule(self, line):
        self.watch(line)
        line.findChild(QtCore.QTimer, "mintParamTimer").start(900)

    def eventFilter(self, obj, ev):
        if ev.type() == QtCore.QEvent.KeyPress and ev.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            if self._convert(obj, True):
                return True
        return False

    def _convert(self, line, confirm):
        try:
            sp = self._spin_of(line)
            if sp is None:
                return False
            expr = expand_names(line.text())
            if not expr:
                return False
            line.setText("")
            # "=" im Feld öffnet den Formeleditor; dort Ausdruck eintragen und bestätigen
            sp.setFocus()
            QtWidgets.QApplication.sendEvent(sp, QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Equal,
                                                                  QtCore.Qt.NoModifier, "="))
            QtCore.QTimer.singleShot(60, lambda: self._fill_dialog(sp, expr, confirm))
            return True
        except Exception as exc:
            FreeCAD.Console.PrintWarning("MINT-CAD: Parameter im Feld: %s\n" % exc)
            return False

    def _fill_dialog(self, spin, expr, confirm):
        for w in QtWidgets.QApplication.topLevelWidgets():
            if w.isVisible() and "DlgExpressionInput" in w.metaObject().className():
                edit = w.findChild(QtWidgets.QWidget, "expression")  # ExpressionTextEdit (Textfeld, kein QLineEdit)
                if edit is None:
                    continue
                edit.setPlainText(expr)
                QtCore.QTimer.singleShot(250, lambda box=w, ex=expr: self._press_ok(box, ex))
                if confirm:
                    win = spin.window()
                    if isinstance(win, QtWidgets.QDialog):
                        QtCore.QTimer.singleShot(700, win.accept)
                return

    @staticmethod
    def _press_ok(box, expr):
        ok = [b for b in box.findChildren(QtWidgets.QPushButton) if b.text().replace("&", "") in ("OK", "Ok")]
        if ok and ok[0].isEnabled():
            ok[0].click()
        else:
            FreeCAD.Console.PrintWarning("MINT-CAD: Ausdruck nicht übernommen: %s\n" % expr)
            box.reject()


_field_filter = None


def install_fields():
    """Aktiviert die Parameternamen in Maßfeldern (Skizzenmaße, Pad-Länge usw.)."""
    global _field_filter
    if _field_filter is not None:
        return
    _field_filter = _FieldFilter(Gui.getMainWindow())

    def focus_changed(_old, new):
        if isinstance(new, QtWidgets.QLineEdit) and _field_filter._spin_of(new) is not None:
            _field_filter.watch(new)

    QtWidgets.QApplication.instance().focusChanged.connect(focus_changed)

    # Modale Dialoge (z. B. "Länge eingeben" in der Skizze): Felder gleich beim Öffnen anbinden
    def scan():
        modal = QtWidgets.QApplication.activeModalWidget()
        if modal is not None:
            for sp in modal.findChildren(QtWidgets.QAbstractSpinBox):
                if "QuantitySpinBox" in sp.metaObject().className():
                    _field_filter.watch(sp.lineEdit())

    timer = QtCore.QTimer(_field_filter)
    timer.timeout.connect(scan)
    timer.start(400)


class _ParametersCommand:
    def GetResources(self):
        return {"MenuText": "Parameter", "ToolTip": "Maße und eigene Parameter in einer Tabelle ändern",
                "Pixmap": "Spreadsheet"}

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        ParamDialog(FreeCAD.ActiveDocument).exec()


def register():
    Gui.addCommand("MintCAD_Parameters", _ParametersCommand())
