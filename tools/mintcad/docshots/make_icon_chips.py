# SPDX-License-Identifier: LGPL-2.1-or-later
"""Erzeugt Icon-Bilder für die Arbeitsblätter: die hellen MINT-CAD-Icons auf einem dunklen Chip (wie im Programm)."""
import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ICONS = sys.argv[1]
OUT = sys.argv[2]
NAMES = sys.argv[3:]
QGuiApplication([])
os.makedirs(OUT, exist_ok=True)
for name in NAMES:
    path = os.path.join(ICONS, name + ".svg")
    if not os.path.exists(path):
        print("fehlt:", name)
        continue
    img = QImage(96, 96, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
    p.setBrush(QColor("#0f172a"))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(QRectF(0, 0, 96, 96), 16, 16)
    QSvgRenderer(path).render(p, QRectF(12, 12, 72, 72))
    p.end()
    img.save(os.path.join(OUT, os.path.basename(name) + ".png"))
print("Icons:", len(NAMES))
