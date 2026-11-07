# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Kurzanleitung im Hilfe-Menü (Skizze -> Körper -> technische Zeichnung)."""

import FreeCAD
import FreeCADGui as Gui
from PySide6 import QtCore, QtWidgets

GUIDE_HTML = """
<style>
  body { color:#e2e8f0; font-size:14px; line-height:150%; }
  h1 { color:#f8fafc; font-size:24px; margin-bottom:0; }
  h2 { color:#60a5fa; font-size:17px; margin-top:22px; margin-bottom:4px; }
  .muted { color:#94a3b8; }
  b { color:#f8fafc; }
  li { margin-bottom:3px; }
</style>
<h1>MINT-CAD Kurzanleitung</h1>
<p class="muted">Vom Skizzieren über das 3D-Bauteil zur technischen Zeichnung.<br>Tipp: Hält man den Mauszeiger über ein Symbol, erscheint sein Name.</p>

<h2>1. Der Weg in drei Schritten</h2>
<ol>
  <li><b>Skizzieren</b> – im Arbeitsbereich <i>Part Design</i> eine neue Skizze anlegen und die Form zeichnen.</li>
  <li><b>Körper erzeugen</b> – aus der Skizze mit <i>Pad</i> (Ausformen), <i>Rotation</i> oder <i>Tasche</i> ein 3D-Bauteil machen.</li>
  <li><b>Zeichnung ableiten</b> – im Arbeitsbereich <i>TechDraw</i> Ansichten einfügen, bemaßen und das Schriftfeld ausfüllen.</li>
</ol>

<h2>2. Skizze</h2>
<ul>
  <li>Arbeitsbereich <b>Part Design</b> wählen, <b>Neuer Körper</b>, dann <b>Neue Skizze</b> und eine Ebene (z. B. XY) wählen.</li>
  <li>Mit <b>Linie</b>, <b>Kreis</b>, <b>Rechteck</b> usw. zeichnen. Ein Klick setzt einen Punkt, <i>Esc</i> beendet das Werkzeug.</li>
  <li>Mit <b>Randbedingungen</b> (waagerecht, senkrecht, parallel, tangential …) und <b>Maßen</b> die Form festlegen.</li>
  <li>Die Skizze ist <b>vollständig bestimmt</b>, wenn die Linien grün werden und im Aufgabenbereich „Vollständig bestimmt“ steht.</li>
  <li>Mit <b>Skizze verlassen</b> (oder Schließen) zurück zum Körper.</li>
</ul>

<h2>3. Körper</h2>
<ul>
  <li><b>Pad</b> – zieht die Skizze in die Höhe (Länge eingeben).</li>
  <li><b>Tasche</b> – schneidet die Skizze aus dem Körper heraus. <b>Bohrung</b> macht runde Löcher.</li>
  <li><b>Rotation</b> – dreht ein Profil um eine Achse (z. B. für Wellen).</li>
  <li><b>Fase</b> und <b>Rundung</b> – Kanten brechen oder abrunden: erst Kante anklicken, dann Werkzeug.</li>
  <li><b>Muster</b> und <b>Spiegeln</b> wiederholen oder spiegeln Merkmale.</li>
</ul>

<h2>4. Technische Zeichnung</h2>
<ul>
  <li>Arbeitsbereich <b>TechDraw</b> wählen und <b>Standard-Zeichenblatt</b> einfügen (A4 quer mit Schulschriftfeld).</li>
  <li>Den Körper im Baum anklicken, dann <b>Ansicht einfügen</b>. Weitere Ansichten (von oben, von links) ergänzen,
      dazu <b>Schnitt</b> oder <b>Detailansicht</b> bei Bedarf.</li>
  <li>Maße setzen: <b>Maß</b> wählen, dann Kanten oder Punkte anklicken.</li>
  <li>Schriftfeld: Blatt anklicken und <b>Vorlagenfelder ausfüllen</b> (Benennung, Name, Klasse, Datum, Werkstoff).</li>
  <li>Ausgabe: <b>Export als SVG</b> oder über <i>Datei &rarr; Drucken/PDF</i>.</li>
  <li>Die Zeichnungen sind in der <b>1. Projektionsmethode</b> (Europa) angelegt.</li>
</ul>

<h2>5. Weitere Arbeitsbereiche</h2>
<ul>
  <li><b>Assembly</b> – einfache Baugruppen: Teile einfügen und mit Gelenken (fest, Dreh-, Schubgelenk …) verbinden.</li>
  <li><b>Draft</b> – 2D-Zeichnen ohne Körper, z. B. Pläne oder Skizzen mit Maßen.</li>
  <li><b>FEM</b> – Festigkeitsberechnung: Material, Einspannung, Kraft, Netz, Berechnen, Ergebnis.</li>
</ul>

<h2>6. Beispiele</h2>
<p>Auf der <b>Startseite</b> findest Du drei vorbereitete Beispiele (Winkelstück, Welle, Platte)
   mit Skizze, Körper und fertiger Zeichnung zum Ausprobieren und Nachbauen.</p>
"""


class _QuickGuide:
    def GetResources(self):
        return {
            "Pixmap": "WhatsThis",
            "MenuText": "Kurzanleitung",
            "ToolTip": "Zeigt die MINT-CAD Kurzanleitung",
        }

    def Activated(self):
        dlg = QtWidgets.QDialog(Gui.getMainWindow())
        dlg.setWindowTitle("MINT-CAD Kurzanleitung")
        dlg.resize(760, 640)
        lay = QtWidgets.QVBoxLayout(dlg)
        view = QtWidgets.QTextBrowser()
        view.setOpenExternalLinks(True)
        view.setHtml(GUIDE_HTML)
        lay.addWidget(view)
        close = QtWidgets.QPushButton("Schließen")
        close.clicked.connect(dlg.accept)
        row = QtWidgets.QHBoxLayout()
        row.addStretch()
        row.addWidget(close)
        lay.addLayout(row)
        dlg.exec()

    def IsActive(self):
        return True


def register():
    Gui.addCommand("MintCAD_QuickGuide", _QuickGuide())
